from enum import Enum


class EmittedEvents(Enum):
  """events dispatched by the state manager event emitter"""

  PLAYER_OUT = "player-out"
  """
    When a player is out
    param (Player): The player that is out 
  """

  GAME_START = "game-start"
  """
    When the game starts
  """

  ROUND_START = "round-start"
  """
    When a round has started
    param (int): The current round
  """

  POST_ANTE = "post-ante"
  """
    When an ante has been posted
    param (int): Ante amount
    param (uuid7): The id of the player posted to
  """

  POST_BLIND = "post-blind"
  """
    When a blind has been posted
    param (int): Blind amount
    param (uuid7): The id of the player posted to
  """

  BURN_CARD = "burn-card"
  """
    When a card has been burned
  """

  BETS = "bets"
  """
    When a player needs to bet
    param (uuid7): id of the player that needs to bet
  """

  DEAL_BOARD_CARDS = "deal-board-cards"
  """
    When a board card has been dealt
    param (Card): The card dealt
  """

  SHOW_OR_MUCK = "show-or-muck"
  """
    When a player need to show or muck
    param (Optional[List[Card]]): The cards shown if shown
    param (uuid7): Id of the player that showed or mucked
  """

  COLLECT_BETS = "collect-bets"
  """
    When the bets gets collected
  """

  ROUND_END = "round-end"
  """
    When a round ends
  """

  GAME_WIN = "game-win"
  """
    When the game has been won
    param (uuid7): Id of the player who won
  """

  PULL_CHIPS = "pull-chips"
  """
    When chips are pulled by a player
    (A player takes their winnings and adds it to their stack)
    param (uuid7): Id of the player who pulled chips
  """

  PUSH_CHIPS = "push-chips"
  """
    When chips have been pushed to a player
    (A player has been given the their winnings for the round (happens before chip pulling))
    param (uuid7): Id of the player that chips were pushed
  """

  KILL_HAND = "kill-hand"
  """
    When a hand can be killed
    param (uuid7): Id of the player that hand was killed
  """

  DEAL_HOLE_CARDS = "deal-hole-cards"
  """
    When a hole card is dealt
    param (uuid7): Id of the player that card was dealt to
  """
