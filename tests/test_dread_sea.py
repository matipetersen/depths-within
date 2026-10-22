from dread import nav
"""The navigator's uncertainty, the hours of the day, fog and the traffic that is none of our business (DESIGN.md 15.3)."""
from dread import hud
from dread import orders as O
from dread import sea
from dread.nav import contacts, navigation, periscope, true_xy
from dread.world import DreadWorld


def _w(seed=3):
    w = DreadWorld(seed=seed)
    for c in w.crew:
        c.fear, c.fatigue = 0.05, 0.05
    return w


def test_the_position_we_believe_drifts_from_the_true_one_and_a_fix_pulls_it_back():
    w = _w()
    assert navigation(w)["err_nm"] == 0.0
    nav.set_course(w, 5.0, 75.0, "somewhere")
    for _ in range(12):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.tick()
    assert w.ship.dr_error > 1.0
    n = navigation(w)
    tx, ty = true_xy(w)
    assert (n["x"], n["y"]) != (tx, ty)                         # the chart shows where we think we are, not where we are
    err = w.ship.dr_error
    w.ship.flags.discard("fog")
    w.tick_no = 2
    O.raise_periscope(w)
    assert "Fix by the coast" in O.take_fix(w)
    assert w.ship.dr_error < err and w.ship.last_fix == w.tick_no


def test_a_fix_needs_the_periscope_the_surface_or_the_sky():
    w = _w()
    assert "needs the periscope" in O.take_fix(w)
    O.surface(w)
    w.tick_no = 14                                              # 20:00 by the chronometer
    assert "stars" in O.take_fix(w)
    w.tick_no = 2                                               # broad day
    for c in w.crew:
        if c.role == "radio":
            c.alive = False
    assert "No stars, and no radio" in O.take_fix(w)


def test_a_tired_helm_and_a_watching_presence_make_the_error_grow_faster():
    a, b = _w(), _w()
    for c in b.crew:
        if c.role == "helm":
            c.fear = c.fatigue = 0.9
    b.ship.attention = 0.6
    for x in (a, b):
        x.do_act()
        for _ in range(10):
            x.tick()
    assert b.ship.dr_error > a.ship.dr_error * 1.5


def test_a_step_that_needs_a_known_position_is_blocked_until_a_fix_is_taken():
    w = _w()
    w.run.acts_done = 2
    w.ship.dr_error = 6.0
    a, ok, why = w.act_status()
    assert a.id == "ready" and not ok and "Take a fix" in why
    w.ship.dr_error = 1.0
    assert w.act_status()[1]
    w.ship.dr_error = 6.0
    w.run.acts_done = 1
    assert w.act_status()[1]                                    # the step before it needs no fix


def test_at_night_the_eye_reaches_less_and_fog_makes_it_less_again():
    w = _w()
    w.tick_no = 2
    day = sea.visibility(w)
    w.tick_no = 18
    night = sea.visibility(w)
    w.ship.flags.add("fog")
    fog = sea.visibility(w)
    assert day == 12.0 > night > fog and sea.night(w)
    O.raise_periscope(w)
    assert "visibility" in O.take_fix(w)                        # nothing to take a bearing on


def test_fog_and_darkness_feed_the_eye_that_sees_things():
    w = _w()
    O.raise_periscope(w)
    w.ship.attention, w.ship.moral_debt = 0.4, 0.4
    def seen(tick, fog):
        n = 0
        w.ship.flags.discard("fog")
        if fog:
            w.ship.flags.add("fog")
        for t in range(tick, tick + 300, 3):
            w.tick_no = t
            n += len(periscope(w)["distortions"])
        return n
    assert seen(30, True) > seen(30, False)


def test_traffic_comes_and_goes_and_never_during_an_attack():
    w = _w()
    seen = 0
    for _ in range(300):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.tick()
        seen = max(seen, len(w.traffic))
        assert len(w.traffic) <= sea.TRAFFIC_MAX
        assert all(o["age"] < o["life"] for o in w.traffic)
    assert seen >= 1
    w = _w()
    w.combat(0.5)
    n = len(w.traffic)
    for _ in range(3):
        w.tick()
        if w.pending is not None:
            w.choose("hold")
    assert len(w.traffic) <= n                                  # no new hull while the charges fall


def test_a_hull_on_the_scope_is_real_and_looks_like_every_other_contact():
    w = _w()
    bx, by = true_xy(w)
    w.traffic.append({"id": 1, "kind": "merchant", "flag": "neutral", "x": bx + 10, "y": by, "vx": 0, "vy": 0, "age": 0, "life": 20})
    cs = contacts(w)
    assert len(cs) == 1 and set(cs[0]) == {"tag", "bearing", "range_nm", "label"} and cs[0]["bearing"] == 90
    O.raise_periscope(w)
    assert len(periscope(w)["others"]) == 1


def test_the_crossing_offers_three_ways_out_and_each_has_its_price():
    from dread.events import apply_effects
    w = _w()
    bx, by = true_xy(w)
    def hull(flag, kind="merchant"):
        w.traffic[:] = [{"id": 2, "kind": kind, "flag": flag, "x": bx + 3, "y": by, "vx": 0, "vy": 0, "age": 0, "life": 20}]
    hull("neutral")
    d0 = w.ship.moral_debt
    apply_effects([{"op": "traffic_act", "action": "sink"}], w)
    assert w.ship.moral_debt > d0 + 0.3 and "neutral_sunk" in w.ship.flags and w.ship.torpedoes == 10 and not w.traffic
    w = _w()
    bx, by = true_xy(w)
    w.traffic[:] = [{"id": 2, "kind": "merchant", "flag": "enemy", "x": bx + 3, "y": by, "vx": 0, "vy": 0, "age": 0, "life": 20}]
    apply_effects([{"op": "traffic_act", "action": "sink"}], w)
    assert "enemy_sunk" in w.ship.flags and w.ship.moral_debt == 0.0
    w = _w()
    bx, by = true_xy(w)
    w.traffic[:] = [{"id": 2, "kind": "fishing", "flag": "enemy", "x": bx + 3, "y": by, "vx": 0, "vy": 0, "age": 0, "life": 20}]
    lost = w.run.lost
    apply_effects([{"op": "traffic_act", "action": "shadow"}], w)
    assert w.run.lost == lost + 3.0 and ("neutral" in w.log[-1] or "enemy" in w.log[-1])


def test_a_neutral_sunk_ends_in_the_same_stain_as_a_civilian():
    from dread.endings import classify_ending
    w = _w()
    w.ship.flags.add("neutral_sunk")
    assert classify_ending(w, len(w.crew)) == "stained_victory"


def test_the_hud_states_how_sure_we_are_of_where_we_are():
    w = _w()
    w.ship.dr_error = 2.3
    text = "\n".join(hud.instruments(w))
    assert "within 2.3 nm" in text and "no fix since the pier" in text
