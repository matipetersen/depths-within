"""Navigation and instruments, derived from the world (display only; nothing reads them back).

The chart is 110 x 80 units, ten per grid square (columns A-K, rows 1-8). Each mission lists the
waypoints its acts lead to; the boat sits between the last one reached and the next, in proportion
to the work done. Numbers are exact and deterministic: they hold no dice and no hidden value.
"""
import math
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
