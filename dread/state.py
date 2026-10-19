"""State model for the dread system (see DESIGN.md section 3).

Every value is 0..1 unless noted. The *true* values live here; what the player
sees is always filtered through ``Crew.reported`` and ``Crew.symptoms``.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set

ROLES = ("sonar", "torpedo", "engine", "helm", "radio", "medic", "cook", "deck")

ROUTINE_ITEMS = ("meals", "music", "cards", "coffee", "watches")


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


@dataclass
class Crew:
    id: int
    name: str
    role: str
    section: int = 0          # watch section 0..2
    candor: float = 0.5       # fixed trait: how much they say what they feel
    fear: float = 0.1
    fatigue: float = 0.1
    guilt: float = 0.0
    trust: float = 0.8
    alive: bool = True
    missing: bool = False
    isolated: bool = False
    isolated_ticks: int = 0
    name_known: bool = False  # the presence learned this name
    believes: Set[str] = field(default_factory=set)

    @property
    def active(self) -> bool:
        """Present on the boat and able to act."""
        return self.alive and not self.missing

    def stress(self) -> float:
        return clamp(0.45 * self.fear + 0.35 * self.fatigue + 0.20 * self.guilt)

    def reported(self, cohesion: float) -> float:
        """Stress as the crew member *says* it is (DESIGN.md 3.2)."""
        candor_eff = clamp(self.candor * self.trust * (0.6 + 0.4 * cohesion))
        return lerp(0.15, self.stress(), candor_eff)

    def symptoms(self) -> List[str]:
        """Observable tells, deterministic on the true values."""
        out = []
        if self.fear > 0.5:
            out.append("jumpy")
        if self.fear > 0.7:
            out.append("talks to himself")
        if self.fatigue > 0.6:
            out.append("errors at station")
        if self.fatigue > 0.8:
            out.append("microsleeps")
        if self.guilt > 0.5:
            out.append("avoids eyes")
        if self.trust < 0.4:
            out.append("silent when the captain speaks")
        if self.guilt > 0.4 and self.fear > 0.4:
            out.append("leaves small offerings")
        if self.believes and self.fear > 0.3:
            out.append("repeats rumors")
        return out


@dataclass
class Rumor:
    id: str
    text: str
    intensity: float = 0.5
    believers: Set[int] = field(default_factory=set)
    drift: Dict[str, float] = field(default_factory=dict)  # per-tick effect on believers


@dataclass
class Ship:
    cohesion: float = 0.8
    discipline: float = 0.7
    hull: float = 1.0
    readiness: float = 1.0
    co2: float = 0.005        # fraction of air; 0.015 bothersome, 0.03+ dangerous
    noise: float = 0.1
    attention: float = 0.0    # hidden: the presence's interest (DESIGN.md 2)
    progress: float = 0.0     # mission progress 0..1
    # The ledger: honest numbers, unlike everything about the people (DESIGN.md 12)
    food: float = 1.0
    water: float = 1.0
    fuel: float = 1.0
    rations: float = 1.0      # 1.0 full, 0.75, 0.5
    returning: bool = False   # on the way home from the station
    owed: float = 0.0         # hidden: what the sea expects for what it gave
    orders_doubt: float = 0.0 # how little the crew trusts where the orders came from
    moral_debt: float = 0.0   # hidden: what the boat has done that it cannot undo
    scrubber: float = 1.0     # remaining CO2 absorbent
    sonar_on: bool = True
    silent_running: bool = False
    surfaced: bool = False
    rest_cancelled: bool = False
    stand_down: bool = False   # all hands but a skeleton watch rest; the presence is fed by sleepers
    hours_submerged: int = 0
    routines: Dict[str, float] = field(
        default_factory=lambda: {k: 0.9 for k in ROUTINE_ITEMS})
    flags: Set[str] = field(default_factory=set)
    rumors: Dict[str, Rumor] = field(default_factory=dict)

    @property
    def routine(self) -> float:
        return sum(self.routines.values()) / len(self.routines)


def dread_index(ship: Ship, crew: List[Crew]) -> float:
    """Composite pressure used for presentation and act selection (DESIGN.md 3.4)."""
    live = [c for c in crew if c.active]
    if not live:
        return 1.0
    n = len(live)
    fear = sum(c.fear for c in live) / n
    guilt = sum(c.guilt for c in live) / n
    trust = sum(c.trust for c in live) / n
    fatigue = sum(c.fatigue for c in live) / n
    co2_pressure = clamp((ship.co2 - 0.005) / 0.025)
    return clamp(0.30 * fear + 0.15 * guilt + 0.15 * (1 - trust)
                 + 0.15 * fatigue + 0.10 * co2_pressure + 0.15 * (1 - ship.routine))


STAGES = ("DENIAL", "UNEASE", "DREAD", "TERROR", "MADNESS")
_STAGE_CUTS = (0.15, 0.28, 0.42, 0.58)


def stage_for(dread: float) -> str:
    """Presentation-only stage name derived from the dread index."""
    for cut, name in zip(_STAGE_CUTS, STAGES):
        if dread < cut:
            return name
    return STAGES[-1]
