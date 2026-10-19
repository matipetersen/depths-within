import time
import math
from world.tactical_map import TacticalMap


def test_torpedo_hits_contact():
    tm = TacticalMap(width=20, height=10)
    # place a single contact deterministically at (10,5)
    # give a fixed route to prevent wandering during the test
    tm.contacts = [{'id': 1, 'x': 10, 'y': 5, 'type': 'merchant', 'route': [(10, 5)], 'route_index': 0}]

    # spawn torpedo at (5,5) heading east (bearing 90 degrees is east in compass terms)
    # spawn homing torpedo targeted at contact id 1
    torp = tm.spawn_torpedo('testsub', 5, 5, bearing_deg=90, speed=1.0, target_id=1, homing_strength=0.4)
    assert torp is not None

    hit = False
    for i in range(30):
        events = tm.step()
        # events may be returned when torpedo hits
        if events:
            for ev in events:
                if ev.get('type') == 'hit':
                    hit = True
        if hit:
            break

    assert hit, "Torpedo did not hit the contact"


def test_torpedo_timeout():
    tm = TacticalMap(width=10, height=5)
    tm.contacts = []
    # spawn torpedo that heads out of bounds quickly
    torp = tm.spawn_torpedo('ts', 0, 0, bearing_deg=270, speed=5.0)
    assert torp is not None

    timed_out = False
    for i in range(10):
        events = tm.step()
        if events:
            for ev in events:
                if ev.get('type') in ('timeout', 'wall'):
                    timed_out = True
        if timed_out:
            break

    assert timed_out, 'Torpedo did not timeout or leave map as expected'
