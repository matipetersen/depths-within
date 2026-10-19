#!/usr/bin/env python3
"""Test the fixed tileset rendering."""

import tcod
from ui.tileset import load_preferred_tileset

# Load tileset with the fix
tileset = load_preferred_tileset()
print(f"Tileset loaded: {tileset is not None}")

if not tileset:
    print("ERROR: Tileset failed to load!")
    exit(1)

# Create console
SCREEN_W, SCREEN_H = 60, 40
console = tcod.console.Console(SCREEN_W, SCREEN_H)

# Create context
with tcod.context.new_terminal(
    SCREEN_W, SCREEN_H,
    tileset=tileset,
    title="Tileset Test - Fixed",
    vsync=True
) as context:
    
    console.clear()
    
    # Draw a grid of tiles to visualize
    console.print(2, 1, "Tile Rendering Test", fg=(255, 255, 255))
    console.print(2, 2, "Press ESC to quit", fg=(180, 180, 180))
    console.print(2, 3, "─" * 40, fg=(140, 140, 140))
    
    # Draw ocean tiles (0-7)
    console.print(2, 5, "Ocean tiles (0-7):", fg=(180, 200, 220))
    for i in range(8):
        console.rgb[6 + i * 2, 6] = (ord(chr(i)), (255, 255, 255), (0, 0, 0))
    
    # Draw submarine tiles (8-15)
    console.print(2, 8, "Submarine angles (8-15):", fg=(180, 200, 220))
    for i in range(8):
        console.rgb[6 + i * 2, 9] = (ord(chr(8 + i)), (255, 255, 255), (0, 0, 0))
    
    # Draw ship tiles (24-29)
    console.print(2, 11, "Ships (24-29):", fg=(180, 200, 220))
    for i in range(6):
        console.rgb[6 + i * 2, 12] = (ord(chr(24 + i)), (255, 255, 255), (0, 0, 0))
    
    # Draw torpedo (30)
    console.print(2, 14, "Torpedo (30):", fg=(180, 200, 220))
    console.rgb[6, 15] = (ord(chr(30)), (255, 255, 255), (0, 0, 0))
    
    # Draw gauge tiles (36-47)
    console.print(2, 17, "Gauges (36-47):", fg=(180, 200, 220))
    for i in range(12):
        console.rgb[6 + i * 2, 18] = (ord(chr(36 + i)), (255, 255, 255), (0, 0, 0))
    
    print("\nCheck the window - you should see actual tile graphics!")
    print("If you see strange characters, the tileset mapping is still wrong.")
    
    context.present(console)
    
    # Wait for ESC
    running = True
    while running:
        for event in tcod.event.wait():
            if event.type == "QUIT":
                running = False
            elif event.type == "KEYDOWN":
                if event.sym == tcod.event.KeySym.ESCAPE:
                    running = False

print("Test complete!")
