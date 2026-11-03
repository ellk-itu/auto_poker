from enum import Enum


class GameEvents(Enum):
  """events dispatched by the state manager event emitter"""

  DEFAULT = "default"

  GAME_START = "game-start"
  """
    When the game starts
  """

  ROUND_START = "round-start"
  """
    When a round has started
  """

  POST_ANTE = "post-ante"
  """
    When an ante has been posted
  """

  POST_BLIND = "post-blind"
  """
    When a blind has been posted
  """

  BURN_CARD = "burn-card"
  """
    When a card has been burned
  """

  BETS = "bets"
  """
    When a player needs to bet
  """

  DEAL_BOARD_CARDS = "deal-board-cards"
  """
    When a board card has been dealt
  """

  SHOW_OR_MUCK = "show-or-muck"
  """
    When a player need to show or muck
  """

  COLLECT_BETS = "collect-bets"
  """
    When the bets gets collected
  """

  ROUND_END = "round-end"
  """
    When a round ends
  """

  PULL_CHIPS = "pull-chips"
  """
    When chips are pulled by a player
    (A player takes their winnings and adds it to their stack)
  """

  PUSH_CHIPS = "push-chips"
  """
    When chips have been pushed to a player
    (A player has been given the their winnings for the round (happens before chip pulling))
  """

  KILL_HAND = "kill-hand"
  """
    When a hand can be killed
  """

  DEAL_HOLE_CARDS = "deal-hole-cards"
  """
    When a hole card is dealt
  """

  GAME_WIN = "game-win"
  """
    When the game has been won
  """
