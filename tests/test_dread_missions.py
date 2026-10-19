"""Missions as an event trigger, and orders whose origin is never settled."""
import copy
import json

import pytest

from dread.events import load_events
from dread.missions import load_missions, provenance_line
from dread.orders import verify_orders
from dread.world import DreadWorld


def _play(w, policy="crew_first", max_ticks=400):
    """Play a whole patrol with one of the simulator's captains."""
    from dread.sim import issue_orders, pick_choice
    while not w.finished and w.tick_no < max_ticks:
        if w.pending:
            w.choose(pick_choice(policy, w.pending, None, w))
        else:
            issue_orders(policy, w)
            w.tick()
    return w


def test_every_mission_has_both_origins_and_a_provenance():
    ms = load_missions()
    assert len(ms) >= 4
    assert any(m.moral for m in ms)
    for m in ms:
        assert m.mundane_origin.strip() and m.uncanny_origin.strip(), m.id
        assert provenance_line(m)
        assert 0.0 <= m.quality <= 1.0


def test_provenance_degrades_as_the_patrol_goes_on():
    q = [m.quality for m in load_missions()]
    assert q == sorted(q, reverse=True)
    assert q[-1] < 0.3          # by the end nobody can say where the orders came from


def test_mission_rejects_missing_uncanny_origin(tmp_path):
    raw = json.load(open("data/missions.json"))
    del raw["missions"][0]["uncanny_origin"]
    p = tmp_path / "m.json"
    p.write_text(json.dumps(raw))
    with pytest.raises(ValueError):
        load_missions(str(p))


def test_briefing_is_logged_with_provenance_not_origin():
    w = DreadWorld(seed=1)
    text = "\n".join(w.log)
    assert w.run.mission.title in text
    assert "Received:" in text
    assert w.run.mission.mundane_origin not in text
    assert w.run.mission.uncanny_origin not in text


def test_missions_run_in_sequence_and_each_fires_its_own_events():
    fired, completed = set(), 0
    for seed in range(10):
        w = _play(DreadWorld(seed=seed))
        ids = [m.id for m in w.missions]
        got = [r["mission"] for r in w.results]
        assert got == ids[:len(got)]                  # strictly in order; a lost boat may stop early
        completed += len(got) == len(ids)
        fired |= {f.id for f in w.fired}
    assert {"m1_contact", "m1_attack", "m2_smoke", "m2_ack", "m3_sighting", "m3_decision",
            "m4_survivors", "m4_unrecorded"} <= fired
    assert completed >= 5


def test_phase_events_fire_by_progress_and_only_for_their_mission():
    w = DreadWorld(seed=1)
    assert w.run.mission.id == "m1_battleship"
    w.ship.progress = 0.6
    w.tick()
    ids = {f.id for f in w.fired}
    assert "m1_contact" in ids
    assert not any(i.startswith(("m2_", "m3_", "m4_")) for i in ids)


def test_no_missions_means_no_mission_events():
    w = DreadWorld(seed=1, missions=[])
    for _ in range(60):
        w.choose(w.pending.choices[0].key) if w.pending else w.tick()
    assert not any(f.id.startswith("m") and f.id[1].isdigit() for f in w.fired)


def test_the_moral_choice_has_three_ways_out():
    w = DreadWorld(seed=1)
    w._start_mission(2)
    w.ship.progress = 1.0
    w.engine.fire(w.engine.events["m3_decision"], w)
    keys = {c.key for c in w.pending.choices}
    assert keys == {"sink", "alter", "refuse"}
    tags = {t for c in w.pending.choices for t in c.tags}
    assert {"comply", "alter", "refuse"} <= tags


def _decide(key):
    w = DreadWorld(seed=1)
    w._start_mission(2)
    w.ship.progress = 1.0
    w.engine.fire(w.engine.events["m3_decision"], w)
    guilt0 = sum(c.guilt for c in w.crew)
    trust0 = sum(c.trust for c in w.crew)
    w.choose(key)
    return w, sum(c.guilt for c in w.crew) - guilt0, sum(c.trust for c in w.crew) - trust0


def test_sinking_the_hospital_ship_marks_the_boat():
    w, dguilt, dtrust = _decide("sink")
    assert "civilian_sunk" in w.ship.flags
    assert w.ship.moral_debt >= 0.5
    assert dguilt > 2.0 and dtrust < 0
    assert "santa_lucia" in w.ship.rumors


def test_refusing_is_defiance_and_the_crew_notices_the_other_way():
    w, dguilt, dtrust = _decide("refuse")
    assert "orders_defied" in w.ship.flags and "civilian_sunk" not in w.ship.flags
    assert w.ship.moral_debt == 0
    assert dtrust > 0
    assert w.results[-1]["outcome"] == "refused"


def test_moral_debt_feeds_the_presence_and_guilt_over_time():
    clean, stained = DreadWorld(seed=5, missions=[]), DreadWorld(seed=5, missions=[])
    stained.ship.moral_debt = 0.6
    for _ in range(25):
        for w in (clean, stained):
            w.choose(w.pending.choices[0].key) if w.pending else w.tick()
    mean = lambda w: sum(c.guilt for c in w.active_crew()) / len(w.active_crew())
    assert stained.ship.attention > clean.ship.attention
    assert mean(stained) > mean(clean)


def test_verify_orders_reassures_or_disturbs_but_never_names_the_source():
    seen = set()
    for seed in range(60):
        w = DreadWorld(seed=seed)
        msg = verify_orders(w)
        seen.add(msg.split(",")[0].split(":")[0])
        assert "enemy" not in msg.lower() and "admiral" not in msg.lower()
        assert verify_orders(w) == "Nothing more to verify."   # once per mission
    assert len(seen) >= 2                                      # not always the same answer


def test_doubtful_orders_erode_trust():
    sure, doubtful = DreadWorld(seed=2, missions=[]), DreadWorld(seed=2, missions=[])
    doubtful.ship.orders_doubt = 0.8
    for _ in range(15):
        for w in (sure, doubtful):
            w.choose(w.pending.choices[0].key) if w.pending else w.tick()
    t = lambda w: sum(c.trust for c in w.active_crew()) / len(w.active_crew())
    assert t(doubtful) < t(sure)


def test_orders_may_or_may_not_be_on_record():
    unrecorded = recorded = 0
    for seed in range(80):
        w = DreadWorld(seed=seed)
        w._start_mission(3)
        w.ship.progress = 1.0
        w.engine.fire(w.engine.events["m4_unrecorded"], w)
        unrecorded += "orders_unrecorded" in w.ship.flags
        recorded += "orders_on_record" in w.ship.flags
    assert unrecorded > 10 and recorded > 10


def test_debrief_reveals_both_origins_after_the_patrol():
    w = _play(DreadWorld(seed=3))
    d = "\n".join(w.debrief())
    by_id = {m.id: m for m in w.missions}
    assert w.results
    for r in w.results:
        m = by_id[r["mission"]]
        assert m.mundane_origin in d and m.uncanny_origin in d


def test_a_closed_window_fails_the_mission_without_freezing_the_patrol():
    w = DreadWorld(seed=1)
    w.ship.readiness = 0.0
    for _ in range(80):
        if w.pending:
            w.choose(w.pending.choices[0].key)
        w.ship.progress = 0.0      # never gets anywhere
        w.tick()
        if w.mission_i >= 1:
            break
    assert w.results and w.results[0]["outcome"] == "failed"
    assert w.run.mission.id == "m2_convoy"
