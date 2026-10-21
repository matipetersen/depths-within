"""The people's side of the boat: the radio room, the officers' council, sickness, and the log (DESIGN.md 15.4).

Each is a man (or men) telling the captain something, and what they say bends with what they feel.
"""
import random

from .events import Choice, Pending
from .state import clamp
from . import systems


# -- the radio room -------------------------------------------------------------------------------------
def listen_radio(w) -> str:
    """An hour at the set. What comes is a message, or static; and a frightened operator reads it wrong."""
    s = w.ship
    if not (s.surfaced or s.scope_up):
        return "The antenna is under water. Raise the periscope or surface."
    if not any(c.role == "radio" for c in w.active_crew()):
        return "There is no radio man to listen."
    if "fault_radio" in s.flags:
        return "The set is dead."
    w.lose_hours(1.0)
    s.attention = clamp(s.attention + 0.01)
    allr = [e for e in w.engine.events.values() if e.get("radio")]
    err = systems.role_error(w, "radio")
    ready = [e for e in allr if w.engine.radio_ready(e, w)]
    if w.rng.random() < 0.35 or not ready:
        return "Static. Under it, something that might be music, or someone counting."
    pool = ready
    if w.rng.random() < err * 0.8:                     # the clerk reads it wrong: what was sent is not what he writes
        pool = allr
        w.log.append(f"[{w.tick_no:03d}] The clerk reads it twice, and the second reading is not the first.")
    ev = w.rng.choices(pool, weights=[e.get("weight", 1.0) for e in pool], k=1)[0]
    w.engine.fire(ev, w)
    return "The radio man hands you a slip."


# -- the officers ---------------------------------------------------------------------------------------
def _officers(w):
    out = []
    first = lambda role: next((c for c in w.active_crew() if c.role == role), None)
    for title, c in (("first officer", w.crew[0] if w.crew and w.crew[0].active else None),
                     ("chief engineer", first("engine")), ("doctor", first("medic"))):
        if c is not None and all(c is not o[1] for o in out):
            out.append((title, c))
    return out


def honest_advice(w, title: str) -> str:
    s, live = w.ship, w.active_crew()
    n = max(1, len(live))
    fatigue = sum(c.fatigue for c in live) / n
    fear = sum(c.fear for c in live) / n
    if title == "chief engineer":
        if s.hull < 0.7:
            return "She is hurt, sir. I would not ask more of her."
        if s.battery < 0.3:
            return "We have to charge, sir, and soon."
        if s.spares < 0.3:
            return "We are nearly out of things to mend her with."
        return "The engines are sound."
    if title == "doctor":
        ill = sum(1 for c in live if c.ill)
        if ill:
            return f"{'One man is' if ill == 1 else str(ill) + ' men are'} sick, sir, and some of them are hiding it."
        if fear > 0.5:
            return "It is fear, sir. Not fever."
        return "They will do."
    if fatigue > 0.6:
        return "The men are close to the end, sir. Let them sleep."
    if s.orders_doubt > 0.3:
        return "I would like those orders verified, sir."
    if s.moral_debt > 0.3:
        return "They are not sleeping, sir. Not since the steamer."
    return "Steady, sir. Nothing that is not on the board."


def call_council(w) -> str:
    """Ask the officers. Honest advice comes in proportion to their trust and candor; the rest is flattery."""
    s = w.ship
    officers = _officers(w)
    if not officers:
        return "There is nobody to ask."
    w.lose_hours(0.5)
    look = random.Random(w.tick_no * 8101 + 13)
    for title, c in officers:
        p = max(0.0, min(1.0, c.candor * c.trust * (0.6 + 0.4 * s.cohesion)))
        said = honest_advice(w, title) if look.random() < p else "Whatever you think best, sir."
        w.log.append(f'[{w.tick_no:03d}] {c.name}, {title}: "{said}"')
        c.trust = clamp(c.trust + (0.02 if c.trust > 0.5 else -0.02))
    s.flags.add("council_recent")
    w.flag_expiry["council_recent"] = w.tick_no + 24
    return "The officers are called to the wardroom."


# -- sickness -------------------------------------------------------------------------------------------
def health_tick(w):
    """Disease needs a man, a damp boat and something to carry it. Frightened men hide it; hiding spreads it."""
    s, live = w.ship, w.active_crew()
    ill_n = sum(1 for c in live if c.ill and not c.isolated)
    for c in live:
        if not c.ill:
            p = 0.0015 + (0.004 if (s.food < 0.4 or s.water < 0.4) else 0.0) + (0.003 if s.co2 > 0.03 else 0.0) + 0.002 * ill_n
            if w.rng.random() < p:
                c.ill = True
                c.ill_ticks = 0
                c.hides = c.candor < 0.5 and c.trust < 0.6
        else:
            c.ill_ticks += 1
            c.fatigue = clamp(c.fatigue + 0.008)
            c.fear = clamp(c.fear + 0.002)
            if c.ill_ticks > 40 and w.rng.random() < 0.02:
                c.alive = False
                w.log.append(f"[{w.tick_no:03d}] {c.name} does not wake. The medic says what it was; nobody remembers the word.")
            elif w.rng.random() < 0.01:
                c.ill = False
                c.hides = False


def sick_call(w) -> str:
    live = w.active_crew()
    medic = next((c for c in live if c.role == "medic"), None)
    if medic is None:
        return "There is no medic. You do what you can, and it is not much."
    w.lose_hours(0.5)
    sick = [c for c in live if c.ill]
    if not sick:
        return "Every man is fit, or says so."
    cured = []
    for c in sick:
        c.hides = False
        if w.rng.random() < 0.7:
            c.ill = False
            cured.append(c.name)
    w.log.append(f"[{w.tick_no:03d}] The medic goes berth by berth. " + (f"{', '.join(cured)} {'is' if len(cured) == 1 else 'are'} treated." if cured else "He can do nothing."))
    return f"{len(sick)} sick found."


# -- the log --------------------------------------------------------------------------------------------
def write_log(w) -> str:
    s = w.ship
    if w.tick_no - s.last_log < 24:
        return "Not yet. The page is still wet from the last entry."
    s.last_log = w.tick_no
    w.pending = Pending("log_entry", "The day's entry. Three things happened that you would rather not have written down.", None, [
        Choice("true", "Write what happened, as it happened.", ["care"], "It is on record. So is the rest.",
               [{"op": "log_entry", "kind": "true"}, {"op": "ship", "stat": "moral_debt", "value": -0.03}, {"op": "crew", "who": "all", "stat": "trust", "value": 0.01}]),
        Choice("soft", "Soften it. A rough night, a difficult man.", ["comply"], "Easier. The page will be read, someday.",
               [{"op": "log_entry", "kind": "soft"}, {"op": "ship", "stat": "moral_debt", "value": 0.02}]),
        Choice("blank", "Leave the page blank.", ["silence"], "The men notice what the captain does not write.",
               [{"op": "log_entry", "kind": "blank"}, {"op": "crew", "who": "all", "stat": "trust", "value": -0.01}]),
    ])
    return "You open the log."
