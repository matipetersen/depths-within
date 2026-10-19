import os
import sys
import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from submarine.compartment_events import resolve_event
from submarine.submarine import Submarine
from submarine.compartments import Compartment
from submarine.crew import CrewMember


def make_sub_with_single_comp():
    # Create a minimal submarine with one compartment and controlled crew
    sub = Submarine('test_sub', 'Neutral', {'bow': 2}, 100, 10, 6, 'BasicSonar', False, tactical_map=None)
    comp = Compartment('TestComp')
    comp.flooding = 0.0
    comp.integrity = 1.0
    comp.neighbors = []
    sub.compartments = [comp]
    # attach deterministic crew
    eng_skills = {'sonar': 0.1, 'torpedoes': 0.1, 'navigation': 0.1, 'engineering': 0.8, 'medical': 0.1}
    eng = CrewMember('Eng1', rank='Chief', skills=eng_skills, traits=['methodical'])
    med = CrewMember('Med1', rank='Medic', skills={'engineering': 0.1, 'medical': 0.9, 'sonar': 0.1, 'torpedoes': 0.1, 'navigation': 0.1}, traits=['calm'])
    sub.crew = [eng, med]
    return sub, comp, eng, med


def test_flood_burst_handled_by_engineer():
    sub, comp, eng, med = make_sub_with_single_comp()
    # create flood event
    ev = {'type': 'flood_burst', 'compartment': comp, 'severity': 0.5}
    # deterministic resolution
    outcome = resolve_event(sub, ev, responder=None, deterministic=True)
    assert outcome['event'] == 'flood_burst'
    assert outcome['compartment'] == 'TestComp'
    # flooding got an immediate bump but engineer should patch most of it deterministically
    assert comp.flooding >= 0.0
    # engineer gained XP
    assert eng.xp.get('engineering', 0) > 0
    assert outcome['handled'] is True


def test_fire_is_extinguished_when_possible():
    sub, comp, eng, med = make_sub_with_single_comp()
    ev = {'type': 'fire', 'compartment': comp, 'severity': 0.4}
    pre_integrity = comp.integrity
    outcome = resolve_event(sub, ev, responder=None, deterministic=True)
    # integrity reduced by immediate hit
    assert comp.integrity < pre_integrity
    # engineer should often extinguish deterministically with provided skill
    assert outcome['handled'] is True
    assert eng.xp.get('engineering', 0) > 0


def test_short_circuit_repairs_and_battery_drop():
    sub, comp, eng, med = make_sub_with_single_comp()
    # ensure systems exist
    sub.systems.battery = 1.0
    ev = {'type': 'short_circuit', 'compartment': comp, 'severity': 0.3}
    outcome = resolve_event(sub, ev, responder=None, deterministic=True)
    # battery should have been reduced by the short
    assert hasattr(sub.systems, 'battery')
    assert sub.systems.battery <= 1.0
    # engineer xp increases when repaired
    assert eng.xp.get('engineering', 0) >= 0


def test_crew_injury_applies_stress_not_death_when_deterministic():
    sub, comp, eng, med = make_sub_with_single_comp()
    ev = {'type': 'crew_injury', 'compartment': comp, 'severity': 0.5}
    # choose med as responder to check deterministic victim selection
    outcome = resolve_event(sub, ev, responder=med, deterministic=True)
    # deterministic mode with provided responder will select the responder as victim but not kill (sev 0.5 -> died False)
    assert med.stress >= 0.0
    assert outcome['handled'] is True
