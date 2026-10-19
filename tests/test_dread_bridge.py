"""Bridge between the dread simulation and the live game."""
import random

import pytest

from dread.bridge import DreadBridge, crew_from_roster
from engine.decisions import DecisionManager
from engine.horror_progression import HorrorManager, HorrorStage


class _Member:
    def __init__(self, name):
        self.name = name


class _Roster:
    crew_members = {"sonar_operator": _Member("Hartmann"), "chief_engineer": _Member("Beck"),
                    "radio_operator": _Member("Zeller")}


def test_crew_built_from_roster_with_roles_and_padding():
    crew = crew_from_roster(_Roster(), random.Random(0))
    names = {c.name: c.role for c in crew}
    assert names["Hartmann"] == "sonar" and names["Beck"] == "engine" and names["Zeller"] == "radio"
    assert len(crew) >= 8


def test_bridge_decisions_apply_their_effects():
    b = DreadBridge(_Roster(), seed=3)
    w = b.world
    w.tick_no = 20
    w.engine.fire(w.engine.events["clock_slow"], w)
    decision = b.pending_decision()
    assert decision is not None and decision.source == "dread"
    assert b.pending_decision() is decision                # stable until resolved
    before = w.ship.routines["watches"]
    DecisionManager().resolve_option(decision, "1", object())
    assert w.pending is None
    assert w.ship.routines["watches"] > before             # "reset the clock" restored a routine
    assert b.pending_decision() is None


def test_world_holds_still_while_a_decision_is_pending():
    b = DreadBridge(None, seed=1)
    w = b.world
    w.engine.fire(w.engine.events["clock_slow"], w)
    tick = w.tick_no
    assert b.tick() == []
    assert w.tick_no == tick


def test_hull_damage_is_mirrored_to_the_submarine():
    class Sub:
        hull = 0.8
    sub = Sub()
    b = DreadBridge(None, seed=1)
    b.world.ship.hull = 0.1                                # stale value must be overwritten
    b.tick(100.0, sub)
    assert 0.7 < sub.hull <= 0.81      # starts from the submarine's 0.8, not the stale 0.1 (minus/plus damage control)


def test_stage_comes_from_state_not_days():
    hm = HorrorManager()
    hm.attach_dread(DreadBridge(None, seed=1))
    for _ in range(40):                                    # many hours, nothing wrong happening
        w = hm.dread.world
        if w.pending:
            w.choose(w.pending.choices[0].key)
        for c in w.crew:
            c.fear, c.fatigue, c.guilt, c.trust = 0.05, 0.05, 0.0, 0.95
        w.ship.routines = {k: 1.0 for k in w.ship.routines}
        w.ship.co2 = 0.005
        hm.advance_turn(24.0, 100.0)                       # a whole day each call
    assert hm.metrics.total_days >= 40
    assert hm.current_stage in (HorrorStage.DENIAL, HorrorStage.UNEASE)


def test_legacy_model_unchanged_without_bridge():
    hm = HorrorManager()
    for _ in range(30):
        hm.advance_turn(24.0, 100.0)
    assert hm.current_stage == HorrorStage.MADNESS         # legacy: days drive the stage


def test_game_loop_smoke():
    pytest.importorskip("tcod")
    from engine.game import Game
    random.seed(1)
    g = Game()
    assert g.horror_manager.dread is not None
    resolved = 0
    for _ in range(120):
        g._tick()
        dm = g.decision_manager
        if dm.pending_decision:
            dm.resolve_option(dm.pending_decision, dm.pending_decision.options[0].key, g)
            resolved += 1
    assert resolved > 0
    assert not [e for e in g.logger.entries if "[horror] error" in str(e["text"]) or "[dread]" in str(e["text"])]


def test_bridge_can_start_a_mission_that_drives_its_own_events():
    b = DreadBridge(None, seed=2)
    assert b.world.run is None                         # the live game supplies its own missions
    m = b.begin_mission("m3_hospital_ship")
    assert b.world.run.mission.id == m.id
    b.world.ship.progress = 1.0
    for _ in range(3):
        b.tick()
        if b.world.pending:
            break
    d = b.pending_decision()
    assert d is not None and d.id.startswith("m3_")        # earliest phase fires first: m3_envelope
    with pytest.raises(KeyError):
        b.begin_mission("nope")


def test_bridge_end_mission_resolves_it():
    b = DreadBridge(None, seed=2)
    b.begin_mission("m1_battleship")
    b.end_mission("failed")
    assert b.world.results[-1]["outcome"] == "failed"
    assert b.world.run is None
