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
    def __init__(self, roster=None, seed: Optional[int] = None, events=None, missions=()):
        """``missions=()`` runs no missions (the game supplies its own);
        ``missions=None`` runs the whole five-mission sequence of data/missions.json."""
        rng = random.Random(seed)
        self.world = DreadWorld(crew=crew_from_roster(roster, rng), seed=rng.randrange(2 ** 31),
                                patrol_ticks=10 ** 6, events=events, use_schedule=False,
                                missions=missions if missions is None else list(missions))
        self.initial = len(self.world.crew)
        self._decision = None
        self._decision_for = None
        self._logged = 0

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
        if w.pending is not None or w.finished:
            return []
        # listening to the world is a surfacing in the story even if the boat stays deep
        w.ship.surfaced = depth < 10 or ("checking" in w.ship.flags and w.tick_no < w.check_until)
        if submarine is not None and hasattr(submarine, "hull"):
            w.ship.hull = clamp(float(submarine.hull))
        w.tick()
        if submarine is not None and hasattr(submarine, "hull"):
            submarine.hull = w.ship.hull
        lines = w.log[self._logged:]            # includes the briefing written before the first tick
        self._logged = len(w.log)
        return lines

    @property
    def finished(self) -> bool:
        return self.world.finished

    def ending(self) -> str:
        from .endings import classify_ending
        return classify_ending(self.world, self.initial)

    # -- missions -----------------------------------------------------------
    def begin_mission(self, mission_id: str):
        """Start one of data/missions.json on the live boat.

        The game's own quest system can call this when a mission is accepted. The
        mission's phase events then fire as ``progress`` advances (one game hour
        per tick) and its moral decisions arrive as ordinary captain's decisions.
        """
        from .missions import load_missions
        found = next((m for m in load_missions() if m.id == mission_id), None)
        if found is None:
            raise KeyError(mission_id)
        w = self.world
        w.missions = [found]
        w._start_mission(0)
        return found

    def end_mission(self, outcome: str = "failed"):
        """Close the current mission from outside (e.g. the quest was abandoned)."""
        self.world.resolve_mission(outcome)

    # -- decisions ----------------------------------------------------------
    def pending_decision(self):
        """A ``Decision`` for the captain, or None. Same object until resolved."""
        from engine.decisions import Decision, DecisionOption
        p = self.world.pending
        if p is None:
            self._decision = None
            self._decision_for = None
            return None
        # One Decision per pending event. (Keyed on the event, not on "was called while idle":
        # the game asks again only once the next event is already waiting.)
        if self._decision is None or self._decision_for is not p:
            self._decision_for = p
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
