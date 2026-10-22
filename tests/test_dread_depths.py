"""The sea floor, the crush depth, the three kinds of torpedo and the men on deck (DESIGN.md 16)."""
from dread import hud, orders as O, systems
from dread.bathy import crush_depth, seabed
from dread.events import apply_effects
from dread.nav import lookout, navigation, true_xy
from dread.world import DreadWorld


def _w(seed=3):
    w = DreadWorld(seed=seed)
    for c in w.crew:
        c.fear, c.fatigue = 0.05, 0.05
    return w


def _at(w, x, y):
    """Put the boat at a chart position by making the mission's route pass through it."""
    ch = w.run.mission.chart
    ch["from"] = [x, y, "here"]
    ch["points"] = [[x + 1, y, "there"]] * len(ch["points"])


# ---- the sea floor ---------------------------------------------------------------------------------------
def test_the_water_is_shallow_by_the_coast_and_deep_far_out_but_never_bottomless_on_the_chart():
    assert seabed(100, 12) < 80 < seabed(60, 40) < seabed(20, 70)
    assert all(seabed(x, y) <= 900 for x in range(0, 110, 7) for y in range(0, 80, 5))


def test_the_boat_cannot_go_deeper_than_the_water_allows():
    w = _w()                                                    # at the pier: about 65 m of water
    assert "not the water" in O.set_depth(w, "deep")
    assert w.ship.depth_order == "shallow"
    assert navigation(w)["depth"] <= systems.seabed_here(w) - 8 and navigation(w)["keel"] >= 8
    w2 = _w()
    w2.run.acts_done = 1
    _at(w2, 40, 50)
    w2.ship.hull = 1.0
    assert O.set_depth(w2, "test").startswith("Going to 180") and w2.ship.depth_order == "test"
    assert navigation(w2)["keel"] > 50


def test_a_hull_that_is_hurt_will_not_take_the_depth_and_the_chief_says_how_far_she_will_go():
    w = _w()
    w.run.acts_done = 1
    _at(w, 40, 50)
    w.ship.hull = 0.35                                          # crush depth 170 m
    assert crush_depth(0.35) == 170
    assert "would not survive" in O.set_depth(w, "test")
    from dread.people import honest_advice
    assert "140 metres" in honest_advice(w, "chief engineer")


def test_the_hull_gives_when_it_is_taken_past_what_it_can_bear():
    w = _w()
    w.run.acts_done = 1
    _at(w, 40, 50)
    w.ship.hull = 1.0
    O.set_depth(w, "test")
    w.ship.hull = 0.3                                           # damage while deep: crush depth is now 160 m
    w.tick()
    assert w.ship.hull == 0.0 and "pressure hull gives" in "\n".join(w.log)
    from dread.endings import classify_ending
    assert classify_ending(w, len(w.crew)) == "lost_with_all_hands"


def test_close_to_the_limit_the_frames_complain_before_they_fail():
    w = _w()
    w.run.acts_done = 1
    _at(w, 40, 50)
    O.set_depth(w, "test")
    w.ship.hull = 0.45                                          # crush depth 190 m, boat at 180
    buckled = 0
    for _ in range(60):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.ship.hull = 0.45
        w.tick()
        buckled += "A frame buckles" in "\n".join(w.log[-2:])
        if w.ship.hull == 0.0:
            break
    assert buckled >= 1


def test_the_boat_that_sinks_past_her_orders_finds_the_bottom_or_is_crushed():
    w = _w()
    w.run.acts_done = 1
    _at(w, 70, 25)                                              # about 190 m of water
    w.ship.flags.add("sinking")
    for _ in range(10):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.ship.flags.add("sinking")
        w.tick()
    assert w.ship.depth_extra >= 60
    assert "The keel scrapes" in "\n".join(w.log) or w.ship.hull == 0.0
    w.ship.flags.discard("sinking")
    w.ship.hull = 1.0
    for _ in range(18):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.ship.hull = 1.0
        w.tick()
    assert w.ship.depth_extra == 0


def test_the_sounder_that_returns_nothing_and_the_choice_it_forces():
    w = _w()
    w.run.acts_done = 1
    _at(w, 40, 50)
    O.set_depth(w, "deep")
    w.ship.attention = 0.5
    ev = w.engine.events["no_bottom"]
    w.engine.fire(ev, w)
    assert "bottomless" in w.ship.flags and navigation(w)["keel"] is None
    assert {c.key for c in w.pending.choices} == {"blow", "check", "hold"}
    w.choose("blow")
    assert w.ship.surfaced and not w.ship.flags & {"sinking"}
    assert "no return from the sounder" in "\n".join(hud.instruments(_with_flag()))


def _with_flag():
    w = _w()
    w.run.acts_done = 1
    _at(w, 40, 50)
    O.set_depth(w, "deep")
    w.ship.flags.add("bottomless")
    return w


# ---- torpedoes -------------------------------------------------------------------------------------------
def test_the_stock_is_by_kind_and_loading_another_kind_costs_an_hour():
    w = _w()
    assert w.ship.types == {"steam": 6, "electric": 4, "acoustic": 2} and w.ship.torpedo_type == "steam"
    lost = w.run.lost
    assert "reloads the tubes with acoustic" in O.load_torpedoes(w, "acoustic")
    assert w.ship.torpedo_type == "acoustic" and w.run.lost == lost + 1.0
    assert "already hold" in O.load_torpedoes(w, "acoustic")
    w.ship.types["electric"] = 0
    assert "no electric" in O.load_torpedoes(w, "electric")


def test_firing_spends_the_kind_loaded_and_falls_back_when_it_runs_out():
    w = _w()
    w.ship.torpedo_type = "acoustic"
    apply_effects([{"op": "tubes", "state": "open"}, {"op": "fire", "n": 3}], w)
    assert w.ship.types["acoustic"] == 0 and w.ship.torpedoes == 9
    assert w.ship.types["steam"] == 5 and w.ship.torpedo_type == "steam"      # the room loaded the plentiful kind
    assert "No more acoustic" in "\n".join(w.log)
    assert sum(w.ship.types.values()) == w.ship.torpedoes


def test_steam_leaves_a_wake_electric_does_not():
    def attacked(kind):
        n = 0
        for seed in range(60):
            w = _w(seed)
            w.ship.torpedo_type = kind
            apply_effects([{"op": "tubes", "state": "open"}, {"op": "fire", "n": 3}], w)
            n += w.engagement is not None
        return n
    assert attacked("electric") == 0 and attacked("steam") >= 10


def test_an_acoustic_fish_follows_the_wrong_sound_and_a_loud_boat_gets_it_back():
    from dread.nav import _rows
    ghosts = circles = 0
    for seed in range(80):
        w = _w(seed)
        w.ship.torpedo_type = "acoustic"
        op = next(c for c in w.crew if c.role == "sonar")
        op.candor, op.trust = 1.0, 1.0
        w.deck.spawn("echo", {op.id}, 0.5, rng=w.rng, crew=w.crew)
        assert any(not r[3] for r in _rows(w))
        apply_effects([{"op": "tubes", "state": "open"}, {"op": "fire", "n": 1}], w)
        ghosts += "torp_ghost" in w.ship.flags
        circles += "torp_circular" in w.ship.flags
    assert ghosts >= 20
    quiet = loud = 0
    for seed in range(120):
        for noise, tag in ((0.1, "q"), (0.3, "l")):
            w = _w(seed)
            w.ship.torpedo_type, w.ship.noise = "acoustic", noise
            apply_effects([{"op": "tubes", "state": "open"}, {"op": "fire", "n": 1}], w)
            if "torp_circular" in w.ship.flags:
                quiet, loud = (quiet + 1, loud) if tag == "q" else (quiet, loud + 1)
    assert loud > quiet


def test_the_attack_reads_the_kind_of_fish():
    def hits(kind, flags=()):
        n = 0
        for seed in range(160):
            w = _w(seed)
            w.run.acts_done = 2
            w.run.working = 2
            w.run.work_left = 0.5
            w.ship.torpedo_type = kind
            for _ in range(24):
                if w.pending is not None and w.pending.event_id == "m1_attack":
                    break
                if w.pending is not None:
                    w.choose(w.pending.choices[0].key)
                else:
                    w.tick()
            else:
                continue
            for f in flags:
                w.ship.flags.add(f)
            w.choose("spread")
            n += bool(w.results and w.results[-1]["outcome"] == "success")
        return n
    assert hits("acoustic") > hits("steam") > hits("electric")


def test_run_time_follows_the_kind():
    from dread.nav import weapons
    runs = {}
    for kind in ("steam", "electric", "acoustic"):
        w = _w()
        w.ship.flags.add("in_combat")
        w.ship.torpedo_type = kind
        runs[kind] = weapons(w)["solutions"][0]["run_s"]
    assert runs["steam"] < runs["electric"] < runs["acoustic"]


# ---- the deck gang ---------------------------------------------------------------------------------------
def _on_the_bridge(w, kind="merchant"):
    w.ship.cohesion = 1.0
    O.surface(w)
    bx, by = true_xy(w)
    w.traffic.append({"id": 9, "kind": kind, "flag": "enemy", "x": bx + 5, "y": by + 1, "vx": 0, "vy": 0, "age": 0, "life": 30})


def test_a_rested_lookout_reports_the_hulls_he_sees_with_no_numbers_but_miles_and_a_bearing_in_words():
    w = _w()
    for c in w.crew:
        if c.role == "deck":
            c.candor, c.trust = 1.0, 1.0
    w.tick_no = 2
    _on_the_bridge(w)
    lines = lookout(w)
    assert lines and "steamer" in lines[0] and "about" in lines[0] and "lookout" in lines[0]
    assert "mile" in lines[0]
    O.dive(w)
    assert lookout(w) == []                                       # nobody is on the bridge once we are down


def test_a_frightened_lookout_also_reports_what_is_not_there_and_a_dumb_one_misses_what_is():
    def reports(fear, candor):
        n = 0
        for seed in range(80):
            w = _w(seed)
            for c in w.crew:
                if c.role == "deck":
                    c.fear = c.fatigue = fear
                    c.candor, c.trust = candor, 0.9
            w.tick_no = 2 + seed
            O.surface(w)
            n += sum("sail" in l for l in lookout(w))
        return n
    assert reports(0.05, 0.9) == 0 and reports(0.95, 0.9) >= 8
    w = _w()
    for c in w.crew:
        if c.role == "deck":
            c.candor, c.trust = 0.05, 0.1
    w.tick_no = 2
    _on_the_bridge(w)
    silent = sum(not any("steamer" in l for l in lookout(_tick(w, t))) for t in range(40))
    assert silent >= 25


def _tick(w, t):
    w.tick_no = 2 + t
    return w


def test_with_nobody_on_deck_the_bridge_is_unmanned_and_the_hatch_sticks():
    w = _w()
    for c in w.crew:
        if c.role == "deck":
            c.alive = False
    O.surface(w)
    assert lookout(w) == ["Nobody is posted on the bridge."]
    late = []
    for seed in range(40):
        x = _w(seed)
        for c in x.crew:
            if c.role == "deck":
                c.fear = c.fatigue = 0.95
        O.surface(x)
        O.dive(x)
        if x.ship.surfaced:
            late.append(x)
    assert len(late) >= 12
    x = late[0]
    x.tick(); x.tick()
    assert not x.ship.surfaced and "hatch is dogged" in "\n".join(x.log)


def test_the_rendezvous_needs_a_man_to_handle_the_lines():
    w = _w()
    w._start_mission(3)
    w.run.acts_done = 1
    w.ship.dr_error = 0.0
    assert w.act_status()[1]
    for c in w.crew:
        if c.role == "deck":
            c.alive = False
    a, ok, why = w.act_status()
    assert a.id == "rendezvous" and not ok and "handle the lines" in why


def test_the_bridge_sees_further_with_good_lookouts_and_less_with_bad_ones():
    from dread import sea
    w = _w()
    w.tick_no = 2
    O.surface(w)
    good = sea.visibility(w)
    for c in w.crew:
        if c.role == "deck":
            c.fear = c.fatigue = 0.95
    bad = sea.visibility(w)
    assert good > 12.0 > bad


def test_the_hud_shows_the_kinds_of_torpedo_and_what_the_lookout_says():
    w = _w()
    text = "\n".join(hud.instruments(w))
    assert "steam 6, electric 4, acoustic 2" in text and "tubes hold steam" in text
    w.tick_no = 2
    _on_the_bridge(w)
    for c in w.crew:
        if c.role == "deck":
            c.candor, c.trust = 1.0, 1.0
    assert "lookout" in "\n".join(hud.sonar(w))
