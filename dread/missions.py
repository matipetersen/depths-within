"""Missions: a second trigger for events, and the source of the orders' doubtful origin.

A mission is a stretch of the patrol with its own pace, its own window and its
own events (fired when ``ship.progress`` crosses ``at_progress``). The briefing
is shown with its *provenance* (channel, signature, quality 0..1). Where the
order really came from is never settled: each mission carries a
``mundane_origin`` and an ``uncanny_origin`` that only the debrief reveals.
"""
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "missions.json")
OUTCOMES = ("success", "failed", "refused", "altered")
WINDOW_FACTOR = 1.25


@dataclass
class Mission:
    id: str
    kind: str
    ticks: int
    moral: bool
    title: str
    briefing: str
    channel: str
    signed: str
    quality: float
    mundane_origin: str
    uncanny_origin: str
    window: float = WINDOW_FACTOR   # moral missions get slack: the clock must not steal the dilemma


@dataclass
class MissionRun:
    """Runtime state of the mission currently being carried out."""
    mission: Mission
    start_tick: int
    outcome: Optional[str] = None
    phase_fired: set = field(default_factory=set)

    @property
    def deadline(self) -> float:
        return self.start_tick + self.mission.ticks * self.mission.window


def load_missions(path: str = DEFAULT_PATH) -> List[Mission]:
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)["missions"]
    missions = []
    seen = set()
    for m in raw:
        for f in ("id", "kind", "ticks", "title", "briefing", "provenance",
                  "mundane_origin", "uncanny_origin"):
            if f not in m:
                raise ValueError(f"mission {m.get('id', '?')!r} missing {f!r}")
        if m["id"] in seen:
            raise ValueError(f"duplicate mission id {m['id']!r}")
        seen.add(m["id"])
        for f in ("mundane_origin", "uncanny_origin"):
            if not str(m[f]).strip():
                raise ValueError(f"mission {m['id']!r} has empty {f}")
        prov = m["provenance"]
        q = float(prov.get("quality", 0.5))
        if not 0.0 <= q <= 1.0:
            raise ValueError(f"mission {m['id']!r} quality out of range")
        missions.append(Mission(m["id"], m["kind"], int(m["ticks"]), bool(m.get("moral", False)),
                                m["title"], m["briefing"], prov.get("channel", ""),
                                prov.get("signed", ""), q, m["mundane_origin"], m["uncanny_origin"],
                                float(m.get("window", WINDOW_FACTOR))))
    return missions


def provenance_line(m: Mission) -> str:
    """What the captain is shown about where the order came from."""
    return f"{m.channel} {m.signed}".strip()
