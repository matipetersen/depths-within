"""State model: reported vs true, symptoms, derived (not time-driven) stages."""
import random

from dread.state import Crew, Ship, dread_index, stage_for
from dread.world import DreadWorld, default_crew


def test_low_trust_crew_reports_calm_while_broken():
    ship = Ship(cohesion=0.8)
    broken = Crew(0, "A", "sonar", candor=0.9, fear=0.9, fatigue=0.9, guilt=0.5, trust=0.1)
    trusting = Crew(1, "B", "sonar", candor=0.9, fear=0.9, fatigue=0.9, guilt=0.5, trust=0.9)
    assert broken.stress() == trusting.stress()
    assert broken.reported(ship.cohesion) < 0.3          # "todo bien"
    assert trusting.reported(ship.cohesion) > 0.5


def test_symptoms_follow_true_values():
    calm = Crew(0, "A", "deck")
    assert calm.symptoms() == []
    wreck = Crew(1, "B", "deck", fear=0.8, fatigue=0.9, guilt=0.6, trust=0.2)
    s = wreck.symptoms()
    assert {"talks to himself", "microsleeps", "avoids eyes", "silent when the captain speaks"} <= set(s)


def test_stage_is_derived_from_state_not_time():
    w = DreadWorld(seed=1)
    calm = stage_for(w.dread())
    w.tick_no = 500                                # a long time at sea changes nothing by itself
    assert stage_for(w.dread()) == calm
    for c in w.crew:
        c.fear, c.guilt, c.trust, c.fatigue = 0.9, 0.8, 0.1, 0.9
    w.ship.routines = {k: 0.0 for k in w.ship.routines}
    w.ship.co2 = 0.04
    assert stage_for(w.dread()) in ("TERROR", "MADNESS")


def test_dread_index_bounds():
    ship = Ship()
    assert 0.0 <= dread_index(ship, default_crew(random.Random(0))) <= 1.0
    assert dread_index(ship, []) == 1.0


def test_report_hides_true_values_but_shows_symptoms():
    w = DreadWorld(seed=2)
    w.crew[0].fear, w.crew[0].trust = 0.9, 0.1
    rows = w.report(observer_skill=1.0)
    row = next(r for r in rows if r["name"] == w.crew[0].name)
    assert "fear" not in row and "trust" not in row
    assert "jumpy" in row["symptoms"]
