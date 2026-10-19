import math
import sys
import os
# Ensure tests can import project packages when pytest is run from workspace root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from submarine.sonar import detection_probability, Sonar


def test_detection_probability_basic():
    # close target should be detected with high prob
    p_close = detection_probability(100, target_noise=0.9, own_noise=0.1, sea_state=1.0, thermocline=False, active=False, sensitivity=1.0)
    assert 0.7 < p_close <= 1.0

    # far target should have low probability
    p_far = detection_probability(5000, target_noise=0.6, own_noise=0.1, sea_state=1.0, thermocline=False, active=False, sensitivity=1.0)
    assert 0.0 <= p_far < 0.5


class DummyOwner:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.systems = type('S', (), {'speed': 0.0})()
        self.surface_speed = 1.0


class DummyMap:
    def __init__(self):
        self._contacts = [{'id': 1, 'x': 1, 'y': 1, 'type': 'merchant'}]

    def get_contacts(self):
        return list(self._contacts)

    def has_thermocline_between(self, x1, y1, x2, y2):
        return False


def test_sonar_detect_deterministic():
    owner = DummyOwner(0, 0)
    tmap = DummyMap()
    s = Sonar(owner, tactical_map=tmap, sensitivity=2.0, deterministic=True)
    contacts = s.detect(active=False, deterministic=True)
    # with sensitivity bumped to 2.0 and close contact, deterministic detect should return at least one contact
    assert len(contacts) >= 1