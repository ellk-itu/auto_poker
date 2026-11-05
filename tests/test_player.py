from uuid import uuid7

from player import Player


class TestPlayer(Player):
    def __init__(self, uuid: str, index: int):
        super().__init__(uuid, "TestPlayer", index)

    def on_turn(self):
        self.fold()


def test_player():
    player = TestPlayer(str(uuid7()), 0)
