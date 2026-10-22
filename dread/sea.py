"""The living sea: the hours of the day, visibility, traffic that is none of the mission's business, and the
navigator's uncertainty (DESIGN.md 15.3)."""
from . import systems
from .nav import DIRS, SCOPE_NM, periscope, true_xy
from .state import clamp

TRAFFIC_MAX = 3


def hour(w) -> int:
    return (6 + w.tick_no) % 24


def night(w) -> bool:
    h = hour(w)
    return h >= 20 or h < 5


def visibility(w) -> float:
    """How far a man can see, in nm: less at night, much less in fog."""
    v = 12.0
    if night(w):
        v *= 0.4
    if "fog" in w.ship.flags:
        v *= 0.25
    if w.ship.surfaced:                                  # on the bridge, the lookouts' eyes are the boat's
        v *= 1.2 - 0.6 * systems.role_error(w, "deck")
    return v


def update_traffic(w):
    """Merchants and fishing boats go about their own business; their flag is nobody's to read from here."""
    for o in list(w.traffic):
        o["x"] += o["vx"]
        o["y"] += o["vy"]
        o["age"] += 1
        if o["age"] >= o["life"]:
            w.traffic.remove(o)
    if w.engagement is None and len(w.traffic) < TRAFFIC_MAX and w.rng.random() < 0.05:
        bx, by = true_xy(w)
        d = DIRS[int(w.rng.random() * 8)]
        dist = 12 + int(w.rng.random() * 14)
        v = DIRS[int(w.rng.random() * 8)]
        speed = 4 + w.rng.random() * 4
        kind = "merchant" if w.rng.random() < 0.6 else "fishing"
        flag = "neutral" if w.rng.random() < 0.5 else "enemy"
        life = 12 + int(w.rng.random() * 18)
        w.traffic_id += 1
        w.traffic.append({"id": w.traffic_id, "kind": kind, "flag": flag, "x": bx + d[0] * dist, "y": by + d[1] * dist,
                          "vx": v[0] * speed, "vy": v[1] * speed, "age": 0, "life": life})


def traffic_range_nm(w, o) -> float:
    import math
    bx, by = true_xy(w)
    return math.hypot(o["x"] - bx, o["y"] - by) * 0.9


def traffic_near(w) -> int:
    if w.engagement is not None:
        return 0
    return sum(1 for o in w.traffic if traffic_range_nm(w, o) <= 7.0)


def take_fix(w) -> str:
    """Correct the position by stars, radio bearings or the coast through the periscope. It costs an hour."""
    s = w.ship
    if s.surfaced:
        if night(w):
            factor, how = 0.15, "the stars"
        elif any(c.role == "radio" for c in w.active_crew()) and "fault_radio" not in s.flags:
            factor, how = 0.5, "radio bearings"
        else:
            return "No stars, and no radio to take bearings on."
    elif s.scope_up:
        if visibility(w) < 4.0:
            return "There is nothing to take a bearing on in this visibility."
        factor, how = 0.4, "the coast through the periscope"
        s.attention = clamp(s.attention + 0.01)
    else:
        return "A fix needs the periscope or the surface."
    s.dr_error = max(0.3, s.dr_error * factor)
    s.last_fix = w.tick_no
    w.lose_hours(1.0)
    return f"Fix by {how}. We are within about {s.dr_error:.1f} nm of where we think we are."


def _eye_lies(w, o) -> bool:
    return bool(periscope(w, 0)["distortions"]) and (o["id"] + w.tick_no) % 3 == 0


def traffic_act(w, action: str):
    """What the captain does about the vessel crossing ahead. The flag she wears is hidden; the eye may lie."""
    s = w.ship
    near = [o for o in w.traffic if traffic_range_nm(w, o) <= 7.0]
    if not near:
        w.log.append(f"[{w.tick_no:03d}] There is nothing there now.")
        return
    o = min(near, key=lambda x: traffic_range_nm(w, x))
    kind = "steamer" if o["kind"] == "merchant" else "fishing boat"
    if action == "pass":
        w.log.append(f"[{w.tick_no:03d}] The {kind} crosses and goes on about her business.")
    elif action == "shadow":
        w.lose_hours(3.0)
        s.attention = clamp(s.attention + 0.02)
        seen = o["flag"] if not _eye_lies(w, o) else ("enemy" if o["flag"] == "neutral" else "neutral")
        flag = "a neutral's stripes" if seen == "neutral" else "an enemy ensign"
        w.log.append(f"[{w.tick_no:03d}] Three hours on her quarter. She wears {flag}.")
    elif action == "sink":
        n = min(2, s.torpedoes)
        if n == 0:
            w.log.append(f"[{w.tick_no:03d}] There is nothing left to fire.")
            return
        for _ in range(n):
            systems.spend_one(w)
        s.noise = clamp(s.noise + 0.2)
        w.traffic.remove(o)
        if o["flag"] == "neutral" or o["kind"] == "fishing":
            s.moral_debt = clamp(s.moral_debt + 0.35)
            for c in w.active_crew():
                c.guilt = clamp(c.guilt + 0.15)
                c.trust = clamp(c.trust - 0.06)
            s.flags.add("neutral_sunk")
            w.log.append(f"[{w.tick_no:03d}] The {kind} goes down by the stern. There is a flag on the surface, and it is not the one you were told to expect.")
        else:
            for c in w.active_crew():
                c.trust = clamp(c.trust + 0.03)
                c.guilt = clamp(c.guilt + 0.03)
            s.flags.add("enemy_sunk")
            w.log.append(f"[{w.tick_no:03d}] The {kind} breaks in two. Nobody cheers, and nobody looks at the others.")
