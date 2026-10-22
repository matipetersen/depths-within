# How to Run the Game - Complete Guide

## Quick Start

```bash
cd "/Users/matiaspetersen/Documents/Depths within"
python main.py
```

The game will start with the hotkey system enabled. You'll see the quick reference automatically.

## The Captain's Bridge (the horror/story layer)

Inside the window press **TAB** for the captain's bridge: an exact ledger, the men (what they
say vs. what you can see), the sonar room, the log and the orders menu. Type an order number and
press **ENTER**; **ENTER/SPACE** waits an hour, **W** waits for news. Decisions stop the clock:
answer with their number. See `DESIGN.md` section 12.5.

Without a window: `python tools/dread_preview.py out_dir` saves PNG screenshots of a scripted patrol,
and `python -m dread.play` plays the same layer in a plain terminal.

## First Time Playing

### Basic Commands
```
h              # Show all hotkeys/commands
h full         # Show all commands (full list)
help crew      # Show crew management commands
crew help      # Same as above
```

### Navigation
```
UP/DOWN/LEFT/RIGHT      # Move submarine
OR
w/a/s/d                 # WASD movement
OR
move <dx> <dy>          # move 1 0 (move right)
```

### Combat
```
t              # Fire torpedo
n              # Cycle target selection
p              # Active ping/sonar scan
```

### Status
```
status         # Quick submarine status
dashboard      # Full tactical dashboard
sonar          # Active sonar contacts
compartments   # Show compartment status
supplies       # Supply inventory
```

### Diving
```
dive 100       # Dive to 100 meters
surface        # Return to surface
```

## Crew Management - NEW FEATURES

### Viewing Crew
```
crew list                     # Show all crew
crew detailed                 # Show detailed crew stats
crew by-assignment            # Show crew by compartment assignment
crew morale                   # Show crew morale/stress report
crew stress-tips              # Show stress management advice
```

### Crew Stories & Factions - EXPANDED SYSTEM
```
crew stories                  # Show all historical crew stories (10+ narratives)
crew biography <name>         # Show detailed biography of crew member
crew factions                 # List available factions (6 nations)
crew faction Kriegsmarine     # Show German Navy crew
crew faction 'US Navy'        # Show American Navy crew
crew theater                  # Show patrol theater information
```

### Managing Crew
```
crew assign anderson engine   # Assign crew member to compartment
crew rest                     # Order crew to rest (reduce stress)
crew inspire                  # Captain's speech (boost morale)
```

## Example Game Session

### Part 1: Start Game and Check Crew
```
$ python main.py

[Game loads]
> crew list
═══ CREW ROSTER ═══
Personnel: 47/50

 1. Commander Anderson | Captain | Health: 98.5%
 2. Chief Peterson | Chief | Health: 95.2%
[... more crew ...]
```

### Part 2: Learn Crew History
```
> crew stories
═══ HISTORICAL CREW STORIES ═══

Kriegsmarine:
  • Klaus Lehmann (Kapitänleutnant) - U-96
    Lehmann-Willenbrock commanded U-96, made famous by the novel...

US Navy:
  • Richard O'Kane (Commander) - USS Tang
    O'Kane was one of the most successful US submarine commanders...
[Shows 10+ stories from 6 nations]
```

### Part 3: Check Specific Crew Member
```
> crew biography O'Kane
═══ CREW BIOGRAPHY ═══

Richard O'Kane
Rank: Commander
Faction: US Navy
Home: Portsmouth, New Hampshire
Personality: Aggressive
Background: Naval Academy Graduate

Personal Story:
O'Kane was the most successful US submarine commander, with 31
confirmed kills across multiple submarines...

Motivations:
• Aggressive prosecution of war
• Protect American shipping
• Naval supremacy in Pacific

Fears:
• Malfunctioning weapons
• Friendly fire
• Crew capture
```

### Part 4: Manage Crew
```
> crew morale
═══ CREW MORALE REPORT ═══
Average Morale: 78.3%
Average Stress: 34.5%
Crew morale is excellent!

> crew rest
✓ Crew ordered to rest. Stress levels reduced.

> crew inspire
✓ Captain's inspiring speech boosts crew morale!
```

### Part 5: Explore Factions
```
> crew factions
═══ AVAILABLE FACTIONS ═══
  crew faction Kriegsmarine
  crew faction 'Imperial Japanese Navy'
  crew faction 'US Navy'
  crew faction 'Royal Navy'
  crew faction 'Soviet Navy'
  crew faction 'Regia Marina'

> crew faction Kriegsmarine
═══ KRIEGSMARINE ═══
Personnel: 5 members

 1. Klaus Lehmann | Kapitänleutnant | Skill: Command
 2. Friedrich Weber | Oberleutnant | Skill: Navigation
[Shows German Navy crew]
```

### Part 6: Gameplay
```
> sonar
Sonar contacts: 2 detected
 - [001] Freighter | Bearing: 045.0° | Range: 2500m
 - [002] Destroyer | Bearing: 125.0° | Range: 3200m

> move 1 0
Moved to (31, 15)

> t
Torpedo fired

Turn 145: Crew thought: "I wonder if we'll make it home..."
Turn 156: Crew: "Engine room reports green across the board!"
```

## Command Categories

### Navigation (h nav)
```
move <dx> <dy>
dive <depth>
surface
position
heading <bearing>
```

### Combat (h combat)
```
fire / torpedo
target <id>
select_target / cycle_target
```

### Systems (h systems)
```
status / status_brief
dashboard
compartments
supplies
ration_level <LEVEL>
```

### Crew (h crew)
```
crew <subcommand>
(crew help shows all crew commands)
```

### Information (h info)
```
legend
lore
journal / log
sonar
encounter_status
spy_status
```

### Supplies (h supplies)
```
supplies
ration_level NORMAL
ration_level REDUCED
ration_level STRICT
ration_level EMERGENCY
```

### Espionage (h espionage)
```
spy_status
spies
```

### Encounters (h encounters)
```
encounter_status
encounter
```

### Game (h game)
```
help / h
ascii
```

## Tips for New Players

### Crew Management
1. **Check morale regularly**: `crew morale` every 10-20 turns
2. **Manage stress**: Use `crew rest` before stress gets critical
3. **Motivate crew**: Use `crew inspire` strategically after defeats
4. **Learn stories**: Read `crew stories` to understand your crew

### Combat
1. **Use sonar**: `sonar` before firing
2. **Cycle targets**: `n` to select different targets
3. **Fire torpedoes**: `t` when ready
4. **Monitor hits**: Check log for torpedo impacts

### Survival
1. **Check compartments**: `compartments` to see damage
2. **Monitor supplies**: `supplies` to track resources
3. **Manage depth**: `dive` to safe depths between engagements
4. **Rest crew**: Keep stress low for better performance

### Exploration
1. **Read lore**: `lore` for crew stories
2. **View journal**: `journal` for mission history
3. **Check status**: `status` for quick overview
4. **Use dashboard**: `dashboard` for full tactical view

## Faction-Specific Tips

### Kriegsmarine (German)
- Strong submarine tactics
- Long patrol endurance
- Focus on convoy hunting
- Watch for depth charges

### US Navy
- Aggressive combat tactics
- Good surface firepower
- Multiple fast submarines
- Excellent logistics

### Royal Navy
- Anti-submarine specialists
- Good convoy escorts
- Strategic bases
- Limited submarine numbers

### Soviet Navy
- Cold water specialists
- Tight confined waters
- Baltic operations
- Limited supply

### Imperial Japanese Navy
- High-tech submarines
- Limited crews
- Pacific theater
- Advanced weapons

### Regia Marina (Italian)
- Mediterranean operations
- Limited resources
- Historical disadvantage
- Rare patrols

## Advanced Commands

### Hotkey System
```
# Quick hotkey lookup
h <category>        # Show hotkeys for category
h full              # Show all hotkeys
```

### Player Progression
```
player_status       # Career statistics
upgrades            # Available upgrades
install_upgrade <id> # Install upgrade
```

### Journal & Records
```
journal
log
recent_events
```

## Troubleshooting

**Q: Game won't start**
A: Make sure you're in the correct directory and Python is installed: `python --version`

**Q: Commands don't work**
A: Try `help` or `h` to see available commands. Commands are lowercase.

**Q: Can't find crew member**
A: Use `crew list` to see exact names. Names are case-insensitive in commands.

**Q: Morale too low**
A: Use `crew inspire` to boost morale, and `crew rest` to reduce stress.

**Q: Submarine won't move**
A: Use `move 1 0` format, or arrow keys. Movement costs a turn (auto-tick).

**Q: Need more info**
A: Type `h` for hotkey help, `crew help` for crew commands, or see guides in GUIDES/ directory.

## Game Files

**Main Script**: `main.py` - Start here  
**Game Engine**: `engine/game.py`  
**Crew System**: `submarine/crew*.py`  
**Crew Factions**: `engine/crew_factions.py`  
**Crew Stories**: `engine/crew_stories.py`  
**Story Data**: `data/crew_stories.json`  

## Documentation

**Complete Guides**:
- `COLOR_SYSTEM_GUIDE.md` - Color themes and formatting
- `CREW_COMMUNICATIONS_GUIDE.md` - Crew thoughts and dialogue
- `CREW_MANAGEMENT_GUIDE.md` - Crew management commands
- `CREW_FACTIONS_GUIDE.md` - Factions and stories (NEW)
- `HOTKEY_SYSTEM_GUIDE.md` - Complete hotkey reference
- `GAMEPLAY.md` - General gameplay guide

## Performance

- **Start time**: ~1-2 seconds
- **Turn time**: ~50-100ms
- **Command response**: <100ms
- **Game is smooth**: 60+ FPS equivalent

## Game Features

✅ 6 Naval Factions  
✅ 10+ Historical Crew Stories  
✅ Personality-based crew system  
✅ Deep crew management  
✅ Tactical submarine combat  
✅ Full crew communications system  
✅ Colorized output  
✅ Hotkey system  
✅ Journal/logging system  
✅ Supply management  
✅ Crew loyalty system  
✅ Spy network  
✅ Eldritch encounters  
✅ 186+ passing tests  

---

**Happy hunting! Command your submarine wisely.**

*For detailed information about specific systems, see the comprehensive guides in the project directory.*

## Play it in the browser (GitHub Pages) and install it as an app

The touch version is a static page in `docs/` (with its manifest, icons and a small service worker so it also works offline). A GitHub Action (`.github/workflows/pages.yml`) rebuilds it from the sources and publishes it.

1. One time only: **Settings -> Pages -> Build and deployment -> Source: GitHub Actions**.
2. Run the workflow: it runs by itself on every push to `main` that touches `web/`, `data/`, `docs/` or `tools/build_web.py`, or by hand from **Actions -> Deploy the game to GitHub Pages -> Run workflow** (do this after step 1 the first time).
3. A minute later the game is at `https://<user>.github.io/depths-within/` (for this repository: https://matipetersen.github.io/depths-within/). The run's summary also shows the address.
4. Open it on a phone or tablet, hold the device sideways and tap **Begin patrol**. To install it: Chrome/Android -> menu -> *Install app* (or *Add to Home screen*); Safari/iOS -> Share -> *Add to Home Screen*. The icon is a periscope over a sonar scope.

After changing the game, rebuild locally with `python tools/build_web.py` (writes `web/dread.html` and `docs/index.html`, the manifest and the service worker). The icons come from `python tools/make_icons.py`.

## Python version
Use **Python 3.12 or newer**. The JavaScript port (`web/engine.js`) reproduces CPython's random numbers and the compensated float `sum` of 3.12+, and `tests/test_web_parity.py` compares both line by line; on 3.11 one fuzzed patrol can differ in the last digit of a float.
