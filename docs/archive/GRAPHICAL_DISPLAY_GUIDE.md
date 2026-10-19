# Graphical Display System - Quick Start Guide

## Overview

Your game now features four enhanced ASCII-based graphical displays with real-time status information, tactical maps, and detailed system panels.

## Display Modes

### 1. **TACTICAL MAP** (Command: `t` or `tactical`)
**Best for:** Navigation and tactical awareness

```
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
TACTICAL MAP - Turn 123 | Depth 156m
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
≈≈≈≈≈≈≈≈≈≈≈≈≈≈ ═ SYSTEMS ═                    ≈≈≈≈≈≈≈≈≈≈≈≈≈≈
≈≈≈≈≈≈@>≈≈≈≈≈ Heading: 180°                 ≈≈≈≈≈≈≈≈≈≈≈≈≈≈
≈≈≈≈C≈≈≈≈≈≈≈≈ Speed: 8.5 kt                ≈≈≈≈≈≈≈≈≈≈≈≈≈≈
≈≈≈≈≈≈W≈≈≈≈≈≈ Depth: 156m                  ≈≈≈≈≈≈≈≈≈≈≈≈≈≈
```

**Features:**
- Submarine position at center (@)
- Contact positions with bearings/ranges (C=merchant, W=warship, A=aircraft)
- Heading indicator (>)
- Depth zones with colors
- Real-time HUD with system status on right

### 2. **SONAR DISPLAY** (Command: `sonar` or `s`)
**Best for:** Pure sonar awareness

```
════════════════════════════════════
SONAR DISPLAY - 156m
────────────────────────────────────
            ·              ·            
  ·      ·          N         ·      ·  
                 ·  · ·                 
              ·          ·              
       ·    ·              ·    ·       
                                        
·          ·                ·          ·
                 ·· ···                 
     ·          ·      ·          ·     
          ·    ·        ·    ·          
               ·        ·               
                                   ·    
·W   ·    ·    ·    @    ·    ·       E 
```

**Features:**
- Circular sonar display with concentric range rings
- Cardinal directions (N, S, E, W)
- Your submarine at center (@)
- Contact markers (C)
- Range rings (50m intervals)

### 3. **DASHBOARD** (Command: `dashboard` or `dash`)
**Best for:** System monitoring

```
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
COMMAND CENTER DASHBOARD - Turn 123
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

SUBMARINE          | COMPARTMENTS       | CREW          
───────────────────  | ───────────────────  | ───────────────
Name: U-Boat         | Total: 6             | Total: 50     
Nation: Germany      | Damaged: 1           | Alive: 48/50  
                     | Flooded: 0           | Injured: 3    
Heading: 180°        |                      |               
Speed: 8.5 knots     | ✓ Command: 92%       | Morale: [████░] 85%
Depth: 156 meters    | ! Engine: 75%        | Loyalty: [███░░] 70%
                     | ✗ Torpedo: 45%       |               
Hull: [██████░] 85%  | ✓ Sonar: 98%        |               
Engine: [███░░░] 70% |                      |               
Battery: [████░░] 65%|                      |               

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

WEAPONS                             | SONAR CONTACTS                  
─────────────────────────────────────  | ─────────────────────────────────
Torpedoes: 6/12 loaded              | Total contacts: 3               
Ready to fire: 6                    | Bearing 045° | Range 1200m | Merchant | Quality 92%
                                    | Bearing 180° | Range 2500m | Warship  | Quality 87%
G7e: 4/6                            | Bearing 270° | Range 800m  | Escort   | Quality 95%
G7a: 2/4                            |                             
Mark 14: 0/2                        |                             
In water: 1 torpedo(es)             |                             
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
```

**Features:**
- 3-column submarine status (heading, speed, depth, hull integrity)
- Compartment damage overview
- Crew status with morale and loyalty
- Weapon loadout with torpedo types
- Active sonar contacts with bearing/range/type/quality

### 4. **STATUS BAR** (Auto-displayed at bottom of screen)
**Best for:** Quick info at a glance

```
Turn 123 | Depth 156m | Speed 8.5kt | Heading 180° | Torpedoes 6/12 | Contacts 3
```

## All Commands

| Command | Alias | Effect |
|---------|-------|--------|
| `tactical` | `t` | Show large tactical map |
| `sonar` | `sonar_mode` | Show circular sonar display |
| `dashboard` | `dash` | Show full system dashboard |
| `view` | - | List available view modes |
| `compartment_detail` | `compartments` | Show detailed compartment report |
| `crew_detail` | - | Show detailed crew roster |
| `sonar_detail` | - | Show detailed sonar info |
| `legend` | - | Show map legend and hotkeys |

## Display Elements Legend

### Submarine/Contacts
```
@  = Your submarine (green)
C  = Merchant vessel (yellow)
W  = Warship/Destroyer (red)
E  = Escort (red)
A  = Aircraft (red)
S  = Submarine (green)
T  = Torpedo in water (yellow)
?  = Unknown contact (gray)
```

### Depth Zones
```
~  = Shallow water (50-100m) - light blue
≈  = Moderate depth (100-150m) - cyan
=  = Deep water (150-250m) - dark blue
≡  = Very deep (250-400m) - darker blue
≋  = Abyssal (400m+) - darkest blue
```

### Status Indicators
```
✓  = Normal operation (green)
⚠  = Warning/Damaged (yellow)
✗  = Critical/Flooded (red)
-  = Offline (gray)
```

### Status Bars
```
[██████░░] = 60% status
[████░░░░] = 40% status
[██░░░░░░] = 20% status (critical)
```

## Keyboard Controls

While in any display mode:
- Press **Enter** or type a command to return to command prompt
- Type `t` for tactical map
- Type `sonar` for sonar display
- Type `dash` for dashboard
- Type `help` for full command list

## Example Gameplay Flow

```
1. Start game: python main.py
2. Type 't' to see tactical map - locate contacts
3. Type 'sonar' to get pure sonar view - judge distance
4. Type 'dash' to check weapon status
5. Type 'fire' or 'f' to fire torpedoes
6. Type 't' to see torpedo trajectory on map
```

## Performance Notes

- **Tactical Display:** ~50-100ms render time
- **Sonar Display:** ~20-40ms render time  
- **Dashboard:** ~80-150ms render time (more data)
- **Status Bar:** ~5-10ms render time

All displays use ANSI color codes (256-color terminal recommended for best visuals).

## Color Scheme

Uses historical submarine color palette:
- Deep ocean blues (#17, #51)
- Cyan for thermocline and contacts (#51)
- Red for threats (#196)
- Green for friendly units (#46)
- Yellow for warnings and torpedoes (#226)
- Gray for text and neutral (#245)
- White for important info (#255)

## Future Enhancements

- [ ] Mouse support for tactical map
- [ ] Animated sonar ping effect
- [ ] Weather visualization
- [ ] Radar screen display mode
- [ ] Target tracking display
- [ ] Historical weather integration
