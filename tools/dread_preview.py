"""Render the tcod console to PNG files without opening a window.

    python tools/dread_preview.py OUT_DIR [--seed N]

Plays a scripted patrol through the real Game, PanelManager and DreadUI and saves
what the window would draw: the map, the captain's bridge, a decision, the bridge
on station, and the ending. Useful in CI, over SSH, or in a cloud session.
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tcod                                   # noqa: E402
from PIL import Image, ImageDraw, ImageFont   # noqa: E402
from tcod.event import KeySym as K            # noqa: E402

from dread.sim import issue_orders, pick_choice   # noqa: E402
from engine.game import Game                      # noqa: E402
from ui.panels.panel_manager import PanelManager  # noqa: E402

FONTS = ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
         "/System/Library/Fonts/Menlo.ttc")
CELL_W, CELL_H, SIZE = 10, 19, 16


def console_to_png(console, path):
    font = next((ImageFont.truetype(f, SIZE) for f in FONTS if os.path.exists(f)), ImageFont.load_default())
    img = Image.new("RGB", (console.width * CELL_W, console.height * CELL_H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    rgb = console.rgb
    for y in range(console.height):
        for x in range(console.width):
            cell = rgb[x, y]
            bg, fg, ch = tuple(int(v) for v in cell["bg"][:3]), tuple(int(v) for v in cell["fg"][:3]), int(cell["ch"])
            if bg != (0, 0, 0):
                d.rectangle([x * CELL_W, y * CELL_H, (x + 1) * CELL_W - 1, (y + 1) * CELL_H - 1], fill=bg)
            if ch > 32:
                char = chr(ch) if ch < 0xE000 else "#"
                d.text((x * CELL_W, y * CELL_H), char, font=font, fill=fg)
    img.save(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out_dir")
    ap.add_argument("--seed", type=int, default=3)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    random.seed(args.seed)
    game, pm = Game(), PanelManager()
    ui, saved = game.dread_ui, []

    def snap(name):
        console = tcod.console.Console(160, 60, order="F")
        pm.render(console, game)
        path = os.path.join(args.out_dir, name)
        console_to_png(console, path)
        saved.append(path)

    def world():
        return game.horror_manager.dread.world

    def play_until(cond, limit=3000):
        for _ in range(limit):
            if cond() or game.dread_over:
                return
            if game.decision_manager.pending_decision:
                w = world()
                keys = [c.key for c in w.pending.choices]
                game.answer_decision(keys.index(pick_choice("crew_first", w.pending, None, w)) + 1)
            else:
                issue_orders("crew_first", world())
                game._tick()

    snap("1_map.png")
    ui.handle_key(game, K.TAB)
    snap("2_bridge_start.png")
    while not game.decision_manager.pending_decision and not game.dread_over:
        game.wait_for_news()
    snap("3_decision.png")
    play_until(lambda: world().on_station and world().vigil_ticks >= 45 and not game.decision_manager.pending_decision)
    snap("4_bridge_on_station.png")
    play_until(lambda: False)
    snap("5_ending.png")
    ui.scroll = 22
    snap("6_ending_reports.png")
    print("\n".join(saved))


if __name__ == "__main__":
    main()
