"""The chart, the instruments and the hull's compartments (DESIGN.md 12.7). Display only, but exact."""
from dread import hud
from dread import orders as O
from dread.endings import classify_ending
from dread.nav import COLUMNS, grid_ref, hull_report, navigation
from dread.state import COMPARTMENTS
from dread.world import DreadWorld


def test_the_station_is_grid_k7_and_the_chart_agrees_with_the_grid():
    assert grid_ref(104, 66) == "K-7"
    assert grid_ref(0, 0) == "A-1" and grid_ref(109, 79) == "K-8"
    w = DreadWorld(seed=1)
    for m in w.missions:
        for x, y, _ in [m.chart["from"]] + m.chart["points"]:
            assert 0 <= x < 110 and 0 <= y < 80
    assert w.missions[-1].chart["points"][-1][:2] == [104, 66]


def test_the_boat_moves_only_as_the_work_is_done():
    w = DreadWorld(seed=3)
    n0 = navigation(w)
    for _ in range(5):
        w.tick()
    assert navigation(w)["x"] == n0["x"]                  # waiting goes nowhere
    w.do_act()
    last = navigation(w)["x"]
    for _ in range(4):
        w.tick()
    assert navigation(w)["x"] != last
    assert navigation(w)["eta_h"] is not None


def test_the_boat_reaches_each_waypoint_when_its_step_is_done():
    w = DreadWorld(seed=3)
    w.do_act()
    for _ in range(40):
        if w.pending is not None or w.run.acts_done >= 1:
            break
        w.tick()
    n = navigation(w)
    x, y, label = w.missions[0].chart["points"][0]
    assert (n["x"], n["y"]) == (x, y) and n["next"] == "Contact bearing"


def test_speed_and_depth_follow_what_the_boat_is_doing():
    w = DreadWorld(seed=3)
    assert navigation(w)["speed"] < 3.0 and navigation(w)["depth"] == 60
    O.silent_running(w, True)
    assert navigation(w)["depth"] == 90
    O.silent_running(w, False)
    O.surface(w)
    assert navigation(w)["depth"] == 0


def test_on_station_the_boat_is_at_k7_and_going_home_it_moves_toward_base():
    w = DreadWorld(seed=3)
    w._start_mission(4)
    assert navigation(w)["grid"] == "K-7"
    w.ship.fuel = 1.0
    w.leave_station()
    for _ in range(9):
        w.tick()
    n = navigation(w)
    assert n["next"] == "Base" and 100 - 1 <= n["x"] <= 104 and n["y"] < 66


def test_damage_is_booked_to_a_compartment_and_repair_heals_the_worst_first():
    w = DreadWorld(seed=3)
    assert all(h["integrity"] == 1.0 and h["state"] == "sound" for h in hull_report(w))
    w.ship.hull -= 0.3
    w.settle_damage()
    hurt = [h for h in hull_report(w) if h["integrity"] < 1.0]
    assert len(hurt) == 1 and abs(hurt[0]["integrity"] - 0.4) < 1e-9 and hurt[0]["state"] == "damaged"
    assert abs(sum(w.ship.damage.values()) - 0.3) < 1e-9
    w.ship.hull += 0.1
    w.settle_damage()
    assert abs(sum(w.ship.damage.values()) - 0.2) < 1e-9


def test_booking_damage_is_idempotent_and_takes_no_dice_from_the_world():
    a, b = DreadWorld(seed=5), DreadWorld(seed=5)
    a.ship.hull -= 0.2
    for _ in range(3):
        a.settle_damage()
    b.ship.hull -= 0.2
    b.settle_damage()
    assert a.ship.damage == b.ship.damage and a.rng.random() == b.rng.random()


def test_the_total_booked_matches_the_ledger_over_a_whole_patrol():
    from dread.sim import issue_orders, pick_choice
    import random
    w = DreadWorld(seed=2)
    prng = random.Random(1)
    while not w.finished:
        if w.pending is not None:
            w.choose(pick_choice("mission_first", w.pending, prng, w))
            continue
        issue_orders("mission_first", w, prng)
        w.tick()
    w.settle_damage()
    lost = sum(w.ship.damage.values())
    assert set(w.ship.damage) == set(COMPARTMENTS)
    assert abs(lost - (1.0 - w.ship.hull)) < 0.05          # repairs may not find damage to undo, so only near


def test_the_hud_shows_the_instruments_and_the_hull():
    w = DreadWorld(seed=3)
    text = "\n".join(hud.instruments(w))
    for part in ("INSTRUMENTS", "Grid", "Heading", "Speed", "Depth", "Signature", "Hull by compartment", "bow tubes"):
        assert part in text


def test_sinking_the_fishing_boat_has_its_own_ending():
    w = DreadWorld(seed=3)
    w.ship.flags.add("fishermen_sunk")
    assert classify_ending(w, len(w.crew)) == "the_lamp"
    w.ship.flags.add("offering_made")                       # the sea's verdict still outranks it
    assert classify_ending(w, len(w.crew)) == "the_price"
