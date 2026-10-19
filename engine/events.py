# Event system for in-game events
import time


class Event:
    def __init__(self, event_type, data=None, timestamp=None):
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = timestamp or time.time()


class EventQueue:
    def __init__(self):
        self.events = []

    def push(self, event):
        self.events.append(event)
        # keep queue limited
        if len(self.events) > 1000:
            self.events.pop(0)

    def pop(self):
        if not self.events:
            return None
        return self.events.pop(0)

    def peek(self):
        return self.events[0] if self.events else None
