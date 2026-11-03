from dataclasses import dataclass


@dataclass
class GameOptions:  # pylint: disable=too-many-instance-attributes
    """Options for the gameplay of poker"""

    ante: int
    small_blind: int
    big_blind: int
    min_bet: int
    starting_stacks: int
    round_blind_raise: int
    blind_raise_amount: int
    player_response_time: int
