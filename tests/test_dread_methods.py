"""Every step of a mission can be done more than one way, and each way has a price (DESIGN.md 17.1)."""
from dread import orders as O
from dread.play import available_orders
from dread.world import DreadWorld


def _w(seed=3):
    w = DreadWorld(seed=seed)
    for c in w.crew:
        c.fear, c.fatigue = 0.05, 0.05
    return w


def _hours(w, method):
    w.do_act(method)
    return w.run.work_total


def test_every_step_but_the_station_offers_at_least_two_ways():
    w = _w()
    for m in w.missions:
        for a in m.acts:
            assert len(a.methods) >= 2, (m.id, a.id)
            assert all(x["label"] and x["hint"] and x["hours_mult"] > 0 for x in a.methods)
            assert len({x["id"] for x in a.methods}) == len(a.methods)


def test_the_way_you_choose_sets_the_hours_and_is_in_the_log():
    h = {m: _hours(_w(), m) for m in ("listen", "periscope", "flank")}
    assert h["flank"] < h["periscope"] < h["listen"] and h["listen"] == 5.5
    w = _w()
    w.do_act("flank")
    assert "(Run the grid at flank)" in w.log[-1]
    w = _w()
    w.do_act("listen")
    assert "(" not in w.log[-1].split("order it:")[1]            # the plain way is not remarked on
    w = _w()
    w.do_act("no-such-way")
    assert w.run.work_total == 5.5                                # an unknown way is the plain one


def test_the_ways_do_what_they_say_and_lapse_when_the_work_is_done():
    w = _w()
    w.do_act("flank")
    assert w.ship.speed_order == "flank"
    for _ in range(12):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.tick()
        if w.run.acts_done:
            break
    assert w.run.acts_done == 1 and w.ship.speed_order == "standard"
    w = _w()
    w.run.acts_done = 1
    w.do_act("silent")
    assert w.ship.silent_running and w.ship.speed_order == "slow"
    w.run.work_left = 0.01
    for _ in range(3):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.tick()
    assert not w.ship.silent_running and w.ship.speed_order == "standard"


def test_the_periscope_way_is_worse_in_the_dark_and_in_fog():
    def hours(tick, fog):
        w = _w()
        w.tick_no = tick
        if fog:
            w.ship.flags.add("fog")
        w.do_act("periscope")
        return w.run.work_total
    day, night, fog = hours(2, False), hours(16, False), hours(2, True)
    assert day == 5.5 * 0.7 and night == fog == 5.5 * 1.7


def test_checking_the_solution_twice_costs_an_hour_and_makes_the_shot_truer():
    from dread.nav import solution_error
    w = _w()
    w.run.acts_done = 2
    for c in w.crew:
        if c.role == "torpedo":
            c.fear = c.fatigue = 0.8
    plain = solution_error(w)
    assert w.method_hours(w.next_act(), w.next_act().methods[1]) == 2.0
    w.ship.flags.add("double_checked")
    assert 0 < solution_error(w) < plain and abs(solution_error(w) - plain * 0.6) < 1e-9


def test_the_report_can_be_short_or_in_clear_with_their_own_costs():
    w = _w()
    w._start_mission(1)
    w.run.acts_done = 1
    w.ship.dr_error = 0.0
    d0 = w.ship.orders_doubt
    w.do_act("short")
    assert w.run.work_total == 0.75 and w.ship.orders_doubt > d0
    w2 = _w()
    w2._start_mission(1)
    w2.run.acts_done = 1
    w2.ship.dr_error = 0.0
    w2.ship.orders_doubt = 0.5
    a0 = w2.ship.attention
    w2.do_act("confirm")
    assert w2.run.work_total == 2.25 and w2.ship.orders_doubt < 0.5 and w2.ship.attention > a0


def test_the_menu_offers_every_way_as_an_order():
    labels = [i.label for i in available_orders(_w())]
    assert "Listen: a patient sweep with the headsets" in labels
    assert "Sweep the horizon with the periscope" in labels and "Run the grid at flank" in labels
    first = available_orders(_w())[0]
    assert "5.5 h" in first.hint
    w = _w()
    available_orders(w)[2].run()                                  # the third way
    assert w.run.method == "flank"


def test_each_kind_of_captain_does_things_his_own_way():
    from dread.sim import METHOD_PREFS
    seen = {}
    for pol in METHOD_PREFS:
        used = set()
        for seed in range(12):
            import random
            from dread.sim import issue_orders, pick_choice
            w = DreadWorld(seed=seed)
            prng = random.Random(seed)
            for _ in range(120):
                if w.finished:
                    break
                if w.pending is not None:
                    w.choose(pick_choice(pol, w.pending, prng, w))
                    continue
                issue_orders(pol, w, prng)
                if w.run is not None and w.run.method:
                    used.add(w.run.method)
                w.tick()
        seen[pol] = used
    assert "flank" in seen["mission_first"] and "listen" in seen["crew_first"] and "periscope" in seen["paranoid"]
    assert seen["mission_first"] != seen["crew_first"]
