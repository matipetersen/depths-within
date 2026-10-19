"""Headless patrol simulator: plays the dread loop with fixed policies.

    python -m dread.sim                  # all policies, 200 seeds
    python -m dread.sim --seeds 50 --policy crew_first --log

It exists to answer one question before any more content is written: do the
captain's choices actually trade off against each other? (DESIGN.md section 9.)
"""
import argparse
from collections import Counter
from typing import Dict, List

from . import orders as O
from .world import DreadWorld

PRIORITY = {
    "mission_first": ["mission", "listen", "paranoid", "care", "silence"],
    "crew_first": ["care", "listen", "silence", "mission", "paranoid"],
    "paranoid": ["paranoid", "silence", "mission", "care", "listen"],
}
AVOID = {"mission_first": {"abort"}, "crew_first": set(), "paranoid": {"abort"}}


def pick_choice(policy: str, pending) -> str:
    ranked = sorted(pending.choices,
                    key=lambda c: (bool(set(c.tags) & AVOID[policy]),
                                   min((PRIORITY[policy].index(t) for t in c.tags if t in PRIORITY[policy]),
                                       default=99)))
    return ranked[0].key


def issue_orders(policy: str, w: DreadWorld):
    s = w.ship
    live = w.active_crew()
    if not live:
        return
    fatigue = sum(c.fatigue for c in live) / len(live)
    if policy == "mission_first":
        # push hard, ease off only when the crew is close to collapse
        if w.tick_no > 3 and fatigue < 0.75 and not s.rest_cancelled:
            O.cancel_rest(w)
        elif fatigue > 0.85 and s.rest_cancelled:
            O.grant_rest(w)
        if s.co2 > 0.025:
            O.scrub_air(w)
    elif policy == "crew_first":
        if s.rest_cancelled:
            O.grant_rest(w)
        if s.routine < 0.5 and w.tick_no % 4 == 0:
            O.hold_ritual(w)
        if s.co2 > 0.015:
            O.scrub_air(w)
        if not s.surfaced and (s.co2 > 0.03 or w.dread() > 0.5) and w.tick_no % 8 == 0:
            O.surface(w)
        elif s.surfaced and (s.co2 < 0.012 or w.tick_no % 8 in (3, 4)):
            O.dive(w)
        if not s.sonar_on and w.sonar_off_ticks > 4:
            O.restore_sonar(w)
    elif policy == "paranoid":
        if w.tick_no == 6:
            O.ration(w, "alcohol")
        for c in sorted(live, key=lambda c: -c.fear):
            if c.fear > 0.6 and not c.isolated and sum(1 for x in live if x.isolated) < 3:
                O.isolate(w, c.id)
                break
        if w.deck.phantoms and s.sonar_on:
            O.silence_sonar(w)
        if s.co2 > 0.02:
            O.scrub_air(w)
        # when the air runs out, break for the surface and come back down
        if not s.surfaced and s.co2 > 0.03 and w.tick_no % 6 == 0:
            O.surface(w)
        elif s.surfaced and w.tick_no % 6 in (2, 3):
            O.dive(w)
    else:
        raise ValueError(policy)


def classify_ending(w: DreadWorld, initial_crew: int) -> str:
    s = w.ship
    survivors = len(w.active_crew())
    if s.hull <= 0 or survivors == 0:
        return "lost_with_all_hands"
    if "deposed" in s.flags:
        return "deposed"
    if "aborted" in s.flags:
        return "turned_back"
    if s.progress >= 1.0:
        if s.cohesion < 0.3 or survivors < initial_crew * 0.6:
            return "hollow_victory"
        return "returned"
    return "mission_failed"


def run_patrol(policy: str, seed: int, patrol_ticks: int = 72, verbose: bool = False) -> Dict:
    w = DreadWorld(seed=seed, patrol_ticks=patrol_ticks)
    initial = len(w.crew)
    min_hull_by_24 = 1.0
    while not w.finished:
        if w.pending is not None:
            w.choose(pick_choice(policy, w.pending))
            continue
        issue_orders(policy, w)
        w.tick()
        if w.tick_no <= 24:
            min_hull_by_24 = min(min_hull_by_24, w.ship.hull)
    early = [f for f in w.fired if f.act in (1, 2) and not f.id.startswith("destroyer")]
    result = {
        "policy": policy, "seed": seed, "ending": classify_ending(w, initial),
        "ticks": w.tick_no, "progress": round(w.ship.progress, 3), "hull": round(w.ship.hull, 3),
        "survivors": len(w.active_crew()), "initial": initial,
        "cohesion": round(w.ship.cohesion, 3), "peak_dread": round(w.peak_dread, 3),
        "events": len(w.fired), "min_hull_by_24": round(min_hull_by_24, 3),
        "early_events": len(early), "early_mundane": sum(1 for f in early if f.mundane_ok),
        "event_ids": [f.id for f in w.fired],
    }
    if verbose:
        result["log"] = list(w.log)
    return result


def summarize(policy: str, seeds: List[int], patrol_ticks: int = 72) -> Dict:
    runs = [run_patrol(policy, s, patrol_ticks) for s in seeds]
    n = len(runs)
    endings = Counter(r["ending"] for r in runs)
    early = sum(r["early_events"] for r in runs)
    return {
        "policy": policy, "n": n,
        "progress": sum(r["progress"] for r in runs) / n,
        "ticks": sum(r["ticks"] for r in runs) / n,
        "hull": sum(r["hull"] for r in runs) / n,
        "cohesion": sum(r["cohesion"] for r in runs) / n,
        "survival": sum(r["survivors"] / r["initial"] for r in runs) / n,
        "peak_dread": sum(r["peak_dread"] for r in runs) / n,
        "events": sum(r["events"] for r in runs) / n,
        "ambiguity": (sum(r["early_mundane"] for r in runs) / early) if early else 1.0,
        "min_hull_by_24": min(r["min_hull_by_24"] for r in runs),
        "endings": {k: v / n for k, v in endings.most_common()},
        "dominant_ending": endings.most_common(1)[0][1] / n,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--policy", default="all", choices=["all", *PRIORITY])
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--log", action="store_true", help="print the log of seed 0")
    args = ap.parse_args(argv)
    names = list(PRIORITY) if args.policy == "all" else [args.policy]
    for name in names:
        s = summarize(name, list(range(args.seeds)))
        ends = ", ".join(f"{k} {v:.0%}" for k, v in s["endings"].items())
        print(f"{name:14s} progress {s['progress']:.2f}  ticks {s['ticks']:.0f}  hull {s['hull']:.2f}  cohesion {s['cohesion']:.2f}  "
              f"survival {s['survival']:.2f}  peak dread {s['peak_dread']:.2f}  "
              f"events {s['events']:.1f}  ambiguity {s['ambiguity']:.0%}")
        print(f"{'':14s} endings: {ends}")
        if args.log:
            print("\n".join(run_patrol(name, 0, verbose=True)["log"]))


if __name__ == "__main__":
    main()
