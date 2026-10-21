"""Helm, batteries, depth, damaged systems and damage control (DESIGN.md 15.1)."""
from dread import hud
from dread import orders as O
from dread import systems
from dread.nav import navigation
from dread.state import COMPARTMENTS
from dread.world import DreadWorld


def _w(seed=3):
    w = DreadWorld(seed=seed)
    for c in w.crew:
        c.fear, c.fatigue = 0.05, 0.05      # a rested, calm crew: orders are carried out at once
    return w


def _hurt(w, comp, damage):
    w.ship.damage[comp] = damage


def test_a_calm_helm_carries_the_order_out_at_once_and_a_frightened_one_late():
    w = _w()
    assert O.set_speed(w, "flank") == "Ahead flank." and w.ship.speed_order == "flank"
    late = 0
    for seed in range(40):
        w = DreadWorld(seed=seed)
        for c in w.crew:
            if c.role == "helm":
                c.fear, c.fatigue = 0.95, 0.95
        O.set_speed(w, "slow")
        late += w.ship.speed_order != "slow"
    assert late >= 12
    w.tick(); w.tick()
    assert w.ship.speed_order == "slow" and "The helm answers" in "\n".join(w.log)


def test_without_a_helmsman_orders_are_often_late():
    w = _w()
    for c in w.crew:
        if c.role == "helm":
            c.alive = False
    assert systems.role_error(w, "helm") == 0.6


def test_speed_sets_the_pace_of_the_work_and_the_noise_and_the_drain():
    out = {}
    for lv in ("slow", "standard", "flank"):
        w = _w()
        O.set_speed(w, lv)
        w.do_act()
        for _ in range(3):
            w.tick()
        out[lv] = (w.run.work_left, w.ship.noise, w.ship.battery)
    assert out["flank"][0] < out["standard"][0] < out["slow"][0]
    assert out["flank"][1] > out["standard"][1] > out["slow"][1]
    assert out["flank"][2] < out["standard"][2] < out["slow"][2]


def test_the_batteries_run_down_submerged_and_charge_on_the_surface_or_the_snorkel():
    w = _w()
    for _ in range(10):
        w.tick()
    low = w.ship.battery
    assert low < 1.0
    O.surface(w)
    for _ in range(4):
        w.tick()
    assert w.ship.battery > low
    O.dive(w)
    w.ship.battery = 0.5
    assert "periscope" in O.snorkel(w, True).lower()
    O.raise_periscope(w)
    O.snorkel(w, True)
    f = w.ship.fuel
    w.tick()
    assert w.ship.battery > 0.5 and w.ship.fuel < f and w.ship.noise > 0.1


def test_flat_batteries_stop_the_boat_and_the_dark_frightens_the_men():
    w = _w()
    w.do_act()
    w.ship.battery = 0.01
    for _ in range(3):
        w.tick()
    assert "battery_dead" in w.ship.flags and navigation(w)["speed"] == 0.0
    left = w.run.work_left
    w.tick()
    assert w.run.work_left == left and "flat" in w.work_blocked
    a, b = _w(), _w()
    for x in (a, b):
        for c in x.crew:
            c.fear = 0.3
    a.ship.battery, b.ship.battery = 0.2, 0.8
    a.tick(); b.tick()
    assert sum(c.fear for c in a.crew) > sum(c.fear for c in b.crew)    # dim lights
    O.surface(w)
    for _ in range(4):
        w.tick()
    assert "battery_dead" not in w.ship.flags


def test_depth_hides_the_boat_but_the_hull_and_the_men_pay():
    w = _w()
    f = sum(c.fear for c in w.crew)
    O.set_depth(w, "test")
    w.tick()
    assert navigation(w)["depth"] == 180 and sum(c.fear for c in w.crew) > f
    w.ship.hull = 0.5
    leaks = 0
    for _ in range(60):
        while w.pending is not None:
            w.choose(w.pending.choices[0].key)
        h = w.ship.hull
        w.tick()
        leaks += "A seam gives" in "\n".join(w.log[-3:]) and w.ship.hull < h
    assert leaks >= 1


def test_a_hurt_engine_cannot_give_flank_and_a_drowned_control_room_jams_the_planes():
    w = _w()
    _hurt(w, "engine room", 0.2)                                    # 60 %: damaged
    assert O.set_speed(w, "flank") == "The engine room cannot give it."
    _hurt(w, "engine room", 0.4)                                    # 20 %: dead
    w.ship.speed_order = "slow"
    assert "slow" in O.set_speed(w, "standard")
    p0 = systems.pace(w)
    assert p0 < 0.4
    _hurt(w, "control room", 0.4)
    assert "jammed" in O.set_depth(w, "deep")


def test_a_hurt_bow_room_gives_fewer_tubes_and_a_drowned_one_none():
    from dread.events import apply_effects
    w = _w()
    apply_effects([{"op": "tubes", "state": "open"}], w)
    _hurt(w, "bow torpedo room", 0.2)
    apply_effects([{"op": "fire", "n": 3}], w)
    assert w.ship.torpedoes == 10                                   # only two tubes could fire
    w = _w()
    apply_effects([{"op": "tubes", "state": "open"}], w)
    _hurt(w, "bow torpedo room", 0.4)
    apply_effects([{"op": "fire", "n": 3}], w)
    assert w.ship.torpedoes == 12


def test_damaged_berths_make_poor_sleep():
    a, b = _w(), _w()
    _hurt(b, "crew quarters", 0.4)
    for w in (a, b):
        w.tick_no = 2
        for c in w.crew:
            c.section = 2                                          # everyone off watch
            c.fatigue = 0.6
        w.tick()
    assert sum(c.fatigue for c in b.crew) > sum(c.fatigue for c in a.crew)


def test_damage_control_mends_the_worst_compartment_and_spends_the_spares():
    w = _w()
    w.ship.hull = 0.6
    w.settle_damage()
    worst = max(COMPARTMENTS, key=lambda c: w.ship.damage[c])
    O.damage_control(w, True)
    s0 = w.ship.spares
    for _ in range(10):
        w.tick()
    assert w.ship.hull > 0.65 and w.ship.spares < s0
    assert w.ship.damage[worst] < 0.4
    w.ship.spares = 0.0
    w.tick()
    assert not w.ship.dc_active and "spares are gone" in "\n".join(w.log)
    assert "nothing left" in O.damage_control(w, True)


def test_the_hud_shows_the_battery_the_spares_and_the_orders():
    w = _w()
    O.set_speed(w, "slow")
    text = "\n".join(hud.ledger(w) + hud.instruments(w))
    assert "Battery" in text and "Spares" in text and "ordered slow" in text


def test_the_menu_offers_the_helm_and_depth_and_only_what_makes_sense():
    from dread.play import available_orders
    w = _w()
    labels = [i.label for i in available_orders(w)]
    assert "Ahead slow" in labels and "Ahead flank" in labels and "Ahead standard" not in labels
    assert "Go to 120 metres" in labels and "Run the diesels at snorkel depth" not in labels
    assert not any("Damage control" in l for l in labels)           # nothing is broken
    w.ship.hull = 0.7
    O.raise_periscope(w)
    labels = [i.label for i in available_orders(w)]
    assert any("Damage control" in l for l in labels) and "Run the diesels at snorkel depth" in labels


def test_a_dead_sonar_gives_no_contacts_and_no_reports():
    from dread.nav import contacts
    w = _w()
    w.ship.flags.add("in_combat")
    assert contacts(w)
    w.ship.flags.add("fault_sonar")
    assert contacts(w) == []
    assert "DEAD" in "\n".join(hud.sonar(w))
