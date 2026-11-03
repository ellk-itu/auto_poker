from typing import List, TYPE_CHECKING
from copy import deepcopy
from .public_player import PublicPlayerState

if TYPE_CHECKING:
  from pokerkit import State, Card


class GameState:  # pylint: disable=too-few-public-methods, too-many-instance-attributes

  "Serializable state information about the game (board)"

  def __init__(self, state: "State", player_index: int):
    self.stacks: List[int] = deepcopy(state.stacks)
    self.board_cards: List[Card] = self.__get_board_cards(state)
    self.pots: List[int] = deepcopy(list(state.pots))
    self.small_blind: int = deepcopy(state.blinds_or_straddles[1])
    self.big_blind: int = deepcopy(state.blinds_or_straddles[0])
    self.bets: List[int] = deepcopy(state.bets)
    self.call_amount: int = deepcopy(state.checking_or_calling_amount)
    self.players: List[PublicPlayerState] = self.__create_public_player_states(
      state, player_index)

  def __get_board_cards(self, state: "State"):
    if not state.board_cards:
      return []
    return deepcopy(state.board_cards[0])

  def __create_public_player_states(self, state: "State", player_index: int) -> List[PublicPlayerState]:  # pylint: disable=line-too-long
    player_indices = list(range(0, state.player_count))
    del player_indices[player_index]
    return list(map(lambda player_index: PublicPlayerState(player_index, self), player_indices))
