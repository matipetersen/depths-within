"""TCOD visual demo: sonar circle, submarine, and contacts.

Run with: `python scripts/visual_demo.py`

This script is a small, self-contained demo that uses python-tcod
(`tcod`) if installed. It opens a window, draws a sonar-style circle
in the center, and displays random contacts provided by
`submarine.submarine.Submarine.sonar.detect()`.
"""
import time
try:
    import tcod
    import tcod.event
except Exception as e:
    print("tcod is required for the visual demo. Install with: pip install tcod")
    raise

from submarine.submarine import Submarine
from ui.tileset import load_preferred_tileset
import math


SCREEN_W = 80
SCREEN_H = 50


def draw_sonar(console, cx, cy, radius, contacts):
    # draw circle
    for y in range(-radius, radius + 1):
        for x in range(-radius, radius + 1):
            if x * x + y * y <= radius * radius:
                console.print(cx + x, cy + y, " ", fg=(50, 70, 90), bg=(20, 30, 40))

    # draw submarine at center
    console.print(cx, cy, "S", fg=(255, 220, 80))

    # draw contacts
    for c in contacts:
        bearing = float(c.get('bearing', 0))
        r = c.get('range', 3000)
        # map range 0..6000 to 0..radius
        rn = max(0.0, min(1.0, r / 6000.0))
        dist = int(rn * radius)
        angle = math.radians((90 - bearing) % 360)
        x = cx + int(round(math.cos(angle) * dist))
        y = cy + int(round(math.sin(angle) * dist))
        console.print(x, y, "X", fg=(200, 80, 80))


def main():
    sub = Submarine.from_json_default()

    tileset = load_preferred_tileset()
    if tileset is None:
        try:
            if hasattr(tcod.tileset, 'get_default'):
                tileset = tcod.tileset.get_default()
            elif hasattr(tcod.tileset, 'load_default'):
                tileset = tcod.tileset.load_default()
            else:
                tileset = None
        except Exception:
            tileset = None
    # Only pass a tileset if one was successfully loaded; otherwise let tcod use its default internal font
    if tileset is not None:
        ctx_kw = dict(tileset=tileset, title="WWII Submarine Roguelike - Sonar Demo", vsync=True)
    else:
        ctx_kw = dict(title="WWII Submarine Roguelike - Sonar Demo", vsync=True)

    with tcod.context.new_terminal(
        SCREEN_W,
        SCREEN_H,
        **ctx_kw,
    ) as context:
        console = tcod.console.Console(SCREEN_W, SCREEN_H, order="F")
        last = time.time()
        running = True
        show_compartments = False
        while running:
            now = time.time()
            # update contacts at ~4 Hz
            if now - last > 0.25:
                contacts = sub.sonar.detect()
                last = now

            console.clear()
            # draw background
            console.fill(bg=(10, 16, 22))

            cx = SCREEN_W // 2
            cy = SCREEN_H // 2
            radius = min(SCREEN_W, SCREEN_H) // 4

            draw_sonar(console, cx, cy, radius, contacts)

            # HUD
            console.print(1, 1, f"Sub: {sub.id}  Depth: {sub.systems.depth}m")
            console.print(1, 2, "Press Q or ESC to quit.  C toggles compartments")
            if show_compartments:
                # show a tiny compartments/status panel
                status = sub.status()
                lines = str(status).splitlines()
                for i, line in enumerate(lines[:6]):
                    console.print(2, 4 + i, line[:60])

            context.present(console)

            for event in tcod.event.wait(0):
                if event.type == "KEYDOWN":
                    key = event.sym
                    if key in (tcod.event.K_q, tcod.event.K_ESCAPE):
                        running = False
                    elif key == tcod.event.K_c:
                        show_compartments = not show_compartments
                elif event.type == "QUIT":
                    running = False


if __name__ == "__main__":
    main()
