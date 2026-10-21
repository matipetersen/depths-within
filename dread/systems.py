"""The boat's machinery: helm, batteries, depth, damaged systems and damage control (DESIGN.md 15.1).

Orders here are really carried out by men, so a tired or frightened helm carries them out late, and a
compartment that has taken water no longer gives what it did. Nothing in this module shows a hidden value.
"""
from .state import clamp

SPEEDS = {"slow": (0.5, 4.0), "standard": (1.0, 8.0), "flank": (1.6, 13.0)}      # work rate, knots
DEPTHS = {"shallow": 60, "deep": 120, "test": 180}
DRAIN = {"slow": 0.003, "standard": 0.006, "flank": 0.02}                          # battery per hour under way
HOTEL = 0.001                                                                     # lights, galley, air
IDLE_DRAIN = 0.002
SYSTEM_OF = {"engine room": "propulsion", "control room": "planes", "bow torpedo room": "bow tubes",
             "after torpedo room": "stern tubes", "crew quarters": "berths"}


def integrity(w, comp: str) -> float:
    return max(0.0, min(1.0, 1.0 - 2.0 * w.ship.damage[comp]))


def system_state(w, comp: str) -> str:
    i = integrity(w, comp)
    return "dead" if i < 0.35 else "damaged" if i < 0.7 else "ok"


def role_error(w, role: str) -> float:
    """How often the men of this trade get it wrong: nothing for rested, calm ones; 0.6 for nobody at all."""
    crew = [c for c in w.active_crew() if c.role == role]
    if not crew:
        return 0.6
    strain = sum((c.fear + c.fatigue) / 2 for c in crew) / len(crew)
    return max(0.0, min(0.6, 1.2 * strain - 0.2))


def depth_m(w) -> int:
    s = w.ship
    return 0 if s.surfaced else DEPTHS[s.depth_order]


def moving(w) -> bool:
    return w.ship.returning or (w.working is not None and not w.work_blocked)


def pace(w) -> float:
    """How fast the work goes: the speed ordered, the engine's state, silence, and whether there is current."""
    s = w.ship
    engine = {"ok": 1.0, "damaged": 0.6, "dead": 0.3}[system_state(w, "engine room")]
    if s.battery <= 0 and not s.surfaced:
        return 0.0
    return SPEEDS[s.speed_order][0] * (0.5 if s.silent_running else 1.0) * engine


def usable_bow_tubes(w) -> int:
    return {"ok": 4, "damaged": 2, "dead": 0}[system_state(w, "bow torpedo room")]


# -- orders -------------------------------------------------------------------------------------------
def _helm_order(w, kind: str, level: str, text: str) -> str:
    s = w.ship
    err = role_error(w, "helm")
    if system_state(w, "control room") != "ok":
        err = max(err, 0.3)
    if err > 0 and w.rng.random() < err * 0.8:
        s.helm_pending = (kind, level)
        s.helm_lag = 2
        return "The helmsman repeats the old order. It will take a moment."
    _apply_helm(w, kind, level)
    return text


def _apply_helm(w, kind: str, level: str):
    if kind == "speed":
        w.ship.speed_order = level
    else:
        w.ship.depth_order = level


def set_speed(w, level: str) -> str:
    s = w.ship
    if level == s.speed_order and s.helm_pending is None:
        return f"We are already making {level} speed."
    state = system_state(w, "engine room")
    if level == "flank" and state != "ok":
        return "The engine room cannot give it."
    if state == "dead" and level != "slow":
        return "The engine room can give no more than slow."
    return _helm_order(w, "speed", level, f"Ahead {level}.")


def set_depth(w, level: str) -> str:
    s = w.ship
    if s.surfaced:
        return "We are on the surface."
    if level == s.depth_order and s.helm_pending is None:
        return f"We are already at {DEPTHS[level]} metres."
    if system_state(w, "control room") == "dead":
        return "The planes are jammed. We stay where we are."
    s.scope_up = False if level != "shallow" else s.scope_up
    return _helm_order(w, "depth", level, f"Going to {DEPTHS[level]} metres.")


def snorkel(w, on: bool) -> str:
    s = w.ship
    if on and not (s.scope_up and not s.surfaced):
        return "Snorkel depth means the periscope is up."
    s.snorkel = on
    return "The diesels run on the snorkel. The boat shudders and the air moves." if on else "The diesels stop."


def damage_control(w, on: bool) -> str:
    s = w.ship
    if on and s.spares <= 0:
        return "There is nothing left to repair with."
    if on and s.hull >= 0.999:
        return "Nothing is broken that anyone can find."
    s.dc_active = on
    return "All hands that can be spared go to the worst compartment." if on else "The damage control party stands down."


# -- the tick -----------------------------------------------------------------------------------------
def tick(w):
    s, live = w.ship, w.active_crew()
    t = w.tick_no
    if s.helm_pending is not None:
        s.helm_lag -= 1
        if s.helm_lag <= 0:
            kind, level = s.helm_pending
            s.helm_pending = None
            _apply_helm(w, kind, level)
            w.log.append(f"[{t:03d}] The helm answers: {'ahead ' + level if kind == 'speed' else str(DEPTHS[level]) + ' metres'}.")
    # dead reckoning drifts: faster when under way, when the helm is tired and when the presence leans on the chart
    g = (0.12 if moving(w) else 0.03) * (1.0 + 1.5 * role_error(w, "helm") + s.attention)
    s.dr_error = min(40.0, s.dr_error + g)
    # batteries
    if s.snorkel and not (s.scope_up and not s.surfaced):
        s.snorkel = False
        w.log.append(f"[{t:03d}] The diesels stop; there is no snorkel to breathe through.")
    if s.surfaced:
        s.battery = clamp(s.battery + 0.06)
    elif s.snorkel:
        s.battery = clamp(s.battery + 0.03)
        s.fuel = clamp(s.fuel - 0.005)
        s.co2 = clamp(s.co2 - 0.004, 0.005, 0.1)
        s.attention = clamp(s.attention + 0.004)
    else:
        rate = DRAIN[s.speed_order] if moving(w) else IDLE_DRAIN
        s.battery = clamp(s.battery - (rate * (0.6 if s.silent_running else 1.0) + HOTEL))
    if s.battery <= 0.0 and not s.surfaced:
        if "battery_dead" not in s.flags:
            s.flags.add("battery_dead")
            w.log.append(f"[{t:03d}] The batteries are flat. The lights go. We cannot move until we surface or run the diesels.")
    elif "battery_dead" in s.flags and s.battery > 0.1:
        s.flags.discard("battery_dead")
        w.log.append(f"[{t:03d}] The lights come back. The motors turn.")
    if s.battery < 0.25 and not s.surfaced:                        # dim lights: the dark is a presence of its own
        for c in live:
            c.fear = clamp(c.fear + 0.003)
        s.attention = clamp(s.attention + 0.003)
    # depth: pressure on the hull and on the men
    if not s.surfaced:
        if s.depth_order == "deep":
            for c in live:
                c.fear = clamp(c.fear + 0.0015)
            if s.hull < 0.6 and w.rng.random() < 0.02:
                s.hull = clamp(s.hull - 0.02)
                w.log.append(f"[{t:03d}] A seam weeps at 120 metres.")
        elif s.depth_order == "test":
            for c in live:
                c.fear = clamp(c.fear + 0.004)
            if s.hull < 0.8 and w.rng.random() < 0.05:
                s.hull = clamp(s.hull - 0.04)
                w.log.append(f"[{t:03d}] A seam gives at test depth. The pumps race.")
    # damage control: hands, parts and hours
    if s.dc_active:
        if s.hull >= 0.999 or s.spares <= 0.0:
            s.dc_active = False
            w.log.append(f"[{t:03d}] Damage control stands down: " + ("nothing left to mend." if s.hull >= 0.999 else "the spares are gone."))
        else:
            s.hull = clamp(s.hull + 0.005)
            s.spares = clamp(s.spares - 0.012)
            for c in live:
                c.fatigue = clamp(c.fatigue + 0.003)
