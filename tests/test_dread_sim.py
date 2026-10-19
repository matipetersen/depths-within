"""Acceptance criteria from DESIGN.md section 9, enforced on the headless simulator."""
import pytest

from dread.events import load_events
from dread.sim import PRIORITY, run_patrol, summarize

SEEDS = list(range(120))


@pytest.fixture(scope="module")
def results():
    return {p: summarize(p, SEEDS) for p in PRIORITY}


def completed(s):
    return s["endings"].get("returned", 0) + s["endings"].get("hollow_victory", 0)


def test_policies_diverge_on_a_real_tradeoff(results):
    m, c = results["mission_first"], results["crew_first"]
    assert completed(m) > completed(c) + 0.1          # pushing finishes the job more often...
    assert c["cohesion"] > m["cohesion"] + 0.15       # ...but caring leaves a crew intact
    assert c["survival"] > m["survival"]
    assert c["hull"] > m["hull"]


def test_no_policy_has_one_dominant_ending(results):
    for name, s in results.items():
        assert s["dominant_ending"] <= 0.8, (name, s["endings"])


def test_early_events_keep_a_mundane_explanation(results):
    for name, s in results.items():
        assert s["ambiguity"] >= 0.7, (name, s["ambiguity"])


def test_no_sudden_death_in_first_day(results):
    for name, s in results.items():
        assert s["min_hull_by_24"] > 0.3, name


def test_every_event_is_reachable_by_some_policy():
    seen = set()
    for pol in PRIORITY:
        for seed in range(250):
            seen.update(run_patrol(pol, seed)["event_ids"])
    dead = {e["id"] for e in load_events()} - seen
    assert not dead, f"events that never fire: {sorted(dead)}"


def test_simulation_is_deterministic_per_seed():
    a = run_patrol("crew_first", 7)
    b = run_patrol("crew_first", 7)
    assert a == b


SEVERE = {"hatch_caller", "unaccounted_count", "tube_breathing"}


def test_careful_play_still_meets_the_presence(results):
    """Good management delays the presence; it never removes it (DESIGN.md 2)."""
    for name, s in results.items():
        assert s["beat_coverage"] >= 0.95, (name, s["beat_coverage"])
        assert s["first_beat"] <= 30, (name, s["first_beat"])


def test_severe_beats_are_earned_by_bad_play():
    def severe(policy):
        n = 0
        for seed in range(120):
            n += sum(1 for i in run_patrol(policy, seed)["event_ids"] if i in SEVERE)
        return n
    assert severe("mission_first") > 3 * max(1, severe("crew_first"))


def test_attention_has_a_floor_that_grows_with_time_submerged():
    from dread.world import DreadWorld
    w = DreadWorld(seed=1)
    for c in w.crew:
        c.fear, c.fatigue, c.guilt, c.trust = 0.05, 0.05, 0.0, 0.95
    w.ship.routines = {k: 1.0 for k in w.ship.routines}
    w.ship.hours_submerged = 75
    w.ship.attention = 0.0
    w.tick() if w.pending is None else None
    assert w.ship.attention >= 0.2


def test_a_quiet_stretch_forces_a_beat():
    from dread.world import DreadWorld
    w = DreadWorld(seed=1)
    w.tick_no = 30
    w.ship.hours_submerged = 30
    w.engine.last_beat = 0                     # nothing has shown itself for 30 ticks
    w.engine.last_any = -99
    ev = w.engine.select(w)
    assert ev is not None and ev.get("beat")
