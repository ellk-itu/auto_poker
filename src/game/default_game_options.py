from .game_options import GameOptions


class DefaultGameOptions(GameOptions):  # pylint: disable=too-many-instance-attributes
  """Options for the gameplay of poker"""

  def __init__(self):
    super().__init__(
        ante=0,
        small_blind=100,
        big_blind=200,
        min_bet=100,
        starting_stacks=3000,
        round_blind_raise=10,
        blind_raise_amount=100,
        player_response_time=100,
    )
