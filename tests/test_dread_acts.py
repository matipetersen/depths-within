"""Missions are carried out by orders, not by waiting (DESIGN.md section 7.5)."""
from dread import orders as O
from dread.world import DreadWorld


def _hours(w, n):
    for _ in range(n):
        if w.pending is not None or w.finished:
            break
        w.tick()


def _answer_all(w):
    while w.pending is not None:
        w.choose(w.pending.choices[0].key)


def test_waiting_alone_never_advances_a_mission():
    w = DreadWorld(seed=3)
    for _ in range(40):
        if w.pending is not None:
            w.choose(w.pending.choices[-1].key)
        if w.run.mission.id != "m1_battleship":
            break
        assert w.ship.progress == 0.0 and w.run.acts_done == 0
        w.tick()
    assert w.results and w.results[0]["outcome"] == "failed"      # the window closed on a captain who only waited


def test_an_order_takes_hours_and_progress_follows():
    w = DreadWorld(seed=3)
    a, ok, _ = w.act_status()
    assert ok and a.id == "search"
    w.do_act()
    assert w.working is a and w.run.work_left == a.hours
    _hours(w, 3)
    assert 0.0 < w.ship.progress < 1 / len(w.run.mission.acts) + 1e-9
    for _ in range(40):
        _answer_all(w)
        if w.run.acts_done >= 1 or w.run is None:
            break
        w.tick()
    assert w.run.acts_done == 1 and "m1_located" in w.ship.flags


def test_the_next_step_cannot_start_while_one_is_under_way():
    w = DreadWorld(seed=3)
    w.do_act()
    a, ok, why = w.act_status()
    assert not ok and "under way" in why.lower()
    assert w.do_act() == why


def test_an_act_that_needs_the_headsets_is_refused_with_the_reason():
    w = DreadWorld(seed=3)
    O.silence_sonar(w)
    assert "listening" in w.do_act() and w.working is None
    O.restore_sonar(w)
    w.do_act()
    assert w.working is not None
    O.silence_sonar(w)                         # silencing mid-search stops the work, it does not cancel it
    left = w.run.work_left
    _hours(w, 3)
    assert w.run.work_left == left and w.work_blocked
    O.restore_sonar(w)
    _hours(w, 1)
    assert w.run.work_left < left


def test_nothing_is_done_on_the_surface():
    w = DreadWorld(seed=3)
    O.surface(w)
    assert "surface" in w.do_act().lower() and w.working is None
    O.dive(w)
    w.do_act()
    O.surface(w)
    left = w.run.work_left
    _hours(w, 2)
    assert w.run.work_left == left


def test_a_worn_crew_takes_longer():
    fresh, worn = DreadWorld(seed=3), DreadWorld(seed=3)
    for c in worn.crew:
        c.fatigue = 0.85
    for w in (fresh, worn):
        w.do_act()
        w.tick()
    assert worn.run.work_left > fresh.run.work_left


def test_a_step_that_needs_a_man_fails_when_he_is_gone():
    w = DreadWorld(seed=3)
    w.run.acts_done = 2                        # "order the tubes flooded"
    for c in w.crew:
        if c.role == "torpedo":
            c.alive = False
    a, ok, why = w.act_status()
    assert a.id == "ready" and not ok and "nobody" in why.lower()


def test_hours_spent_on_the_crew_shorten_the_window():
    w = DreadWorld(seed=3)
    d0 = w.run.deadline
    O.hold_ritual(w)
    assert w.run.deadline == d0 - 1.5


def test_a_captain_who_gives_the_orders_finishes_the_mission():
    w = DreadWorld(seed=3)
    for _ in range(60):
        _answer_all(w)
        a, ok, _ = w.act_status()
        if ok:
            w.do_act()
        if w.results:
            break
        w.tick()
    assert w.results and w.results[0]["mission"] == "m1_battleship"
    assert w.results[0]["outcome"] == "success"


def test_every_mission_but_the_station_has_steps_and_each_names_its_hours():
    w = DreadWorld(seed=0)
    for m in w.missions:
        if m.kind == "hold":
            assert m.acts == []
            continue
        assert len(m.acts) >= 2
        assert all(a.hours > 0 and a.label for a in m.acts)
        assert all(a.why for a in m.acts if a.requires)
        assert sum(a.hours for a in m.acts) < m.ticks * m.window     # it can be done inside its window
