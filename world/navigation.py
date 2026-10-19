# Navigation, dead reckoning, drift errors
import random


class Navigation:
    def __init__(self):
        self.current_position = (0, 0)
        self.drift_error = 0.0

    def set_position(self, x, y):
        self.current_position = (float(x), float(y))

    def apply_drift(self):
        # Apply small random drift to the current position
        dx = random.uniform(-self.drift_error, self.drift_error)
        dy = random.uniform(-self.drift_error, self.drift_error)
        x, y = self.current_position
        self.current_position = (x + dx, y + dy)

    def estimate_position(self):
        return self.current_position

    def set_drift(self, error):
        self.drift_error = max(0.0, float(error))
