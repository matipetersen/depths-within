
# Copilot Instructions: WWII Submarine Roguelike (Python + libtcod)

## Project Context
- Python project using [libtcod](https://python-tcod.readthedocs.io/) for rendering and input.
- Modular architecture: `engine/`, `ui/`, `world/`, `submarine/`, `data/`, `assets/`.
- Tactical (tile-based) and strategic (region-based) gameplay are separated by module.

## Key Patterns & Conventions
- **Game loop**: `engine/game.py` (entry: `main.py`).
- **State management**: `engine/state_manager.py`.
- **Event system**: `engine/events.py` (all logs/events timestamped with in-game time).
- **UI panels**: Modular, in `ui/panels/` (main, compartment, log, lore). Use stubs for new panels.
- **Rendering**: Use libtcod in `ui/renderer.py`. Main display = sonar, periscope, or map.
- **Data-driven**: Ships, submarines, torpedoes, crew, regions, crew stories, historical encounters, and lore snippets in `data/*.json`.
- **Compartment & crew simulation**: `submarine/compartments.py`, `submarine/crew.py`.
- **Sonar/periscope logic**: `submarine/sonar.py`, `submarine/periscope.py`.
- **Strategic world & lore**: `world/regions.py`, `world/encounters.py`, `world/weather.py`, `world/navigation.py`, `world/lore.py`.

## Developer Workflow
1. Install dependencies: `pip install -r requirements.txt` (add `libtcod`)
2. Run: `python main.py`
3. Add new features by extending/creating modules in the appropriate folder.
4. Add new data (ships, subs, etc.) by editing JSON files in `data/`.
5. UI/UX: Use desaturated blues/greens/grays for color palette. Avoid classic ASCII colors.

## Examples
- To add a new compartment: extend `Compartment` in `submarine/compartments.py` and update data/logic as needed.
- To add a new region: add to `data/regions.json` and update `world/regions.py` if logic is needed.
- To add a new log type: extend `LogPanel` in `ui/panels/log_panel.py` and event system.
- To add new lore or historical content: update `data/crew_stories.json`, `data/historical_encounters.json`, or `data/lore_snippets.json` and use `world/lore.py` for integration.

## Integration Points
- All rendering and input via libtcod (see `ui/renderer.py`, `ui/controls.py`).
- Data files are the source of truth for historical/gameplay content.
- Logs/events are routed through the event system for UI display.

## Testing & Debugging
- Use modular design for easy unit testing (add tests as needed).
- Run the game in debug mode by modifying `main.py` or adding debug panels.

---
Keep instructions concise and focused on THIS project’s architecture and conventions. Update this file as the codebase evolves.
