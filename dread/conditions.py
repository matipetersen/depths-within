"""Small declarative condition DSL for events (no eval).

Forms (all JSON-serializable):
    {"path": "ship.co2", "op": ">=", "value": 0.015}
    {"path": "crew.avg.fear", "op": ">", "value": 0.4}      # avg | max | min | count
    {"flag": "sailor_missing"}        {"no_flag": "sailor_missing"}
    {"crew_where": {"role": "sonar", "stat": "fear", "op": ">=", "value": 0.5}}
    {"phantom": "voice"}              # a phantom of that kind exists
    {"rumor": "marked", "believers_gte": 3}
    {"mission": "m3_hospital_ship"}   # the mission in progress is that one (or one of a list)
    {"outcome": {"mission": "m3_hospital_ship", "is": "refused"}}
    {"never": true}                   # always false (act III "unexplained" events)
    {"all": [...]}  {"any": [...]}  {"not": {...}}
"""
import operator

_OPS = {">": operator.gt, ">=": operator.ge, "<": operator.lt,
        "<=": operator.le, "==": operator.eq, "!=": operator.ne}

CREW_STATS = ("fear", "fatigue", "guilt", "trust")


def resolve_path(path, world):
    """Resolve a dotted path to a number."""
    parts = path.split(".")
    head = parts[0]
    if head == "ship":
        return float(getattr(world.ship, parts[1]))
    if head == "world":
        return float(getattr(world, parts[1]))
    if head == "crew":
        live = world.active_crew()
        kind = parts[1]
        if kind == "count":
            return float(len(live))
        stat = parts[2]
        vals = [getattr(c, stat) for c in live]
        if not vals:
            return 0.0
        return {"avg": sum(vals) / len(vals), "max": max(vals), "min": min(vals)}[kind]
    if head == "dread":
        return float(world.dread())
    raise ValueError(f"unknown path {path!r}")


def evaluate(cond, world) -> bool:
    if cond is None or cond == {}:
        return True
    if "never" in cond:      # used by mundane_when: no mundane explanation exists
        return False
    if "all" in cond:
        return all(evaluate(c, world) for c in cond["all"])
    if "any" in cond:
        return any(evaluate(c, world) for c in cond["any"])
    if "not" in cond:
        return not evaluate(cond["not"], world)
    if "path" in cond:
        return _OPS[cond["op"]](resolve_path(cond["path"], world), cond["value"])
    if "flag" in cond:
        return cond["flag"] in world.ship.flags
    if "no_flag" in cond:
        return cond["no_flag"] not in world.ship.flags
    if "crew_where" in cond:
        w = cond["crew_where"]
        op = _OPS[w.get("op", ">=")]
        for c in world.active_crew():
            if "role" in w and c.role != w["role"]:
                continue
            if "stat" in w and not op(getattr(c, w["stat"]), w["value"]):
                continue
            return True
        return False
    if "mission" in cond:
        want = cond["mission"] if isinstance(cond["mission"], list) else [cond["mission"]]
        return world.run is not None and world.run.mission.id in want
    if "outcome" in cond:
        o = cond["outcome"]
        return f"outcome:{o['mission']}:{o['is']}" in world.ship.flags
    if "phantom" in cond:
        return any(p.kind == cond["phantom"] for p in world.deck.phantoms)
    if "rumor" in cond:
        r = world.ship.rumors.get(cond["rumor"])
        if r is None:
            return False
        return len(r.believers) >= cond.get("believers_gte", 1)
    raise ValueError(f"unknown condition {cond!r}")
