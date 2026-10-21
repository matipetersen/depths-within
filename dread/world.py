"""DreadWorld: the per-tick simulation that ties state, phantoms and events together."""
import random
from typing import List, Optional

from .conditions import evaluate
from .events import EventEngine, FiredEvent, Pending, apply_effects, load_events
from .missions import MissionRun, load_missions, provenance_line
from .phantom import SonarDeck
from . import systems
from .state import COMPARTMENTS, Crew, ROLES, Ship, clamp, dread_index, lerp, stage_for

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
                 use_schedule: bool = True, missions=None):
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
        self.legacy_loss = 0.0    # progress lost to rituals when no mission is running
        self.peak_dread = 0.0
        self._hull_seen = 1.0
        # Missions (DESIGN.md section 7). missions=[] disables them (the live game
        # supplies its own); None loads the default sequence.
        self.missions = load_missions() if missions is None else list(missions)
        self.run = None
        self.mission_i = -1
        self.results = []
        # The endgame's hidden truths come from their own dice so they never shift
        # anything that happens earlier in a patrol (DESIGN.md section 8).
        trng = random.Random(seed * 31 + 7)
        war_over = trng.random() < 0.5
        self.truth = {"war_over": war_over, "notice_at": None if war_over else trng.randint(50, 150)}
        self.notice_at_override = None
        self.vigil_ticks = 0
        self.travel_left = 0
        self.check_until = -1
        self.starving = 0
        if self.missions:
            self._start_mission(0)

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

    @property
    def names_known(self) -> int:
        return len(self.deck.names_learned)

    @property
    def on_station(self) -> bool:
        return self.run is not None and self.run.mission.kind == "hold"

    @property
    def depth_m(self) -> int:
        return systems.depth_m(self)

    @property
    def solution_error(self) -> float:
        from .nav import solution_error
        return solution_error(self)

    @property
    def notice_ready(self) -> float:
        """1.0 once 'further notice' is due (it never is, if the war is over and nobody paid)."""
        if not self.on_station or "notice_received" in self.ship.flags:
            return 0.0
        due = self.notice_at_override if self.notice_at_override is not None else self.truth["notice_at"]
        return 1.0 if due is not None and self.vigil_ticks >= due else 0.0

    def act(self) -> int:
        d = self.dread()
        by_dread = 1 if d < 0.22 else 2 if d < 0.38 else 3
        return min(by_dread, 1 + self.tick_no // 24)

    @property
    def finished(self) -> bool:
        f = self.ship.flags
        done = (self.mission_i >= len(self.missions)) if self.missions else self.ship.progress >= 1.0
        # Without missions the legacy window applies; with them, each mission has its
        # own window (or none, on station) and this is only a safety net.
        limit = self.patrol_ticks * HARD_LIMIT_FACTOR if not self.missions else 2000
        return (done or self.ship.hull <= 0.0 or "deposed" in f
                or "aborted" in f or not self.active_crew() or self.tick_no >= limit)

    # -- player-facing views -------------------------------------------------
    def report(self, observer_skill: float = 0.6) -> List[dict]:
        """What the captain gets to see: reported stress and *observed* symptoms."""
        medic = any(c.role == "medic" for c in self.active_crew())
        p = min(0.95, observer_skill + (0.25 if medic else 0.0))
        # Looking must never change the patrol: observe with dice of its own, fixed per tick.
        look = random.Random(self.tick_no * 7919 + 17)
        rows = []
        for c in self.active_crew():
            seen = [s for s in c.symptoms() if look.random() < p]
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
        self.settle_damage()
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
        self.settle_damage()
        self.tick_no += 1
        s = self.ship
        for name, until in list(self.flag_expiry.items()):
            if self.tick_no >= until:
                s.flags.discard(name)
                del self.flag_expiry[name]
        if not s.surfaced:
            s.hours_submerged += 1
        self._physics()
        self._resources()
        systems.tick(self)
        self._voyage()
        self._rumors()
        self.deck.tick(self)
        self._mission()
        self._mission_flow()
        if self.on_station:
            self.vigil_ticks += 1
        self._mutiny()
        ev = self.engine.select(self)
        if ev is not None:
            self.engine.fire(ev, self)
        self.settle_damage()
        self.peak_dread = max(self.peak_dread, self.dread())
        return self.log[start:]

    def settle_damage(self):
        """Book what the hull lost (or got back) against a compartment. Display only: nothing reads it.

        The compartment is a function of the tick and the hull, so it needs no dice of the world's
        and gives the same answer however often it is called."""
        s = self.ship
        d = self._hull_seen - s.hull
        if abs(d) < 1e-9:
            return
        if d > 0:
            name = random.Random(self.tick_no * 6151 + int(round(s.hull * 1000))).choice(COMPARTMENTS)
            s.damage[name] += d
        else:                                              # damage control works on the worst compartment first
            name = max(COMPARTMENTS, key=lambda c: s.damage[c])
            s.damage[name] = max(0.0, s.damage[name] + d)
        self._hull_seen = s.hull

    def _physics(self):
        s, live = self.ship, self.active_crew()
        n = max(1, len(live))
        # air
        if s.surfaced:
            s.co2 = max(0.005, s.co2 - 0.01)
        else:
            s.co2 = clamp(s.co2 + 0.00075 * n / 10, 0.0, 0.1)
        # noise
        base = max(0.01, (0.04 if s.silent_running else 0.1) + {"slow": -0.03, "standard": 0.0, "flank": 0.15}[s.speed_order]
                   + (0.2 if s.snorkel else 0.0))
        s.noise = clamp(base + (s.noise - base) * 0.6)
        # routines wear out on their own
        for k in s.routines:
            s.routines[k] = clamp(s.routines[k] - 0.008)
        if s.rest_cancelled:
            s.routines["watches"] = clamp(s.routines["watches"] - 0.01)
        routine, cohesion = s.routine, s.cohesion
        for c in live:
            on_watch = (self.tick_no // 4) % 3 == c.section
            if s.stand_down:
                c.fatigue = clamp(c.fatigue + (0.005 if on_watch else -0.03))
            elif on_watch:
                c.fatigue = clamp(c.fatigue + 0.015)
            elif s.rest_cancelled:
                c.fatigue = clamp(c.fatigue + REST_CANCEL_FATIGUE)
            else:
                quality = ((0.5 if s.co2 > 0.015 else 1.0) * (0.5 if c.fear > 0.6 else 1.0)
                           * {"ok": 1.0, "damaged": 0.7, "dead": 0.4}[systems.system_state(self, "crew quarters")])
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
        if mean("fatigue") > 0.6 and not s.stand_down:   # exhausted crews cause accidents
            s.hull = clamp(s.hull - 0.004 * clamp((mean("fatigue") - 0.5) / 0.4))
        elif mean("fatigue") < (0.8 if s.stand_down else 0.5) and s.hull < 1.0:
            s.hull = clamp(s.hull + 0.0015)             # damage control, when there are hands to do it
        if s.rest_cancelled:
            for c in live:
                c.trust = clamp(c.trust - 0.004)
        # doubtful orders erode trust; what the boat has done feeds guilt and the presence
        floor = 0.3 * (1 - self.run.mission.quality) if self.run is not None else 0.0
        s.orders_doubt = max(floor, s.orders_doubt - 0.002)
        for c in live:
            c.trust = clamp(c.trust - 0.0012 * s.orders_doubt)
            c.guilt = clamp(c.guilt + 0.0008 * s.moral_debt)
        if s.stand_down:
            s.discipline = clamp(s.discipline - 0.002)
            s.attention = clamp(s.attention + 0.004)         # a sleeping boat is an unwatched one
            if mean("fatigue") < 0.3:
                s.stand_down = False
                self.log.append(f"[{self.tick_no:03d}] The boat wakes. Normal watches resume.")
        # the presence
        d = self.dread()
        da = (0.003 * sum(1 for c in live if c.isolated) + 0.012 * d + 0.01 * s.moral_debt
              - 0.004 * routine * s.cohesion - 0.001)
        if s.scope_up and not s.surfaced:
            da += 0.004                                        # a raised periscope is a window both ways
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

    # -- the ledger -----------------------------------------------------------
    def _resources(self):
        s, live = self.ship, self.active_crew()
        share = len(live) / 12
        s.food = clamp(s.food - 0.0036 * share * s.rations)
        s.water = clamp(s.water - 0.0042 * share * s.rations)
        if s.surfaced:
            s.fuel = clamp(s.fuel - 0.006)
        if self.ship.surfaced and self.tick_no >= self.check_until > 0 and "checking" in s.flags:
            s.flags.discard("checking")
            s.surfaced = False
        if s.food < 0.2 or s.water < 0.2:
            for c in live:                       # hunger makes people blame the captain
                c.fear = clamp(c.fear + 0.004)
                c.fatigue = clamp(c.fatigue + 0.003)
                c.trust = clamp(c.trust - 0.002)
        if s.food <= 0 or s.water <= 0:
            self.starving += 1
            if self.starving % 8 == 0 and live:
                victim = max(live, key=lambda c: c.fatigue)
                victim.alive = False
                self.log.append(f"[{self.tick_no:03d}] {victim.name} does not wake. Nobody says what he died of.")
                for c in self.active_crew():
                    c.fear = clamp(c.fear + 0.06)
                    c.guilt = clamp(c.guilt + 0.04)
        else:
            self.starving = 0

    # -- the exits (DESIGN.md section 8) --------------------------------------
    def leave_station(self) -> str:
        s = self.ship
        if not self.on_station:
            return "There is no station to leave."
        if s.returning:
            return "We are already under way."
        if s.fuel < 0.25 or "adrift" in s.flags:
            return "Not enough diesel for the passage. We would drift. Surface and charge first."
        s.returning = True
        self.travel_left = 18
        s.flags.add("left_station")
        lawful = "notice_received" in s.flags or "peace_known" in s.flags
        if not lawful:
            s.flags.add("orders_defied")              # the order said: until further notice
        s.surfaced = False
        return ("Setting course for base." if lawful
                else "Setting course for base. There has been no notice; everyone knows it.")

    def check_world(self) -> str:
        s = self.ship
        s.surfaced = True
        s.flags.add("checking")
        self.check_until = self.tick_no + 3
        s.noise = clamp(s.noise + 0.1)
        s.attention = clamp(s.attention - 0.1)
        for c in self.active_crew():
            c.fear = clamp(c.fear - 0.04)
        if self.truth["war_over"]:
            s.flags.add("peace_known")
            return ("On the surface the radio plays dance music. A voice reads the date: "
                    "eleven months past an armistice nobody told us about.")
        return "On the surface, static. Under it something that might be music, or someone counting."

    def _voyage(self):
        s = self.ship
        if not s.returning:
            return
        s.fuel = clamp(s.fuel - 0.012)
        self.travel_left -= 1
        if s.fuel <= 0:
            s.returning = False
            s.flags.add("adrift")
            self.log.append(f"[{self.tick_no:03d}] The engines die. We are adrift.")
        elif self.travel_left <= 0:
            self._arrive()

    def _arrive(self):
        s = self.ship
        s.returning = False
        p = min(0.8, 0.08 + 0.35 * s.owed + 0.2 * ("survivors_taken" in s.flags or "extra_man" in s.flags)
                + 0.03 * self.names_known)
        if self.rng.random() < p:
            s.flags.add("home_unaccounted")
            self.log.append(f"[{self.tick_no:03d}] The pier is there. The count on the gangway does not match the roll, "
                            "and nobody can say which of us is the extra.")
        else:
            self.log.append(f"[{self.tick_no:03d}] The pier is there. Lines are passed. The roll is called, and it is right.")
        lawful = "notice_received" in s.flags or "peace_known" in s.flags
        self.resolve_mission("success" if lawful else "left")

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

    # -- missions -------------------------------------------------------------
    def _start_mission(self, i: int):
        self.mission_i = i
        m = self.missions[i]
        self.run = MissionRun(m, self.tick_no)
        s = self.ship
        s.tubes = ["loaded" if i < s.torpedoes else "empty" for i in range(6)]       # the torpedo room reloads between orders
        s.progress = 0.0
        s.orders_doubt = clamp(max(s.orders_doubt * 0.5, (1 - m.quality) * 0.6 + (0.15 if m.moral else 0.0)))
        self.log.append(f"[{self.tick_no:03d}] ORDERS: {m.title}. {m.briefing}")
        self.log.append(f"[{self.tick_no:03d}]   Received: {provenance_line(m)}")

    # -- the acts: what the captain orders to carry the mission out ------------
    def lose_hours(self, hours: float):
        """Hours of the window spent on something other than the mission."""
        if self.run is not None and self.run.outcome is None:
            self.run.lost += hours
        else:
            self.legacy_loss += hours / self.patrol_ticks

    def next_act(self):
        """The act that carries the mission forward, or None (on station, or all done)."""
        run = self.run
        if run is None or run.outcome is not None:
            return None
        acts = run.mission.acts
        return acts[run.acts_done] if run.acts_done < len(acts) else None

    def act_status(self):
        """(act, ok, why): the next act, whether it can start now, and the reason if not."""
        a = self.next_act()
        if a is None:
            return None, False, ""
        if self.run.working is not None:
            return a, False, "Already under way."
        if self.ship.surfaced:
            return a, False, "We are on the surface. Dive first."
        if not evaluate(a.requires, self):
            return a, False, a.why or "It cannot be done now."
        return a, True, ""

    @property
    def working(self):
        """The act being carried out right now, or None."""
        run = self.run
        if run is None or run.working is None:
            return None
        return run.mission.acts[run.working]

    @property
    def work_blocked(self) -> str:
        """Why the work under way is stopped ('' if it is running)."""
        a = self.working
        if a is None:
            return ""
        if self.ship.surfaced:
            return "We are on the surface."
        if self.ship.stand_down:
            return "The crew is asleep."
        if self.ship.battery <= 0 and not self.ship.surfaced:
            return "The batteries are flat."
        return "" if evaluate(a.requires, self) else (a.why or "It cannot go on.")

    def do_act(self) -> str:
        """Order the next step of the mission. The hours then pass tick by tick."""
        a, ok, why = self.act_status()
        if a is None:
            return "There is nothing to order. The rest is waiting."
        if not ok:
            return why
        run = self.run
        run.working = run.acts_done
        run.work_left = float(a.hours)
        self._set_progress()
        msg = f"You order it: {a.label}."
        self.log.append(f"[{self.tick_no:03d}] > {msg}")
        return msg

    def _set_progress(self):
        run = self.run
        n = len(run.mission.acts)
        part = 0.0
        if run.working is not None:
            part = 1.0 - run.work_left / run.mission.acts[run.working].hours
        self.ship.progress = clamp((run.acts_done + part) / n)

    def _work(self):
        run = self.run
        if run is None or run.outcome is not None or run.working is None:
            return
        if self.work_blocked:
            return
        a = run.mission.acts[run.working]
        run.work_left -= min(1.0, self.ship.readiness) * systems.pace(self)     # a tired crew, a slow ordered speed or a hurt engine take longer
        if run.work_left <= 0.0:
            run.work_left = 0.0
            run.acts_done += 1
            run.working = None
            self.log.append(f"[{self.tick_no:03d}] Done: {a.label}.")
            apply_effects(a.effects, self)
        if run.outcome is None and self.run is run:
            self._set_progress()

    def resolve_mission(self, outcome: str):
        run = self.run
        if run is None or run.outcome is not None:
            return
        run.outcome = outcome
        m = run.mission
        self.results.append({"mission": m.id, "outcome": outcome, "tick": self.tick_no})
        self.ship.flags.add(f"outcome:{m.id}:{outcome}")
        self.log.append(f"[{self.tick_no:03d}] Mission '{m.title}': {outcome}.")
        if self.mission_i + 1 < len(self.missions):
            self._start_mission(self.mission_i + 1)
        else:
            self.mission_i += 1
            self.run = None

    def _mission_flow(self):
        run = self.run
        if run is None or run.outcome is not None:
            return
        m = run.mission
        if m.kind == "hold":
            if self.vigil_ticks > 480:                       # nothing ever ends a vigil by itself
                self.ship.flags.add("derelict")
                self.resolve_mission("failed")
            return
        if self.tick_no > run.deadline:
            self.log.append(f"[{self.tick_no:03d}] The window for '{m.title}' has closed.")
            self.resolve_mission("failed")
        elif self.ship.progress >= 1.0:
            final = [e for e in self.engine.events.values()
                     if e.get("mission") == m.id and e.get("at_progress", 0) >= 1.0
                     and e["id"] not in run.phase_fired]
            if not final:
                self.resolve_mission("success")

    def debrief(self) -> List[str]:
        """After the patrol: everything the captain was never told (DESIGN.md 2, 8)."""
        out = []
        by_id = {m.id: m for m in self.missions}
        for r in self.results:
            m = by_id[r["mission"]]
            out += [f"{m.title}: {r['outcome']} (tick {r['tick']})",
                    f"  Received: {provenance_line(m)}",
                    f"  Plausibly: {m.mundane_origin}",
                    f"  Or: {m.uncanny_origin}"]
        for f in self.fired:
            ev = self.engine.events[f.id]
            if ev.get("beat") or ev.get("mission"):
                out += [f"[{f.tick:03d}] {f.id}: {'explicable' if f.mundane_ok else 'NOT explicable'}",
                        f"  Plausibly: {ev['mundane_cause']}", f"  Or: {ev['uncanny_cause']}"]
        return out

    def _mission(self):
        s = self.ship
        run = self.run
        speed = s.readiness * systems.pace(self) * (0.0 if s.surfaced else 1.0) * (0.3 if s.stand_down else 1.0)
        if run is not None:
            if run.outcome is None and run.mission.acts:
                self._work()
            elif run.outcome is None and run.mission.kind != "hold":
                s.progress = clamp(s.progress + speed / (run.mission.ticks * PACE))
        else:
            s.progress = clamp(s.progress + speed / (self.patrol_ticks * PACE) - self.legacy_loss)
            self.legacy_loss = 0.0
        if s.surfaced and self.rng.random() < 0.08 and not (self.truth["war_over"] and self.vigil_ticks > 0):
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
