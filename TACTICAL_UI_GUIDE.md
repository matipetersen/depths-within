# Tactical UI Panels - User Guide

## Overview

The tactical UI panels provide comprehensive visual displays for the three new tactical systems:
- **Time System**: Environmental conditions, visibility, detection risk
- **Diver Operations**: Personnel status, mission progress, intelligence
- **Sensor Systems**: Active sensors, contacts, fog of war

All panels feature ASCII box-drawing characters for clean, professional displays that work in any terminal.

---

## Quick Reference

### Display Commands

| Command | Description |
|---------|-------------|
| `time` | Show time and environmental conditions |
| `divers` | Show diver operations status |
| `sensors` | Show sensor and contact status |
| `tactical_status` | Show all three panels side-by-side |
| `tactical_hud` | Show compact status bar |

### Help Commands

| Command | Description |
|---------|-------------|
| `time_help` | Detailed time system guide |
| `diver_help` | Detailed diver operations guide |
| `sensor_help` | Detailed sensor systems guide |
| `help tactical` | Quick reference for all tactical systems |

---

## Time & Conditions Panel

**Command:** `time`

```
╔═══════════════════════════════════╗
║    TIME & CONDITIONS              ║
╠═══════════════════════════════════╣
║ 🌅 06:00 - Day 1, Summer         ║
║ Period: DAWN                      ║
║                                   ║
║ Moon: Waxing Crescent       25%   ║
║ Visibility: [██████░░░░░░░░░░░░░░] ║
║ Detection:  [██████████░░░░░░░░░░] ║
║                                   ║
║ Surface: ⚠ CAUTION                ║
║ Periscope Range:  7.5 km          ║
╚═══════════════════════════════════╝
```

### Information Displayed

- **Time & Date**: Current game time and day
- **Period**: Night, Dawn, Morning, Noon, Afternoon, Dusk, Evening
- **Moon Phase**: 8 phases with illumination percentage
- **Visibility Bar**: Visual detection capability (5%-100%)
- **Detection Risk Bar**: Enemy detection chance (10%-100%)
- **Surface Safety**: Safe/Caution/Danger assessment
- **Periscope Range**: Visual range in kilometers

### Time Icons

- 🌙 Night/Evening
- 🌅 Dawn
- ☀️ Day (Morning/Noon/Afternoon)
- 🌇 Dusk

### Tactical Usage

**Night Operations (Safe):**
- Low detection risk (20-35%)
- Limited visibility (5-30%)
- Ideal for: Surface running, diver missions, battery charging

**Day Operations (Dangerous):**
- High detection risk (90-100%)
- Maximum visibility (100%)
- Ideal for: Periscope attacks, visual identification
- Risk: Stay submerged!

**Dawn/Dusk (Balanced):**
- Moderate detection risk (50%)
- Moderate visibility (50%)
- Ideal for: Depth transitions, cautious surface operations

---

## Diver Operations Panel

**Command:** `divers`

```
╔═══════════════════════════════════╗
║    DIVER OPERATIONS               ║
╠═══════════════════════════════════╣
║ Available:  2/ 3                  ║
║                                   ║
║ Personnel:                        ║
║  John Smith  Reconnaissan         ║
║   Status: READY     Fatigue:  15% ║
║  Mike Jones  Sabotage             ║
║   Status: BUSY      Fatigue:  45% ║
║                                   ║
║ Active Missions:                  ║
║  harbor recon         67%         ║
║                                   ║
║ Completed Missions:  5            ║
╚═══════════════════════════════════╝
```

### Information Displayed

- **Available Count**: Ready divers / Total divers
- **Personnel List**: First 3 divers with names and specialties
- **Status**: READY (available) or BUSY (on mission)
- **Fatigue**: 0-100% (high fatigue reduces effectiveness)
- **Active Missions**: Current operations with progress bars
- **Completed Missions**: Historical count

### Specializations

- **Reconnaissance**: Scouting, intelligence gathering
- **Sabotage**: Limpet mines, ship damage
- **Rescue**: Downed pilots, crew recovery
- **Infiltration**: Harbor penetration, facility entry
- **Demolition**: Obstacle clearing, underwater demolition
- **Combat**: Underwater combat specialist

### Commands

```bash
# Recruit a new diver
recruit_diver reconnaissance

# Launch a mission (type, target, difficulty 0.0-1.0)
diver_mission harbor_recon "Scapa Flow" 0.6

# Check status
divers
```

---

## Sensor & Contact Panel

**Command:** `sensors`

```
╔═══════════════════════════════════╗
║    SENSOR STATUS                  ║
╠═══════════════════════════════════╣
║ Active Sensors:                   ║
║  ● Periscope     ON   Visual      ║
║  ● Sonar         ON   Acoustic    ║
║  ○ Radar         OFF  Surface     ║
║  ○ Hydrophone    OFF  Passive     ║
║                                   ║
║ Contacts:  2                      ║
║ Visible Tiles: 234                ║
║ Map Explored: 15.2%               ║
║                                   ║
║ Tracked Contacts:                 ║
║  merchant    045°  3.2km  85%     ║
║  warship     315°  5.8km  95%     ║
╚═══════════════════════════════════╝
```

### Information Displayed

- **Active Sensors**: Status (ON/OFF) for each sensor type
- **Contact Count**: Number of tracked contacts
- **Visible Tiles**: Currently visible map area
- **Map Explored**: Percentage of map discovered
- **Contact Details**: Type, bearing, distance, confidence

### Sensor Types

**Periscope (Visual)**
- Range: 15 tiles (~7.5 km at full visibility)
- Requirement: Depth ≤ 15m
- Best for: Visual identification, daylight
- Affected by: Time of day, weather, fog

**Sonar (Acoustic)**
- Range: 30 tiles (~15 km)
- Works at: Any depth
- Best for: Underwater detection, limited detail
- Always active: Passive mode

**Radar (Surface)**
- Range: 50 tiles (~25 km)
- Requirement: Surface (depth = 0m)
- Best for: Long-range surface detection
- Weather independent

**Hydrophone (Passive)**
- Range: 60 tiles (~30 km)
- Works at: Any depth
- Best for: Silent detection, acoustic analysis
- Gives less detail than sonar

### Commands

```bash
# Toggle sensors on/off
sensor periscope
sensor sonar
sensor radar
sensor hydrophone

# View status
sensors
```

### Contact Types

- **Unknown**: Unidentified contact
- **Merchant**: Cargo ship, tanker
- **Warship**: Destroyer, cruiser, battleship
- **Submarine**: Allied or enemy submarine
- **Aircraft**: Patrol aircraft, reconnaissance
- **Coastal**: Shore battery, lighthouse, buoy

### Confidence Levels

- **Uncertain (<50%)**: Initial detection, needs confirmation
- **Probable (50-80%)**: Likely classification
- **Certain (>80%)**: Confirmed identification

---

## Combined Tactical Display

**Command:** `tactical_status`

Shows all three panels side-by-side for complete situational awareness:

```
╔═══════════════════════════════════╗  ╔═══════════════════════════════════╗  ╔═══════════════════════════════════╗
║    TIME & CONDITIONS              ║  ║    DIVER OPERATIONS               ║  ║    SENSOR STATUS                  ║
╠═══════════════════════════════════╣  ╠═══════════════════════════════════╣  ╠═══════════════════════════════════╣
║ 🌙 22:00 - Day 1, Summer         ║  ║ Available:  2/ 3                  ║  ║ Active Sensors:                   ║
║ Period: EVENING                   ║  ║                                   ║  ║  ● Periscope     ON   Visual      ║
║                                   ║  ║ Personnel:                        ║  ║  ● Sonar         ON   Acoustic    ║
║ Moon: Waxing Crescent       25%   ║  ║  John Smith  Reconnaissan         ║  ║  ○ Radar         OFF  Surface     ║
║ Visibility: [████░░░░░░░░░░░░░░░░] ║  ║   Status: READY     Fatigue:  15% ║  ║  ○ Hydrophone    OFF  Passive     ║
║ Detection:  [█████░░░░░░░░░░░░░░░] ║  ║  Mike Jones  Sabotage             ║  ║                                   ║
║                                   ║  ║   Status: BUSY      Fatigue:  45% ║  ║ Contacts:  2                      ║
║ Surface: ✓ SAFE                   ║  ║                                   ║  ║ Visible Tiles: 234                ║
║ Periscope Range:  4.2 km          ║  ║ Active Missions:                  ║  ║ Map Explored: 15.2%               ║
╚═══════════════════════════════════╝  ║  harbor recon         67%         ║  ║                                   ║
                                        ╚═══════════════════════════════════╝  ║ Tracked Contacts:                 ║
                                                                                ║  merchant    045°  3.2km  85%     ║
                                                                                ╚═══════════════════════════════════╝
```

**Best for:** Quick overview before major decisions, mission planning

---

## Compact Status Bar

**Command:** `tactical_hud`

```
⏰06:00 DAWN Vis:50% │ 👤2/3 🎯1 │ 📡2 🎯2
```

Single-line summary showing:
- Time, period, visibility
- Available divers / total, active missions
- Active sensors, tracked contacts

**Best for:** Real-time monitoring during tactical operations

---

## Tile Graphics Reference

All panels use tiles from `assets/tilesets/atlas.json` for graphical rendering when available:

### Diver Tiles (126-138)
- Specialty icons (recon, sabotage, rescue, etc.)
- Status indicators (deployed, returning, idle)
- Equipment icons (limpet mine, rebreather, diving gear)

### Time/Visibility Tiles (139-158)
- Time period icons (dawn, noon, dusk, night)
- Moon phase icons (new, crescent, quarter, gibbous, full)
- Visibility indicators (high, medium, low)
- Detection risk indicators (safe, caution, danger)

### Fog of War Tiles (159-179)
- Visibility states (unexplored, explored, visible, sonar)
- Sensor states (active/inactive for each type)
- Contact type icons (merchant, warship, submarine, aircraft, coastal)
- Confidence indicators (uncertain, probable, certain)

### Mission/Intel Tiles (180-211)
- Mission type icons (harbor recon, sabotage, rescue, etc.)
- Mission status (active, success, failed)
- Intelligence type icons (harbor, ship, defense, classified)
- Status indicators (fatigue, skill levels, alerts)

---

## Tips & Best Practices

### Planning Operations

1. **Check time before missions:**
   ```
   time
   ```
   - Night = safe for diver operations
   - Day = dangerous, stay deep

2. **Review sensor coverage:**
   ```
   sensors
   ```
   - Multiple sensors reveal more
   - Check for gaps in coverage

3. **Monitor diver status:**
   ```
   divers
   ```
   - Don't send fatigued divers
   - Match specialty to mission type

### During Operations

1. **Use compact HUD for monitoring:**
   ```
   tactical_hud
   ```
   - Quick status check without scrolling

2. **Full panel review at key moments:**
   ```
   tactical_status
   ```
   - Before surfacing
   - Before launching missions
   - When contacts detected

### Learning the Systems

1. **Read detailed help:**
   ```
   time_help
   diver_help
   sensor_help
   ```

2. **Experiment with time progression:**
   - Watch how visibility changes through day
   - Note detection risk at different times
   - Observe moon phase effects

3. **Test sensor combinations:**
   - Try different sensor combinations
   - See how each extends your awareness
   - Learn when to use passive vs active

---

## Keyboard Shortcuts

While in-game, you can set up hotkeys for quick access:

```
# Example hotkey bindings (configure in game)
T  - time
D  - divers
S  - sensors
F  - tactical_status (full display)
H  - tactical_hud (compact)
```

---

## Integration with Gameplay

### Time-Sensitive Decisions

**Surfacing:**
- Check `time` first
- Night = safe
- Day = stay deep

**Diver Missions:**
- Check `time` for stealth
- Check `divers` for availability
- New moon nights = lowest detection

**Periscope Attacks:**
- Dawn/dusk = balanced conditions
- Check `sensors` for target confirmation
- Use `time` to verify visibility

### Information Warfare

**Intelligence Gathering:**
- Diver recon missions provide harbor layouts
- Contact tracking builds enemy movement patterns
- Fog of war reveals safe routes

**Tactical Advantage:**
- Multiple sensors = better contact classification
- Time awareness = better survival
- Diver operations = strategic disruption

---

## Troubleshooting

**Panels not displaying:**
- Check if systems initialized: Look for "New tactical systems initialized" in log
- Try individual commands first: `time`, `divers`, `sensors`

**Missing contacts:**
- Verify sensors are active: `sensor sonar` to toggle
- Check depth requirements: Periscope needs ≤15m, radar needs surface
- Contacts can become stale: They're removed after 100 turns without re-detection

**Diver missions not progressing:**
- Missions tick every game turn
- Use `tick` or `wait` to advance time
- Check fatigue: High fatigue slows mission progress

**Time seems stuck:**
- Time advances 5 minutes per turn
- Use `tick` or perform actions to advance turns
- Check time with `time` command

---

## See Also

- [NEW_SYSTEMS_GUIDE.md](NEW_SYSTEMS_GUIDE.md) - Backend system documentation
- [SYSTEMS_SUMMARY.md](SYSTEMS_SUMMARY.md) - Technical overview
- `test_tactical_ui.py` - Interactive demo of all panels
- `test_new_systems.py` - System integration tests

---

**Note:** All panels gracefully degrade to text-only mode if graphical tiles are unavailable. The box-drawing characters work in any modern terminal that supports UTF-8.
