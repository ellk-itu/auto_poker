from threading import Timer

from .game_options import GameOptions
from auto_poker.player import Player
from event_emitter import EventEmitter
from pokerkit import NoLimitTexasHoldem, State

from src.common.event_loop import EventLoop

# Enums
from ..player.player_actions import PlayerActions  # pylint: disable=wrong-import-order
from ..serializable_state import SerializableState
from .emitted_events import EmittedEvents
from .game_events import GameEvents


# TODO: Add Some thing that makes it
# easier to do default action thing


class Game(EventLoop[GameEvents]):
    """
    Game engine.
    As of right now can only play texas Holdem
    """

    def __init__(
        self,
        players: list[Player],
        game_options: GameOptions,
    ):

        super().__init__(GameEvents)

        # Game Settings
        self.__ante: int = game_options.ante
        self.__small_blind: int = game_options.small_blind
        self.__big_blind: int = game_options.big_blind
        self.__min_bet: int = game_options.min_bet
        self.__starting_stacks: int = game_options.starting_stacks
        self.__round_blind_raise: int = game_options.round_blind_raise
        self.__blind_raise_amount: int = game_options.blind_raise_amount
        self.__player_response_time: int = game_options.player_response_time
        self.__current_round: int = 0

        # Players
        self.__players: list[Player] = players

        # Pokerkit State
        self.__state: State = NoLimitTexasHoldem.create_state(
            automations=(),
            ante_trimming_status=True,
            raw_antes=self.__ante,
            raw_blinds_or_straddles={self.__small_blind, self.__big_blind},
            min_bet=self.__min_bet,
            raw_starting_stacks=self.__starting_stacks,
            player_count=len(self.__players),
        )

        # Events
        self.event_emitter = EventEmitter()

    @property
    def __player_to_act(self) -> Player | None:
        """
        The player needed to act.
        Will return null if no player currently needs to act.
        """

        if self.__state.actor_index is None:
            return None

        return self.__players[self.__state.actor_index]

    @property
    def __is_game_won(self) -> bool:
        """
        Determines weather or not the game is won
        """

        return len(self.__players) <= 1

    @property
    def __next_event(self) -> GameEvents:
        """
        Get the next state based on board
        """

        if self.__state.can_push_chips():
            return GameEvents.PUSH_CHIPS

        if self.__state.can_pull_chips():
            return GameEvents.PULL_CHIPS

        if self.__state.can_post_ante():
            return GameEvents.POST_ANTE

        if self.__state.can_collect_bets():
            return GameEvents.COLLECT_BETS

        if self.__state.can_post_blind_or_straddle():
            return GameEvents.POST_BLIND

        if self.__state.can_burn_card():
            return GameEvents.BURN_CARD

        if self.__state.can_deal_hole():
            return GameEvents.DEAL_HOLE_CARDS

        if self.__state.can_deal_board():
            return GameEvents.DEAL_BOARD_CARDS

        if self.__state.can_kill_hand():
            return GameEvents.KILL_HAND

        if self.__state.can_show_or_muck_hole_cards():
            return GameEvents.SHOW_OR_MUCK

        return GameEvents.BETS

    def __update_pokerkit_state(self):
        """
        Creates a new pokerkit state based on the game
        """

        self.__state = NoLimitTexasHoldem.create_state(
            automations=(),
            ante_trimming_status=True,
            raw_antes=self.__ante,
            raw_blinds_or_straddles={self.__small_blind, self.__big_blind},
            min_bet=self.__min_bet,
            raw_starting_stacks=filter(lambda stack: stack > 0, self.__state.stacks),
            player_count=len(self.__players),
        )

    def __remove_out_players(self):
        """
        Removes players that are out of the game (have stack of <= 0)
        """
        for i, stack in enumerate(self.__state.stacks):
            if stack <= 0:
                self.event_emitter.emit(EmittedEvents.PLAYER_OUT, self.__players[i])
                del self.__players[i]

        for i, player in enumerate(self.__players):
            player.index = i

    def __raise_blinds(self):
        """
        Raise the blinds
        """

        if self.__current_round % self.__round_blind_raise != 0:
            return

        self.__small_blind += self.__blind_raise_amount
        self.__big_blind = self.__small_blind * 2

    def __handle_game_start(self):
        """
        Read the name...
        """
        self.event_emitter.emit(EmittedEvents.GAME_START)
        self.queue_event(GameEvents.ROUND_START)

    def __handle_round_start(self):
        """
        Increment [__current_round] and emit events
        """
        self.__current_round += 1
        self.event_emitter.emit(EmittedEvents.ROUND_START, self.__current_round)
        self.queue_event(GameEvents.DEFAULT)

    def __handle_post_ante(self):
        self.__state.post_ante()
        self.event_emitter.emit(
            EmittedEvents.POST_ANTE,
            self.__ante,
            tuple(self.__state.ante_poster_indices)[0],
        )
        self.queue_event(GameEvents.DEFAULT)

    def __handle_bet_collect(self):
        self.__state.collect_bets()
        self.event_emitter.emit(EmittedEvents.COLLECT_BETS)
        self.queue_event(GameEvents.DEFAULT)

    def __handle_post_blind(self):
        self.__state.post_blind_or_straddle()
        self.event_emitter.emit(EmittedEvents.POST_BLIND)
        self.queue_event(GameEvents.DEFAULT)
        # TODO Fix the emitter for blinds

    def __handle_burn_card(self):
        self.__state.burn_card("??")
        self.event_emitter.emit(EmittedEvents.BURN_CARD)
        self.queue_event(GameEvents.DEFAULT)

    def __handle_deal_hole(self):
        self.__state.deal_hole()
        self.event_emitter.emit(EmittedEvents.DEAL_HOLE_CARDS)
        self.queue_event(GameEvents.DEFAULT)

    def __handle_deal_board(self):
        self.__state.deal_board()
        self.event_emitter.emit(EmittedEvents.DEAL_BOARD_CARDS)
        self.queue_event(GameEvents.DEFAULT)
        # TODO fix board card for the emitter

    def __handle_kill_hand(self):
        self.__state.kill_hand()
        self.event_emitter.emit(EmittedEvents.KILL_HAND)
        self.queue_event(GameEvents.DEFAULT)

    def __handle_push_chips(self):
        self.__state.push_chips()
        self.event_emitter.emit(EmittedEvents.PUSH_CHIPS)
        self.queue_event(GameEvents.DEFAULT)

    def __handle_pull_chips(self):
        self.__state.pull_chips()
        self.event_emitter.emit(EmittedEvents.PULL_CHIPS)
        self.queue_event(GameEvents.ROUND_END)

    def __handle_round_end(self):
        self.event_emitter.emit(EmittedEvents.ROUND_END)

        self.__remove_out_players()
        self.__raise_blinds()

        if self.__is_game_won:
            self.queue_event(GameEvents.GAME_WIN)
            return

        self.__update_pokerkit_state()
        self.queue_event(GameEvents.ROUND_START)

    def __handle_show_or_muck(self):
        self.__state.show_or_muck_hole_cards(True)
        self.event_emitter.emit(EmittedEvents.SHOW_OR_MUCK)
        self.queue_event(GameEvents.DEFAULT)

  def __handle_push_chips(self):
    self.__state.push_chips()
    self.event_emitter.emit(EmittedEvents.PUSH_CHIPS)
    self.queue_event(GameEvents.DEFAULT)

  def __handle_pull_chips(self):
    self.__state.pull_chips()
    self.event_emitter.emit(EmittedEvents.PULL_CHIPS)
    self.queue_event(GameEvents.ROUND_END)

  def __handle_round_end(self):
    self.event_emitter.emit(EmittedEvents.ROUND_END)

    self.__remove_out_players()
    self.__raise_blinds()

    if self.__is_game_won:
      self.queue_event(GameEvents.GAME_WIN)
      return

    self.__update_pokerkit_state()
    self.queue_event(GameEvents.ROUND_START)

  def __handle_show_or_muck(self):
    self.__state.show_or_muck_hole_cards(True)
    self.event_emitter.emit(EmittedEvents.SHOW_OR_MUCK)
    self.queue_event(GameEvents.DEFAULT)

  def __handle_game_win(self):
    self.event_emitter.emit(EmittedEvents.GAME_WIN, self.__players[0].id)
    self.end()

  def __handle_bets(self):

    current_player = self.__player_to_act

    def on_action(action: PlayerActions.value, amount: "Optional[int]"):
      """Callback when a player acts"""

      try:
        match action:
          case PlayerActions.CHECK_OR_CALL:
            self.__state.check_or_call()
          case PlayerActions.FOLD:
            self.__state.fold()
          case PlayerActions.RAISE:
            self.__state.complete_bet_or_raise_to(amount)
      except:  # pylint: disable=bare-except
        print("An error occuored, defaulting")
        try:
          self.__state.fold()
        except:  # pylint: disable=bare-except
          self.__state.check_or_call()

      current_player.event_emitter.remove("action", on_action)

    def timeout():
      """Callback when timed out"""

      print("An error occuored, defaulting")
      try:
        self.__state.fold()
      except:  # pylint: disable=bare-except
        self.__state.check_or_call()
      current_player.event_emitter.remove("action", on_action)

    if not current_player:
      print(list(self.__state.pots))

    # Update player state
    current_player.update_serializable_state(
      SerializableState(current_player, self.__state)
    )

    # Subscribe to events from player
    current_player.event_emitter.on("action", on_action)
    current_player.on_turn()

    Timer(timeout, self.__player_response_time)

    self.queue_event(GameEvents.DEFAULT)

  def start(self):  # pylint: disable=arguments-differ
    super().start(GameEvents.GAME_START)

  def on_event_cycle(self, event: GameEvents.value):  # pylint: disable=unused-private-member
    """Called once every event cycle"""
    match event:
      case GameEvents.DEFAULT:
        self.on_event_cycle(self.__next_event)
      case GameEvents.GAME_START:
        self.__handle_game_start()
      case GameEvents.ROUND_START:
        self.__handle_round_start()
      case GameEvents.POST_ANTE:
        self.__handle_post_ante()
      case GameEvents.COLLECT_BETS:
        self.__handle_bet_collect()
      case GameEvents.POST_BLIND:
        self.__handle_post_blind()
      case GameEvents.BURN_CARD:
        self.__handle_burn_card()
      case GameEvents.DEAL_HOLE_CARDS:
        self.__handle_deal_hole()
      case GameEvents.DEAL_BOARD_CARDS:
        self.__handle_deal_board()
      case GameEvents.KILL_HAND:
        self.__handle_kill_hand()
      case GameEvents.PUSH_CHIPS:
        self.__handle_push_chips()
      case GameEvents.PULL_CHIPS:
        self.__handle_pull_chips()
      case GameEvents.SHOW_OR_MUCK:
        self.__handle_show_or_muck()
      case GameEvents.ROUND_END:
        self.__handle_round_end()
      case GameEvents.BETS:
        self.__handle_bets()
      case GameEvents.GAME_WIN:
        self.__handle_game_win()
      case _:
        self.end()

    def __handle_bets(self):

        current_player = self.__player_to_act

        def on_action(action: PlayerActions.value, amount: "Optional[int]"):
            """Callback when a player acts"""

            try:
                match action:
                    case PlayerActions.CHECK_OR_CALL:
                        self.__state.check_or_call()
                    case PlayerActions.FOLD:
                        self.__state.fold()
                    case PlayerActions.RAISE:
                        self.__state.complete_bet_or_raise_to(amount)
            except:  # pylint: disable=bare-except
                print("An error occuored, defaulting")
                try:
                    self.__state.fold()
                except:  # pylint: disable=bare-except
                    self.__state.check_or_call()

            current_player.event_emitter.remove("action", on_action)

        def timeout():
            """Callback when timed out"""

            print("An error occuored, defaulting")
            try:
                self.__state.fold()
            except:  # pylint: disable=bare-except
                self.__state.check_or_call()
            current_player.event_emitter.remove("action", on_action)

        if not current_player:
            print(list(self.__state.pots))

        # Update player state
        current_player.update_serializable_state(
            SerializableState(current_player, self.__state)
        )

        # Subscribe to events from player
        current_player.event_emitter.on("action", on_action)
        current_player.on_turn()

        Timer(timeout, self.__player_response_time)

        self.queue_event(GameEvents.DEFAULT)

    def start(self):  # pylint: disable=arguments-differ
        super().start(GameEvents.GAME_START)

    def on_event_cycle(self, event: GameEvents):  # pylint: disable=unused-private-member
        """Called once every event cycle"""
        match event:
            case GameEvents.DEFAULT:
                self.on_event_cycle(self.__next_event)
            case GameEvents.GAME_START:
                self.__handle_game_start()
            case GameEvents.ROUND_START:
                self.__handle_round_start()
            case GameEvents.POST_ANTE:
                self.__handle_post_ante()
            case GameEvents.COLLECT_BETS:
                self.__handle_bet_collect()
            case GameEvents.POST_BLIND:
                self.__handle_post_blind()
            case GameEvents.BURN_CARD:
                self.__handle_burn_card()
            case GameEvents.DEAL_HOLE_CARDS:
                self.__handle_deal_hole()
            case GameEvents.DEAL_BOARD_CARDS:
                self.__handle_deal_board()
            case GameEvents.KILL_HAND:
                self.__handle_kill_hand()
            case GameEvents.PUSH_CHIPS:
                self.__handle_push_chips()
            case GameEvents.PULL_CHIPS:
                self.__handle_pull_chips()
            case GameEvents.SHOW_OR_MUCK:
                self.__handle_show_or_muck()
            case GameEvents.ROUND_END:
                self.__handle_round_end()
            case GameEvents.BETS:
                self.__handle_bets()
            case GameEvents.GAME_WIN:
                self.__handle_game_win()
            case _:
                self.end()
                raise ValueError(f"{event} not recognized")
