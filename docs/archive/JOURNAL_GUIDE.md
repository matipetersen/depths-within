# Journal & Graphics Guide

## Event Journal System

The **Event Journal** logs all major gameplay events, creating a persistent record of your submarine's adventures. The journal supports filtering, searching, and statistical analysis.

## Event Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **MISSION** | Quest-related events | Mission accepted, completed, failed |
| **CREW** | Crew management events | Recruitment, promotion, injuries, deaths |
| **COMBAT** | Battle and weapon events | Torpedo fired, hits, misses, sinking |
| **WORLD** | Environmental events | Weather changes, encounters, discoveries |
| **PROGRESSION** | Character advancement | Level up, upgrades installed, abilities |
| **SYSTEM** | Submarine mechanics | Damage, repairs, malfunctions, system alerts |
| **LORE** | Story/narrative events | Discoveries, mysteries, historical encounters |
| **OTHER** | Miscellaneous events | Config changes, debug events |

## Event Severity Levels

| Severity | Weight | Examples |
|----------|--------|----------|
| **TRIVIAL** | 0 | Minor crew morale change, small repairs |
| **MINOR** | 1 | Crew assignments, small damage, transfers |
| **STANDARD** | 2 | Normal missions, standard combat, skill gains |
| **MAJOR** | 3 | Mission completion, crew death, significant damage |
| **CRITICAL** | 4 | Near-sinking, massive damage, game events |

## Console Commands

### Basic Journal Access

**Display recent events:**
```
> journal
> log
```

Shows the last 10 events with turn number, title, and description.

**Output Example:**
```
Recent Events (Last 5):
──────────────────────────────────────────────────
[Turn 0010] Mission: Cargo Smuggle - Started mission: Cargo Smuggle
[Turn 0050] ✓ Cargo Smuggle Complete - Successfully completed Cargo Smuggle. Earned 250 XP and 5000 credits.
[Turn 0005] New Crew: Hans - Recruited new crew member: Hans
[Turn 0015] Hans Assigned - Hans assigned to compartment
[Turn 0020] Level Up! - Reached Level 5
```

### Search Journal

**Search for specific events:**
```
> log_search <query>
```

Searches across all event titles and descriptions (case-insensitive).

**Examples:**
```
> log_search cargo              # Find cargo-related events
> log_search torpedo            # Find combat events
> log_search Hans               # Find crew-related events
> log_search mission_5          # Find events for mission 5
```

### Filter by Category

**Show events from specific category:**
```
> log_category <category>
```

**Available categories:**
- mission, crew, combat, world, progression, system, lore, other

**Examples:**
```
> log_category mission          # Show all mission events
> log_category crew             # Show all crew events
> log_category combat           # Show all combat events
> log_category progression      # Show skill/upgrade gains
```

### View Statistics

**Show journal statistics:**
```
> log_stats
```

**Output Example:**
```
Journal Statistics:
  Total Events: 127
  First Event: Turn 5
  Last Event: Turn 2150

Events by Category:
    mission:      35
    crew:         42
    combat:       28
    progression:  18
    system:        4

Events by Severity:
    TRIVIAL:       5
    MINOR:        50
    STANDARD:     50
    MAJOR:        20
    CRITICAL:      2
```

### Detailed Event View

**Show last event with full details:**
```
> log_detail
```

**Output Example:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Turn 0050 | MISSION | MAJOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Cargo Smuggle Complete

Successfully completed Cargo Smuggle. Earned 250 XP and 5000 credits.

Tags: mission, mission_1, mission_smuggle

Details:
  • mission_name: Cargo Smuggle
  • event_type: completed
  • reward_xp: 250
  • reward_credits: 5000
```

## Programming Interface

### Basic Event Logging

**Log a custom event:**
```python
journal.log_event(
    category=EventCategory.MISSION,
    title="Event Title",
    description="Event description",
    severity=EventSeverity.MAJOR,
    turn=game.turn,
    tags=['mission_1', 'smuggle'],
    data={'mission_id': 1, 'reward': 500}
)
```

### Mission Events

**Log mission lifecycle:**
```python
from engine.journal import create_mission_event

# Mission accepted
create_mission_event(
    journal=game.journal,
    mission_name="Cargo Smuggle",
    event_type="accepted",
    turn=game.turn,
    mission_id=1
)

# Mission completed
create_mission_event(
    journal=game.journal,
    mission_name="Cargo Smuggle",
    event_type="completed",
    turn=game.turn,
    mission_id=1,
    reward_xp=250,
    reward_credits=5000
)

# Mission failed
create_mission_event(
    journal=game.journal,
    mission_name="Cargo Smuggle",
    event_type="failed",
    turn=game.turn,
    mission_id=1
)

# Mission abandoned
create_mission_event(
    journal=game.journal,
    mission_name="Cargo Smuggle",
    event_type="abandoned",
    turn=game.turn,
    mission_id=1
)
```

### Crew Events

**Log crew management:**
```python
from engine.journal import create_crew_event

# Crew recruited
create_crew_event(
    journal=game.journal,
    crew_name="Hans",
    event_type="recruited",
    turn=game.turn
)

# Crew assigned
create_crew_event(
    journal=game.journal,
    crew_name="Hans",
    event_type="assigned",
    turn=game.turn,
    details={'compartment': 'Engine Room'}
)

# Crew promoted
create_crew_event(
    journal=game.journal,
    crew_name="Hans",
    event_type="promoted",
    turn=game.turn,
    details={'new_rank': 'Chief', 'bonus_xp': 100}
)

# Crew injured
create_crew_event(
    journal=game.journal,
    crew_name="Hans",
    event_type="injured",
    turn=game.turn,
    details={'damage': 25, 'recovery_turns': 10}
)

# Crew deceased
create_crew_event(
    journal=game.journal,
    crew_name="Hans",
    event_type="deceased",
    turn=game.turn,
    details={'cause': 'Flooding'}
)
```

### Combat Events

**Log combat actions:**
```python
from engine.journal import create_combat_event

# Torpedo fired
create_combat_event(
    journal=game.journal,
    event_type="torpedo_fired",
    turn=game.turn
)

# Direct hit
create_combat_event(
    journal=game.journal,
    event_type="hit",
    turn=game.turn,
    target="Destroyer",
    damage=75,
    xp_reward=100
)

# Miss
create_combat_event(
    journal=game.journal,
    event_type="miss",
    turn=game.turn,
    target="Merchant Ship"
)

# Enemy sinking
create_combat_event(
    journal=game.journal,
    event_type="sinking",
    turn=game.turn,
    target="Destroyer",
    xp_reward=500
)
```

### Progression Events

**Log character advancement:**
```python
from engine.journal import create_progression_event

# Level up
create_progression_event(
    journal=game.journal,
    event_type="level_up",
    turn=game.turn,
    details="Reached Level 5"
)

# Upgrade installed
create_progression_event(
    journal=game.journal,
    event_type="upgrade_installed",
    turn=game.turn,
    details="Installed Enhanced Sonar (Tier 2)"
)

# New ability
create_progression_event(
    journal=game.journal,
    event_type="new_ability",
    turn=game.turn,
    details="Unlocked Silent Running"
)
```

## Querying the Journal

### Get Recent Events

```python
# Get last N entries
recent = journal.get_last_entries(count=10)
for entry in recent:
    print(entry.format_line())
```

### Filter by Category

```python
# Get all mission events
missions = journal.get_entries(category=EventCategory.MISSION)

# Get all critical events
critical = journal.get_entries(severity=EventSeverity.CRITICAL)

# Get tagged events
mission_5_events = journal.get_entries(tag='mission_5')
```

### Search Events

```python
# Full-text search
results = journal.search("cargo")
for entry in results:
    print(entry.format_line())

# Get mission-specific events
mission_events = journal.get_mission_events(mission_id=5)

# Get crew-specific events
crew_events = journal.get_crew_events(crew_name="Hans")
```

### Get Statistics

```python
stats = journal.get_statistics()
print(f"Total events: {stats['total_events']}")
print(f"First event: Turn {stats['first_entry_turn']}")
print(f"Last event: Turn {stats['last_entry_turn']}")
print(f"Categories: {stats['events_by_category']}")
print(f"Severities: {stats['events_by_severity']}")
```

## Graphics System

### Rendering Backends

The game automatically selects the best available rendering backend:

1. **Tilesheet** (Recommended)
   - Full pixel graphics with 32×32 tiles
   - Requires tcod 14.0+ and tileset asset
   - Best visual quality

2. **TCOD Fallback**
   - Character-based with tcod library
   - Available if tcod is installed
   - Medium compatibility

3. **ASCII Console**
   - Pure text rendering
   - Always available
   - Minimal requirements

### Tileset Assets

**Submarine Tiles (0-7):**
- Sonar ping
- Submarine silhouette
- Ship silhouette
- Damage indicator
- Battery status
- Oxygen status
- Depth indicator
- Torpedo

**System Tiles (8-15):**
- Compartment
- Crew member
- Flooding
- Fire
- Repair
- Alert
- Contact
- Empty/blank

**UI Tiles (16-31):**
- Sonar screen
- UI panels
- Status bars
- Buttons
- Icons (sonar, periscope, torpedo, damage, crew, journal, nav, status)
- UI corners and borders

**World Tiles (36-51):**
- Water
- Trench
- Wreck
- Rocks
- Kelp
- Thermal vent
- Mine
- Buoy
- Whale
- Merchant ship
- Military ship
- Enemy submarine
- Horror entity
- Explosion
- Wave effect

### Checking Graphics Availability

```python
from ui.graphics import GraphicsRenderer

renderer = GraphicsRenderer()

# Check backend
backend = renderer.get_render_backend()
print(f"Current backend: {backend}")

# Check tileset
if renderer.has_tilesheet():
    print("Pixel graphics available!")
else:
    print("Using fallback rendering")

# Get full graphics info
info = renderer.get_graphics_info()
print(f"ASCII rendering: {info['features']['ascii_rendering']}")
print(f"Tilesheet support: {info['features']['tilesheet']}")
```

### Using Tileset Manager

```python
from ui.graphics import TilesheetManager

manager = TilesheetManager()

# Get specific tile
tile_code = manager.get_tile_code('sonar_ping')

# List tiles by category
ui_tiles = manager.list_tiles_by_prefix('ui_')
world_tiles = manager.list_tiles_by_prefix('water')

# Get all tiles
all_tiles = manager.get_all_tiles()

# Get tile categories
categories = manager.get_tile_categories()
```

### Rendering Sonar Display

```python
from ui.graphics import SonarDisplay

display = SonarDisplay()

# Render single contact
contact = {'type': 'destroyer', 'bearing': 90, 'range': 8000}
char = display.render_contact(contact, use_tiles=False)

# Render full sonar screen
sonar_data = {
    'contacts': [
        {'type': 'submarine', 'bearing': 0, 'range': 5000},
        {'type': 'ship', 'bearing': 90, 'range': 8000},
    ]
}
screen = display.render_sonar_screen(sonar_data, width=40, height=20)
print(screen)
```

## Best Practices

### Event Logging
1. **Always include turns:** Events are time-stamped with in-game turns
2. **Use appropriate severity:** Don't mark everything as CRITICAL
3. **Add relevant tags:** Makes searching and filtering easier
4. **Include quantitative data:** Rewards, damage, XP values

### Journal Queries
1. **Search before logging:** Avoid duplicate events
2. **Cache statistics:** Don't call get_statistics() every frame
3. **Limit event count:** Older entries are automatically pruned
4. **Filter early:** Use category/tag filters before searching

### Graphics
1. **Check backend availability:** Graceful degradation for all platforms
2. **Use TilesheetManager:** Centralized asset management
3. **Cache graphics info:** Backend detection is one-time operation
4. **Test on multiple systems:** Verify console output on Linux/Mac/Windows

## Troubleshooting

### Journal not working?
- Check that `Game` instance has `journal` attribute
- Verify `engine/journal.py` is imported in `game.py`
- Test with: `game.journal.log_event(...)`

### Graphics rendering wrong?
- Run `> help` to verify graphics commands are listed
- Check console for `[Graphics]` messages
- Verify tileset exists at `assets/tilesets/modern_tileset.png`

### Search returning no results?
- Search is case-insensitive (should find "Cargo" and "cargo")
- Check exact tag names with `log_stats`
- Try broader search term

### Commands not working?
- Make sure you're in the game console (after starting game)
- Type `help` to see all available commands
- Check for typos (journal vs jurnal, etc.)

## Performance Tips

1. **Limit journal size:** Use smaller max_entries for constrained systems
2. **Batch queries:** Get all needed events in one call
3. **Cache results:** Store frequently-accessed queries
4. **Use tags:** Faster than full-text search
5. **Prune old events:** Clear history between playthroughs

## Examples

### Track player career statistics
```python
# At end of game
stats = game.journal.get_statistics()
print(f"Missions completed: {stats['events_by_category'].get('mission', 0)}")
print(f"Total events: {stats['total_events']}")
print(f"Game duration: Turn {stats['last_entry_turn']} - {stats['first_entry_turn']}")
```

### Generate after-action report
```python
# Get final statistics
missions = game.journal.get_entries(category=EventCategory.MISSION)
combat = game.journal.get_entries(category=EventCategory.COMBAT)
crew = game.journal.get_entries(category=EventCategory.CREW)

report = f"""
=== PATROL REPORT ===
Duration: Turns {stats['first_entry_turn']}-{stats['last_entry_turn']}
Total Events: {stats['total_events']}

Missions: {len(missions)}
Combat Engagements: {len(combat)}
Crew Changes: {len(crew)}
"""
print(report)
```

### Find critical events during playthrough
```python
# Alert on critical events
critical = game.journal.get_entries(severity=EventSeverity.CRITICAL)
if critical:
    print(f"⚠️  CRITICAL EVENTS: {len(critical)}")
    for event in critical[-3:]:
        print(f"  - {event.title}: {event.description}")
```

---

**Master Your Submarine's Legacy!** 📜 Use the journal to track your missions, crew, and victories.
