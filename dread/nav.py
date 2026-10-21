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
    depth = 0 if s.surfaced else 90 if s.silent_running else 60
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


def contacts(w) -> List[Dict]:
    """What is on the scope: real and false contacts, drawn alike. Nothing here says which is which.

    A false one shows only while the sonar room reports it; a real one is steady but may drop out
    for an hour, so the difference cannot be read off the screen."""
    s, run = w.ship, w.run
    if not (s.sonar_on or s.surfaced):
        return []
    raw = []
    me = (navigation(w)["x"], navigation(w)["y"])
    tgt = run.mission.chart.get("target") if run is not None and run.outcome is None else None
    drop = random.Random(w.tick_no * 3571 + 11).random() < 0.12
    if tgt and run.acts_done >= 1 and not drop:
        dist = math.hypot(tgt[0] - me[0], tgt[1] - me[1]) * 0.9
        if dist <= SCOPE_NM:
            raw.append((_bearing(me, tgt), dist, tgt[2]))
    if "in_combat" in s.flags:
        k = w.tick_no // 5
        raw.append(((k * 83 + 17) % 360, float(3 + (k * 7) % 6), "fast screws, closing"))
    if s.sonar_on:
        for p, _ in sonar_reports(w):
            if p is not None and p.kind == "echo":
                raw.append(((p.id * 97 + 41 + p.age * 2) % 360, float(4 + (p.id * 53 + p.age) % 22),
                            LABEL_POOL[(p.id * 7) % len(LABEL_POOL)]))
    raw.sort(key=lambda r: r[0])
    return [{"tag": f"C{i + 1}", "bearing": int(r[0]), "range_nm": round(r[1], 1), "label": r[2]}
            for i, r in enumerate(raw)]
