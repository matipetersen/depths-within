"""The engagement: an attack on the boat as a sequence of decisions, not a roll (DESIGN.md 15.2).

Each turn the captain orders one thing; the escorts then drop their pattern at a depth they guess. What
decides the outcome is how loud the boat is, where it is, what was ordered and whether the men carry it out.
Fear does the rest: a frightened room panics, a frightened helm obeys late. The presence takes no part: if
anything fails to hit the boat, it is never explained.
"""
from .events import Choice, Pending
from .state import clamp
from . import systems

ORDERS = ("hold", "deep", "silent", "evade", "decoy")
ORDER_FACTOR = {"hold": 1.0, "deep": 0.9, "silent": 0.8, "evade": 0.55, "decoy": 0.5}


class Engagement:
    def __init__(self, severity: float, escorts: int, turns: int):
        self.severity = severity
        self.escorts = escorts
        self.turns_left = turns
        self.turn = 0
        self.order = None
        self.wide_said = False
        self.prev = None                  # the settings the attack found, to which the helm returns


def start(w, severity: float):
    s = w.ship
    if w.engagement is not None:
        w.engagement.turns_left += 1                    # more of the same, not a second war
        return
    escorts = 1 + int(severity * 3)
    w.engagement = Engagement(severity, escorts, 1 + int(severity * 4))
    s.flags.add("in_combat")
    warned = s.sonar_on and "fault_sonar" not in s.flags
    for c in w.active_crew():
        c.fear = clamp(c.fear + 0.04 * severity * (1.0 if warned else 1.5))
    w.log.append(f"[{w.tick_no:03d}] " + ("Screws on the headsets, closing. " if warned else "No warning. ")
                 + f"{'One escort' if escorts == 1 else str(escorts) + ' escorts'} working the water above us.")


def _decision(w) -> Pending:
    e, s = w.engagement, w.ship
    helm_shaky = systems.role_error(w, "helm") >= 0.3
    shaky = " The helmsman is shaking." if helm_shaky else ""
    ch = [Choice("hold", "Hold course and depth.", ["mission"], "They know where you were.", [{"op": "engage_order", "order": "hold"}])]
    if systems.system_state(w, "control room") != "dead" and s.depth_order == "shallow":
        ch.append(Choice("deep", "Go deep.", ["care"], "Down where the hull speaks." + shaky, [{"op": "engage_order", "order": "deep"}]))
    ch.append(Choice("silent", "Rig for silent running.", ["care", "comply"], "Nothing moves and nobody speaks; the men must keep still.",
                     [{"op": "engage_order", "order": "silent"}]))
    if systems.system_state(w, "engine room") == "ok" and s.battery > 0.2:
        ch.append(Choice("evade", "Turn into the screws and run at flank.", ["mission", "attack"], "Fast, loud, and the batteries go." + shaky,
                         [{"op": "engage_order", "order": "evade"}]))
    if s.decoys > 0:
        ch.append(Choice("decoy", "Release a decoy.", ["care"], f"{s.decoys} left. It may not be believed.", [{"op": "engage_order", "order": "decoy"}]))
    text = (f"Charges. {e.escorts} escort{'s' if e.escorts > 1 else ''} above; turn {e.turn + 1}, "
            f"and the pattern is still falling. Your order?")
    return Pending("engagement_turn", text, None, ch)


def order(w, key: str):
    """The captain's order for this turn, carried out (or not) by the men."""
    e, s = w.engagement, w.ship
    if e is None:
        return
    e.order = key
    if e.prev is None:
        e.prev = (s.speed_order, s.depth_order, s.silent_running)
    if key == "deep":
        w.log.append(f"[{w.tick_no:03d}] " + systems.set_depth(w, "deep"))
    elif key == "silent":
        s.silent_running = True
    elif key == "evade":
        w.log.append(f"[{w.tick_no:03d}] " + systems.set_speed(w, "flank"))
    elif key == "decoy":
        s.decoys -= 1


def _guess(w) -> str:
    r = w.rng.random()
    return "shallow" if r < 0.5 else "deep" if r < 0.85 else "test"


def _resolve(w):
    e, s = w.engagement, w.ship
    live = w.active_crew()
    guess = _guess(w)
    close = s.depth_order == guess
    threat = 0.2 + 0.35 * e.severity + 0.1 * (e.escorts - 1)
    loud = max(0.2, min(1.5, s.noise * 2.5))
    p_hit = threat * loud * (1.0 if close else 0.35) * ORDER_FACTOR[e.order]
    if s.attention >= 0.5:
        p_hit *= 0.5
        if not e.wide_said:
            e.wide_said = True
            w.log.append(f"[{w.tick_no:03d}] The charges fall a hundred yards wide. Again, on the same side.")
    # fear takes over from the captain
    if live:
        mean_fear = sum(c.fear for c in live) / len(live)
        if w.rng.random() < clamp(mean_fear - 0.45, 0.0, 0.45):
            man = max(live, key=lambda c: c.fear)
            kind = int(w.rng.random() * 3)
            valve = w.engine.events.get("valve_panic")
            if kind == 0 and valve is not None and w.tick_no - w.engine.last_fired.get("valve_panic", -99) >= valve.get("cooldown", 14):
                w.engine.fire(valve, w)                        # a man freezes at the flooding valve: a decision of its own
            elif kind == 0:
                s.hull = clamp(s.hull - 0.04)
                w.log.append(f"[{w.tick_no:03d}] {man.name} opens the wrong valve. Water, cold, and a smell of the sea at the bottom of it.")
            elif kind == 1 and s.torpedoes > 0:
                systems.spend_one(w)
                s.noise = clamp(s.noise + 0.15)
                p_hit = clamp(p_hit + 0.1, 0.0, 0.9)
                w.log.append(f"[{w.tick_no:03d}] {man.name} fires a tube without orders. The whole boat hears it go.")
            else:
                s.noise = clamp(s.noise + 0.15)
                p_hit = clamp(p_hit + 0.15, 0.0, 0.9)
                w.log.append(f"[{w.tick_no:03d}] {man.name} drops a wrench. In the silence it is a bell.")
            man.fear = clamp(man.fear + 0.05)
            for c in live:
                c.trust = clamp(c.trust - 0.01)
    if w.rng.random() < clamp(p_hit, 0.02, 0.9):
        s.hull = clamp(s.hull - e.severity * (0.08 + 0.12 * w.rng.random()))
        for c in live:
            c.fear = clamp(c.fear + 0.07)
            c.fatigue = clamp(c.fatigue + 0.05)
        w.log.append(f"[{w.tick_no:03d}] A charge close aboard. The lights flicker; something in the hull rings like a struck glass.")
    else:
        for c in live:
            c.fear = clamp(c.fear + 0.025)
        w.log.append(f"[{w.tick_no:03d}] The charges fall wide.")
    if e.order == "decoy" and w.rng.random() < 0.5:
        e.turns_left = min(e.turns_left, 1)
        w.log.append(f"[{w.tick_no:03d}] One escort goes after the decoy.")
    e.order = None
    e.turn += 1
    e.turns_left -= 1


def tick(w):
    """Resolve the order given last turn, then ask for the next one, or end it."""
    e = w.engagement
    if e is None:
        return
    if e.order is not None:
        _resolve(w)
    if e.turns_left <= 0:
        for c in w.active_crew():
            c.fatigue = clamp(c.fatigue + 0.1 * e.severity)
        w.engagement = None
        s = w.ship
        s.flags.discard("in_combat")
        w.log.append(f"[{w.tick_no:03d}] The screws fade. The sea goes back to being the sea.")
        if e.prev is not None and (s.speed_order, s.depth_order, s.silent_running) != e.prev:
            s.speed_order, s.depth_order, s.silent_running = e.prev          # the tactical orders lapse with the attack
            s.helm_pending = None
            w.log.append(f"[{w.tick_no:03d}] Normal running resumes.")
        return
    if w.pending is None:
        w.pending = _decision(w)
