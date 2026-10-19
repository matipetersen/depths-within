# WWII Submarine Roguelike (Python + libtcod)

## Overview
A modern-feeling roguelike submarine simulator set in World War II, blending tactical stealth, sonar-based detection, crew management, environmental hazards, and historical accuracy. Built with Python and libtcod.

> **Diseño vigente: [`DESIGN.md`](DESIGN.md).** Horror por estado (moral oculta, sonar fantasma,
> eventos con causa mundana y sobrenatural). Simulador de balance: `python -m dread.sim`.
> Documentos de fases anteriores: `docs/archive/`.
> Prototipo jugable en terminal (la interfaz del puente): `python -m dread.play`; verlo jugar solo: `python -m dread.play --auto crew_first`.

## Project Structure
- `dread/`: horror state model, event engine, phantom sonar, captain's orders, headless simulator, game bridge
- `engine/`: Game loop, state management, event system
- `ui/`: Rendering, controls, and UI panels (main, compartment, log, lore)
- `world/`: Regions, encounters, weather, navigation, lore integration
- `submarine/`: Compartments, crew, systems, sonar, periscope, damage
- `data/`: JSON data for ships, submarines, torpedoes, crew names, regions, crew stories, historical encounters, lore snippets
- `assets/charts/`: Navigation chart images (placeholder)
- `main.py`: Entry point

## Developer Workflow
1. Install dependencies: `pip install -r requirements.txt` (includes `tcod`)
2. Run the game: `python main.py`
3. Add new features by extending modular systems in their respective folders.
4. Data-driven: Add/edit JSON files in `data/` for new ships, subs, etc.

Visual demo (tcod)

If you installed `tcod` (see `requirements.txt`), run a small visual demo to see a sonar-style display:

```bash
python scripts/visual_demo.py
```

This opens a TCOD window showing a sonar circle with contacts. Quit with `q` or `Esc`.

Tilesets and visual style

This project supports loading a user-provided tilesheet placed at `assets/tilesets/modern_tileset.png` (or `tileset.png`). The demo and future tcod renderers will try common tile sizes (32,24,16) and fall back to the built-in libtcod default tileset.

Recommended workflow:

1. Choose a modern tileset (see recommendations in project notes): M4CRO/Spellnerd, Kenney icons, or a custom dark tileset.
2. Place the PNG file in `assets/tilesets/modern_tileset.png`.
3. Run the visual demo: `python scripts/visual_demo.py`.

Palette suggestion: deep navy background, sonar-green pings, steel-gray UI, amber alerts. The renderer will not recolor tiled images automatically — prefer tilesets with neutral palettes or preprocessed recolors.

## Key Conventions
- Tactical and strategic systems are separated by module.
- All logs/events use in-game time for timestamps.
- UI panels are modular and can be swapped or extended.
- Data files are the source of truth for historical/gameplay content and lore.
- Lore and historical content is integrated via `world/lore.py` and displayed in UI panels.

## Next Steps
- Implement core gameplay loop in `engine/game.py`
- Integrate libtcod rendering in `ui/renderer.py`
- Expand data files for more content
- Add tests and documentation as systems mature

---
For detailed AI agent instructions, see `.github/copilot-instructions.md`.
