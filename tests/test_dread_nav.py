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


# ---- the scope ---------------------------------------------------------------------------------------

def _near_the_target(seed=3):
    from dread.world import DreadWorld
    w = DreadWorld(seed=seed)
    w.run.acts_done = 1
    w.run.working = 1
    w.run.work_left = 1.0           # nearly there: the target is inside 30 nm
    w._set_progress()
    return w


def test_a_real_contact_shows_once_the_search_has_found_it_and_is_in_range():
    from dread.nav import contacts
    w = DreadWorld(seed=3)
    assert contacts(w) == []                                   # nothing found yet
    w = _near_the_target()
    seen = []
    for _ in range(8):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        seen.append(contacts(w))
        w.tick()
    seen = [c for c in seen if c]
    assert seen and all(c[0]["label"] == "heavy screws, steady" for c in seen if len(c) == 1 and c[0]["range_nm"] < 20)


def test_a_false_contact_looks_exactly_like_a_real_one():
    from dread.nav import LABEL_POOL, contacts
    w = DreadWorld(seed=3)
    op = next(c for c in w.crew if c.role == "sonar")
    op.candor, op.trust = 1.0, 1.0
    w.deck.spawn("echo", {op.id}, 0.5, rng=w.rng, crew=w.crew)
    cs = contacts(w)
    assert len(cs) == 1
    assert set(cs[0]) == {"tag", "bearing", "range_nm", "label"}   # no kind, no id, no flag: nothing to tell them apart
    assert cs[0]["label"] in LABEL_POOL                          # drawn from the same words the real ones use
    assert all(m.chart["target"][2] in LABEL_POOL for m in w.missions if "target" in m.chart)   # no real label a false one cannot wear


def test_contacts_are_ordered_by_bearing_not_by_what_they_are():
    from dread.nav import contacts
    w = DreadWorld(seed=3)
    w.ship.flags.add("in_combat")
    for cid in range(1, 4):
        c = w.crew[cid]
        c.candor, c.trust = 1.0, 1.0
        w.deck.spawn("echo", {c.id}, 0.5, rng=w.rng, crew=w.crew)
    bearings = [c["bearing"] for c in contacts(w)]
    assert bearings == sorted(bearings) and len(bearings) >= 2


def test_with_the_sonar_off_the_scope_is_dark_but_the_radar_works_on_the_surface():
    from dread.nav import contacts
    w = DreadWorld(seed=3)
    w.ship.flags.add("in_combat")
    assert contacts(w)
    O.silence_sonar(w)
    assert contacts(w) == []
    O.surface(w)
    assert contacts(w)                                          # radar: the real ones only, and no false echoes


# ---- torpedoes and the periscope ---------------------------------------------------------------------

def _at_the_firing_point(seed=3):
    w = DreadWorld(seed=seed)
    w.run.acts_done = 2
    w.run.working = 2
    w.run.work_left = 0.5
    w._set_progress()
    return w


def _to_the_attack(w):
    for _ in range(20):
        if w.pending is not None and w.pending.event_id == "m1_attack":
            return
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        else:
            w.tick()


def test_the_ready_step_floods_the_bow_tubes_and_the_attack_spends_the_torpedoes():
    w = DreadWorld(seed=3)
    assert w.ship.tubes == ["loaded"] * 6 and w.ship.torpedoes == 12
    w.run.acts_done = 2
    w.run.working = 2
    w.run.work_left = 0.5
    w.tick()
    assert w.ship.tubes[:4] == ["flooded"] * 4 and w.ship.tubes[4:] == ["loaded"] * 2
    _to_the_attack(w)
    assert w.pending is not None and w.pending.event_id == "m1_attack"
    assert w.ship.tubes[:4] == ["open"] * 4                      # "tubes flooded, doors open"
    w.choose("spread")
    assert w.ship.torpedoes == 9                                  # three fish are gone, whatever the shot did


def test_firing_empties_the_tubes_it_used_and_nothing_else():
    from dread.events import apply_effects
    w = DreadWorld(seed=3)
    apply_effects([{"op": "tubes", "state": "open"}, {"op": "fire", "n": 3}], w)
    assert w.ship.tubes == ["empty"] * 3 + ["open", "loaded", "loaded"] and w.ship.torpedoes == 9
    apply_effects([{"op": "tubes", "state": "loaded"}], w)
    assert w.ship.tubes == ["empty"] * 3 + ["loaded"] * 3         # a tube with nothing in it stays empty


def test_breaking_off_keeps_every_torpedo_and_the_next_mission_reloads():
    w = _at_the_firing_point()
    _to_the_attack(w)
    w.choose("break_off")
    assert w.ship.torpedoes == 12 and "open" not in w.ship.tubes and "flooded" not in w.ship.tubes
    w.ship.tubes[0] = "empty"
    w._start_mission(1)
    assert w.ship.tubes == ["loaded"] * 6                         # the torpedo room reloads between orders


def test_a_calm_torpedo_room_reports_the_truth_and_a_frightened_one_does_not():
    from dread.nav import weapons
    w = DreadWorld(seed=3)
    assert weapons(w)["tubes"] == w.ship.tubes
    for c in w.crew:
        if c.role == "torpedo":
            c.fear, c.fatigue = 0.95, 0.95
    wrong = sum(weapons(w)["tubes"] != w.ship.tubes for _ in range(1) for w.tick_no in range(40))
    assert wrong >= 10                                            # it lies often, and never says so
    assert weapons(w)["stock"] == w.ship.torpedoes                # the ledger's count is exact all the same


def test_with_no_torpedo_man_alive_the_room_does_not_answer():
    from dread.nav import weapons
    w = DreadWorld(seed=3)
    for c in w.crew:
        if c.role == "torpedo":
            c.alive = False
    r = weapons(w)
    assert not r["manned"] and r["tubes"] == ["no report"] * 6 and r["solutions"] == []


def test_every_contact_gets_a_solution_the_false_ones_too():
    from dread.nav import contacts, weapons
    w = DreadWorld(seed=3)
    w.ship.flags.add("in_combat")
    op = next(c for c in w.crew if c.role == "sonar")
    op.candor, op.trust = 1.0, 1.0
    w.deck.spawn("echo", {op.id}, 0.5, rng=w.rng, crew=w.crew)
    cs, sols = contacts(w), weapons(w)["solutions"]
    assert len(cs) == 2 and [x["tag"] for x in sols] == [c["tag"] for c in cs]
    assert set(sols[0]) == {"tag", "bearing", "range_yd", "run_s", "gyro"}


def test_the_periscope_is_housed_until_raised_and_raising_it_has_a_price():
    from dread.nav import periscope
    w = DreadWorld(seed=3)
    assert periscope(w)["mode"] == "down" and navigation(w)["depth"] == 60
    before = w.ship.attention
    O.raise_periscope(w)
    assert periscope(w)["mode"] == "periscope" and navigation(w)["depth"] == 14
    for _ in range(10):
        w.tick()
    assert w.ship.attention > before
    O.surface(w)
    assert not w.ship.scope_up and periscope(w)["mode"] == "bridge"


def test_the_periscope_shows_the_target_only_once_it_is_found_and_only_when_trained_on_it():
    from dread.nav import periscope
    w = DreadWorld(seed=3)
    O.raise_periscope(w)
    assert periscope(w)["ship"] is None                           # not found yet
    w = _at_the_firing_point()
    O.raise_periscope(w)
    sh = periscope(w)["ship"]
    assert sh is not None and sh["kind"] == "capital" and sh["escorts"] == 3 and not sh["in_field"]
    sh = periscope(w, train=sh["rel"])["ship"]
    assert sh["in_field"]


def test_a_calm_clean_eye_sees_only_the_sea_and_a_troubled_one_sees_more():
    from dread.nav import DISTORTIONS, periscope
    w = _at_the_firing_point()
    O.raise_periscope(w)
    calm = 0
    for t in range(60):
        w.tick_no = t
        calm += len(periscope(w)["distortions"])
    assert calm == 0
    w.ship.moral_debt, w.ship.attention = 0.8, 0.6
    for c in w.crew:
        c.fear, c.fatigue = 0.7, 0.6
    seen = set()
    for t in range(0, 300, 3):
        w.tick_no = t
        seen |= set(periscope(w)["distortions"])
    assert seen and seen <= set(DISTORTIONS) and len(seen) >= 3


def test_a_ghost_hull_can_only_stand_where_a_false_contact_is():
    from dread.nav import periscope
    w = DreadWorld(seed=3)
    O.raise_periscope(w)
    op = next(c for c in w.crew if c.role == "sonar")
    op.candor, op.trust = 1.0, 1.0
    p = w.deck.spawn("echo", {op.id}, 0.5, rng=w.rng, crew=w.crew)
    bearing = (p.id * 97 + 41 + p.age * 2) % 360
    hits = 0
    for t in range(0, 90, 3):
        w.tick_no = t
        hits += len(periscope(w, train=((bearing - navigation(w)["heading"] + 180) % 360) - 180)["ghosts"])
        assert periscope(w, train=180)["ghosts"] == [] or abs(((bearing - (navigation(w)["heading"] + 180)) + 180) % 360 - 180) <= 25
    assert hits > 0


def test_the_hud_shows_the_tubes_the_torpedoes_and_the_periscope():
    w = _at_the_firing_point()
    O.raise_periscope(w)
    text = "\n".join(hud.instruments(w))
    assert "Torpedoes aboard 12" in text and "1:" in text and "Periscope:" in text
    assert "Torpedoes 12" in "\n".join(hud.ledger(w))


# ---- the attack reads the room and the eye ------------------------------------------------------------

def test_the_solution_error_is_the_rooms_unless_the_eye_has_the_target():
    from dread.nav import solution_error
    w = _at_the_firing_point()
    assert solution_error(w) == 0.0                              # a rested, calm room
    for c in w.crew:
        if c.role == "torpedo":
            c.fear, c.fatigue = 0.9, 0.9
    room = solution_error(w)
    assert room > 0.4
    O.raise_periscope(w)
    w.tick_no = 7
    clear = solution_error(w)
    assert clear < room and abs(clear - room * 0.4) < 1e-9       # a clear eye mends the room's error
    w.ship.moral_debt, w.ship.attention = 0.9, 0.8               # ...a troubled one makes it worse
    for c in w.crew:
        c.fear, c.fatigue = 0.8, 0.8
    bad = [solution_error(_set_tick(w, t)) for t in range(0, 300, 3)]
    assert max(bad) == 0.5


def _set_tick(w, t):
    w.tick_no = t
    return w


def test_a_clear_eye_wins_the_attack_more_often_than_a_room_that_is_afraid():
    from dread.events import apply_effects
    def shots(raise_scope):
        hits = 0
        for seed in range(150):
            w = _at_the_firing_point(seed)
            for c in w.crew:
                if c.role == "torpedo":
                    c.fear, c.fatigue = 0.85, 0.85
            if raise_scope:
                O.raise_periscope(w)
            _to_the_attack(w)
            if w.pending is None or w.pending.event_id != "m1_attack":
                continue
            w.choose("spread")
            hits += w.results[-1]["outcome"] == "success" if w.results else 0
        return hits
    assert shots(True) > shots(False) + 10


def test_a_frightened_room_loses_tubes_and_a_calm_one_never_does():
    from dread.events import apply_effects
    lost = calm = 0
    for seed in range(60):
        w = DreadWorld(seed=seed)
        apply_effects([{"op": "tubes", "state": "open"}, {"op": "fire", "n": 3}], w)
        calm += w.ship.torpedoes != 9
        w = DreadWorld(seed=seed)
        for c in w.crew:
            if c.role == "torpedo":
                c.fear, c.fatigue = 0.95, 0.95
        apply_effects([{"op": "tubes", "state": "open"}, {"op": "fire", "n": 3}], w)
        lost += w.ship.torpedoes > 9
    assert calm == 0 and lost >= 20
