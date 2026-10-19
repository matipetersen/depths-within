"""Simple in-game logger for UI and event recording."""
import time


class Logger:
    def __init__(self, capacity=200):
        self.capacity = capacity
        self.entries = []

    def log(self, text, category='system', timestamp=None):
        ts = timestamp or time.time()
        self.entries.append({'time': ts, 'category': category, 'text': text})
        if len(self.entries) > self.capacity:
            self.entries.pop(0)

    def recent(self, limit=20):
        return list(self.entries[-limit:])
