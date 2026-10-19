"""Event table loader, effect interpreter and per-tick event selection.

Events live in ``data/events.json`` (schema in DESIGN.md section 6).
"""
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .conditions import evaluate, resolve_path
from .state import Rumor, clamp

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "events.json")

REQUIRED_FIELDS = ("id", "acts", "text", "mundane_cause", "uncanny_cause", "mundane_when")
GLOBAL_COOLDOWN = 3
BEAT_GAP = 14          # ticks without the presence showing itself before one is forced
BEAT_START = 8         # no forced beat before this tick
CREW_STATS = ("fear", "fatigue", "guilt", "trust")
SHIP_CLAMP = {"co2": (0.0, 0.1)}


def load_events(path: str = DEFAULT_PATH) -> List[dict]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    events = data["events"]
    validate_events(events)
    return events


def validate_events(events: List[dict]):
    """Enforce the golden rule: every event has both a mundane and an uncanny cause."""
    seen = set()
    for ev in events:
        missing = [f for f in REQUIRED_FIELDS if f not in ev]
        if missing:
            raise ValueError(f"event {ev.get('id', '?')!r} missing {missing}")
        if ev["id"] in seen:
            raise ValueError(f"duplicate event id {ev['id']!r}")
        seen.add(ev["id"])
        for f in ("mundane_cause", "uncanny_cause"):
            if not str(ev[f]).strip():
                raise ValueError(f"event {ev['id']!r} has empty {f}")
        for ch in ev.get("choices", []):
            if "key" not in ch or "text" not in ch or "effects" not in ch:
                raise ValueError(f"event {ev['id']!r} has malformed choice {ch!r}")


@dataclass
class Choice:
    key: str
    text: str
    tags: List[str]
    cost: str
    effects: List[dict]


@dataclass
class Pending:
    event_id: str
    text: str
    target_id: Optional[int]
    choices: List[Choice]


@dataclass
class FiredEvent:
    tick: int
    id: str
    act: int
    text: str
    mundane_ok: bool
    choice: Optional[str] = None
    beat: bool = False


class EventEngine:
    def __init__(self, events: List[dict], use_schedule: bool = True):
        validate_events(events)
        self.use_schedule = use_schedule  # False in the live game: real combat is the clock
        self.events = {e["id"]: e for e in events}
        self.last_fired: Dict[str, int] = {}
        self.last_any = -99
        self.last_beat = 0

    # -- selection ----------------------------------------------------------
    def select(self, world) -> Optional[dict]:
        t = world.tick_no
        act = world.act()
        # Mission phases are the second trigger (after state): fired by progress.
        run = world.run
        if run is not None:
            due = [e for e in self.events.values()
                   if e.get("mission") == run.mission.id and "at_progress" in e
                   and e["id"] not in run.phase_fired
                   and world.ship.progress >= e["at_progress"] and evaluate(e.get("requires"), world)]
            if due:
                return min(due, key=lambda e: e["at_progress"])
        scheduled = [e for e in self.events.values()
                     if self.use_schedule and t in e.get("schedule", [])
                     and self._ready(e, t, act, world, check_global=False)]
        if scheduled:
            return scheduled[0]
        if t - self.last_any < GLOBAL_COOLDOWN:
            return None
        cands = [e for e in self.events.values()
                 if "schedule" not in e and self._ready(e, t, act, world)]
        # Good management delays the presence, it does not remove it (DESIGN.md 2):
        # when it has been quiet for too long, the next event is one that shows it.
        overdue = t >= BEAT_START and t - self.last_beat >= BEAT_GAP
        beats = [e for e in cands if e.get("beat")]
        if overdue and beats:
            return world.rng.choices(beats, weights=[e.get("weight", 1.0) for e in beats], k=1)[0]
        if world.rng.random() > 0.22 + 0.35 * world.dread():
            return None
        if not cands:
            return None
        weights = [e.get("weight", 1.0) for e in cands]
        return world.rng.choices(cands, weights=weights, k=1)[0]

    def _ready(self, ev, t, act, world, check_global=True) -> bool:
        if "at_progress" in ev:
            return False                       # phase events fire from select(), not the pool
        if "mission" in ev:
            ms = ev["mission"] if isinstance(ev["mission"], list) else [ev["mission"]]
            if world.run is None or world.run.mission.id not in ms:
                return False
        if "schedule" in ev and not self.use_schedule:
            return False
        if act not in ev["acts"] and "schedule" not in ev:
            return False
        if ev.get("once") and ev["id"] in self.last_fired:
            return False
        if t - self.last_fired.get(ev["id"], -99) < ev.get("cooldown", 12):
            return False
        return evaluate(ev.get("requires"), world)

    # -- firing -------------------------------------------------------------
    def fire(self, ev: dict, world) -> FiredEvent:
        t = world.tick_no
        self.last_fired[ev["id"]] = t
        self.last_any = t
        if "at_progress" in ev and world.run is not None:
            world.run.phase_fired.add(ev["id"])
        target = self._pick_target(ev.get("target"), world)
        world.event_target = target
        mundane_ok = evaluate(ev.get("mundane_when"), world)
        text = ev["text"].format(target=target.name if target else "someone")
        record = FiredEvent(t, ev["id"], world.act(), text, mundane_ok, beat=bool(ev.get("beat")))
        if ev.get("beat"):
            self.last_beat = t
        world.fired.append(record)
        world.log.append(f"[{t:03d}] {text}")
        apply_effects(ev.get("effects", []), world, target)
        choices = [Choice(c["key"], c["text"], c.get("tags", []), c.get("cost", ""), c["effects"])
                   for c in ev.get("choices", []) if evaluate(c.get("requires"), world)]
        if choices:
            world.pending = Pending(ev["id"], text, target.id if target else None, choices)
        return record

    def _pick_target(self, spec, world):
        if not spec:
            return None
        pool = [c for c in world.active_crew() if not c.isolated or spec.get("include_isolated")]
        if "role" in spec:
            pool = [c for c in pool if c.role == spec["role"]] or pool
        if not pool:
            return None
        sel = spec.get("select", "random")
        if sel == "highest":
            return max(pool, key=lambda c: getattr(c, spec["stat"]))
        if sel == "lowest":
            return min(pool, key=lambda c: getattr(c, spec["stat"]))
        return world.rng.choice(pool)


# -- effect interpreter ----------------------------------------------------
def _who(spec, world, target):
    if spec == "target":
        return [target] if target else []
    if spec == "all":
        return world.active_crew()
    if spec == "random":
        pool = world.active_crew()
        return [world.rng.choice(pool)] if pool else []
    if spec == "others":
        return [c for c in world.active_crew() if target is None or c.id != target.id]
    if spec.startswith("role:"):
        return [c for c in world.active_crew() if c.role == spec[5:]]
    raise ValueError(f"unknown who {spec!r}")


def apply_effects(effects: List[dict], world, target=None):
    ship = world.ship
    for fx in effects:
        op = fx["op"]
        if op == "ship":
            lo, hi = SHIP_CLAMP.get(fx["stat"], (0.0, 1.0))
            setattr(ship, fx["stat"], clamp(getattr(ship, fx["stat"]) + fx["value"], lo, hi))
        elif op == "crew":
            for c in _who(fx["who"], world, target):
                setattr(c, fx["stat"], clamp(getattr(c, fx["stat"]) + fx["value"]))
        elif op == "flag":
            ship.flags.add(fx["name"])
            if "ttl" in fx:
                world.flag_expiry[fx["name"]] = world.tick_no + fx["ttl"]
        elif op == "unflag":
            ship.flags.discard(fx["name"])
        elif op == "routine":
            item = fx["item"]
            ship.routines[item] = clamp(ship.routines[item] + fx["value"])
        elif op == "rumor":
            r = ship.rumors.get(fx["id"]) or Rumor(fx["id"], fx["text"], fx.get("intensity", 0.5),
                                                  drift=dict(fx.get("drift", {})))
            r.intensity = clamp(max(r.intensity, fx.get("intensity", r.intensity)))
            seed = fx.get("seed", "target")
            for c in _who(seed, world, target) if seed != "none" else []:
                r.believers.add(c.id)
                c.believes.add(r.id)
            ship.rumors[r.id] = r
        elif op == "phantom":
            aud = {c.id for c in _who(fx["audible"], world, target)}
            if aud:
                world.deck.spawn(fx["kind"], aud, fx.get("intensity", 0.4), fx.get("text", ""),
                                 rng=world.rng, crew=world.crew)
        elif op == "vanish":
            for c in _who(fx["who"], world, target):
                c.missing = True
            ship.flags.add("sailor_missing")
        elif op == "isolate":
            for c in _who(fx["who"], world, target):
                c.isolated = True
        elif op == "release":
            for c in _who(fx["who"], world, target):
                c.isolated = False
                c.isolated_ticks = 0
        elif op == "kill":
            for c in _who(fx["who"], world, target):
                c.alive = False
        elif op == "combat":
            world.combat(fx["severity"])
        elif op == "set":
            setattr(ship, fx["stat"], fx["value"])
        elif op == "time":
            world.time_cost += fx["value"]
        elif op == "rumor_intensity":
            r = ship.rumors.get(fx["id"])
            if r is not None:
                r.intensity = clamp(r.intensity + fx["value"])
        elif op == "verify_orders":
            from .orders import verify_orders
            world.log.append(f"[{world.tick_no:03d}] {verify_orders(world)}")
        elif op == "mission_outcome":
            world.resolve_mission(fx["value"])
        elif op == "if":
            apply_effects(fx["then"] if evaluate(fx["cond"], world) else fx.get("else", []), world, target)
        elif op == "chance":
            p = fx["p"]
            if "mod" in fx:
                m = fx["mod"]
                p += m["k"] * (resolve_path(m["path"], world) - m.get("ref", 0.0))
            for flag, bonus in fx.get("if_flag", {}).items():
                if flag in ship.flags:
                    p += bonus
            apply_effects(fx["then"] if world.rng.random() < clamp(p, 0.02, 0.98) else fx.get("else", []),
                          world, target)
        elif op == "mute_phantoms":
            world.deck.mute_all()
        elif op == "log":
            world.log.append(f"[{world.tick_no:03d}] {fx['text']}")
        else:
            raise ValueError(f"unknown effect op {op!r}")
