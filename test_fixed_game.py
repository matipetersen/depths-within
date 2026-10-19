#!/usr/bin/env python3
"""Quick test of the fixed rendering."""

print("Testing fixed rendering system...")
print("\n1. Setup screen should show readable text")
print("2. Game map should center on submarine")
print("3. Only ONE submarine should be visible at center")
print("4. Map should scroll as submarine moves")
print("\nStarting game...\n")

from ui.setup_screen import quick_setup
from engine.game import Game

# Quick setup
faction, crew = quick_setup("Germany")
print(f"✓ Setup complete: {faction['name']}, {len(crew)} crew")

# Create game
game = Game(faction, crew)
print(f"✓ Game created")
print(f"✓ Submarine at world position: ({game.submarine.x}, {game.submarine.y})")

print("\nLaunching game window...")
print("The submarine should be centered on screen.")
print("Press Q to quit after checking.")
