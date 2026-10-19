"""Headless patrol simulator: plays the dread loop with fixed policies.

    python -m dread.sim                  # all policies, 200 seeds
    python -m dread.sim --seeds 50 --policy crew_first --log

It exists to answer one question before any more content is written: do the
captain's choices actually trade off against each other? (DESIGN.md section 9.)
"""
import argparse
import random
from collections import Counter
from typing import Dict, List

from . import orders as O
from .world import DreadWorld

PRIORITY = {
    "mission_first": ["comply", "mission", "attack", "report", "listen", "paranoid", "care", "silence"],
    "crew_first": ["alter", "refuse", "care", "patient", "listen", "silence", "mission", "paranoid"],
    "paranoid": ["verify", "paranoid", "comply", "silence", "mission", "care", "listen"],
}
AVOID = {"mission_first": {"abort", "retreat"}, "crew_first": set(), "paranoid": {"abort"}}


def pick_choice(policy: str, pending, prng=None) -> str:
    if policy == "random":
        return prng.choice(pending.choices).key
    ranked = sorted(pending.choices,
                    key=lambda c: (bool(set(c.tags) & AVOID[policy]),
                                   min((PRIORITY[policy].index(t) for t in c.tags if t in PRIORITY[policy]),
                                       default=99)))
    return ranked[0].key


def issue_orders(policy: str, w: DreadWorld, prng=None):
    s = w.ship
    live = w.active_crew()
    if not live:
        return
    if policy == "random":
        return random_orders(w, prng)
    run = w.run
    if run is not None and "verified" not in run.phase_fired:
        # a captain who distrusts where the order came from asks, once per mission
        if (policy == "paranoid" and run.mission.quality < 0.7) or \
           (policy == "crew_first" and run.mission.quality < 0.4):
            w.log.append(f"[{w.tick_no:03d}] {O.verify_orders(w)}")
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


def random_orders(w: DreadWorld, prng: random.Random):
    """A captain with no plan: sometimes does something, sometimes not."""
    if prng.random() > 0.15:
        return
    s, live = w.ship, w.active_crew()
    choice = prng.choice(["cancel_rest", "grant_rest", "hold_ritual", "scrub_air", "silence_sonar",
                          "restore_sonar", "surface", "dive", "isolate", "address_crew", "verify_orders"])
    if choice == "isolate":
        O.isolate(w, prng.choice(live).id)
    else:
        O.ORDERS[choice](w)


def classify_ending(w: DreadWorld, initial_crew: int) -> str:
    s = w.ship
    survivors = len(w.active_crew())
    if s.hull <= 0 or survivors == 0:
        return "lost_with_all_hands"
    if "deposed" in s.flags:
        return "deposed"
    if "aborted" in s.flags:
        return "turned_back"
    done = sum(1 for r in w.results if r["outcome"] in ("success", "altered"))
    if "civilian_sunk" in s.flags:
        return "stained_victory"             # the crew knows, whatever HQ's ledger says
    # Disobedience only counts if the orders are on record. Sometimes there is no
    # record at all (m4_unrecorded): nobody can court-martial you for an order
    # that, as far as anyone can prove, was never given.
    on_record = "orders_unrecorded" not in s.flags
    if "orders_defied" in s.flags and on_record:
        return "court_martial"
    if done >= 3:
        if s.cohesion < 0.3 or survivors < initial_crew * 0.6:
            return "hollow_victory"
        if "orders_bent" in s.flags and on_record:
            return "returned_under_a_cloud"    # HQ will have questions about the log
        return "returned"
    return "mission_failed"


def run_patrol(policy: str, seed: int, patrol_ticks: int = 72, verbose: bool = False) -> Dict:
    w = DreadWorld(seed=seed, patrol_ticks=patrol_ticks)
    prng = random.Random(seed * 7919 + 13)      # the captain's own dice, apart from the world's
    initial = len(w.crew)
    min_hull_by_24 = 1.0
    while not w.finished:
        if w.pending is not None:
            w.choose(pick_choice(policy, w.pending, prng))
            continue
        issue_orders(policy, w, prng)
        w.tick()
        if w.tick_no <= 24:
            min_hull_by_24 = min(min_hull_by_24, w.ship.hull)
    beats = [f for f in w.fired if f.beat]
    early = [f for f in w.fired if f.act in (1, 2) and not f.id.startswith("destroyer")]
    result = {
        "policy": policy, "seed": seed, "ending": classify_ending(w, initial),
        "ticks": w.tick_no, "progress": round(sum(1 for r in w.results if r["outcome"] == "success")
                                              / max(1, len(w.missions)), 3),
        "outcomes": {r["mission"]: r["outcome"] for r in w.results},
        "civilian_sunk": "civilian_sunk" in w.ship.flags, "defied": "orders_defied" in w.ship.flags,
        "bent": "orders_bent" in w.ship.flags, "doubt": round(w.ship.orders_doubt, 3),
        "guilt": round(sum(c.guilt for c in w.active_crew()) / max(1, len(w.active_crew())), 3), "hull": round(w.ship.hull, 3),
        "survivors": len(w.active_crew()), "initial": initial,
        "cohesion": round(w.ship.cohesion, 3), "peak_dread": round(w.peak_dread, 3),
        "events": len(w.fired), "min_hull_by_24": round(min_hull_by_24, 3),
        "beats": len(beats), "first_beat": beats[0].tick if beats else None,
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
        "civilian_rate": sum(r["civilian_sunk"] for r in runs) / n,
        "defied_rate": sum(r["defied"] for r in runs) / n,
        "bent_rate": sum(r["bent"] for r in runs) / n,
        "guilt": sum(r["guilt"] for r in runs) / n,
        "hull": sum(r["hull"] for r in runs) / n,
        "cohesion": sum(r["cohesion"] for r in runs) / n,
        "survival": sum(r["survivors"] / r["initial"] for r in runs) / n,
        "peak_dread": sum(r["peak_dread"] for r in runs) / n,
        "events": sum(r["events"] for r in runs) / n,
        "beats": sum(r["beats"] for r in runs) / n,
        "first_beat": sum(r["first_beat"] for r in runs if r["first_beat"] is not None)
                      / max(1, sum(1 for r in runs if r["first_beat"] is not None)),
        "beat_coverage": sum(1 for r in runs if r["beats"] >= 2
                             and r["first_beat"] is not None and r["first_beat"] <= 30) / n,
        "ambiguity": (sum(r["early_mundane"] for r in runs) / early) if early else 1.0,
        "min_hull_by_24": min(r["min_hull_by_24"] for r in runs),
        "endings": {k: v / n for k, v in endings.most_common()},
        "dominant_ending": endings.most_common(1)[0][1] / n,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--policy", default="all", choices=["all", "random", *PRIORITY])
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--log", action="store_true", help="print the log of seed 0")
    args = ap.parse_args(argv)
    names = list(PRIORITY) if args.policy == "all" else [args.policy]
    for name in names:
        s = summarize(name, list(range(args.seeds)))
        ends = ", ".join(f"{k} {v:.0%}" for k, v in s["endings"].items())
        print(f"{name:14s} progress {s['progress']:.2f}  ticks {s['ticks']:.0f}  hull {s['hull']:.2f}  cohesion {s['cohesion']:.2f}  "
              f"survival {s['survival']:.2f}  peak dread {s['peak_dread']:.2f}  "
              f"civilian {s['civilian_rate']:.0%}  defied {s['defied_rate']:.0%}  guilt {s['guilt']:.2f}  "
              f"events {s['events']:.1f}  beats {s['beats']:.1f} (first t{s['first_beat']:.0f}, "
              f"covered {s['beat_coverage']:.0%})  ambiguity {s['ambiguity']:.0%}")
        print(f"{'':14s} endings: {ends}")
        if args.log:
            print("\n".join(run_patrol(name, 0, verbose=True)["log"]))


if __name__ == "__main__":
    main()
