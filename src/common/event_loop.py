from collections import deque
from enum import Enum


class EventLoop[E: Enum]:
    """
    A continuous dispatcher of events.
    Blocks a thread as long as it is running, and only allows execution of code through the loop.
    """

    def __init__(self, events: type[E]):
        """
        Creates new event loop.

        Args:
            events (type[E]): Available events that can be dispatched from loop
        """

        self.events: type[E] = events
        self.running: bool = False
        self.queue: deque[E] = deque()

    def queue_event(self, event: E):
        """
        Queues a new event to be executed when the thread is free.

        Args:
            event (E): Description.
        """

        self.__validate_event(event)
        self.queue.append(event)

    def on_event_cycle(self, event: E):
        """
        Function called everytime the tread is free and a new Event is dispatched.
        @Abstract

        Args:
            event (E): The new dispatched event.
        """

    def __validate_event(self, event: Enum):
        """
        Validates event for dynimically typed events.

        Args:
            event (Enum): Event to validate.

        Raises:
            ValueError: Error if the event type is not included in [E].
        """
        if event not in self.events:
            raise ValueError("Event is not in event list")

    def start(self, event: E):
        """
        Start the event loop.

        Args:
            event (E): The initial event.
        """

        self.__validate_event(event)

        self.running = True
        self.queue.append(event)

        while self.running:
            next_event = self.queue.popleft()
            self.on_event_cycle(next_event)

    def end(self):
        """End the event loop, freeing the thread."""

        self.running = False
