from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import GameState


class PublicPlayerState:
    "Public data of other players"

    def __init__(self, player_index: int, game_state: GameState):
        self.bet: int = game_state.bets[player_index]
        self.stack: int = game_state.stacks[player_index]
        self.index: int = player_index
