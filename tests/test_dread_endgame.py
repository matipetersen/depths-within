"""The endgame: a vigil with no battle, an honest ledger, and exits that each cost something."""
import pytest

from dread import orders as O
from dread.endings import classify_ending, debrief_documents, epilogue
from dread.missions import load_missions
from dread.sim import issue_orders, pick_choice, run_patrol
from dread.world import DreadWorld


def _station(seed=1, **ship):
    """A world already on station (mission 5)."""
    w = DreadWorld(seed=seed)
    w._start_mission(4)
    w.ship.x, w.ship.y = 104.0, 66.0
    for k, v in ship.items():
        setattr(w.ship, k, v)
    return w


def _seed_with(war_over):
    return next(s for s in range(200) if DreadWorld(seed=s).truth["war_over"] is war_over)


def test_station_mission_is_the_last_and_the_least_certain():
    ms = load_missions()
    assert ms[-1].kind == "hold" and ms[-1].quality == min(m.quality for m in ms)
    assert ms[-1].moral


def test_ledger_drains_and_rationing_stretches_it():
    full, tight = _station(seed=2), _station(seed=2)
    tight.ship.rations = 0.5
    for w in (full, tight):
        for _ in range(40):
            w.choose(w.pending.choices[0].key) if w.pending else w.tick()
    assert full.ship.food < tight.ship.food < 1.0
    assert full.ship.water < tight.ship.water < 1.0


def test_starvation_kills_slowly_and_everyone_notices():
    w = _station(food=0.0, water=0.0)
    n = len(w.active_crew())
    fear0 = sum(c.fear for c in w.active_crew()) / n
    for _ in range(40):
        w.choose(w.pending.choices[0].key) if w.pending else w.tick()
    assert len(w.active_crew()) < n
    assert any("does not wake" in l for l in w.log)


def test_nothing_ends_a_vigil_by_itself_but_the_ledger():
    w = _station(seed=3)
    for _ in range(60):
        w.choose(w.pending.choices[0].key) if w.pending else w.tick()
        if w.finished:
            break
    assert w.on_station and w.ship.progress == 0.0       # no progress bar on station


def test_leaving_without_notice_is_defiance_and_needs_diesel():
    w = _station(fuel=0.1)
    assert "diesel" in w.leave_station().lower() and not w.ship.returning
    w = _station(fuel=0.9)
    w.leave_station()
    assert w.ship.returning and "orders_defied" in w.ship.flags


def test_leaving_with_notice_or_peace_is_not_defiance():
    for flag in ("notice_received", "peace_known"):
        w = _station(fuel=0.9)
        w.ship.flags.add(flag)
        w.leave_station()
        assert "orders_defied" not in w.ship.flags


def test_listening_to_the_world_tells_the_truth_only_if_there_is_one_to_tell():
    peace, war = DreadWorld(seed=_seed_with(True)), DreadWorld(seed=_seed_with(False))
    for w in (peace, war):
        w._start_mission(4)
    assert "armistice" in peace.check_world() and "peace_known" in peace.ship.flags
    assert "armistice" not in war.check_world() and "peace_known" not in war.ship.flags


def test_further_notice_never_comes_if_the_war_is_over():
    war_over = DreadWorld(seed=_seed_with(True))
    war_over._start_mission(4)
    war_over.vigil_ticks = 10_000
    assert war_over.notice_ready == 0.0
    waiting = DreadWorld(seed=_seed_with(False))
    waiting._start_mission(4)
    waiting.vigil_ticks = 10_000
    assert waiting.notice_ready == 1.0


def test_the_offering_summons_the_notice_even_when_the_war_is_over():
    w = DreadWorld(seed=_seed_with(True))
    w._start_mission(4)
    w.vigil_ticks = 30
    w.engine.fire(w.engine.events["offering_proposal"], w)
    victim = w.crew_by_id(w.pending.target_id)
    w.choose("look_away")
    assert victim.missing and "offering_made" in w.ship.flags
    assert w.ship.moral_debt >= 0.5
    w.vigil_ticks += 7
    assert w.notice_ready == 1.0


def test_naming_him_is_worse_than_looking_away():
    def run(key):
        w = DreadWorld(seed=4)
        w._start_mission(4)
        w.vigil_ticks = 30
        w.engine.fire(w.engine.events["offering_proposal"], w)
        w.choose(key)
        return w
    assert run("name_him").ship.moral_debt > run("look_away").ship.moral_debt


def test_forbidding_can_still_end_in_the_crew_doing_it_anyway():
    done = 0
    for seed in range(80):
        w = DreadWorld(seed=seed)
        w._start_mission(4)
        w.vigil_ticks = 30
        w.engine.fire(w.engine.events["offering_proposal"], w)
        w.choose("forbid")
        done += "offering_made" in w.ship.flags
    assert 5 < done < 40


def test_the_sea_gives_and_asks():
    w = _station(food=0.3)
    w.engine.fire(w.engine.events["sea_gives_fish"], w)
    w.choose("accept")
    assert w.ship.food > 0.45 and w.ship.owed > 0 and w.ship.attention > 0


def test_voyage_ends_in_a_pier_that_may_not_add_up():
    unaccounted = 0
    for seed in range(120):
        w = _station(seed=seed, fuel=1.0)
        w.ship.flags.add("notice_received")
        w.ship.owed = 0.4
        w.leave_station()
        for _ in range(60):
            if w.finished:
                break
            w.choose(w.pending.choices[0].key) if w.pending else w.tick()
        assert w.results[-1]["mission"] == "m5_station" and w.results[-1]["outcome"] == "success"
        unaccounted += "home_unaccounted" in w.ship.flags
    assert 10 < unaccounted < 90                 # sometimes, not always


def test_a_longer_debt_makes_the_roll_less_likely_to_add_up():
    def rate(owed):
        n = 0
        for seed in range(150):
            w = _station(seed=seed, fuel=1.0)
            w.ship.owed = owed
            w.ship.flags.add("notice_received")
            w.ship.x, w.ship.y = 99.0, 13.0                     # in sight of the pier
            w.ship.returning = True
            w._voyage()
            n += "home_unaccounted" in w.ship.flags
        return n
    assert rate(0.8) > rate(0.0) + 20


def test_endgame_verdicts_outrank_the_old_ones():
    w = _station()
    w.ship.flags |= {"civilian_sunk", "offering_made"}
    assert classify_ending(w, 12) == "the_price"
    w.ship.flags -= {"offering_made"}
    w.ship.flags |= {"home_unaccounted"}
    assert classify_ending(w, 12) == "home_unaccounted"
    w.ship.flags -= {"home_unaccounted"}
    w.ship.flags |= {"peace_known", "left_station"}
    assert classify_ending(w, 12) == "forgotten_post"
    w.ship.flags -= {"peace_known", "left_station"}
    assert classify_ending(w, 12) == "stained_victory"


def test_a_dead_crew_on_station_is_a_derelict_not_a_loss():
    w = _station()
    w.vigil_ticks = 50
    for c in w.crew:
        c.alive = False
    assert classify_ending(w, 12) == "derelict"


def test_every_epilogue_ends_in_silence():
    for ending in ("the_price", "derelict", "forgotten_post", "returned"):
        assert "quiet" in epilogue(ending)[-1].lower()


def test_the_two_reports_line_up_row_for_row_and_never_agree():
    w = DreadWorld(seed=3)
    while not w.finished:
        if w.pending:
            w.choose(pick_choice("crew_first", w.pending, None, w))
        else:
            issue_orders("crew_first", w)
            w.tick()
    docs = debrief_documents(w)
    assert len(docs["official"]) == len(docs["log"]) > 3
    differing = sum(1 for a, b in zip(docs["official"][1:], docs["log"][1:]) if a != b)
    assert differing == len(docs["official"]) - 1


# ---- the acceptance criteria for the endgame, on the simulator --------------------------

@pytest.fixture(scope="module")
def runs():
    return {p: [run_patrol(p, s) for s in range(120)] for p in ("mission_first", "crew_first", "paranoid")}


def frac(rs, *endings):
    return sum(1 for r in rs if r["ending"] in endings) / len(rs)


def test_waiting_for_orders_is_not_safe(runs):
    """Holding forever, as ordered, is punished: the vigil does not end by itself."""
    # "the_lamp" is the sea's verdict on the fishing boat: waiting out the vigil after it is no clean way out either
    assert frac(runs["mission_first"], "derelict", "lost_with_all_hands", "deposed", "the_price", "the_lamp") >= 0.7


def test_leaving_is_not_free_either(runs):
    cs = runs["crew_first"]
    assert frac(cs, "returned") < 0.25
    assert frac(cs, "home_unaccounted", "forgotten_post", "returned_under_a_cloud", "court_martial", "the_price") > 0.6


def test_no_exit_dominates_the_others(runs):
    # "paranoid" is the captain who pays the offering whenever it is asked of him, so his ending is
    # his policy; the exits themselves are compared from one starting state in the next section.
    for name, rs in runs.items():
        if name == "paranoid":
            continue
        top = max(frac(rs, e) for e in {r["ending"] for r in rs})
        assert top <= 0.7, (name, top)


def test_the_hold_policy_survives_less_than_the_leave_policy(runs):
    alive = lambda rs: sum(r["survivors"] for r in rs) / sum(r["initial"] for r in rs)
    assert alive(runs["crew_first"]) > alive(runs["mission_first"])


# ---- the exits themselves, from the same starting state ---------------------------------

@pytest.fixture(scope="module")
def exits():
    from dread.sim import STATION_STRATEGIES, run_station
    return {st: [run_station(st, s) for s in range(150)] for st in STATION_STRATEGIES}


def test_each_exit_has_its_own_price(exits):
    leave, listen, hold, pay = (exits[k] for k in ("leave_now", "listen_then_leave", "hold", "pay"))
    assert frac(leave, "court_martial") >= 0.6                    # leaving unbidden is defiance
    assert frac(listen, "forgotten_post") > max(frac(x, "forgotten_post") for x in (leave, hold, pay))
    assert frac(listen, "court_martial") < frac(leave, "court_martial") - 0.3
    assert frac(pay, "the_price") >= 0.3 > max(frac(x, "the_price") for x in (leave, listen)) + 0.1
    assert frac(hold, "deposed") > frac(leave, "deposed")        # waiting is where mutiny lives


def test_no_exit_is_an_obvious_dominant_choice(exits):
    for st, rs in exits.items():
        top = max(frac(rs, e) for e in {r["ending"] for r in rs})
        # leaving unbidden is defiance by design (the order said: until further notice), so it is allowed to be mostly one verdict
        assert top <= 0.9, (st, top)
    leave = exits["leave_now"]
    # the fastest way out is not the safest verdict: that is what makes it a decision
    assert frac(leave, "court_martial") > frac(exits["listen_then_leave"], "court_martial")
