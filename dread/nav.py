"""Navigation and instruments, derived from the world (display only; nothing reads them back).

The chart is 110 x 80 units, ten per grid square (columns A-K, rows 1-8). Each mission lists the
waypoints its acts lead to; the boat sits between the last one reached and the next, in proportion
to the work done. Numbers are exact and deterministic: they hold no dice and no hidden value.
"""
import math
import random
from typing import Dict, List, Optional

from . import systems
from .state import COMPARTMENTS

BASE = (100.0, 12.0, "Base")
COLUMNS = "ABCDEFGHIJK"
WIDTH, HEIGHT = 110, 80


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


NM_PER_UNIT = 0.9          # one chart unit in nautical miles
SITE_R = 8.0               # a step is done "at" its site when the boat is this close (units)
ARRIVE_R = 1.0


def places(w) -> List[Dict]:
    """The names on the chart the captain can set course for: the base and the points of the orders in hand."""
    out = [{"id": "base", "label": BASE[2], "x": BASE[0], "y": BASE[1]}]
    run = w.run
    if run is not None and run.outcome is None and run.mission.chart:
        for i, p in enumerate(run.mission.chart["points"]):
            out.append({"id": f"p{i}", "label": p[2], "x": float(p[0]), "y": float(p[1])})
    return out


def site(w):
    """[x, y, label] where the next step of the mission has to be done, or None."""
    run = w.run
    if run is None or run.outcome is not None or not run.mission.chart:
        return None
    pts = run.mission.chart["points"]
    if run.mission.kind == "hold":
        return list(pts[-1])                                 # the station itself
    if run.acts_done >= len(run.mission.acts):
        return None
    return list(pts[run.acts_done]) if run.acts_done < len(pts) else None


def dist2(ax: float, ay: float, bx: float, by: float) -> float:
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)


def dist_to(w, x: float, y: float) -> float:
    """True distance in chart units from the boat to a point."""
    s = w.ship
    return dist2(x, y, s.x, s.y)


def at_site(w) -> bool:
    st = site(w)
    return st is None or dist_to(w, st[0], st[1]) <= SITE_R


def estimate(w, pos):
    """Where the captain believes the boat is: the truth, plus the dead-reckoning error in a slowly drifting direction."""
    s = w.ship
    off = s.dr_error / NM_PER_UNIT
    d = DIRS[((w.tick_no // 12) * 5 + 3) % 8]
    return (max(0.0, min(109.9, pos[0] + d[0] * off)), max(0.0, min(79.9, pos[1] + d[1] * off)))


def speed_kn(w) -> float:
    """The speed the hull makes good now (0 when it cannot move)."""
    s = w.ship
    if "adrift" in s.flags:
        return 0.0
    if s.surfaced:
        return 11.0 * {"ok": 1.0, "damaged": 0.6, "dead": 0.3}[systems.system_state(w, "engine room")]
    if s.battery <= 0:
        return 0.0
    kn = systems.SPEEDS[s.speed_order][1] * min(1.0, s.readiness) * {"ok": 1.0, "damaged": 0.6, "dead": 0.3}[systems.system_state(w, "engine room")]
    if s.silent_running:
        kn = min(kn, 3.0)
    return kn


def set_course(w, x: float, y: float, label: str = "") -> str:
    s = w.ship
    x, y = max(0.0, min(109.9, float(x))), max(0.0, min(79.9, float(y)))
    s.dest = [x, y, label or grid_ref(x, y)]
    est = estimate(w, (s.x, s.y))
    nm = math.sqrt((x - est[0]) ** 2 + (y - est[1]) ** 2) * NM_PER_UNIT
    kn = max(speed_kn(w), 0.1)
    msg = f"Course set for {s.dest[2]}: {nm:.0f} nm, about {max(1, math.ceil(nm / kn))} h at this speed."
    if w.working is not None:
        msg += " The work in hand comes first; she turns when it is done."
    return msg


def course_head(w, k: int) -> str:
    est = estimate(w, (w.ship.x, w.ship.y))
    d = DIRS[k % 8]
    return set_course(w, est[0] + d[0] * 18.0, est[1] + d[1] * 18.0, "")


def all_stop(w) -> str:
    w.ship.dest = None
    return "All stop. We hold our place."


def step(w):
    """One hour under way: the boat sails towards the course set, steering by where the captain believes it is."""
    s = w.ship
    s.under_way = False
    d = s.dest
    if d is None or w.engagement is not None or w.working is not None:
        return
    kn = speed_kn(w)
    if kn <= 0.0:
        return
    est = estimate(w, (s.x, s.y))
    vx, vy = d[0] - est[0], d[1] - est[1]
    dist = math.sqrt(vx * vx + vy * vy)
    if dist <= ARRIVE_R:
        s.dest = None
        return
    run_u = kn / NM_PER_UNIT
    k = min(dist, run_u) / dist
    s.x = max(0.0, min(109.9, s.x + vx * k))
    s.y = max(0.0, min(79.9, s.y + vy * k))
    s.heading = _bearing(est, d)
    s.under_way = True
    if dist <= run_u:
        s.dest = None
        w.log.append(f"[{w.tick_no:03d}] We have reached {d[2]}.")


def displace(w, hours: float):
    """A reckoning gone wrong: push the boat along the line to the base by so many hours of passage (+ away, - nearer)."""
    s = w.ship
    vx, vy = BASE[0] - s.x, BASE[1] - s.y
    dist = math.sqrt(vx * vx + vy * vy)
    if dist < 1e-9:
        return
    u = hours * 8.0 / NM_PER_UNIT
    s.x = max(0.0, min(109.9, s.x - vx / dist * u))
    s.y = max(0.0, min(79.9, s.y - vy / dist * u))


def _where(w):
    """Where the boat truly is: (position, heading, name of the place it is bound for, range to it in nm)."""
    s = w.ship
    pos = (s.x, s.y)
    tgt = s.dest or site(w)
    if tgt is None:
        return pos, s.heading, "", 0.0
    rng_nm = math.sqrt((tgt[0] - pos[0]) ** 2 + (tgt[1] - pos[1]) ** 2) * NM_PER_UNIT
    return pos, s.heading, tgt[2], rng_nm


# eight unit-ish directions with no trigonometry in them, so Python and JavaScript agree to the last digit
DIRS = ((1.0, 0.0), (0.7, 0.7), (0.0, 1.0), (-0.7, 0.7), (-1.0, 0.0), (-0.7, -0.7), (0.0, -1.0), (0.7, -0.7))


def true_xy(w):
    s = w.ship
    return (round(s.x, 1), round(s.y, 1))


def navigation(w) -> Dict:
    """What the instruments say: the position we believe we are at, heading, speed, depth and range."""
    s, run = w.ship, w.run
    pos, heading, nxt, rng_nm = _where(w)
    est = estimate(w, pos)
    speed = speed_kn(w) if s.under_way else 0.0
    if not s.under_way and not s.surfaced:
        speed = 2.5 if (w.working is not None and not w.work_blocked) else 0.0
    if s.silent_running and not s.surfaced:
        speed = min(speed, 3.0)
    depth = systems.depth_m(w)
    eta = None
    if s.under_way and s.dest is not None:
        eta = max(1, math.ceil(dist2(s.dest[0], s.dest[1], est[0], est[1]) * NM_PER_UNIT / max(speed, 0.1)))
    elif run is not None and run.working is not None:
        eta = max(1, int(-(-run.work_left // 1)))
    return {
        "x": round(est[0], 1), "y": round(est[1], 1), "grid": grid_ref(*est), "heading": heading, "err_nm": round(s.dr_error, 1),
        "speed": round(speed, 1), "depth": depth, "range_nm": round(rng_nm), "next": nxt, "eta_h": eta,
        "noise": s.noise, "keel": systems.under_keel(w), "dest": ([s.dest[0], s.dest[1], s.dest[2]] if s.dest else None),
        "at_site": at_site(w),
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
    if "fault_sonar" in s.flags:
        return []
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
    if not (s.sonar_on or s.surfaced) or "fault_sonar" in s.flags:
        return []
    raw = []
    me = true_xy(w)
    tgt = run.mission.chart.get("target") if run is not None and run.outcome is None else None
    drop = random.Random(w.tick_no * 3571 + 11).random() < 0.12
    if tgt and run.acts_done >= 1 and not drop:
        dist = math.hypot(tgt[0] - me[0], tgt[1] - me[1]) * 0.9
        if dist <= SCOPE_NM:
            raw.append((_bearing(me, tgt), dist, tgt[2], True))
    if "in_combat" in s.flags:
        k = w.tick_no // 5
        for i in range(w.engagement.escorts if w.engagement is not None else 1):
            raw.append(((k * 83 + 17 + i * 71) % 360, float(3 + (k * 7 + i * 5) % 6), "fast screws, closing", True))
    for o in w.traffic:                                      # merchants and fishermen are real hulls too
        dist = math.hypot(o["x"] - me[0], o["y"] - me[1]) * 0.9
        if dist <= SCOPE_NM:
            raw.append((_bearing(me, (o["x"], o["y"])), dist, LABEL_POOL[0] if o["kind"] == "merchant" else LABEL_POOL[3], True))
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


def _room_error(crew) -> float:
    """How often a torpedo room in this state gets it wrong: nothing for a rested, calm one."""
    if not crew:
        return 0.6
    strain = sum((c.fear + c.fatigue) / 2 for c in crew) / len(crew)
    return max(0.0, min(0.6, 1.2 * strain - 0.2))


def solution_error(w) -> float:
    """How far off the shot will be: the room's real error, unless the captain has the target in the eyepiece.
    A clear eye mends the room's error; an eye that is seeing things makes it worse. Hidden: never shown."""
    s = w.ship
    p_room = _room_error(_torpedo_room(w)) * (0.6 if "double_checked" in s.flags else 1.0)
    if s.surfaced or s.scope_up:
        ps = periscope(w, 0)
        if ps["ship"] is not None:
            return 0.5 if ps["distortions"] else p_room * 0.4
    return p_room


def weapons(w) -> Dict:
    """The torpedo room's readings. The stock is the ledger's (exact); the tubes and the firing solutions are
    what the men report, and a frightened, tired room reports them wrong. Nothing says when."""
    s = w.ship
    crew = _torpedo_room(w)
    stock = s.torpedoes
    if not crew:
        return {"stock": stock, "manned": False, "tubes": ["no report"] * 6, "solutions": [], "types": dict(s.types), "loaded": s.torpedo_type}
    p = _room_error(crew)
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
                     "run_s": int(round(rng_nm / systems.TYPE_KN[s.torpedo_type] * 3600)),
                     "gyro": ((brg - nv["heading"] + 540) % 360) - 180})
    return {"stock": stock, "manned": True, "tubes": tubes, "solutions": sols, "types": dict(s.types), "loaded": s.torpedo_type}


def periscope(w, train: int = 0) -> Dict:
    """What the captain sees at the eyepiece, trained `train` degrees off the bow. The sea is real; what
    the tired eye adds to it is not, and nothing tells the two apart."""
    s = w.ship
    nv = navigation(w)
    if not (s.surfaced or s.scope_up):
        return {"mode": "down", "train": train, "centre": (nv["heading"] + train) % 360, "ship": None,
                "distortions": [], "ghosts": [], "others": [], "visibility": 0.0}
    mode = "bridge" if s.surfaced else "periscope"
    centre = (nv["heading"] + train) % 360
    from . import sea
    vis = sea.visibility(w)
    me = true_xy(w)
    run = w.run
    ship = None
    tgt = run.mission.chart.get("target") if run is not None and run.outcome is None else None
    if tgt and run.acts_done >= 1:
        dist = math.hypot(tgt[0] - me[0], tgt[1] - me[1]) * 0.9
        if dist <= vis:
            brg = _bearing(me, tgt)
            rel = ((brg - centre + 540) % 360) - 180
            sight = run.mission.chart.get("sight", {})
            ship = {"bearing": brg, "rel": rel, "range_nm": round(dist, 1), "in_field": abs(rel) <= FIELD_DEG // 2,
                    "kind": sight.get("kind", "steamer"), "escorts": sight.get("escorts", 0),
                    "ships": sight.get("ships", 1), "markings": bool(sight.get("markings", False))}
    live = w.active_crew()
    strain = sum((c.fear + c.fatigue) / 2 for c in live) / len(live) if live else 1.0
    p = max(0.0, min(0.7, strain + 0.3 * s.moral_debt + 0.3 * s.attention - 0.15
                     + (0.08 if sea.night(w) else 0.0) + (0.12 if "fog" in s.flags else 0.0)))
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
    others = []
    for o in w.traffic:
        dist = math.hypot(o["x"] - me[0], o["y"] - me[1]) * 0.9
        if dist <= vis:
            brg = _bearing(me, (o["x"], o["y"]))
            rel = ((brg - centre + 540) % 360) - 180
            others.append({"kind": o["kind"], "bearing": brg, "rel": rel, "range_nm": round(dist, 1),
                           "in_field": abs(rel) <= FIELD_DEG // 2})
    return {"mode": mode, "train": train, "centre": centre, "ship": ship, "distortions": kinds, "ghosts": ghosts,
            "others": others, "visibility": vis}


# -- the lookout (DESIGN.md 16.3) ------------------------------------------------------------------------
def lookout(w) -> List[str]:
    """What the deck men report from the bridge. A rested man sees what is there; a frightened one also sees what is not."""
    from . import sea
    s = w.ship
    if not s.surfaced:
        return []
    deck = [c for c in w.active_crew() if c.role == "deck"]
    if not deck:
        return ["Nobody is posted on the bridge."]
    man = deck[0]
    look = random.Random(w.tick_no * 5233 + 19)
    candor = max(0.0, min(1.0, man.candor * man.trust * (0.6 + 0.4 * s.cohesion)))
    heading = _where(w)[1]
    me = true_xy(w)
    vis = sea.visibility(w)
    seen = []
    run = w.run
    tgt = run.mission.chart.get("target") if run is not None and run.outcome is None else None
    if tgt and run.acts_done >= 1:
        dist = math.hypot(tgt[0] - me[0], tgt[1] - me[1]) * 0.9
        if dist <= vis:
            kind = {"capital": "warship", "convoy": "smudge of smoke, several ships", "steamer": "steamer"}.get(run.mission.chart.get("sight", {}).get("kind"), "steamer")
            seen.append((_bearing(me, tgt), dist, kind))
    for o in w.traffic:
        dist = math.hypot(o["x"] - me[0], o["y"] - me[1]) * 0.9
        if dist <= vis:
            seen.append((_bearing(me, (o["x"], o["y"])), dist, "steamer" if o["kind"] == "merchant" else "fishing boat"))
    lines = []
    for brg, dist, kind in seen:
        if look.random() < candor:
            lines.append(_sighting(man.name, kind, ((brg - heading + 540) % 360) - 180, dist))
    if look.random() < systems.role_error(w, "deck") * 0.6:                  # he sees what is not there
        brg = int(look.random() * 360)
        lines.append(_sighting(man.name, "sail", ((brg - heading + 540) % 360) - 180, 4 + (brg % 5)))
    return lines


def _sighting(name: str, kind: str, rel: int, dist: float) -> str:
    a = abs(rel)
    where = "dead ahead" if a < 20 else ("on the starboard bow" if rel > 0 else "on the port bow") if a < 60 \
        else ("on the starboard beam" if rel > 0 else "on the port beam") if a < 120 \
        else ("on the starboard quarter" if rel > 0 else "on the port quarter") if a < 160 else "astern"
    n = max(1, int(round(dist)))
    return f'{name}, lookout: a {kind} {where}, about {n} mile{"s" if n > 1 else ""}.'
