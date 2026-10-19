#!/usr/bin/env python3
"""Simple test to verify tileset rendering works."""

import tcod
from ui.tileset import load_preferred_tileset
from ui.graphics_renderer import get_renderer

# Load tileset
tileset = load_preferred_tileset()
print(f"Tileset loaded: {tileset is not None}")

# Create console and context
SCREEN_W, SCREEN_H = 80, 50
console = tcod.console.Console(SCREEN_W, SCREEN_H, order="F")

with tcod.context.new_terminal(
    SCREEN_W, SCREEN_H,
    tileset=tileset,
    title="Depths Within - Tileset Test",
    vsync=True
) as context:
    
    # Get graphics renderer
    renderer = get_renderer()
    
    print("Drawing test tiles...")
    
    # Clear console
    console.clear()
    
    # Draw ocean background
    for y in range(20):
        for x in range(40):
            depth = 50 + (y * 20)
            tile_name = renderer.get_ocean_tile_for_depth(depth)
            renderer.render_tile_to_console(console, tile_name, x, y)
    
    # Draw submarine at center
    renderer.render_submarine(console, 20, 10, 0, 0)  # Surface, heading 0°
    
    # Draw some ships
    renderer.render_ship(console, 15, 5, 'merchant')
    renderer.render_ship(console, 25, 8, 'warship')
    renderer.render_ship(console, 30, 12, 'destroyer')
    
    # Draw torpedoes
    renderer.render_torpedo(console, 22, 10)
    renderer.render_torpedo(console, 24, 10)
    
    # Draw UI elements
    console.print(1, 22, "═══ TILESET TEST ═══", fg=(180, 200, 220))
    console.print(1, 23, "Press ESC or Q to quit", fg=(160, 170, 180))
    
    # Draw some gauges
    renderer.render_gauge(console, 1, 25, 'battery', 0.8)
    console.print(3, 25, "Battery 80%", fg=(200, 210, 220))
    
    renderer.render_gauge(console, 1, 26, 'horizontal', 0.6)
    console.print(3, 26, "Oxygen 60%", fg=(200, 210, 220))
    
    renderer.render_gauge(console, 1, 27, 'circular', 0.4)
    console.print(3, 27, "Hull 40%", fg=(200, 210, 220))
    
    # Draw crew status
    renderer.render_crew_icon(console, 1, 29, 'ok')
    console.print(3, 29, "Crew: OK", fg=(200, 210, 220))
    
    # Draw compartment status
    renderer.render_compartment(console, 1, 30, 'ok')
    console.print(3, 30, "Compartment: OK", fg=(200, 210, 220))
    
    print("Test tiles drawn. Check the SDL window!")
    print("If you see actual tiles (not colored blocks), it's working!")
    
    # Present and wait for input
    context.present(console)
    
    running = True
    while running:
        for event in tcod.event.wait():
            if event.type == "QUIT":
                running = False
            elif event.type == "KEYDOWN":
                if event.sym == tcod.event.KeySym.ESCAPE or event.sym == tcod.event.KeySym.q:
                    running = False

print("Test complete!")
