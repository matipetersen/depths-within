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
