"""The engagement: an attack as a sequence of decisions where fear decides what is tactical (DESIGN.md 15.2)."""
from dread import orders as O
from dread.world import DreadWorld


def _offshore(w):
    """Put the boat in deep water: at the pier there is hardly any (DESIGN.md 16.1)."""
    ch = w.run.mission.chart
    ch["from"] = [40, 50, "offshore"]
    ch["points"] = [[41, 50, "offshore"]] * len(ch["points"])
    w.run.acts_done = 1
    return w


def _w(seed=3, fear=0.05):
    w = DreadWorld(seed=seed)
    for c in w.crew:
        c.fear, c.fatigue = fear, 0.05
    return w


def _fight(w, choose, limit=40):
    for _ in range(limit):
        if w.pending is not None:
            keys = [c.key for c in w.pending.choices]
            want = choose(w.pending)
            w.choose(want if want in keys else keys[0])          # another event may cut in; take its first option
        elif w.engagement is None:
            return
        else:
            w.tick()


def test_an_attack_is_a_decision_every_turn_and_it_ends():
    w = _w()
    w.combat(0.6)
    assert w.engagement is not None and "in_combat" in w.ship.flags
    w.tick()
    assert w.pending is not None and w.pending.event_id == "engagement_turn"
    keys = {c.key for c in w.pending.choices}
    assert {"hold", "deep", "silent", "evade", "decoy"} <= keys
    _fight(w, lambda p: "hold")
    assert w.engagement is None and "in_combat" not in w.ship.flags
    assert "The sea goes back to being the sea" in "\n".join(w.log)


def test_nothing_else_happens_and_no_work_is_done_while_it_lasts():
    w = _w()
    w.do_act()
    w.combat(0.5)
    left = w.run.work_left
    w.tick()
    assert w.pending is not None and "under attack" in w.work_blocked
    w.choose("hold")
    w.tick()
    assert w.run.work_left == left


def test_orders_do_what_they_say():
    w = _offshore(_w())
    w.combat(0.6)
    w.tick()
    w.choose("deep")
    assert w.ship.depth_order == "deep"
    w.tick()
    w.choose("silent")
    assert w.ship.silent_running
    w.tick()
    if w.pending:
        w.choose("evade") if "evade" in {c.key for c in w.pending.choices} else None
    assert w.ship.speed_order == "flank" or w.engagement is None
    w = _w()
    w.combat(0.9)
    w.tick()
    n = w.ship.decoys
    w.choose("decoy")
    assert w.ship.decoys == n - 1


def test_a_loud_boat_at_the_guessed_depth_is_hit_more_than_a_quiet_one_elsewhere():
    def hull_after(speed, silent, depth):
        total = 0.0
        for seed in range(80):
            w = _w(seed)
            w.ship.speed_order, w.ship.silent_running, w.ship.depth_order = speed, silent, depth
            w.ship.noise = 0.1 if speed == "standard" else 0.25 if speed == "flank" else 0.04
            w.combat(0.8)
            _fight(w, lambda p: "hold")
            total += 1.0 - w.ship.hull
        return total
    assert hull_after("flank", False, "shallow") > hull_after("standard", False, "shallow") > hull_after("slow", True, "shallow")


def test_a_frightened_crew_panics_a_calm_one_does_not():
    def panics(fear):
        n = 0
        for seed in range(60):
            w = _w(seed, fear)
            w.combat(0.6)
            _fight(w, lambda p: "hold")
            text = "\n".join(w.log)
            n += any(k in text for k in ("wrong valve", "without orders", "drops a wrench"))
        return n
    assert panics(0.05) == 0 and panics(0.9) >= 20


def test_a_frightened_helm_obeys_the_order_to_dive_late():
    late = 0
    for seed in range(40):
        w = _w(seed)
        for c in w.crew:
            if c.role == "helm":
                c.fear, c.fatigue = 0.95, 0.95
        w.combat(0.6)
        w.tick()
        assert "shaking" in next(c.cost for c in w.pending.choices if c.key == "deep")
        w.choose("deep")
        late += w.ship.depth_order != "deep"
    assert late >= 12


def test_when_the_presence_is_near_the_charges_always_fall_wide_and_nobody_explains_it():
    w = _w()
    w.ship.attention = 0.7
    w.combat(0.9)
    _fight(w, lambda p: "hold")
    assert "same side" in "\n".join(w.log)


def test_the_scope_shows_every_escort_the_same_way_as_any_other_contact():
    from dread.nav import contacts
    w = _w()
    w.combat(0.9)
    cs = contacts(w)
    assert len(cs) == w.engagement.escorts >= 3
    assert all(set(c) == {"tag", "bearing", "range_nm", "label"} for c in cs)


def test_a_policy_can_fight_through_a_whole_patrol_without_getting_stuck():
    from dread.sim import run_patrol
    assert all(run_patrol(p, 1)["ticks"] > 20 for p in ("mission_first", "crew_first", "paranoid"))


def test_the_tactical_orders_lapse_when_the_attack_ends():
    w = _w()
    w.ship.speed_order, w.ship.depth_order = "slow", "shallow"
    w.combat(0.5)
    _fight(w, lambda p: "silent" if "silent" in [c.key for c in p.choices] else p.choices[0].key)
    assert not w.ship.silent_running and w.ship.depth_order == "shallow" and w.ship.speed_order == "slow"
    assert "Normal running resumes" in "\n".join(w.log)
