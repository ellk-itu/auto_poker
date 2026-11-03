from collections import deque
from enum import Enum


class EventLoop[E: Enum]:
    """Event loop that queues events to circumvent stack overflow"""

    def __init__(self, events: type[E]):
        """
        param:
          events(Enum)
          enum containing the possible event states
        """

        self.events: type[E] = events
        self.running: bool = False
        self.queue: deque[E] = deque()

    def queue_event(self, event: E):  # pylint: disable=unused-private-member
        """Queues a new event to be executed in the loop"""

        self.__validate_event(event)
        self.queue.append(event)

    def on_event_cycle(self, event: E):
        """Called every time a cycle is started"""

    def __validate_event(self, event: E):
        if event not in self.events:
            raise ValueError("Event is not in event list")

    def start(self, event: E):
        """Start the event loop"""

        self.__validate_event(event)

        self.running = True
        self.queue.append(event)

        while self.running:
            next_event = self.queue.popleft()
            self.on_event_cycle(next_event)

    def end(self):
        """End the event loop"""

        self.running = False
