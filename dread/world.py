"""DreadWorld: the per-tick simulation that ties state, phantoms and events together."""
import random
from typing import List, Optional

from .events import EventEngine, FiredEvent, Pending, apply_effects, load_events
from .phantom import SonarDeck
from .state import Crew, ROLES, Ship, clamp, dread_index, lerp, stage_for

DEFAULT_NAMES = ("Brandt", "Keller", "Vogel", "Hahn", "Lenz", "Ostrow",
                 "Weiss", "Maier", "Fuchs", "Reiter", "Arndt", "Kopp")
HARD_LIMIT_FACTOR = 1.1        # the patrol window closes at patrol_ticks * 1.1
ATTENTION_FLOOR = 0.25          # attention the presence reaches on its own after ~70 h submerged
REST_CANCEL_FATIGUE = 0.012    # per-tick fatigue for off-watch crew when rest is cancelled
PACE = 0.95                    # ticks needed = patrol_ticks * PACE / effective readiness


def default_crew(rng: random.Random, names=DEFAULT_NAMES) -> List[Crew]:
    crew = []
    for i, name in enumerate(names):
        crew.append(Crew(id=i, name=name, role=ROLES[i % len(ROLES)], section=i % 3,
                         candor=round(rng.uniform(0.25, 0.85), 2)))
    return crew


class DreadWorld:
    def __init__(self, crew: Optional[List[Crew]] = None, seed: int = 0,
                 patrol_ticks: int = 72, events: Optional[List[dict]] = None,
                 use_schedule: bool = True):
        self.rng = random.Random(seed)
        self.crew = crew if crew is not None else default_crew(self.rng)
        self.ship = Ship()
        self.deck = SonarDeck()
        self.engine = EventEngine(events if events is not None else load_events(), use_schedule)
        self.patrol_ticks = patrol_ticks
        self.tick_no = 0
        self.log: List[str] = []
        self.fired: List[FiredEvent] = []
        self.pending: Optional[Pending] = None
        self.event_target: Optional[Crew] = None
        self.flag_expiry = {}
        self.mutiny_clock = 0
        self.time_cost = 0.0      # progress lost to rituals etc., applied next tick
        self.peak_dread = 0.0

    # -- accessors ----------------------------------------------------------
    def active_crew(self) -> List[Crew]:
        return [c for c in self.crew if c.active]

    def crew_by_id(self, cid: int) -> Optional[Crew]:
        return next((c for c in self.crew if c.id == cid), None)

    def dread(self) -> float:
        return dread_index(self.ship, self.crew)

    def stage(self) -> str:
        return stage_for(self.dread())

    @property
    def sonar_off_ticks(self) -> int:
        return self.deck.sonar_off_ticks

    def act(self) -> int:
        d = self.dread()
        by_dread = 1 if d < 0.22 else 2 if d < 0.38 else 3
        return min(by_dread, 1 + self.tick_no // 24)

    @property
    def finished(self) -> bool:
        f = self.ship.flags
        return (self.ship.progress >= 1.0 or self.ship.hull <= 0.0 or "deposed" in f
                or "aborted" in f or not self.active_crew()
                or self.tick_no >= self.patrol_ticks * HARD_LIMIT_FACTOR)

    # -- player-facing views -------------------------------------------------
    def report(self, observer_skill: float = 0.6) -> List[dict]:
        """What the captain gets to see: reported stress and *observed* symptoms."""
        medic = any(c.role == "medic" for c in self.active_crew())
        p = min(0.95, observer_skill + (0.25 if medic else 0.0))
        rows = []
        for c in self.active_crew():
            seen = [s for s in c.symptoms() if self.rng.random() < p]
            rows.append({"name": c.name, "role": c.role, "says": round(c.reported(self.ship.cohesion), 2),
                         "symptoms": seen})
        return rows

    # -- decisions ----------------------------------------------------------
    def choose(self, key: str) -> str:
        if self.pending is None:
            raise RuntimeError("no pending decision")
        ch = next((c for c in self.pending.choices if c.key == key), None)
        if ch is None:
            raise KeyError(key)
        target = self.crew_by_id(self.pending.target_id) if self.pending.target_id is not None else None
        apply_effects(ch.effects, self, target)
        for rec in reversed(self.fired):
            if rec.id == self.pending.event_id:
                rec.choice = key
                break
        self.log.append(f"[{self.tick_no:03d}] > {ch.text}")
        self.pending = None
        return ch.text

    # -- the tick -----------------------------------------------------------
    def tick(self) -> List[str]:
        if self.pending is not None:
            raise RuntimeError("a decision is pending; call choose() first")
        start = len(self.log)
        self.tick_no += 1
        s = self.ship
        for name, until in list(self.flag_expiry.items()):
            if self.tick_no >= until:
                s.flags.discard(name)
                del self.flag_expiry[name]
        if not s.surfaced:
            s.hours_submerged += 1
        self._physics()
        self._rumors()
        self.deck.tick(self)
        self._mission()
        self._mutiny()
        ev = self.engine.select(self)
        if ev is not None:
            self.engine.fire(ev, self)
        self.peak_dread = max(self.peak_dread, self.dread())
        return self.log[start:]

    def _physics(self):
        s, live = self.ship, self.active_crew()
        n = max(1, len(live))
        # air
        if s.surfaced:
            s.co2 = max(0.005, s.co2 - 0.01)
        else:
            s.co2 = clamp(s.co2 + 0.00075 * n / 10, 0.0, 0.1)
        # noise
        base = 0.04 if s.silent_running else 0.1
        s.noise = clamp(base + (s.noise - base) * 0.6)
        # routines wear out on their own
        for k in s.routines:
            s.routines[k] = clamp(s.routines[k] - 0.008)
        if s.rest_cancelled:
            s.routines["watches"] = clamp(s.routines["watches"] - 0.01)
        routine, cohesion = s.routine, s.cohesion
        for c in live:
            on_watch = (self.tick_no // 4) % 3 == c.section
            if on_watch:
                c.fatigue = clamp(c.fatigue + 0.015)
            elif s.rest_cancelled:
                c.fatigue = clamp(c.fatigue + REST_CANCEL_FATIGUE)
            else:
                quality = (0.5 if s.co2 > 0.015 else 1.0) * (0.5 if c.fear > 0.6 else 1.0)
                c.fatigue = clamp(c.fatigue - 0.012 * quality)
            if s.co2 > 0.015:
                c.fatigue = clamp(c.fatigue + 0.003)
            decay = 0.006 * routine * cohesion * (1 - 0.5 * s.attention)
            c.fear = max(0.05, c.fear - decay)
            if c.fatigue > 0.5:
                c.fear = clamp(c.fear + 0.003 + 0.01 * (c.fatigue - 0.5))
            if s.co2 > 0.03:
                c.fear = clamp(c.fear + 0.006)
            if c.isolated:
                c.isolated_ticks += 1
                if c.isolated_ticks > 6:
                    c.fear = clamp(c.fear + 0.01)
            if cohesion > 0.6:
                c.guilt = clamp(c.guilt - 0.002)
            if routine > 0.5:
                c.trust = clamp(c.trust + 0.002, 0.0, 0.9)
            elif routine < 0.3:
                c.trust = clamp(c.trust - 0.002)
        mean = lambda a: sum(getattr(c, a) for c in live) / n
        iso_frac = sum(1 for c in live if c.isolated) / n
        s.cohesion = lerp(s.cohesion, clamp(0.4 * mean("trust") + 0.45 * routine
                                            + 0.15 * (1 - 3 * iso_frac)), 0.06)
        s.discipline = lerp(s.discipline, clamp(0.35 + 0.4 * mean("trust")
                                                + 0.25 * (1 - mean("fatigue"))), 0.05)
        s.readiness = clamp(1.05 - 0.4 * mean("fatigue") - 0.3 * (1 - s.discipline)
                            + (0.35 if s.rest_cancelled else 0.0), 0.0, 1.4)
        if mean("fatigue") > 0.6:      # exhausted crews cause accidents
            s.hull = clamp(s.hull - 0.004)
        if s.rest_cancelled:
            for c in live:
                c.trust = clamp(c.trust - 0.004)
        # the presence
        d = self.dread()
        da = (0.003 * sum(1 for c in live if c.isolated) + 0.012 * d
              - 0.004 * routine * s.cohesion - 0.001)
        if s.surfaced:
            da -= 0.03
        s.attention = clamp(s.attention + da)
        # The presence is patient: time under the water alone gives it a foothold,
        # whatever the captain does. Only hours submerged count; surfacing pauses the clock.
        s.attention = max(s.attention, ATTENTION_FLOOR * clamp((s.hours_submerged - 10) / 60))
        # alone on the night watch feeds it, but only for the unlucky
        for c in live:
            if c.isolated or (self.tick_no % 24 in (0, 1, 2, 3, 22, 23) and c.fear > 0.5):
                if self.rng.random() < 0.15 * s.attention and not c.name_known:
                    c.name_known = True
                    self.deck.names_learned.add(c.id)

    def _rumors(self):
        s, live = self.ship, self.active_crew()
        n = max(1, len(live))
        for rid, r in list(s.rumors.items()):
            for cid in list(r.believers):
                c = self.crew_by_id(cid)
                if c is None or not c.active:
                    r.believers.discard(cid)
                    continue
                c.fear = clamp(c.fear + 0.004 * r.intensity)
                for stat, v in r.drift.items():
                    setattr(c, stat, clamp(getattr(c, stat) + v))
            if r.believers:
                share = len(r.believers) / n
                for c in live:
                    if c.id in r.believers or c.isolated:
                        continue
                    p = 0.05 * r.intensity * share * (0.5 + c.fear) * (0.5 + s.cohesion)
                    if self.rng.random() < p:
                        r.believers.add(c.id)
                        c.believes.add(rid)
            r.intensity = clamp(r.intensity - 0.004)
            if r.intensity < 0.03:
                for cid in r.believers:
                    c = self.crew_by_id(cid)
                    if c:
                        c.believes.discard(rid)
                del s.rumors[rid]

    def _mission(self):
        s = self.ship
        speed = s.readiness * (0.5 if s.silent_running else 1.0) * (0.0 if s.surfaced else 1.0)
        s.progress = clamp(s.progress + speed / (self.patrol_ticks * PACE) - self.time_cost)
        self.time_cost = 0.0
        if s.surfaced and self.rng.random() < 0.08:
            self.log.append(f"[{self.tick_no:03d}] Aircraft overhead. We are exposed.")
            s.hull = clamp(s.hull - 0.12)
            for c in self.active_crew():
                c.fear = clamp(c.fear + 0.05)

    def _mutiny(self):
        s = self.ship
        if "mutiny_brewing" not in s.flags:
            self.mutiny_clock = 0
            return
        live = self.active_crew()
        if live and sum(c.trust for c in live) / len(live) > 0.5:
            s.flags.discard("mutiny_brewing")
            self.log.append(f"[{self.tick_no:03d}] The whispering stops. The moment passes.")
            return
        self.mutiny_clock += 1
        if self.mutiny_clock >= 12:
            s.flags.add("deposed")
            self.log.append(f"[{self.tick_no:03d}] The crew takes the control room. You are relieved of command.")

    # -- combat (the external clock) -----------------------------------------
    def combat(self, severity: float):
        s = self.ship
        warned = self.rng.random() < self.deck.real_detection_chance(s)
        noise = s.noise * (0.5 if warned else 1.0) * (0.4 if s.silent_running else 1.0)
        s.hull = clamp(s.hull - severity * (0.25 + 0.75 * noise) * (1.0 if warned else 1.6))
        for c in self.active_crew():
            c.fear = clamp(c.fear + 0.08 * severity * (1.0 if warned else 1.5))
            c.fatigue = clamp(c.fatigue + 0.12 * severity)
        s.noise = clamp(s.noise + 0.2)
        s.flags.add("in_combat")
        self.flag_expiry["in_combat"] = self.tick_no + 5
        self.log.append(f"[{self.tick_no:03d}] " + (
            "Contact warned in time. Rigged for silent running." if warned
            else "No warning. Charges close aboard."))
