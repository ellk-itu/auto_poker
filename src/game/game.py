import asyncio

from event_emitter import EventEmitter
from pokerkit import NoLimitTexasHoldem, State

from player import Player

# Enums
from ..player.player_actions import PlayerActions  # pylint: disable=wrong-import-order
from ..serializable_state import SerializableState
from .emitted_events import EmittedEvents
from .game_events import GameEvents
from .game_options import GameOptions

# TODO: Add Some thing that makes it
# easier to do default action thing


class Game:
    """
    Game engine.
    As of right now can only play texas Holdem
    """

    def __init__(
        self,
        players: list[Player],
        game_options: GameOptions,
    ):

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
        The current player to act.

        Returns:
            Player | None: Player or None if no player is has to act.
        """

        if self.__state.actor_index is None:
            return None

        return self.__players[self.__state.actor_index]

    @property
    def __is_game_won(self) -> bool:
        """
        Determines weather or not the game is won.
        This is determined by the amount of players left, 1 (or fewer) will be assumed to be won by said player.

        Returns:
            bool: Whether or not the game has been won.
        """

        return len(self.__players) <= 1

    @property
    def __next_event(self) -> GameEvents:
        """
        Gets next event based on the current state of the board.

        Returns:
            GameEvents: Enum of next states.
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

    def __handle_post_ante(self):
        self.__state.post_ante()
        self.event_emitter.emit(
            EmittedEvents.POST_ANTE,
            self.__ante,
            next(iter(self.__state.ante_poster_indices)),
        )

    def __handle_bet_collect(self):
        self.__state.collect_bets()
        self.event_emitter.emit(EmittedEvents.COLLECT_BETS)

    def __handle_post_blind(self):
        self.__state.post_blind_or_straddle()
        self.event_emitter.emit(EmittedEvents.POST_BLIND)
        # TODO Fix the emitter for blinds

    def __handle_burn_card(self):
        self.__state.burn_card("??")
        self.event_emitter.emit(EmittedEvents.BURN_CARD)

    def __handle_deal_hole(self):
        self.__state.deal_hole()
        self.event_emitter.emit(EmittedEvents.DEAL_HOLE_CARDS)

    def __handle_deal_board(self):
        self.__state.deal_board()
        self.event_emitter.emit(EmittedEvents.DEAL_BOARD_CARDS)
        # TODO fix board card for the emitter

    def __handle_kill_hand(self):
        self.__state.kill_hand()
        self.event_emitter.emit(EmittedEvents.KILL_HAND)

    def __handle_show_or_muck(self):
        self.__state.show_or_muck_hole_cards(True)
        self.event_emitter.emit(EmittedEvents.SHOW_OR_MUCK)

    def __handle_push_chips(self):
        self.__state.push_chips()
        self.event_emitter.emit(EmittedEvents.PUSH_CHIPS)

    def __handle_pull_chips(self):
        self.__state.pull_chips()
        self.event_emitter.emit(EmittedEvents.PULL_CHIPS)

    async def __handle_bets(self):
        current_player = self.__player_to_act

        if current_player is None:
            raise ValueError("Something wrong happened")

        current_player.update_serializable_state(
            SerializableState(current_player, self.__state)
        )

        response = await self.__await_action(current_player)
        self.__apply_action(response)

    async def __await_action(self, player: Player) -> tuple[PlayerActions, int] | None:
        """
        Waits for the player to act.
        Returns None if the player does not respond within the response time.
        """

        loop = asyncio.get_running_loop()
        response: asyncio.Future[tuple[PlayerActions, int]] = loop.create_future()

        def on_action(action: PlayerActions, amount: int):
            def resolve():
                if not response.done():
                    response.set_result((action, amount))

            # Thread-safe, so actions can come from an API thread as well as a bot
            loop.call_soon_threadsafe(resolve)

        player.event_emitter.on("action", on_action)
        player.on_turn()

        try:
            return await asyncio.wait_for(response, timeout=self.__player_response_time)
        except TimeoutError:
            print("Player timed out, defaulting")
            return None
        finally:
            player.event_emitter.remove("action", on_action)

    def __apply_action(self, response: tuple[PlayerActions, int] | None):
        if response is None:
            self.__apply_default_action()
            return

        action, amount = response

        try:
            match action:
                case PlayerActions.CHECK_OR_CALL:
                    self.__state.check_or_call()
                case PlayerActions.FOLD:
                    self.__state.fold()
                case PlayerActions.RAISE:
                    self.__state.complete_bet_or_raise_to(amount)
        except ValueError:
            print("An error occuored, defaulting")
            self.__apply_default_action()

    def __apply_default_action(self):
        """
        Default action for a player to take.
        Will default to folding if possible, and if not will check
        """

        try:
            self.__state.fold()
        except ValueError:
            self.__state.check_or_call()

    async def __handle_event(self, event: GameEvents):
        match event:
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
            case GameEvents.BETS:
                await self.__handle_bets()

    async def __play_round(self):
        """
        Play a single round of poker.

        Round is over when the chips are pulled.
        For more see:
            https://pokerkit.readthedocs.io/en/stable/reference.html#pokerkit.state.State.pull_chips
        """

        self.__current_round += 1
        self.event_emitter.emit(EmittedEvents.ROUND_START, self.__current_round)

        while True:
            event = self.__next_event
            await self.__handle_event(event)

            # Check if the chips have been pulled
            if event is GameEvents.PULL_CHIPS and not self.__state.can_pull_chips():
                return

    def __end_round(self):
        self.event_emitter.emit(EmittedEvents.ROUND_END)

        self.__remove_out_players()
        self.__raise_blinds()

    async def start(self):
        """
        Plays rounds until one player remains.
        Run with asyncio.run(game.start()). To stop early, cancel the task that runs it.
        """

        self.event_emitter.emit(EmittedEvents.GAME_START)

        while True:
            await self.__play_round()
            self.__end_round()

            if self.__is_game_won:
                break

            self.__update_pokerkit_state()

        self.event_emitter.emit(EmittedEvents.GAME_WIN, self.__players[0].uuid)
