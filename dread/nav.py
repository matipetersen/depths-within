"""Navigation and instruments, derived from the world (display only; nothing reads them back).

The chart is 110 x 80 units, ten per grid square (columns A-K, rows 1-8). Each mission lists the
waypoints its acts lead to; the boat sits between the last one reached and the next, in proportion
to the work done. Numbers are exact and deterministic: they hold no dice and no hidden value.
"""
import math
import random
from typing import Dict, List, Optional

from .state import COMPARTMENTS

BASE = (100.0, 12.0, "Base")
COLUMNS = "ABCDEFGHIJK"
WIDTH, HEIGHT = 110, 80
RETURN_TICKS = 18          # must equal the passage length in DreadWorld.leave_station


def grid_ref(x: float, y: float) -> str:
    return f"{COLUMNS[max(0, min(10, int(x // 10)))]}-{max(1, min(8, int(y // 10) + 1))}"


def _points(run) -> List[list]:
    ch = run.mission.chart
    if not ch:
        return []
    return [list(ch["from"])] + [list(p) for p in ch["points"]]


def _lerp(a, b, t):
    return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t


def _bearing(a, b) -> int:
    return int(round(math.degrees(math.atan2(b[0] - a[0], a[1] - b[1])))) % 360


def navigation(w) -> Dict:
    """Position, heading, speed, depth and range for the boat as it is now."""
    s, run = w.ship, w.run
    pts = _points(run) if run is not None else []
    station = None
    if not pts:
        pos, heading, nxt, rng_nm = (BASE[0], BASE[1]), 0, "", 0.0
    elif run.mission.kind == "hold":
        station = pts[-1]
        pos, nxt, heading = (station[0], station[1]), "", 0
        if s.returning:
            t = 1.0 - w.travel_left / RETURN_TICKS
            pos = _lerp(station, BASE, max(0.0, min(1.0, t)))
            heading, nxt = _bearing(station, BASE), "Base"
        rng_nm = math.hypot(BASE[0] - pos[0], BASE[1] - pos[1]) * 0.9 if s.returning else 0.0
    else:
        n = len(pts) - 1
        i = min(run.acts_done, n - 1)
        t = 0.0
        if run.working is not None:
            t = 1.0 - run.work_left / run.mission.acts[run.working].hours
        if run.acts_done >= n:
            i, t = n - 1, 1.0
        pos = _lerp(pts[i], pts[i + 1], t)
        heading = _bearing(pts[i], pts[i + 1])
        nxt = pts[i + 1][2]
        rng_nm = math.hypot(pts[i + 1][0] - pos[0], pts[i + 1][1] - pos[1]) * 0.9
    moving = s.returning or (w.working is not None and not w.work_blocked)
    if s.surfaced:
        speed = 11.0 if moving else 4.0
    elif s.returning:
        speed = 9.0
    elif moving:
        speed = 8.0 * min(1.0, s.readiness)
    else:
        speed = 2.5
    if s.silent_running and not s.surfaced:
        speed = min(speed, 3.0)
    depth = 0 if s.surfaced else 14 if s.scope_up else 90 if s.silent_running else 60
    return {
        "x": round(pos[0], 1), "y": round(pos[1], 1), "grid": grid_ref(*pos), "heading": heading,
        "speed": round(speed, 1), "depth": depth, "range_nm": round(rng_nm), "next": nxt,
        "eta_h": (max(1, int(-(-run.work_left // 1))) if run is not None and run.working is not None else None),
        "noise": s.noise,
    }


def hull_report(w) -> List[Dict]:
    """Integrity per compartment: 100% when nothing was ever lost there."""
    out = []
    for c in COMPARTMENTS:
        integrity = max(0.0, min(1.0, 1.0 - 2.0 * w.ship.damage[c]))
        state = "flooding" if integrity < 0.35 else "damaged" if integrity < 0.7 else "sound"
        out.append({"name": c, "integrity": integrity, "state": state})
    return out


# -- the scope (DESIGN.md 12.8) -------------------------------------------------------------------
SCOPE_NM = 30
LABEL_POOL = ("single screw, steady", "heavy screws, slow", "many screws, slow", "faint screws, irregular",
              "fast screws, closing", "no screw count", "heavy screws, steady")


def sonar_reports(w) -> List[tuple]:
    """(phantom, line): what the sonar room tells the captain. The captain hears only this."""
    s = w.ship
    look = random.Random(w.tick_no * 104729 + 5)
    out = []
    for p in w.deck.phantoms:
        for cid in sorted(p.audible_to):
            c = w.crew_by_id(cid)
            if c is None or not c.active:
                continue
            candor = max(0.0, min(1.0, c.candor * c.trust * (0.6 + 0.4 * s.cohesion)))
            if look.random() < candor:
                out.append((p, f'{c.name} reports: "{p.text}"'))
            elif len(p.audible_to) >= 2:
                out.append((None, "The sonar room has gone quiet around the headphones."))
            break
    return out


def _rows(w) -> List[tuple]:
    """(bearing, range_nm, label, real): the scope's raw picture. `real` never leaves this module's callers
    that draw the scope; the periscope alone uses it, because a hull is either there or not."""
    s, run = w.ship, w.run
    if not (s.sonar_on or s.surfaced):
        return []
    raw = []
    nv = navigation(w)
    me = (nv["x"], nv["y"])
    tgt = run.mission.chart.get("target") if run is not None and run.outcome is None else None
    drop = random.Random(w.tick_no * 3571 + 11).random() < 0.12
    if tgt and run.acts_done >= 1 and not drop:
        dist = math.hypot(tgt[0] - me[0], tgt[1] - me[1]) * 0.9
        if dist <= SCOPE_NM:
            raw.append((_bearing(me, tgt), dist, tgt[2], True))
    if "in_combat" in s.flags:
        k = w.tick_no // 5
        raw.append(((k * 83 + 17) % 360, float(3 + (k * 7) % 6), "fast screws, closing", True))
    if s.sonar_on:
        for p, _ in sonar_reports(w):
            if p is not None and p.kind == "echo":
                raw.append(((p.id * 97 + 41 + p.age * 2) % 360, float(4 + (p.id * 53 + p.age) % 22),
                            LABEL_POOL[(p.id * 7) % len(LABEL_POOL)], False))
    raw.sort(key=lambda r: r[0])
    return raw


def contacts(w) -> List[Dict]:
    """What is on the scope: real and false contacts, drawn alike. Nothing here says which is which.

    A false one shows only while the sonar room reports it; a real one is steady but may drop out
    for an hour, so the difference cannot be read off the screen."""
    return [{"tag": f"C{i + 1}", "bearing": int(r[0]), "range_nm": round(r[1], 1), "label": r[2]}
            for i, r in enumerate(_rows(w))]


# -- torpedoes and the periscope (DESIGN.md 12.9) ---------------------------------------------------
YARDS_PER_NM = 2025
TORPEDO_KNOTS = 30
TUBE_STATES = ("empty", "loaded", "flooded", "open")
VIS_NM = 12
FIELD_DEG = 50
DISTORTIONS = ("figures_on_rail", "cross_on_hull", "second_hull", "lamp", "wake_wrong")


def _torpedo_room(w):
    return [c for c in w.active_crew() if c.role == "torpedo"]


def weapons(w) -> Dict:
    """The torpedo room's readings. The stock is the ledger's (exact); the tubes and the firing solutions are
    what the men report, and a frightened, tired room reports them wrong. Nothing says when."""
    s = w.ship
    crew = _torpedo_room(w)
    stock = s.torpedoes
    if not crew:
        return {"stock": stock, "manned": False, "tubes": ["no report"] * 6, "solutions": []}
    n = len(crew)
    strain = sum((c.fear + c.fatigue) / 2 for c in crew) / n
    p = max(0.0, min(0.6, 1.2 * strain - 0.2))
    look = random.Random(w.tick_no * 2711 + 3)
    tubes = []
    for st in s.tubes:
        if look.random() < p:
            tubes.append(look.choice([x for x in TUBE_STATES if x != st]))
        else:
            tubes.append(st)
    nv = navigation(w)
    sols = []
    for c in contacts(w):
        jb, jr = look.random(), look.random()
        brg = int(round(c["bearing"] + (jb - 0.5) * 2 * p * 20)) % 360
        rng_nm = c["range_nm"] * (1 + (jr - 0.5) * p * 0.6)
        sols.append({"tag": c["tag"], "bearing": brg, "range_yd": int(round(rng_nm * YARDS_PER_NM, -1)),
                     "run_s": int(round(rng_nm / TORPEDO_KNOTS * 3600)),
                     "gyro": ((brg - nv["heading"] + 540) % 360) - 180})
    return {"stock": stock, "manned": True, "tubes": tubes, "solutions": sols}


def periscope(w, train: int = 0) -> Dict:
    """What the captain sees at the eyepiece, trained `train` degrees off the bow. The sea is real; what
    the tired eye adds to it is not, and nothing tells the two apart."""
    s = w.ship
    nv = navigation(w)
    if not (s.surfaced or s.scope_up):
        return {"mode": "down", "train": train, "centre": (nv["heading"] + train) % 360, "ship": None,
                "distortions": [], "ghosts": []}
    mode = "bridge" if s.surfaced else "periscope"
    centre = (nv["heading"] + train) % 360
    me = (nv["x"], nv["y"])
    run = w.run
    ship = None
    tgt = run.mission.chart.get("target") if run is not None and run.outcome is None else None
    if tgt and run.acts_done >= 1:
        dist = math.hypot(tgt[0] - me[0], tgt[1] - me[1]) * 0.9
        if dist <= VIS_NM:
            brg = _bearing(me, tgt)
            rel = ((brg - centre + 540) % 360) - 180
            sight = run.mission.chart.get("sight", {})
            ship = {"bearing": brg, "rel": rel, "range_nm": round(dist, 1), "in_field": abs(rel) <= FIELD_DEG // 2,
                    "kind": sight.get("kind", "steamer"), "escorts": sight.get("escorts", 0),
                    "ships": sight.get("ships", 1), "markings": bool(sight.get("markings", False))}
    live = w.active_crew()
    strain = sum((c.fear + c.fatigue) / 2 for c in live) / len(live) if live else 1.0
    p = max(0.0, min(0.7, strain + 0.3 * s.moral_debt + 0.3 * s.attention - 0.15))
    look = random.Random((w.tick_no // 3) * 6733 + 29)
    kinds = []
    if look.random() < p:
        kinds.append(look.choice(DISTORTIONS))
        if look.random() < p * 0.5:
            kinds.append(look.choice(DISTORTIONS))
    ghosts = []
    g = random.Random((w.tick_no // 3) * 4219 + 7)
    for r in _rows(w):
        if r[3]:
            continue
        rel = ((r[0] - centre + 540) % 360) - 180
        if abs(rel) <= FIELD_DEG // 2 and g.random() < 0.5:
            ghosts.append(int(rel))
    return {"mode": mode, "train": train, "centre": centre, "ship": ship, "distortions": kinds, "ghosts": ghosts}
