"""Smoke script to exercise ASCII GUI and Sonar sensitivity tuning.

Run this to see how different `sonar.sensitivity` values affect deterministic
sonar detection and to preview the ASCII console drawing.
"""
from ui.ascii_gui import draw_ascii_console
from submarine.sonar import Sonar


class DummyMap:
    def __init__(self, width=60, height=20):
        self.width = width
        self.height = height
        # two sample contacts
        self._contacts = [
            {'id': 1, 'x': 10, 'y': 5, 'type': 'merchant'},
            {'id': 2, 'x': 40, 'y': 12, 'type': 'destroyer'},
        ]
        self.torpedoes = []

    def get_contacts(self):
        return list(self._contacts)

    def has_thermocline_between(self, x1, y1, x2, y2):
        # simple deterministic thermocline rule for demo
        return False

    def get_depth(self, x, y):
        # simple depth gradient for visualization
        return int((y / max(1, self.height)) * 400)


class DummyLogger:
    def recent(self):
        return ['Smoke test log entry']


class DummySub:
    def __init__(self, x=5, y=10):
        self.x = x
        self.y = y
        self.systems = type('S', (), {'speed': 0.0})()
        self.surface_speed = 1.0
        self.sonar = None

    def status(self):
        return f"Sub at ({self.x},{self.y})"


class DummyGame:
    def __init__(self):
        self.turn = 1
        self.tactical_map = DummyMap()
        self.submarine = DummySub()
        self.logger = DummyLogger()
        self.ascii_cursor = (self.submarine.x, self.submarine.y)


def main():
    game = DummyGame()
    # attach Sonar
    game.submarine.sonar = Sonar(game.submarine, tactical_map=game.tactical_map, sensitivity=1.0, deterministic=True)

    print('Sonar sensitivity smoke test - ASCII preview')
    for sens in (0.5, 1.0, 2.0):
        game.submarine.sonar.sensitivity = sens
        contacts = game.submarine.sonar.detect(active=False, deterministic=True)
        print('\n' + '=' * 60)
        print(f'Sonar sensitivity: {sens} -> detected {len(contacts)} contact(s):', contacts)
        print('=' * 60 + '\n')
        draw_ascii_console(game, cursor=game.ascii_cursor, use_color=True)
        input('\nPress Enter to continue to next sensitivity...')


if __name__ == '__main__':
    main()
