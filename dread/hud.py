"""What the captain sees (DESIGN.md section 12).

Pure functions: they take a DreadWorld and return text. Nothing here may touch
the world's dice, and nothing here may print a hidden number. Two rules decide
what goes on the screen:

  * The ledger is honest. Hull, stores, air and diesel are shown exactly.
  * The people are not. Each person is shown as what they *say* and what can be
    *seen* of them. Fear, guilt, trust, attention, moral debt and the doubt in
    the crew's mind about the orders never appear.
"""
import random
import re
import textwrap
from typing import Dict, List

WIDTH = 78
ORDERS_NOTE = "Orders are not free. Most of what they cost, you will learn later."


def bar(value: float, width: int = 10) -> str:
    n = max(0, min(width, int(round(value * width))))
    return "#" * n + "." * (width - n)


def _hour(w) -> int:
    return (6 + w.tick_no) % 24


def clock_lines(w) -> List[str]:
    day = w.tick_no // 24 + 1
    hour = _hour(w)
    lines = [f"Day {day}  ·  chronometer {hour:02d}:00"]
    if "clock_drift" in w.ship.flags:
        lines[0] += f"  ·  control-room clock {hour:02d}:00 less eleven minutes"
    if w.on_station and w.vigil_ticks >= 24:
        # On station nobody agrees on the date. The ledger is exact; the calendar is not.
        lines.append(f"Day by the log: {day}.  Day by the chronometer: {day + w.vigil_ticks // 24}.  "
                     "The cook says it is later.")
    return lines


def header(w) -> List[str]:
    out = ["=" * WIDTH]
    if w.run is not None:
        m = w.run.mission
        out.append(f"ORDERS: {m.title}")
        out.append(textwrap.fill(f"Received: {m.channel} {m.signed}".strip(), WIDTH, subsequent_indent="  "))
        out.append(step_line(w))
    out += clock_lines(w)
    out.append("=" * WIDTH)
    return out


def step_line(w) -> str:
    """Where the mission stands, in the captain's own terms: steps ordered, not a gauge."""
    run, acts = w.run, w.run.mission.acts
    if not acts:
        return "Station: nothing is asked of you but to stay."
    if run.acts_done >= len(acts):
        return "Every step ordered. What remains is not up to the sea."
    a = acts[run.acts_done]
    state = f"under way, {max(1, int(-(-run.work_left // 1)))} h more" if run.working is not None else "waiting for your order"
    return f"Step {run.acts_done + 1} of {len(acts)}: {a.label} ({state})"


def ledger(w) -> List[str]:
    s = w.ship
    live = len(w.active_crew())
    share = live / 12
    food_day = 0.0036 * share * s.rations * 24 * 100
    water_day = 0.0042 * share * s.rations * 24 * 100
    air = ("clear" if s.co2 < 0.01 else "stale" if s.co2 < 0.02 else "foul" if s.co2 < 0.035 else "dangerous")
    return [
        "LEDGER (exact)",
        f"  Hull      [{bar(s.hull)}] {s.hull * 100:3.0f}%      Diesel    [{bar(s.fuel)}] {s.fuel * 100:3.0f}%",
        f"  Food      [{bar(s.food)}] {s.food * 100:3.0f}%  (-{food_day:.0f}%/day)    Rations   {s.rations * 100:.0f}%",
        f"  Water     [{bar(s.water)}] {s.water * 100:3.0f}%  (-{water_day:.0f}%/day)    Absorbent [{bar(s.scrubber)}] {s.scrubber * 100:3.0f}%",
        f"  Air       CO2 {s.co2 * 100:.1f}% ({air})    Men aboard: {live}",
    ]


_SAYS = ((0.25, "says he is fine"), (0.45, "says he is tired"), (0.65, "says it has been hard"),
         (1.01, "says nothing good"))


def _says(x: float) -> str:
    return next(label for cut, label in _SAYS if x < cut)


def crew(w) -> List[str]:
    """Reported, not real. The gap between a man's words and his symptoms is the game."""
    rows = {r["name"]: r for r in w.report()}
    out = ["THE MEN (what they say, what you can see)"]
    for c in w.crew:
        if not c.alive:
            continue
        if c.missing:
            out.append(f"  {c.name:<8} {c.role:<8} —  missing")
            continue
        r = rows[c.name]
        tag = "  [confined]" if c.isolated else ""
        seen = ("; ".join(r["symptoms"])) if r["symptoms"] else "nothing you can see"
        out.append(textwrap.fill(f"  {c.name:<8} {c.role:<8} {_says(r['says'])}.  Seen: {seen}.{tag}",
                                 WIDTH, subsequent_indent=" " * 11))
    return out


def sonar(w) -> List[str]:
    """The captain hears only what the sonar room chooses to tell him."""
    s = w.ship
    state = "ON" if s.sonar_on else "OFF (the headsets are silent)"
    look = random.Random(w.tick_no * 104729 + 5)
    reports = []
    for p in w.deck.phantoms:
        for cid in sorted(p.audible_to):
            c = w.crew_by_id(cid)
            if c is None or not c.active:
                continue
            candor = max(0.0, min(1.0, c.candor * c.trust * (0.6 + 0.4 * s.cohesion)))
            if look.random() < candor:
                reports.append(f'  {c.name} reports: "{p.text}"')
            elif len(p.audible_to) >= 2:
                reports.append(f"  The sonar room has gone quiet around the headphones.")
            break
    out = [f"SONAR: {state}"]
    out += reports[:3] if s.sonar_on else []
    if s.sonar_on and not reports:
        out.append("  The sonar room has nothing to report.")
    return out


def log_tail(w, n: int = 8) -> List[str]:
    lines = [l for l in w.log if l.strip()]
    out = ["LOG"]
    for l in lines[-n:]:
        out.append(textwrap.fill(l, WIDTH, subsequent_indent="      "))
    return out


def orders_menu(items) -> List[str]:
    out = ["ORDERS   (enter = wait an hour · w = wait for something · h = help)"]
    for i, it in enumerate(items, 1):
        tail = f"  — not now: {it.why}" if it.why else (f"  — {it.hint}" if it.hint else "")
        out.append(f"  {i:>2}. {it.label}{tail}")
    out.append("  " + ORDERS_NOTE)
    return out


def _decision_lines(title: str, text: str, options) -> List[str]:
    out = ["!" * WIDTH, f"CAPTAIN: {title}", textwrap.fill(text, WIDTH)]
    for i, (label, cost) in enumerate(options, 1):
        out.append(textwrap.fill(f"  {i}. {label}", WIDTH, subsequent_indent="     "))
        if cost:
            out.append(textwrap.fill(f"       ({cost})", WIDTH, subsequent_indent="        "))
    out.append("!" * WIDTH)
    return out


def decision(pending) -> List[str]:
    title = re.sub(r"^m\d_", "", pending.event_id).replace("_", " ").upper()
    return _decision_lines(title, pending.text, [(c.text, c.cost) for c in pending.choices])


def decision_from(d) -> List[str]:
    """The same, from the game's ``engine.decisions.Decision`` (dread or legacy)."""
    if getattr(d, "source", "") == "dread":
        title = re.sub(r"^m\d_", "", d.id).replace("_", " ").upper()
    else:
        title = d.title.upper()
    return _decision_lines(title, d.description, [(o.text, o.tooltip) for o in d.options])


def screen(w, pending=None, items=None, notice: str = "") -> str:
    parts: List[str] = header(w) + ledger(w) + [""] + crew(w) + [""] + sonar(w) + [""] + log_tail(w)
    if notice:
        parts += ["", f"> {notice}"]
    parts.append("")
    if pending is not None:
        parts += decision(pending)
    elif items is not None:
        parts += orders_menu(items)
    return "\n".join(parts)


def side_by_side(left: List[str], right: List[str], width: int = WIDTH) -> List[str]:
    half = (width - 3) // 2
    out = []
    for a, b in zip(left, right):
        la = textwrap.wrap(a, half) or [""]
        lb = textwrap.wrap(b, half) or [""]
        for i in range(max(len(la), len(lb))):
            out.append(f"{(la[i] if i < len(la) else ''):<{half}} | {(lb[i] if i < len(lb) else '')}")
        out.append("")
    return out


def epilogue_screen(w, ending: str) -> str:
    from .endings import debrief_documents, epilogue
    docs = debrief_documents(w)
    out = ["=" * WIDTH, f"END: {ending.replace('_', ' ').upper()}", "=" * WIDTH]
    paragraph: List[str] = []
    for line in epilogue(ending) + [""]:
        if line:
            paragraph.append(line)
        elif paragraph:
            out += [textwrap.fill(" ".join(paragraph), WIDTH), ""]
            paragraph = []
    out += ["", "Two accounts of the same patrol. Nobody has been asked to reconcile them.", ""]
    out += side_by_side(docs["official"], docs["log"])
    return "\n".join(out)
