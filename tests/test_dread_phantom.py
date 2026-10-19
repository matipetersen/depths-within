"""Phantom sonar layer and captain's orders."""
from dread import orders as O
from dread.world import DreadWorld


def _sonar_op(w):
    return next(c for c in w.crew if c.role == "sonar")


def test_phantom_audible_only_to_its_operator():
    w = DreadWorld(seed=1)
    op = _sonar_op(w)
    p = w.deck.spawn("echo", {op.id}, 0.5, rng=w.rng, crew=w.crew)
    assert p.audible_to == {op.id}
    before = {c.id: c.fear for c in w.crew}
    w.deck.tick(w)
    assert op.fear > before[op.id]
    assert all(c.fear == before[c.id] for c in w.crew if c.id != op.id)


def test_silencing_sonar_calms_operator_but_blinds_the_boat():
    w = DreadWorld(seed=1)
    op = _sonar_op(w)
    op.fear = 0.6
    w.deck.spawn("echo", {op.id}, 0.5, rng=w.rng, crew=w.crew)
    sighted = w.deck.real_detection_chance(w.ship)
    O.silence_sonar(w)
    assert op.fear < 0.6
    assert w.deck.real_detection_chance(w.ship) < sighted
    assert not w.ship.sonar_on


def test_unheard_phantom_grows_with_attention():
    w = DreadWorld(seed=1)
    op = _sonar_op(w)
    w.ship.attention = 0.8
    p = w.deck.spawn("echo", {op.id}, 0.3, rng=w.rng, crew=w.crew)
    w.deck.tick(w)
    assert p.intensity > 0.3


def test_voice_uses_a_learned_name():
    w = DreadWorld(seed=1)
    victim = w.crew[2]
    w.deck.names_learned.add(victim.id)
    p = w.deck.spawn("voice", {w.crew[0].id}, 0.5, rng=w.rng, crew=w.crew)
    assert victim.name in p.text


def test_isolation_costs_trust_and_feeds_attention():
    w = DreadWorld(seed=1)
    c = w.crew[4]
    t0, a0 = c.trust, w.ship.attention
    O.isolate(w, c.id)
    assert c.isolated and c.trust < t0 and w.ship.attention > a0


def test_force_compartment_repairs_hull_at_a_trust_price():
    w = DreadWorld(seed=1)
    w.ship.hull = 0.5
    trust = sum(c.trust for c in w.crew)
    O.force_compartment(w, w.crew[1].id)
    assert w.ship.hull > 0.5
    assert sum(c.trust for c in w.crew) < trust


def test_ritual_restores_routine_and_costs_mission_time():
    w = DreadWorld(seed=1)
    w.ship.routines = {k: 0.2 for k in w.ship.routines}
    before = w.ship.routine
    O.hold_ritual(w)
    assert w.ship.routine > before
    assert w.time_cost > 0


def test_cancel_rest_raises_readiness_now_and_fatigue_later():
    base, pushed = DreadWorld(seed=3), DreadWorld(seed=3)
    O.cancel_rest(pushed)
    for _ in range(30):
        base.tick() if base.pending is None else base.choose(base.pending.choices[0].key)
        pushed.tick() if pushed.pending is None else pushed.choose(pushed.pending.choices[0].key)
    mean = lambda w: sum(c.fatigue for c in w.active_crew()) / len(w.active_crew())
    assert mean(pushed) > mean(base)
