"""The captain's bridge inside the tcod window (DESIGN.md section 12).

Three things are drawn over the existing tactical screen, in this order of priority:

  * the ENDING screen (the patrol is over: epilogue and the two reports),
  * the BRIDGE (TAB): exact ledger, the men as they say they are, the sonar room,
    the log and the orders menu,
  * the DECISION modal, on top of whatever is showing. The game used to have no way
    to answer a decision in the graphical mode at all (1-4 are speed keys).

All the text comes from ``dread.hud``; this file only places it and routes keys.
"""
import textwrap
from typing import List, Optional

try:
    import tcod
    from tcod.event import KeySym as K
except Exception:          # the game also runs without tcod
    tcod = None
    K = None

from dread import hud
from dread.play import Session

# desaturated, per .github/copilot-instructions.md: navy, steel, amber only for the ledger's alarms
BG = (8, 12, 20)
PANEL = (12, 18, 30)
FG = (190, 200, 212)
DIM = (105, 120, 138)
STEEL = (140, 165, 190)
AMBER = (232, 172, 62)
ALARM = (240, 120, 70)
GREEN = (120, 190, 150)

LEFT_W = 80
MAX_CMD = 2


def _digit(sym) -> Optional[int]:
    if K is None:
        return None
    pairs = {K.N0: 0, K.N1: 1, K.N2: 2, K.N3: 3, K.N4: 4, K.N5: 5, K.N6: 6, K.N7: 7, K.N8: 8, K.N9: 9,
             K.KP_0: 0, K.KP_1: 1, K.KP_2: 2, K.KP_3: 3, K.KP_4: 4, K.KP_5: 5, K.KP_6: 6, K.KP_7: 7,
             K.KP_8: 8, K.KP_9: 9}
    return pairs.get(sym)


def _line_color(line: str):
    """Colour carries no meaning on its own: every alarm also says so in words."""
    t = line.strip()
    if not t:
        return FG
    if t.startswith(("LEDGER", "THE MEN", "SONAR", "LOG", "ORDERS", "====", "----")):
        return STEEL
    if "[" in line and "]" in line and "%" in line:               # a ledger row with bars
        for chunk in line.split("[")[1:]:
            bar = chunk.split("]")[0]
            if bar.count("#") <= 2:
                return AMBER
        return FG
    if "foul" in t or "dangerous" in t:
        return ALARM
    if "missing" in t or "nothing you can see" in t or "has nothing to report" in t:
        return DIM
    if t.startswith(">") or t.startswith("["):
        return FG
    return FG


class DreadUI:
    def __init__(self):
        self.open = False          # the bridge view
        self.buf = ""              # the command being typed
        self.scroll = 0            # epilogue scroll
        self._session: Optional[Session] = None

    # ------------------------------------------------------------------ plumbing
    @staticmethod
    def bridge(game):
        hm = getattr(game, "horror_manager", None)
        return getattr(hm, "dread", None) if hm else None

    def available(self, game) -> bool:
        return self.bridge(game) is not None

    def session(self, game) -> Session:
        b = self.bridge(game)
        if self._session is None or self._session.w is not b.world:
            self._session = Session(world=b.world, advance=game._tick, answer=game.answer_decision,
                                    game=game, initial=b.initial)
        return self._session

    # ------------------------------------------------------------------ keys
    def handle_key(self, game, sym) -> bool:
        """True if the key was used here and the game must not see it."""
        if K is None or not self.available(game):
            return False
        quitting = sym in (K.Q,) or (sym == K.ESCAPE and not self.open)
        if getattr(game, "dread_over", False):
            if sym in (K.UP, K.PAGEUP, K.DOWN, K.PAGEDOWN):
                step = 1 if sym in (K.UP, K.DOWN) else 10
                self.scroll = max(0, self.scroll + (step if sym in (K.DOWN, K.PAGEDOWN) else -step))
                return True
            return False if quitting else True          # any other key does nothing; Q leaves
        dm = getattr(game, "decision_manager", None)
        if dm is not None and dm.pending_decision is not None:
            n = _digit(sym)
            if n is not None and 1 <= n <= len(dm.pending_decision.options):
                game.answer_decision(n)
                return True
            return False if quitting else True          # the clock is stopped: nothing else counts
        if sym == K.TAB:
            self.open = not self.open
            self.buf = ""
            return True
        if not self.open:
            return False
        if quitting or sym == K.Q:
            return False
        if sym == K.ESCAPE:
            self.open = False
            return True
        n = _digit(sym)
        if n is not None:
            if len(self.buf) < MAX_CMD:
                self.buf += str(n)
            return True
        if sym == K.BACKSPACE:
            self.buf = self.buf[:-1]
            return True
        s = self.session(game)
        if sym in (K.RETURN, K.KP_ENTER, K.SPACE):
            cmd, self.buf = self.buf, ""
            s.handle(cmd)
            return True
        if sym == K.W and not self.buf:
            s.handle("w")
            return True
        return True

    # ------------------------------------------------------------------ drawing
    def render(self, console, game):
        if not self.available(game):
            return
        if getattr(game, "dread_over", False):
            self._draw_ending(console, game)
        elif self.open:
            self._draw_bridge(console, game)
        dm = getattr(game, "decision_manager", None)
        if dm is not None and dm.pending_decision is not None:
            self._draw_modal(console, hud.decision_from(dm.pending_decision))

    def _fill(self, console, color=BG):
        console.draw_rect(0, 0, console.width, console.height, ch=ord(" "), bg=color)

    @staticmethod
    def _flat(lines: List[str]) -> List[str]:
        """The HUD returns paragraphs as single items that contain line breaks."""
        return [sub for line in lines for sub in line.split("\n")]

    @staticmethod
    def _wrap(lines: List[str], width: int) -> List[str]:
        out: List[str] = []
        for line in DreadUI._flat(lines):
            if len(line) <= width:
                out.append(line)
                continue
            indent = " " * (len(line) - len(line.lstrip()) + 4)
            out += textwrap.wrap(line, width, subsequent_indent=indent, drop_whitespace=False) or [""]
        return out

    def _text(self, console, x, y, lines: List[str], width: Optional[int] = None):
        width = width or (console.width - x - 1)
        for i, line in enumerate(self._wrap(lines, width)):
            if 0 <= y + i < console.height - 4:          # keep the prompt rows clear
                console.print(x, y + i, line, fg=_line_color(line), bg=BG)

    def _draw_bridge(self, console, game):
        s = self.session(game)
        w = s.w
        self._fill(console)
        left = hud.header(w) + hud.ledger(w) + [""] + hud.crew(w) + [""] + hud.sonar(w)
        self._text(console, 1, 1, left)
        right = hud.log_tail(w, 16) + [""]
        if s.awaiting is not None:
            right += ["WHICH MAN?"] + [f"  {i}. {c.name} ({c.role})" for i, c in enumerate(s._pickable(), 1)]
        else:
            right += hud.orders_menu(s.orders())
        self._text(console, LEFT_W + 3, 1, right, console.width - LEFT_W - 5)
        if w.run is not None and w.ship.surfaced:
            console.print(1, console.height - 5, "SURFACED: the patrol clock does not run on the surface. Dive (order or - key).",
                          fg=AMBER, bg=BG)
        y = console.height - 3
        console.print(1, y - 1, s.notice[: console.width - 2] if s.notice else "", fg=GREEN, bg=BG)
        console.print(1, y, f"> {self.buf}_", fg=FG, bg=BG)
        console.print(1, y + 1,
                      "number + ENTER: give the order   ENTER/SPACE: wait an hour   W: wait for news   "
                      "BACKSPACE: erase   TAB/ESC: back to the map", fg=DIM, bg=BG)

    def _draw_modal(self, console, lines: List[str]):
        lines = self._flat(lines)
        w = min(console.width - 4, hud.WIDTH + 2)
        h = len(lines) + 2
        x = (console.width - w) // 2
        y = max(1, (console.height - h) // 2)
        console.draw_rect(x, y, w, h, ch=ord(" "), bg=PANEL)
        for i, line in enumerate(lines):
            col = AMBER if line.startswith(("!!!", "CAPTAIN")) else FG
            console.print(x + 1, y + 1 + i, line[: w - 2], fg=col, bg=PANEL)
        console.print(x + 1, y + h - 1, " answer with the number ", fg=DIM, bg=PANEL)

    def _draw_ending(self, console, game):
        self._fill(console)
        b = self.bridge(game)
        lines = hud.epilogue_screen(b.world, game.dread_ending).split("\n")
        room = console.height - 3
        self.scroll = max(0, min(self.scroll, max(0, len(lines) - room)))
        for i, line in enumerate(lines[self.scroll: self.scroll + room]):
            console.print(2, 1 + i, line[: console.width - 3], fg=FG if "|" not in line else _line_color(line), bg=BG)
        console.print(2, console.height - 2, "UP/DOWN/PAGE: read   Q: leave", fg=DIM, bg=BG)
