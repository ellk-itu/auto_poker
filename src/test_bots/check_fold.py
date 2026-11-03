from ..player import Player
from ..player.player_actions import PlayerActions


class CheckFoldBot(Player):
  "Botted Played that always folds or checks"

  def __init__(self, id: str, index: int):
    super().__init__(id, "Check or Fold Bot", index)

  def on_turn(self):
    if PlayerActions.CHECK_OR_CALL in self.actions:
      if self.game.call_amount <= 0:
        self.check_or_call()
        return

    self.fold()
