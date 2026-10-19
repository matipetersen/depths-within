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
from .endings import classify_ending  # noqa: F401  (re-exported)
from .world import DreadWorld

PRIORITY = {
    "mission_first": ["comply", "mission", "attack", "report", "listen", "paranoid", "care", "silence"],
    "crew_first": ["alter", "refuse", "care", "patient", "listen", "silence", "mission", "paranoid"],
    "paranoid": ["verify", "paranoid", "comply", "silence", "mission", "care", "listen"],
}
AVOID = {"mission_first": {"abort", "retreat"}, "crew_first": set(), "paranoid": {"abort"}}


def vigil_choice(policy: str, w: DreadWorld, pending) -> str:
    """The endgame's decisions depend on the ledger, so the policies read it."""
    ev, s = pending.event_id, w.ship
    keys = {c.key for c in pending.choices}

    def pick(*prefs):
        return next((k for k in prefs if k in keys), pending.choices[0].key)

    if ev == "station_council":
        checked = getattr(w, "_policy_checked", False)
        if policy == "mission_first":
            return pick("hold")
        if policy == "crew_first":
            if "peace_known" in s.flags or "notice_received" in s.flags or s.food < 0.3 or s.water < 0.3:
                return pick("leave", "hold")
            if not checked and w.vigil_ticks >= 16:
                w._policy_checked = True
                return pick("check", "hold")
            return pick("hold_tight" if s.rations > 0.75 else "hold", "hold")
        if not checked:                                   # paranoid wants to know first
            w._policy_checked = True
            return pick("check", "hold")
        return pick("leave" if ("peace_known" in s.flags or "notice_received" in s.flags) else "hold", "hold")
    if ev == "offering_proposal":
        return pick({"mission_first": "forbid", "crew_first": "forbid", "paranoid": "name_him"}[policy])
    if ev == "further_notice":
        return pick("verify" if policy == "paranoid" else "obey")
    if ev in ("sea_gives_fish", "sea_gives_rain"):
        want = policy == "mission_first" or (policy == "crew_first" and min(s.food, s.water) < 0.4)
        return pick("accept" if want else "refuse", "drink" if want else "wary")
    if ev == "larder_short":
        return pick("amnesty" if policy == "crew_first" else "lock")
    if ev == "voyage_charts_wrong":
        return pick("reckoning")
    return pending.choices[0].key


VIGIL_EVENTS = {"station_council", "offering_proposal", "further_notice", "sea_gives_fish",
                "sea_gives_rain", "larder_short", "voyage_charts_wrong"}


def pick_choice(policy: str, pending, prng=None, world=None) -> str:
    if policy == "random":
        return prng.choice(pending.choices).key
    if world is not None and pending.event_id in VIGIL_EVENTS:
        return vigil_choice(policy, world, pending)
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
    if w.on_station and fatigue > 0.6 and not s.stand_down and policy != "paranoid":
        O.stand_down(w)                       # nothing to rush on station: let a broken crew sleep
    if policy == "mission_first":
        if w.on_station:                       # nothing to rush on station: normal watches, fresh air
            if s.rest_cancelled:
                O.grant_rest(w)
            if s.routine < 0.4 and w.tick_no % 4 == 0:
                O.hold_ritual(w)
            if not s.surfaced and s.co2 > 0.03 and w.tick_no % 8 == 0:
                O.surface(w)
            elif s.surfaced and "checking" not in s.flags and (s.co2 < 0.012 or w.tick_no % 8 in (3, 4)):
                O.dive(w)
        # push hard, ease off only when the crew is close to collapse
        elif w.tick_no > 3 and fatigue < 0.75 and not s.rest_cancelled:
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


def run_patrol(policy: str, seed: int, patrol_ticks: int = 72, verbose: bool = False) -> Dict:
    w = DreadWorld(seed=seed, patrol_ticks=patrol_ticks)
    prng = random.Random(seed * 7919 + 13)      # the captain's own dice, apart from the world's
    initial = len(w.crew)
    min_hull_by_24 = 1.0
    while not w.finished:
        if w.pending is not None:
            w.choose(pick_choice(policy, w.pending, prng, w))
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


STATION_STRATEGIES = ("hold", "leave_now", "listen_then_leave", "pay")


def run_station(strategy: str, seed: int, max_ticks: int = 700) -> Dict:
    """Start every strategy from the SAME state on station and compare only the exit.

    The full-patrol policies arrive on station in very different shape, which
    hides whether the exits themselves are balanced (DESIGN.md section 9, criterion 9).
    """
    w = DreadWorld(seed=seed)
    w._start_mission(4)
    w.tick_no = 100
    s = w.ship
    s.hull, s.food, s.water, s.fuel, s.scrubber = 0.7, 0.62, 0.6, 0.8, 0.5
    s.owed, s.moral_debt, s.co2 = 0.1, 0.1, 0.012
    for c in w.crew:
        c.fear, c.fatigue, c.guilt, c.trust = 0.25, 0.3, 0.1, 0.55
    w.deck.names_learned.update({1, 2})
    initial = len(w.crew)
    checked = False
    for _ in range(max_ticks):
        if w.finished:
            break
        if w.pending is not None:
            ev, keys = w.pending.event_id, {c.key for c in w.pending.choices}
            pick = lambda *prefs: next((k for k in prefs if k in keys), w.pending.choices[0].key)
            if ev == "station_council":
                if strategy == "leave_now":
                    key = pick("leave")
                elif strategy == "listen_then_leave":
                    if not checked:
                        checked = True
                        key = pick("check")
                    elif "peace_known" in s.flags or "notice_received" in s.flags or s.food < 0.25 or s.water < 0.25:
                        key = pick("leave")
                    else:
                        key = pick("hold_tight" if s.rations > 0.75 else "hold")
                else:
                    key = pick("hold")
            elif ev == "offering_proposal":
                key = pick("look_away" if strategy == "pay" else "forbid")
            elif ev == "further_notice":
                key = pick("obey")
            else:
                key = vigil_choice("crew_first", w, w.pending) if ev in VIGIL_EVENTS else w.pending.choices[0].key
            w.choose(key)
            continue
        if w.on_station and strategy == "leave_now" and not s.returning and s.fuel >= 0.25:
            w.log.append(w.leave_station())
        live = w.active_crew()
        if live and sum(c.fatigue for c in live) / len(live) > 0.6 and not s.stand_down:
            O.stand_down(w)
        if not s.surfaced and s.co2 > 0.03 and w.tick_no % 8 == 0:
            O.surface(w)
        elif s.surfaced and "checking" not in s.flags and (s.co2 < 0.012 or w.tick_no % 8 in (3, 4)):
            O.dive(w)
        w.tick()
    return {"strategy": strategy, "seed": seed, "ending": classify_ending(w, initial),
            "survivors": len(w.active_crew()), "initial": initial, "ticks": w.tick_no - 100}


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
