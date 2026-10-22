"""Missions: a second trigger for events, and the source of the orders' doubtful origin.

A mission is a stretch of the patrol with its own pace, its own window and its
own events (fired when ``ship.progress`` crosses ``at_progress``). The briefing
is shown with its *provenance* (channel, signature, quality 0..1). Where the
order really came from is never settled: each mission carries a
``mundane_origin`` and an ``uncanny_origin`` that only the debrief reveals.
"""
import json
import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "missions.json")
OUTCOMES = ("success", "failed", "refused", "altered", "left")
WINDOW_FACTOR = 1.8


@dataclass
class Act:
    """One thing the captain orders to carry the mission out (nothing advances by waiting)."""
    id: str
    label: str
    hint: str
    hours: float
    needs: List[dict]            # [{'requires': condition, 'why': text}]: all must hold; the first that does not says why
    effects: List[dict]
    methods: List[dict] = field(default_factory=list)   # the ways to do it: [{'id','label','hint','hours_mult','dark_mult','effects'}]


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
    acts: List[Act] = field(default_factory=list)
    chart: dict = field(default_factory=dict)    # {'from': [x, y, label], 'points': [[x, y, label], ...]}

    def travel_allowance(self) -> float:
        """Hours the window allows for sailing between the points: the path at a modest 5 knots."""
        if not self.chart:
            return 0.0
        pts = [self.chart["from"]] + list(self.chart["points"])
        total = 0.0
        for a, b in zip(pts, pts[1:]):
            total += math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
        return total / 6.0


@dataclass
class MissionRun:
    """Runtime state of the mission currently being carried out."""
    mission: Mission
    start_tick: int
    outcome: Optional[str] = None
    phase_fired: set = field(default_factory=set)
    acts_done: int = 0
    working: Optional[int] = None    # index of the act being carried out
    work_left: float = 0.0           # hours of work still to do on it
    work_total: float = 1.0          # hours the chosen way of doing it takes
    method: Optional[str] = None     # how the captain chose to do it
    prev: Optional[tuple] = None     # speed and silence before the method changed them
    lost: float = 0.0                # hours of the window spent on anything but the mission

    @property
    def deadline(self) -> float:
        return self.start_tick + self.mission.ticks * self.mission.window + self.mission.travel_allowance() - self.lost


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
                                float(m.get("window", WINDOW_FACTOR)),
                                [Act(a["id"], a["label"], a.get("hint", ""), float(a["hours"]),
                                     list(a.get("needs", [])), list(a.get("effects", [])), list(a.get("methods", [])))
                                 for a in m.get("acts", [])],
                                dict(m.get("chart", {}))))
    return missions


def provenance_line(m: Mission) -> str:
    """What the captain is shown about where the order came from."""
    return f"{m.channel} {m.signed}".strip()
