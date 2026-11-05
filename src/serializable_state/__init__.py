from copy import deepcopy
from typing import TYPE_CHECKING

from player import PlayerActions
from serializable_state.game import GameState

if TYPE_CHECKING:
    from pokerkit import Card, State

    from player import Player


class SerializableState:  # pylint: disable=too-few-public-methods
    "Serializable (and immutable) version of the pokerkit state"

    def __init__(self, player: Player, state: State):
        self.cards: list[Card] = deepcopy(state.hole_cards[player.index])
        self.stack: int = deepcopy(state.stacks[player.index])
        self.bet: int = deepcopy(state.bets[player.index])
        self.game: GameState = GameState(state, player.index)
        self.actions: list[PlayerActions] = self.__create_available_actions(state)

    def __create_available_actions(self, state: State) -> list[PlayerActions]:
        actions: list[PlayerActions] = []
        if state.can_check_or_call():
            actions.append(PlayerActions.CHECK_OR_CALL)

        if state.can_fold():
            actions.append(PlayerActions.FOLD)

        if state.actor_index is int and state.can_complete_bet_or_raise_to(
            state.stacks[state.actor_index]
        ):
            actions.append(PlayerActions.RAISE)

        return actions
