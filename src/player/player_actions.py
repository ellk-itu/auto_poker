from enum import Enum


class PlayerActions(Enum):
  "Available actions for a player to take during betting round"
  CHECK_OR_CALL = 0
  FOLD = 1
  RAISE = 2
