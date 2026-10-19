#!/usr/bin/env python3
"""
WWII Submarine Roguelike - Playable Console Demo

This is the main entry point for the game in fallback console mode.
It starts the main game loop with a fully playable ASCII GUI.

Run with:
    python main_play.py

In-game commands:
    sonar           - Detect nearby contacts
    fire/torpedo    - Fire at first contact
    dive <depth>    - Dive to a depth (meters)
    surface         - Return to surface
    aim <x> <y>     - Fire torpedo at coordinates
    aimi            - Interactive aim mode
    status          - Show submarine status
    compartments    - Show compartment damage/flooding
    events          - List pending events
    resolve_event   - Resolve a deferred compartment event
    defer_events    - Toggle deferring event resolution
    help            - Show all commands
    q/quit          - Exit game

Tips:
    - Use 'sonar' to detect enemy contacts
    - 'fire' will fire at the first contact detected
    - Keep an eye on battery and O2 levels
    - Dive to avoid attacks, but watch for torpedo impacts
    - Manage compartment flooding with 'events' and 'resolve_event'
"""

import sys
import os

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from engine.game import Game


def main():
    print(__doc__)
    print("\nStarting WWII Submarine Roguelike...")
    game = Game()
    game.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
