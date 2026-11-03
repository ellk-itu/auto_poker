from typing import List, TYPE_CHECKING
from copy import deepcopy, copy
from .game import GameState

# Enums
from ..player.player_actions import PlayerActions

if TYPE_CHECKING:
  from pokerkit import State, Card
  from src.player import Player


class SerializableState:  # pylint: disable=too-few-public-methods
  "Serializable (and immutable) version of the pokerkit state"

  def __init__(self, player: "Player", state: "State"):
    self.cards: List[Card] = deepcopy(state.hole_cards[player.index])
    self.stack: int = deepcopy(state.stacks[player.index])
    self.bet: int = deepcopy(state.bets[player.index])
    self.game: GameState = GameState(state, player.index)
    self.actions: List[PlayerActions.value] = self.__create_available_actions(
      state)

  def __create_available_actions(self, state: "") -> List[PlayerActions.value]:
    actions: List[PlayerActions.value] = []
    if state.can_check_or_call():
      actions.append(PlayerActions.CHECK_OR_CALL)

    if state.can_fold():
      actions.append(PlayerActions.FOLD)

    if state.can_complete_bet_or_raise_to(state.stacks[state.actor_index]):
      actions.append(PlayerActions.RAISE)

    return actions
