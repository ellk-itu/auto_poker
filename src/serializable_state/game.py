from copy import deepcopy
from typing import TYPE_CHECKING

from .public_player import PublicPlayerState

if TYPE_CHECKING:
    from pokerkit import Card, Pot, State


class GameState:
    "Serializable state information about the game (board)"

    def __init__(self, state: State, player_index: int):
        self.stacks: list[int] = deepcopy(state.stacks)
        self.board_cards: list[Card] = self.__get_board_cards(state)
        self.pots: list[Pot] = deepcopy(list(state.pots))
        self.small_blind: int = deepcopy(state.blinds_or_straddles[1])
        self.big_blind: int = deepcopy(state.blinds_or_straddles[0])
        self.bets: list[int] = deepcopy(state.bets)
        self.call_amount: int = deepcopy(state.checking_or_calling_amount or 0)
        self.players: list[PublicPlayerState] = self.__create_public_player_states(
            state, player_index
        )

    def __get_board_cards(self, state: State):
        if not state.board_cards:
            return []
        return deepcopy(state.board_cards[0])

    def __create_public_player_states(
        self, state: State, player_index: int
    ) -> list[PublicPlayerState]:  # pylint: disable=line-too-long
        player_indices = list(range(state.player_count))
        del player_indices[player_index]

        return [
            PublicPlayerState(player_index, self) for player_index in player_indices
        ]
