"""Event table: the golden rule (DESIGN.md section 2) and the effect interpreter."""
import copy

import pytest

from dread.conditions import evaluate
from dread.events import apply_effects, load_events, validate_events
from dread.world import DreadWorld


def test_every_event_has_both_causes():
    events = load_events()
    assert len(events) >= 20
    for ev in events:
        assert ev["mundane_cause"].strip() and ev["uncanny_cause"].strip(), ev["id"]
        assert "mundane_when" in ev, ev["id"]


def test_validation_rejects_event_without_uncanny_cause():
    bad = copy.deepcopy(load_events()[0])
    del bad["uncanny_cause"]
    with pytest.raises(ValueError):
        validate_events([bad])


def test_validation_rejects_duplicate_ids():
    e = load_events()[0]
    with pytest.raises(ValueError):
        validate_events([e, copy.deepcopy(e)])


def test_all_choices_apply_cleanly():
    """Every choice of every event applies without error on a stressed world."""
    for ev in load_events():
        for ch in ev.get("choices", []):
            w = DreadWorld(seed=5)
            target = w.crew[0]
            apply_effects(ch["effects"], w, target)


def test_conditions():
    w = DreadWorld(seed=1)
    assert evaluate({"path": "ship.co2", "op": "<", "value": 0.01}, w)
    assert not evaluate({"never": True}, w)
    assert evaluate({"not": {"never": True}}, w)
    assert evaluate({"all": [{"no_flag": "x"}, {"path": "crew.count", "op": ">=", "value": 5}]}, w)
    w.ship.flags.add("x")
    assert evaluate({"flag": "x"}, w)
    with pytest.raises(ValueError):
        evaluate({"bogus": 1}, w)


def test_vanish_marks_missing_and_sets_flag():
    w = DreadWorld(seed=1)
    victim = w.crew[3]
    apply_effects([{"op": "vanish", "who": "target"}], w, victim)
    assert victim.missing and not victim.active
    assert "sailor_missing" in w.ship.flags
    assert victim not in w.active_crew()


def test_rumor_spreads_and_hurts_believers():
    w = DreadWorld(seed=1)
    apply_effects([{"op": "rumor", "id": "r", "text": "x", "intensity": 0.9, "seed": "random",
                    "drift": {"trust": -0.01}}], w)
    r = w.ship.rumors["r"]
    assert len(r.believers) == 1
    start_trust = {c.id: c.trust for c in w.crew}
    for _ in range(20):
        w._rumors()
    assert len(r.believers) > 1
    assert any(c.trust < start_trust[c.id] for c in w.crew if c.id in r.believers)


def test_choice_blocks_time_until_resolved():
    w = DreadWorld(seed=1)
    ev = w.engine.events["clock_slow"]
    w.tick_no = 20
    w.ship.hours_submerged = 20
    w.engine.fire(ev, w)
    assert w.pending is not None
    with pytest.raises(RuntimeError):
        w.tick()
    w.choose(w.pending.choices[0].key)
    assert w.pending is None
    w.tick()
