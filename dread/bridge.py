"""Bridge between the dread simulation and the live game loop.

The game advances one hour per turn (engine/game.py). The bridge:
  * builds the dread crew from the game's roster (names; roles best-effort),
  * ticks the DreadWorld once per game hour and returns log lines,
  * turns pending dread events into ``engine.decisions.Decision`` objects whose
    ``on_resolve`` applies the chosen effects,
  * mirrors hull damage and surfacing both ways.

Scheduled (vestigial) combat events are disabled here: tactical combat is the
external clock in the real game.
"""
import random
from typing import List, Optional

from .state import Crew, ROLES, clamp
from .world import DEFAULT_NAMES, DreadWorld

_ROLE_HINTS = {
    "sonar": "sonar", "hydro": "sonar", "torpedo": "torpedo", "engin": "engine",
    "helm": "helm", "nav": "helm", "radio": "radio", "med": "medic", "doc": "medic",
    "cook": "cook",
}
MAX_CREW = 14


def _role_for(hint: str, fallback: str) -> str:
    h = (hint or "").lower()
    for key, role in _ROLE_HINTS.items():
        if key in h:
            return role
    return fallback


def crew_from_roster(roster, rng: random.Random) -> List[Crew]:
    """Best-effort mapping of the game's roster to dread crew; falls back to defaults."""
    members = []
    cm = getattr(roster, "crew_members", None)
    if isinstance(cm, dict):
        members = [(k, getattr(v, "name", None)) for k, v in cm.items()]
    elif getattr(roster, "crew", None):
        members = [(getattr(c, "role", ""), getattr(c, "name", None)) for c in roster.crew]
    members = [(h, n) for h, n in members if n][:MAX_CREW]
    crew = []
    for i, (hint, name) in enumerate(members):
        crew.append(Crew(i, str(name), _role_for(hint, ROLES[i % len(ROLES)]), section=i % 3,
                         candor=round(rng.uniform(0.25, 0.85), 2)))
    for name in DEFAULT_NAMES:                       # pad so there is always someone to lose
        if len(crew) >= 8:
            break
        i = len(crew)
        crew.append(Crew(i, name, ROLES[i % len(ROLES)], section=i % 3,
                         candor=round(rng.uniform(0.25, 0.85), 2)))
    return crew


class DreadBridge:
    def __init__(self, roster=None, seed: Optional[int] = None, events=None):
        rng = random.Random(seed)
        self.world = DreadWorld(crew=crew_from_roster(roster, rng), seed=rng.randrange(2 ** 31),
                                patrol_ticks=10 ** 6, events=events, use_schedule=False)
        self._decision = None

    # -- state mirrored from the game ---------------------------------------
    def stage(self) -> str:
        return self.world.stage()

    def mean_sanity(self) -> float:
        """0..100, kept for the legacy HorrorMetrics.average_crew_sanity."""
        live = self.world.active_crew()
        if not live:
            return 0.0
        return 100.0 * (1.0 - sum(c.stress() for c in live) / len(live))

    # -- per game hour ------------------------------------------------------
    def tick(self, depth: float = 100.0, submarine=None) -> List[str]:
        """Advance one hour. While a decision is pending the world holds still."""
        w = self.world
        if w.pending is not None:
            return []
        w.ship.surfaced = depth < 10
        if submarine is not None and hasattr(submarine, "hull"):
            w.ship.hull = clamp(float(submarine.hull))
        lines = w.tick()
        if submarine is not None and hasattr(submarine, "hull"):
            submarine.hull = w.ship.hull
        return lines

    # -- decisions ----------------------------------------------------------
    def pending_decision(self):
        """A ``Decision`` for the captain, or None. Same object until resolved."""
        from engine.decisions import Decision, DecisionOption
        p = self.world.pending
        if p is None:
            self._decision = None
            return None
        if self._decision is None:
            keys = {str(i + 1): c for i, c in enumerate(p.choices)}
            options = [DecisionOption(key=k, text=c.text, tooltip=c.cost,
                                      success_message=f"{c.text} ({c.cost})" if c.cost else c.text)
                       for k, c in keys.items()]
            self._decision = Decision(
                id=p.event_id, title=p.event_id.replace("_", " ").title(), description=p.text,
                options=options, source="dread",
                on_resolve=lambda key, _k=keys: self.world.choose(_k[key].key))
        return self._decision

    # -- shore ---------------------------------------------------------------
    def reach_port(self, friendly: bool = True):
        w = self.world
        gain = 0.4 if friendly else 0.2
        for c in w.active_crew():
            c.fear = clamp(c.fear - gain)
            c.fatigue = clamp(c.fatigue - 2 * gain)
            c.guilt = clamp(c.guilt - gain / 2)
            c.isolated = False
            c.isolated_ticks = 0
        w.ship.co2 = 0.005
        w.ship.attention = clamp(w.ship.attention - 0.3)
        w.ship.routines = {k: min(1.0, v + 0.5) for k, v in w.ship.routines.items()}
        w.ship.scrubber = 1.0
