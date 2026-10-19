# Enhanced Game Loop Integration Guide

## Overview

The game loop has been completely redesigned to integrate:
1. **Historical Weapon Systems** - 8 torpedo types with documented defects
2. **Realistic Sonar Detection** - Period-accurate detection with thermocline physics
3. **Dynamic War Progression** - War status changes from 1939 to 1945+
4. **Mission System** - Procedural missions tied to war status
5. **Random Events** - 15 different types of events that affect gameplay
6. **Captain's Log** - Dynamic logging of all significant events
7. **Crew Experience** - Crew members gain skills and experience
8. **Supply Management** - Supplies diminish based on war progression
9. **Endgame Conditions** - Multiple victory types and final scoring

## Architecture

```
Game Loop (main._tick())
    ↓
GameFlowManager (manages all systems)
    ├─ War Progression (tracks 1939-1945+)
    ├─ Mission System (active/completed/failed)
    ├─ Random Events (15 event types)
    ├─ Captain's Log (timestamped entries)
    ├─ Supply Shortage (war-linked scarcity)
    └─ Endgame Detection (victory conditions)
    
Also running in parallel:
    ├─ SonarManager (historical detection with thermocline)
    ├─ WeaponSystem (with historical defects)
    ├─ CrewSystem (loyalty, morale, experience)
    ├─ SupplyInventory (consumed based on supply shortage)
    └─ CombatSystem (torpedo hits, depth charges, etc)
```

## Game Objectives (Selectable)

Players can pursue one or more of these primary objectives:

1. **DESTROY_ENEMY_SHIPPING** (Default)
   - Sink enemy merchant and combat vessels
   - Each kill contributes to war status shift
   - Rewards XP in combat skills

2. **GATHER_INTELLIGENCE**
   - Reconnaissance missions
   - Decode enemy communications
   - Rewards XP in navigation and sonar

3. **PROTECT_SUPPLY_LINES**
   - Defend allied shipping
   - Convoy escort missions
   - Rewards XP in crew leadership

4. **SURVIVE_WAR**
   - Primary meta-objective
   - Reach September 1945 with crew intact
   - Different victory types based on performance

5. **BUILD_LEGENDARY_CREW**
   - Maximize crew experience and loyalty
   - Avoid mutinies and desertions
   - Rewards come from crew morale actions

6. **DISCOVER_SECRETS**
   - Explore eldritch and mysterious encounters
   - Uncover hidden lore
   - Rewards come from special encounters

7. **STRATEGIC_VICTORY**
   - Control regions and achieve objectives
   - Requires successful missions
   - War-map influenced gameplay

## War Status Progression

War status automatically changes based on historical progression:

```
1939 (STALEMATE)        →  50/50 balance, standard supply levels
    ↓ (Monthly updates)
1940 (STALEMATE)        →  Slight axis advantage (France falls)
    ↓
1941 (AXIS_ADVANTAGE)   →  Germany dominates (Barbarossa), supply shortages increase
    ↓
1942 (AXIS_ADVANTAGE)   →  Continued axis control until late year
    ↓ (Stalingrad, Tunisia)
1943 (STALEMATE)        →  Tide turning, supply shortages moderate
    ↓ (Sicily, Italy)
1944 (ALLIED_ADVANTAGE) →  D-Day and liberation, axis supply critical
    ↓
1945 (AXIS_DECLINE)     →  Axis collapsing, supply nearly exhausted
    ↓
1945/09 (ENDGAME)       →  War ends - victory determined
```

## Supply Shortage System

Supply shortage is **directly tied to war status**:

```
STALEMATE:          10-25% shortage
AXIS_ADVANTAGE:     20-40% shortage (axis losing raw materials)
ALLIED_ADVANTAGE:   15-30% shortage (balanced but restricted)
AXIS_DECLINE:       50-80% shortage (CRITICAL - desperate times)
ENDGAME:            70-90% shortage (severe scarcity)
```

Effects on gameplay:
- Lower availability of supplies in port/rendezvous
- Increased consumption rates when in combat
- Crew rationing becomes mandatory late-war
- Fuel shortages force mission cancellations

## Random Events System

15 different random events can occur (2-15% probability each):

### Opportunity Events
- **Convoy Sighted** - Enemy merchant fleet with light escort
- **Supply Cache Found** - Wreckage with salvageable supplies
- **Rare Naval Asset** - Battleship or aircraft carrier spotted
- **Old Enemy Returns** - Previous damaged enemy reappears
- **Radio Intercept** - Enemy communication intelligence

### Disaster Events
- **Engine Malfunction** - Temporary system failure
- **Spy Detected** - Suspected saboteur identified
- **Mechanical Failure** - Critical system offline
- **Depth Charge Attack** - Surprise enemy attack
- **Crew Illness** - Infectious disease outbreak

### Encounter Events
- **Crew Celebration** - Successful patrol morale boost
- **Lucky Escape** - Narrow evasion of detection
- **Weather Storm** - Heavy weather complicates navigation

### Intelligence Events
- **Decoy Formation** - False targets identified
- **Successful Resupply** - Supply rendezvous succeeds

## Mission System

### Mission Types (Tied to War Status)

**Early War (1939-1941)**
- Standard patrols (STALEMATE objective)
- Convoy escorts
- Reconnaissance (INTELLIGENCE objective)

**Mid War (1941-1943)**
- Ship hunting (DESTROY_SHIPPING objective)
- Supply run escort (PROTECT_SUPPLIES objective)
- Sabotage operations

**Late War (1943-1945)**
- High-value target hunts
- Supply line defense
- Intelligence gathering intensifies

**Endgame (1945/09+)**
- Final strategic objectives
- Survivalist missions
- Eldritch/mysterious encounters available

### Mission Mechanics

Each mission has:
- **Name** - Descriptive title
- **Type** - Affects objective progress
- **Difficulty** - 1-5 scale
- **Time Limit** - Turns available
- **Target** - What to attack/retrieve/protect
- **Reward XP** - Experience on completion
- **Reward Credits** - In-game currency
- **Progress Tracking** - 0-100% completion

Missions auto-progress based on:
- Time passing
- Player actions (destroying targets, collecting supplies)
- Combat encounters
- Random events affecting mission

## Captain's Log

Automatically logs all significant events:

```
[Sep 1939] New game started: War begins
[Sep 1939] First sonar contact detected
[Sep 1945] Heavy Storm Encountered - crew stressed
[Oct 1939] NEW MISSION: Destroy merchant convoy (+100 XP, +1000 credits)
[Oct 1939] ✓ Mission complete: Merchant convoy sunk (+100 XP)
[Oct 1939] SONAR: Contact bearing 045°, range 8000m [CERTAIN]
[Oct 1939] Torpedo hit contact: Transport at 52,38
[Oct 1939] WAR UPDATE (Oct 1939): stalemate
```

Display with: `captain_log [number]` - shows last N entries

## Crew Experience System

### Crew Skills Gain XP From

- **Sonar Operation** - From sonar contacts made
- **Torpedo Accuracy** - From successful hits
- **Evasion** - From escaping detection/combat
- **Resource Management** - From supply mission completion
- **Crew Leadership** - From mission completion, morale actions
- **Navigation** - From distance traveled, exploration
- **Damage Control** - From compartment repairs, damage control actions

### Crew Loyalty/Morale

Affected by:
- Supply rationing (low morale if critical rations)
- Mission success (morale boost on completion)
- Crew celebrations (bonus morale events)
- Losses (negative morale from casualties)
- Dangerous encounters (stress accumulation)

## Experience & Leveling

### Player Leveling
- **Level 1-10**: Early career (0-5000 XP)
- **Level 10+**: Extended career milestone

### Crew Recruitment
- Quality varies (skill 40-95%)
- Experience improves performance
- Loyalty affects reliability

### Captain Influence
- Inspirational speeches boost crew
- Good decisions improve loyalty
- Leadership experience accumulates

## Victory Types (At War End - Sept 1945+)

Based on final stats:

### LEGENDARY_COMMANDER
- 50+ ships sunk
- 5+ capital ships destroyed
- 80%+ crew loyalty
- 20+ missions completed
- 10+ survivors rescued

**Score Multiplier: 1.5x**

### CAPITAL_SHIP_KILLER
- 5+ capital ships sunk
- High combat effectiveness

**Score Multiplier: 1.3x**

### SUBMARINE_ACE
- 25+ ships sunk
- Consistent performance

**Score Multiplier: 1.2x**

### VETERAN
- 10+ ships sunk
- Career experience

**Score Multiplier: 1.1x**

### SAILOR
- 5+ ships sunk
- Competent performance

**Score Multiplier: 1.0x**

### RECRUIT
- 1-4 ships sunk
- Minimal experience

**Score Multiplier: 0.8x**

### CIVILIAN
- 0 ships sunk
- No combat success

**Score Multiplier: 0.5x**

## Final Score Calculation

```
Base Score = 0

+ (Ships Destroyed × 10 points)
+ (Capital Ships × 25 points)
+ (Crew Loyalty Bonus × 1000 points)
+ (Survivors Rescued × 50 points)
+ (Near-Death Escapes × 20 points)
+ (Missions Completed × 100 points)
+ (Perfect Crew Loyalty Bonus = 500 points if no mutinies/desertions)
+ (War Victory Bonus = 2000 points if allied victory)
+ (Survival Bonus = min(1000, Turns Survived / 10))

Final Score = Base Score × Victory Type Multiplier
```

## New Commands

All commands are integrated into the existing hotkey system:

### War & Objectives
- `war` or `war_status` - Show current war status, supply levels
- `objectives` or `goal` - Show current objectives and progress
- `missions` - Show mission status (active/completed/failed)
- `missions active` - List active missions
- `missions completed` - List completed missions
- `missions failed` - List failed missions

### Captain's Log
- `captain_log` - Show last 20 log entries
- `captain_log 50` - Show last 50 entries
- `log` - Shortcut for captain_log

### Sonar Status
- `sonar_status` - Show sonar system details
  - Current system type and nation
  - Base range and reliability
  - Operator fatigue level
  - Contacts detected this patrol

### Historical Context
- `lore` - Show historical crew stories
- `history` - Show war progression timeline
- `date` - Show current game date

## Integration with Existing Systems

### Supply System
- Supply inventory integrated with war progression
- Shortage percentages affect availability
- Rationing affects crew morale
- Can set ration level: `ration_level CRITICAL`

### Crew System
- Crew morale tied to missions and events
- Experience gains from various activities
- Loyalty tracked for mutiny prevention
- Commands: `crew list`, `crew morale`, `crew inspire`

### Journal System
- Captain's log populates game journal
- Events categorized by type
- Search and filter capabilities
- Persistent across saves

### Progression System
- Player stats track career achievements
- Skills improve from actions
- Level-up system based on XP total
- Final rank calculation at war end

### Combat System
- Historical torpedo defects integrated
- Sonar detection guides combat
- Weapon effectiveness varies by type
- Player submarine can be damaged/destroyed

## Replayability Features

### Randomized Elements
- Random seed per game (optional)
- Random event occurrence and order
- Random mission generation and difficulty
- Dynamic war progression (with random swings)
- Crew personality and skill variation
- Supply shortage variations

### Difficulty Variance
- Early war (1939-1940): More forgiving
- Mid war (1941-1943): Balanced challenge
- Late war (1943-1945): Very difficult
- Endgame (1945+): Crisis management

### Multiple Paths to Victory
- Combat-focused (DESTROY_SHIPPING)
- Survival-focused (SURVIVE_WAR)
- Crew-focused (BUILD_LEGENDARY_CREW)
- Mystery-focused (DISCOVER_SECRETS)
- Strategic-focused (STRATEGIC_VICTORY)

## File Locations

**Core Game Loop:**
- `engine/game.py` - Main game loop with integrated systems
- `engine/game_flow.py` - NEW: GameFlowManager for war progression
- `world/sonar_systems.py` - Historical detection system
- `submarine/torpedo.py` - Torpedo system with defects

**Supporting Systems:**
- `engine/progression.py` - Player skill progression
- `engine/crew_loyalty.py` - Crew loyalty and rebellion tracking
- `engine/journal.py` - Captain's log and journal
- `engine/supply_management.py` - Supply inventory
- `engine/crew_management.py` - Crew UI and management
- `engine/quests.py` - Mission/quest system

**Data:**
- `data/torpedoes.json` - 8 historical torpedo types with defects
- `data/submarines.json` - Submarine specs
- `data/sonar_systems.py` - Sonar system definitions

## Testing & Validation

✅ **All 186 existing tests passing**
✅ **Historical systems integrated without breaking changes**
✅ **War progression tracks 1939-1945+**
✅ **Supply shortage linked to war status**
✅ **Random events trigger and affect gameplay**
✅ **Captain's log captures all events**

## Future Enhancements

Possible additions:
- [ ] Base/port management system
- [ ] Crew customization at recruitment
- [ ] Advanced radar/sonar UI visualization
- [ ] Strategic campaign map
- [ ] Historical character encounters
- [ ] Submarine upgrade tree completion
- [ ] Multiplayer competitive score tracking
- [ ] Advanced AI captain decisions
- [ ] Voice narration for log entries
- [ ] Full campaign story branching

## Example Gameplay Flow

```
1. Game starts - September 1939, war declared
   - Random initial crew assigned
   - First mission offered
   - War status: STALEMATE, supply 10% shortage

2. Player completes patrol mission
   - Sinks 2 merchant ships
   - Sonar detects patrol through thermocline (58% effective range)
   - Narrow escape from escort - morale boost
   - War advantage shifts -1% (toward allies)
   - Captain's log records achievements

3. Monthly update triggers (Turn 30)
   - October 1939: War status remains STALEMATE
   - Supply shortage increases to 15% (random variation)
   - Random event: Crew celebration (+5% morale)
   - New missions offered

4. Continue through war years
   - 1940: France falls, axis advantage grows
   - 1941: Barbarossa, supply shortages increase
   - 1942: Turning point, more difficult missions
   - 1943: Allied momentum, critical shortages
   - 1944: Axis losing, missions become desperate
   - 1945: Final missions, endgame approaches

5. September 1945: War ends
   - Final victory type determined
   - Score calculated
   - Achievements recorded
   - Option to start new career
```

## Command Quick Reference

| Command | Effect |
|---------|--------|
| `war` | Show war status, supply shortage, axis/allied advantage |
| `objectives` | Show current objectives progress |
| `missions` | Show active, completed, failed missions |
| `captain_log [n]` | Show last N log entries |
| `sonar_status` | Show sonar system and operator details |
| `crew` | Crew management commands |
| `supplies` | Supply inventory status |
| `stats` | Player statistics and achievements |
| `journal` | Full event journal |

---

**Integration Complete - Ready for Play!**

All systems are now coordinated through a single unified game loop. War progression drives mission availability, supply shortage, and difficulty. Captain's log tracks all events. Crew experience and loyalty contribute to final victory type determination. Random events provide variety for replayability.

The game now has genuine campaign progression with meaningful objectives, stakes, and varied outcomes.
