"""Dynamic weather system for visibility and sea state.

This is intentionally small but provides a tick/update method to change
weather conditions over time which can influence detection and navigation.
"""
import random


class Weather:
    def __init__(self):
        # visibility: 0.0 (none) .. 1.0 (clear)
        self.visibility = 1.0
        # sea_state: Beaufort-like small integer
        self.sea_state = 1
        self.storm = False

    def step(self):
        # small random walk for visibility
        change = random.uniform(-0.05, 0.05)
        self.visibility = max(0.0, min(1.0, self.visibility + change))
        # sea state nudges based on visibility (worse visibility often accompanies rougher seas)
        if random.random() < 0.05:
            self.sea_state = max(0, self.sea_state + random.choice([-1, 0, 1]))
        # storm toggles rarely
        if random.random() < 0.01:
            self.storm = not self.storm
            if self.storm:
                self.visibility = max(0.0, self.visibility - 0.3)
        return {'visibility': self.visibility, 'sea_state': self.sea_state, 'storm': self.storm}
