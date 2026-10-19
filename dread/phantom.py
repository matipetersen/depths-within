"""Phantom sonar layer (DESIGN.md section 4).

Contacts that exist only in the hydrophones. They sit on top of the real sonar
in ``world/sonar_systems.py``; nothing here touches real detections except
``real_detection_chance``.
"""
from dataclasses import dataclass, field
from typing import List, Set

from .state import clamp

VOICE_LINES = (
    "{name}... {name}... come up here.",
    "{name}, it's cold. Open the hatch.",
    "Why did you leave me, {name}?",
    "{name}. {name}. {name}.",
)
ECHO_LINES = (
    "an echo that keeps pace with us, then slows",
    "a slow return moving against the current",
    "something that breathes in time with the screws",
)
MORSE_LINES = (
    "...-- sunk three days ago, still sending",
    "recall order, signed by a dead officer",
    "a list of names, one of them still aboard",
)


@dataclass
class Phantom:
    id: int
    kind: str                  # echo | voice | morse
    audible_to: Set[int] = field(default_factory=set)
    intensity: float = 0.3
    age: int = 0
    text: str = ""


class SonarDeck:
    """Holds phantom contacts and the real-contact penalty of silencing sonar."""

    def __init__(self):
        self.phantoms: List[Phantom] = []
        self.names_learned: Set[int] = set()
        self._next_id = 1
        self.sonar_off_ticks = 0

    # -- creation -----------------------------------------------------------
    def spawn(self, kind, audible_to, intensity=0.3, text="", rng=None, crew=None):
        if not text:
            text = self._text_for(kind, audible_to, rng, crew)
        p = Phantom(self._next_id, kind, set(audible_to), intensity, 0, text)
        self._next_id += 1
        self.phantoms.append(p)
        return p

    def _text_for(self, kind, audible_to, rng, crew):
        if kind == "voice":
            names = [c.name for c in (crew or []) if c.id in self.names_learned and c.active]
            name = rng.choice(names) if names and rng else "someone"
            return (rng.choice(VOICE_LINES) if rng else VOICE_LINES[0]).format(name=name)
        pool = ECHO_LINES if kind == "echo" else MORSE_LINES
        return rng.choice(pool) if rng else pool[0]

    # -- per-tick -----------------------------------------------------------
    def tick(self, world):
        ship, rng, crew = world.ship, world.rng, world.crew
        live = world.active_crew()

        # silence also removes the penalty only while sonar is off
        if ship.sonar_on:
            self.sonar_off_ticks = 0
        else:
            self.sonar_off_ticks += 1

        for p in list(self.phantoms):
            p.age += 1
            p.intensity = clamp(p.intensity + 0.02 * ship.attention - 0.006)
            if p.intensity <= 0.0:
                self.phantoms.remove(p)
                continue
            # a strong phantom becomes audible to the most strained listener
            if p.intensity > 0.6 and rng.random() < 0.08:
                cand = [c for c in live if c.id not in p.audible_to]
                if cand:
                    c = max(cand, key=lambda c: c.fear + c.fatigue)
                    p.audible_to.add(c.id)
            if ship.sonar_on:
                for cid in p.audible_to:
                    c = world.crew_by_id(cid)
                    if c is None or not c.active:
                        continue
                    c.fear = clamp(c.fear + 0.012 * p.intensity)
                    c.fatigue = clamp(c.fatigue + 0.004)
                    if p.kind == "voice" and rng.random() < 0.15 * p.intensity:
                        # being addressed by name teaches the presence the name
                        self.names_learned.add(c.id)
                        c.name_known = True
                        ship.attention = clamp(ship.attention + 0.01)
            elif len([c for c in p.audible_to if c in {x.id for x in live}]) >= 2:
                # several people heard it and the captain muted the set
                for c in live:
                    c.trust = clamp(c.trust - 0.002)

        # spontaneous phantom: tired, afraid sonar operators + attention
        sonar_ops = [c for c in live if c.role == "sonar"]
        if sonar_ops and len(self.phantoms) < 4:
            op = max(sonar_ops, key=lambda c: c.fear + c.fatigue)
            p_spawn = 0.01 + 0.05 * ship.attention + 0.015 * (op.fear + op.fatigue)
            if ship.sonar_on and rng.random() < p_spawn:
                kind = rng.choice(["echo", "echo", "voice", "morse"])
                if kind == "voice" and not self.names_learned:
                    kind = "echo"
                self.spawn(kind, {op.id}, intensity=0.3, rng=rng, crew=crew)

    # -- orders -------------------------------------------------------------
    def mute_all(self):
        """Silencing the sonar removes what the operator hears right now."""
        for p in self.phantoms:
            p.intensity = clamp(p.intensity - 0.15)
        self.phantoms = [p for p in self.phantoms if p.intensity > 0.0]

    def real_detection_chance(self, ship) -> float:
        """Probability the boat notices a *real* contact before it is on top of us."""
        return 0.9 if ship.sonar_on else 0.3
