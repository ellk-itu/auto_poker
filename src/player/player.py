from event_emitter import EventEmitter
from pokerkit import Card

from serializable_state import SerializableState
from serializable_state.game import GameState

from .player_actions import PlayerActions


class Player:
    "Player class exposed to an api or a botting interface"

    def __init__(
        self, uuid: str, name: str, index: int
    ):  # TODO Rename id... later me, uh why?
        self.name: str = name  # Display name of player
        self.uuid: str = uuid  # Player uuid
        self.index: int = index  # Player index in turn order
        self.event_emitter: EventEmitter = EventEmitter()
        self.serializable_state: SerializableState | None = None

    @property
    def cards(self) -> list[Card]:
        "Player Cards"
        if not self.serializable_state:
            raise ValueError("No available gamestate")
        return self.serializable_state.cards

    @property
    def stack(self) -> int:
        "Player Stack"
        if not self.serializable_state:
            raise ValueError("No available gamestate")
        return self.serializable_state.stack

    @property
    def bet(self) -> int:
        "Player Active Bet"
        if not self.serializable_state:
            raise ValueError("No available gamestate")
        return self.serializable_state.bet

    @property
    def game(self) -> GameState:
        "Gamestate"
        if not self.serializable_state:
            raise ValueError("No available gamestate")
        return self.serializable_state.game

    @property
    def actions(self) -> list[PlayerActions]:
        "Gamestate"
        if not self.serializable_state:
            raise ValueError("No available gamestate")
        return self.serializable_state.actions

    def update_serializable_state(self, new_state: SerializableState):
        "Setter for serializable_state"

        self.serializable_state = new_state

    def on_turn(self):
        "Method called when it is players turn to act"

    def fold(self):
        "Checks (if applicable, and folds otherwise)"
        if PlayerActions.FOLD not in self.actions:
            self.check()
            return

        self.event_emitter.emit("action", PlayerActions.FOLD, 0)

    def check(self) -> None:
        "Checks if possible"
        if self.game.call_amount == 0:
            raise ValueError("Call amount not 0")

        if PlayerActions.CHECK_OR_CALL not in self.actions:
            raise ValueError("Cannot check")

        self.event_emitter.emit("action", PlayerActions.CHECK_OR_CALL, 0)

    def call(self):
        "Synonum for check_or_call()"
        self.check_or_call()

    def check_or_call(self):
        "Calls (if applicable, else checks)."
        if PlayerActions.CHECK_OR_CALL not in self.actions:
            raise ValueError("Cannot check")

        self.event_emitter.emit("action", PlayerActions.CHECK_OR_CALL, 0)

    def raise_to(self, amount: int):
        """
        Args:
          amount (int): amount to raise to
        """
        if PlayerActions.RAISE not in self.actions:
            raise ValueError("Cannot raise")

        self.event_emitter.emit("action", PlayerActions.CHECK_OR_CALL, amount)
