"""A playable patrol in the terminal: the UX prototype for the dread system.

    python -m dread.play                     # interactive
    python -m dread.play --seed 7
    python -m dread.play --auto crew_first   # watch a policy play, screen by screen

The prototype exists to check the interface principles in DESIGN.md section 12:
exact ledger, unreliable people, every order priced, no hidden number on screen.
"""
import argparse
import sys
from dataclasses import dataclass
from typing import Callable, List, Optional

from . import hud
from . import orders as O
from .endings import classify_ending
from .sim import PRIORITY, issue_orders, pick_choice
from .world import DreadWorld

WAIT_LIMIT = 12
HELP = """\
  enter   wait one hour           w   wait until something happens (or 12 hours)
  1..N    give that order         o   show the orders again
  l       the whole log           q   quit
  Decisions stop the clock: answer them with their number.
  Nothing is explained to you. Watch the men, trust the ledger."""


@dataclass
class Item:
    label: str
    hint: str
    run: Callable
    needs_crew: bool = False


def _game_depth(game, meters: int, text: str) -> str:
    game.target_depth = meters
    return text


def available_orders(w: DreadWorld, game=None) -> List[Item]:
    """``game``: when the HUD runs inside the real game, depth is the game's, not the story's."""
    s = w.ship
    items: List[Item] = []
    if s.sonar_on:
        items.append(Item("Silence the sonar", "the headsets go quiet; so does the warning", lambda: O.silence_sonar(w)))
    else:
        items.append(Item("Switch the sonar back on", "you will hear what they heard", lambda: O.restore_sonar(w)))
    if s.rest_cancelled:
        items.append(Item("Resume normal watches", "", lambda: O.grant_rest(w)))
    else:
        items.append(Item("Cancel rest for all hands", "faster now; slower later", lambda: O.cancel_rest(w)))
    if not s.stand_down:
        items.append(Item("Stand down: all hands but a skeleton watch sleep", "a broken crew recovers; the boat sleeps unwatched",
                          lambda: O.stand_down(w)))
    items.append(Item("Mess together: music, cards, a hot meal", "costs hours of the patrol", lambda: O.hold_ritual(w)))
    items.append(Item("Speak to the crew over the intercom", "works in proportion to what they still believe", lambda: O.address_crew(w)))
    items.append(Item("Break out fresh absorbent", f"{s.scrubber * 100:.0f}% left", lambda: O.scrub_air(w)))
    if s.surfaced:
        items.append(Item("Dive", "", (lambda: _game_depth(game, 60, "Diving.")) if game else (lambda: O.dive(w))))
    else:
        items.append(Item("Surface for air", "air, and the sky can see you",
                          (lambda: _game_depth(game, 0, "Blowing ballast. The boat climbs.")) if game
                          else (lambda: O.surface(w))))
    if game is None:       # in the real game, silent running and pings are the X and P keys
        items.append(Item("Silent running" if not s.silent_running else "Resume normal running",
                          "quiet in a fight; slow in a race", lambda: O.silent_running(w, not s.silent_running)))
        items.append(Item("One active ping", "information; and a sound the water carries", lambda: O.active_ping(w)))
    if w.run is not None and "verified" not in w.run.phase_fired:
        items.append(Item("Ask headquarters to confirm the orders", "an answer is not the same as a source",
                          lambda: O.verify_orders(w)))
    if w.on_station:
        nxt = {1.0: 0.75, 0.75: 0.5, 0.5: 1.0}[round(s.rations * 4) / 4]
        items.append(Item(f"Set rations to {nxt * 100:.0f}%", "stores last longer; men notice who eats",
                          lambda: _set_rations(w, nxt)))
        items.append(Item("Surface and listen for the world", "exposed; and you may hear something", lambda: w.check_world()))
        items.append(Item("Set course for base", "diesel for the passage; the order has not been revoked",
                          lambda: w.leave_station()))
    items.append(Item("Confine a man", "cuts a rumor; he will remember", lambda: None, needs_crew=True))
    if any(c.isolated for c in w.active_crew()):
        items.append(Item("Release a man from confinement", "", lambda: None, needs_crew=True))
    items.append(Item("Order a man into the flooded compartment", "the job gets done", lambda: None, needs_crew=True))
    return items


def _set_rations(w, level):
    if level < w.ship.rations:                 # the men notice who eats less
        for c in w.active_crew():
            c.trust = max(0.0, c.trust - 0.02)
    w.ship.rations = level
    return f"Rations are now {level * 100:.0f}%."


class Session:
    """Everything the UI does, as text in and text out, so it can be tested."""

    def __init__(self, seed: int = 0, policy: Optional[str] = None, world: Optional[DreadWorld] = None,
                 advance: Optional[Callable[[], None]] = None, answer: Optional[Callable[[int], None]] = None,
                 game=None, initial: Optional[int] = None):
        """Standalone by default. Inside the real game the world, the clock and the
        decision modal belong to the game, so it passes them in."""
        self.w = world if world is not None else DreadWorld(seed=seed)
        self.initial = initial if initial is not None else len(self.w.crew)
        self.policy = policy
        self.over = False
        self.awaiting = None       # an order that needs a man picked
        self.ending: Optional[str] = None
        self.notice = ""           # the last thing an order or an error said
        self._advance_fn = advance or self.w.tick
        self._answer_fn = answer
        self.game = game

    def orders(self) -> List[Item]:
        return available_orders(self.w, self.game)

    # -- rendering ----------------------------------------------------------
    def view(self, notice: str = "") -> str:
        w = self.w
        if self.over:
            return hud.epilogue_screen(w, self.ending)
        if self.awaiting is not None:
            names = [f"  {i}. {c.name} ({c.role})" for i, c in enumerate(self._pickable(), 1)]
            return "\n".join(["Which man?"] + names)
        pending = w.pending
        items = None if pending else self.orders()
        self.notice = notice or self.notice
        return hud.screen(w, pending, items, notice)

    def _pickable(self):
        label = self.awaiting.label
        pool = self.w.active_crew()
        if label.startswith("Release"):
            pool = [c for c in pool if c.isolated]
        return pool

    # -- one input ----------------------------------------------------------
    def handle(self, cmd: str) -> str:
        cmd = cmd.strip().lower()
        self.notice = ""
        w = self.w
        if self.over:
            return self.view()
        if self.awaiting is not None:
            return self._pick_man(cmd)
        if w.pending is not None:
            return self._answer(cmd)
        if cmd == "h":
            return HELP
        if cmd == "l":
            return "\n".join(w.log)
        if cmd == "o":
            return self.view()
        if cmd in ("", "."):
            return self._advance(1)
        if cmd == "w":
            return self._advance(WAIT_LIMIT, stop_on_news=True)
        if cmd.isdigit():
            return self._order(int(cmd))
        return self.view("I don't understand. (h for help)")

    def _answer(self, cmd: str) -> str:
        p = self.w.pending
        if cmd.isdigit() and 1 <= int(cmd) <= len(p.choices):
            if self._answer_fn is not None:
                self._answer_fn(int(cmd))
            else:
                self.w.choose(p.choices[int(cmd) - 1].key)
            return self._after(self.view())
        return self.view(f"A decision is waiting. Choose 1-{len(p.choices)}.")

    def _order(self, n: int) -> str:
        items = self.orders()
        if not 1 <= n <= len(items):
            return self.view(f"There is no order {n}.")
        item = items[n - 1]
        if item.needs_crew:
            self.awaiting = item
            return self.view()
        result = item.run()
        return self.view(result if isinstance(result, str) else "")

    def _pick_man(self, cmd: str) -> str:
        item, pool = self.awaiting, self._pickable()
        self.awaiting = None
        if not (cmd.isdigit() and 1 <= int(cmd) <= len(pool)):
            return self.view("Nobody was named.")
        c = pool[int(cmd) - 1]
        fn = {"Confine": O.isolate, "Release": O.release, "Order": O.force_compartment}[item.label.split()[0]]
        return self.view(fn(self.w, c.id))

    def _advance(self, hours: int, stop_on_news: bool = False) -> str:
        w = self.w
        seen = len(w.log)
        for _ in range(hours):
            if w.finished or w.pending is not None:
                break
            self._advance_fn()
            if stop_on_news and (w.pending is not None or len(w.log) > seen):
                break
        return self._after(self.view())

    def _after(self, text: str) -> str:
        if self.w.finished and not self.over:
            self.over = True
            self.ending = classify_ending(self.w, self.initial)
            return self.view()
        return text


def run_auto(policy: str, seed: int, every: int = 12, max_screens: int = 400) -> str:
    """Let a policy captain play and print what the captain would have seen."""
    s = Session(seed, policy)
    w = s.w
    out = [s.view()]
    prng = None
    last = -every
    while not w.finished and len(out) < max_screens:
        if w.pending is not None:
            out.append(s.view())
            key = pick_choice(policy, w.pending, prng, w)
            n = [c.key for c in w.pending.choices].index(key) + 1
            out.append(f"\n> [{n}] {w.pending.choices[n - 1].text}\n")
            s.handle(str(n))
            continue
        issue_orders(policy, w, prng)
        s._advance(1)
        if w.tick_no - last >= every:
            out.append(s.view())
            last = w.tick_no
    s._after("")
    out.append(hud.epilogue_screen(w, s.ending or classify_ending(w, s.initial)))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--auto", choices=sorted(PRIORITY), help="watch a policy play instead")
    ap.add_argument("--every", type=int, default=12, help="with --auto: hours between screens")
    args = ap.parse_args(argv)
    if args.auto:
        print(run_auto(args.auto, args.seed, args.every))
        return
    s = Session(args.seed)
    print(s.view())
    while not s.over:
        try:
            cmd = input("\n> ")
        except EOFError:
            break
        if cmd.strip().lower() == "q":
            break
        print()
        print(s.handle(cmd))


if __name__ == "__main__":
    main()
