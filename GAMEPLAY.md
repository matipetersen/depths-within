# WWII Submarine Roguelike - Playable Demo

A tactical submarine simulator built in Python with libtcod, featuring compartment damage, crew management, sonar detection, and torpedo combat.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Play the game (console fallback mode)
python main_play.py

# Or test the demo scenario
python scripts/demo_scenario.py

# Run unit tests
pytest -q
```

## Gameplay

### Objective
Command a Type VIIC U-boat during WWII. Accept missions, detect enemy convoys and destroyers via sonar, evade counter-attacks, manage compartment damage, and coordinate crew responses. Survive encounters with eldritch horrors lurking in the deep.

### Core Mechanics

**Mission System**
- `mission [type]` — Generate new mission (patrol, smuggle, sabotage, rescue, hunt, eldritch, etc.)
- `available` — List all available missions
- `accept <id>` — Accept and begin a mission
- `quest_info` — Check active mission status
- `complete` — Successfully complete mission and claim rewards
- `fail [reason]` — Fail current mission, accept penalties
- `abandon` — Give up on current mission

**Sonar Detection**
- `sonar` — Passive sonar scan detecting nearby contacts
- `sonar_set <value>` — Adjust sensitivity (0.1-2.0)

**Movement & Tactics**
- `dive <meters>` — Submerge to depth for evasion
- `surface` — Return to surface (faster, more visible)
- `aim <x> <y>` — Fire torpedo at map coordinates
- `aimi` — Interactive aim mode (arrow keys to move cursor)
- `fire` / `torpedo` — Fire at first detected contact

**Damage & Crew**
- `compartments` — View compartment integrity and flooding
- `status` — Full submarine status including battery/O2
- `events` — List pending compartment emergencies
- `resolve_event <idx> [responder]` — Assign crew to handle an event
- `defer_events on|off` — Toggle deferring event resolution

**Crew Management**
- `recruit [skill]` — Hire crew member
- `crew_list` — Show all crew
- `crew_info <id>` — Detailed crew stats
- `assign <id> <comp> [role]` — Assign crew to compartment
- `reassign <id> <comp>` — Move crew to different compartment
- `fire_crew <id>` — Remove crew member

**Player Progression**
- `player_status` — Show career stats and XP
- `upgrades` — List available submarine upgrades
- `install_upgrade <id>` — Install submarine upgrade

**Other**
- `help` — Show all commands
- `q` / `quit` — Exit game

### ASCII Map Legend

The tactical map displays depth contours:
- `~` = Very shallow (< 100m)
- `=` = Shallow (100-150m)
- `,` = Medium (150-250m)
- `:` = Deep (250-400m)
- `.` = Very deep (> 400m)

**Symbols:**
- `S` = Your submarine
- `X` = Enemy contact (merchant or destroyer)
- `o` = Active torpedo
- `+` = Cursor (aim point)

### Game Loop

Each turn:
1. World advances: AI moves contacts, torpedoes travel, weather changes
2. Compartment events may occur (flooding, fire, injury)
3. Your submarine drains battery and oxygen
4. You can issue commands to respond

### Strategy Tips

- **Stay silent:** Dive deep to avoid detection; shallower depths are riskier
- **Sonar:** Adjust sensitivity to balance detection range vs. battery drain
- **Torpedo management:** Limited ammunition; count your shots
- **Crew:** Manage stress and experience; experienced engineers repair faster
- **Flooding:** Assign crew quickly to resolve leaks before critical damage
- **Battery:** Monitor power; surfacing recharges but increases risk

## Project Structure

```
Depths within/
├── engine/           # Game loop, state management, logger
├── ui/              # Rendering, ASCII GUI, panels, controls
├── submarine/       # Submarine model, sonar, crew, compartments, torpedo
├── world/           # Tactical map, AI, weather, encounters, regions
├── data/            # JSON: submarines, crews, encounters, lore
├── scripts/         # Demo scenario, tileset generator
├── tests/           # Unit tests
├── assets/          # Tilesets (future pixel-perfect rendering)
└── main_play.py     # Playable entry point
```

## Architecture Highlights

- **Modular design:** Each system (sonar, torpedoes, compartments) is independent
- **Data-driven:** Ships, submarines, and lore loaded from JSON
- **Event system:** Compartment events logged and managed via central logger
- **Tactical AI:** Escorts evade torpedoes and counterattack; convoys follow routes
- **Deterministic mode:** Tests use seeded RNG for reproducibility

## Testing

Run the test suite:
```bash
pytest -q                          # All tests
pytest tests/test_sonar.py -q      # Sonar tests
pytest tests/test_compartment_events.py -q  # Event tests
pytest tests/test_world_integration.py -q   # World integration
```

## Future Enhancements

- [ ] Pixel-perfect tcod rendering with tileset
- [ ] Multi-stage mission chains with branching objectives
- [ ] Port system with crew hiring, repairs, resupply
- [ ] Faction reputation system affecting available missions
- [ ] Crew backstories and personal quest lines
- [ ] Submarine damage model (hull vs. pressure hull)
- [ ] Realistic torpedo physics (acoustic homing, decoys)
- [ ] Procedural campaign with rising difficulty
- [ ] Multiplayer skirmish mode (NOT planned - roguelike focus)

## Controls Reference

| Key/Command | Action |
|---|---|
| `sonar` | Detect contacts |
| `dive 100` | Dive to 100m |
| `surface` | Surface submarine |
| `fire` | Fire at first contact |
| `aim 10 5` | Fire at coordinates (10, 5) |
| `aimi` | Interactive aim (arrows + f to fire) |
| `status` | Full submarine status |
| `compartments` | View damage/flooding |
| `events` | Pending compartment events |
| `resolve_event 0` | Resolve first event |
| `defer_events on` | Queue events for manual resolution |
| `help` | Show all commands |
| `q` | Quit game |

## Development Notes

- Console mode auto-enables ASCII GUI for playability
- Fallback console loop supports all game mechanics
- Sonar uses probabilistic detection with adjustable sensitivity
- Compartment events spawn based on damage and stress
- Crew gain experience and can become specialists
- Torpedoes have homing behavior and target tracking

Enjoy commanding your U-boat!
