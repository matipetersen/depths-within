import pytest
import sys
import os

# Ensure project root is on sys.path for imports when running tests.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from submarine.submarine import Submarine


def test_submarine_default_load_and_status():
    s = Submarine.from_json_default()
    assert s is not None
    st = s.status()
    assert 'Battery' in st and 'O2' in st


def test_dive_and_surface():
    s = Submarine.from_json_default()
    s.systems.depth = 0
    s.systems.depth += 50
    assert s.systems.depth == 50
    s.systems.depth = 0
    assert s.systems.depth == 0
