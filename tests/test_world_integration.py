import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world.regions import load_regions
from world.encounters import generate_random_encounter
from world.weather import Weather
from ui.panels.lore_panel import LorePanel


def test_world_and_lore_panel_basic():
    regs = load_regions()
    assert isinstance(regs, list)
    enc = generate_random_encounter()
    assert enc is not None
    w = Weather()
    before = w.visibility
    res = w.step()
    assert 'visibility' in res
    # test lore panel can display a random crew story without crashing
    lp = LorePanel()
    lp.show_random_crew_story()
    lp.draw()
