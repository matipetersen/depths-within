# Enhanced GUI Features - User Guide

## Overview

The game now includes a comprehensive enhanced GUI with four major improvements:

1. **ASCII Tile Legend** - Understand what each character on the tactical map means
2. **Submarine Visualization** - See your submarine and all compartments with status indicators
3. **Control Status Dashboard** - Monitor all controllable variables in one place
4. **Compartment Health Highlighting** - Instantly see which compartments have issues

## Movement with Keys (NOW WORKING!)

### Arrow Keys
```
↑ = Move north (decrease Y)
↓ = Move south (increase Y)
← = Move west (decrease X)
→ = Move east (increase X)
```

### WASD Keys
```
W = Move north (up)
A = Move west (left)
S = Move south (down)
D = Move east (right)
```

**Note:** Arrow keys and WASD work both in tactical GUI mode and console mode!

### Direct Movement Commands
You can also use the explicit command:
```
move <dx> <dy>
> move -1 0    (move 1 tile west)
> move 1 0     (move 1 tile east)
> move 0 -1    (move 1 tile north)
> move 0 1     (move 1 tile south)
```

---

## ASCII Tile Legend

### What It Shows

Each character on the tactical map represents a specific depth zone or object:

```
~  = Shallow water (50-100m)
=  = Moderate depth (100-150m)
,  = Deep water (150-250m)
:  = Very deep (250-400m)
·  = Abyssal trench (400m+)
*  = Thermocline (sound barrier)
C  = Ship/Merchant contact
E  = Escort/Destroyer
A  = Aircraft
S  = Your submarine
T  = Torpedo in water
+  = Your cursor position (in aim mode)
```

### How to View

```
> legend
```

Shows both:
1. Tactical map legend (what each tile means)
2. Hotkey reference (all available commands)

---

## Submarine Visualization

### What It Shows

ASCII representation of your submarine with each compartment's status:

```
  SUBMARINE STATUS
  Vessel: U-995 (Type VIIC)
  Position: (45, 23) | Depth: 200m

  ┌─────────────────────────────────────┐
  │ ✓ Bow        │████████░░░░░░░░░░│  (Hull integrity %)
  │ ✓ Control    │████████████████░░│
  │ ⚠ Engine     │██████░░░░░░░░░░░░│  (Damaged)
  │ ✓ Aft        │████████████████░░│
  └─────────────────────────────────────┘
```

### Status Indicators

```
✓  = Compartment normal
!  = Compartment damaged (reduced capacity)
X  = Compartment flooding (CRITICAL - red color)
-  = Compartment offline
⚠  = Warning - issues detected (yellow)
⬆  = Overload - reduce load (red)
```

### How to View

```
> dashboard
```

Shows the complete tactical interface including submarine visualization.

---

## Control Status Dashboard

### What It Shows

All controllable submarine variables in organized sections:

#### PROPULSION
```
Depth: 200m    [████████░░░░░░░░░░] 50.0%
Heading: N (0°)
Speed: 5.2 kt   [████░░░░░░░░░░░░░░] 26.0%
Battery: 87.5%  [██████████████░░░░] 87.5%
```

#### SUPPLIES
```
O₂:   450L    [██████░░░░░░░░░░░░] 45.0%  (Green if high)
Food: 75      [███████████░░░░░░░] 75.0%  (Yellow if medium)
Fuel: 250L    [██████░░░░░░░░░░░░] 50.0%  (Red if low!)
Ammo: 8 torpedoes [████░░░░░░░░░░░░] 33.3%
```

#### CREW STATUS
```
Personnel: 42/50 [████████░░░░░░░░] 84.0%
Morale: 65.0     (Stressed: 3)
```

### Color Coding

- **🟢 Green (66%+)** - Excellent status
- **🟡 Yellow (33-66%)** - Warning level
- **🔴 Red (<33%)** - Critical status

### How to View

```
> status       (Quick status with hints)
> dashboard    (Full dashboard with all components)
```

---

## Compartment Status Report

### What It Shows

Detailed status of every compartment with issues highlighted:

```
═══ COMPARTMENT STATUS REPORT ═══

✓ Bow             | Integrity:  95.0% | Flooding:   0.0% | Status: NOMINAL
✓ Control        | Integrity:  90.0% | Flooding:   0.0% | Status: NOMINAL
! ! Engine        | Integrity:  55.0% | Flooding:   2.5% | Status: DAMAGED
X X X Aft         | Integrity:  30.0% | Flooding:  45.0% | Status: FLOODING CRITICAL

WARNING: CRITICAL FLOODING IN MULTIPLE COMPARTMENTS
```

### Issue Indicators

```
✓      = Nominal operation
!!     = Severely damaged (red)
...    = Minor leak (yellow)
⚠⚠⚠    = Flooding critical (magenta)
⬆⬆     = High pressure (yellow)
```

### How to View

```
> compartments     (Toggle compartment display)
> dashboard        (Shows in full dashboard)
```

---

## Full Dashboard Command

The `dashboard` command shows everything at once:

```
> dashboard
```

Displays in sequence:
1. Tactical map (top of screen)
2. ASCII tile legend
3. Submarine visualization with compartments
4. Control status dashboard
5. Detailed compartment status report
6. Command hotkey reference

**Perfect for:**
- New players learning the game
- Getting full overview
- Checking all systems at once
- Initial startup

---

## Quick Reference - New Commands

| Command | Function |
|---------|----------|
| `dashboard` | Show full interface with everything |
| `legend` | Show tile legend and hotkey reference |
| `move <dx> <dy>` | Move submarine explicitly |
| `↑/↓/←/→` | Arrow keys for movement |
| `W/A/S/D` | WASD keys for movement |
| `compartments` | Toggle compartment display |
| `status` | Quick status with hints |
| `supplies` | Detailed supply inventory |

---

## What Was Fixed

### Movement Now Works! ✅

**Before:** Arrow keys and WASD didn't do anything
**After:** Full keyboard movement support with:
- Arrow keys (↑↓←→)
- WASD keys (W/A/S/D)
- Explicit `move` commands
- Real-time position updates

### Visual Enhancements ✅

**Added:**
- Submarine ASCII art with compartment layout
- Color-coded health indicators (green/yellow/red)
- Depth visualization on tactical map
- Thermal layer indicators
- Contact and torpedo symbols
- Live status bars for all resources
- Critical damage highlighting

### Better Information Display ✅

**Now Available:**
- Complete tile legend for map symbols
- Compartment-by-compartment health
- All controllable variables in dashboard
- Color-coded warnings (🟢🟡🔴)
- Crew morale tracking
- Supply consumption indicators

---

## Examples

### Example 1: Move Your Sub

```
> move -2 1     (Move 2 tiles west, 1 tile south)
Moved to (43, 24)
> [Auto-ticks]  (Movement actions auto-tick)
```

### Example 2: Check Status Before Diving

```
> legend        (Learn what tiles mean)
> dashboard     (See everything)
> status        (Quick check)
> dive 300      (Dive to 300m - auto-ticks)
```

### Example 3: Monitor Damage

```
> compartments
- Bow            | Int: [████████████████░░] 0.95 | Flood: [░░░░░░░░░░░░░░░░░░░░] 0.00
- Control Room   | Int: [██████████░░░░░░░░░░] 0.50 | Flood: [██░░░░░░░░░░░░░░░░░░] 0.10 ⚠
- Engine         | Int: [██░░░░░░░░░░░░░░░░░░] 0.15 | Flood: [████░░░░░░░░░░░░░░░░] 0.25 !!!
- Aft            | Int: [░░░░░░░░░░░░░░░░░░░░] 0.00 | Flood: [██████████████░░░░░░] 0.75 XXX
```

---

## Technical Details

### Files Modified
- `ui/enhanced_gui.py` - NEW: Complete enhanced GUI system
- `ui/controls.py` - UPDATED: Arrow key and WASD support
- `ui/ascii_gui.py` - UPDATED: Added dashboard and legend functions
- `engine/game.py` - UPDATED: Added move, dashboard, legend commands

### New Classes

**ASCIILegend**
- `draw_tile_legend()` - Tile mapping reference
- `draw_command_legend()` - Hotkey reference

**SubmarineVisual**
- `draw_submarine_status()` - ASCII sub with compartments
- Compartment status indicators
- Visual integrity/flooding bars

**ControlStatusDashboard**
- `draw_control_panel()` - All controllable variables
- Progress bars with color coding
- Heading compass display

**CompartmentHighlighter**
- `get_compartment_status_line()` - Per-compartment detail
- `draw_compartment_status()` - Full report with warnings

### Color Codes Used

```
Green (32)   = Good (>66%)
Yellow (33)  = Warning (33-66%)
Red (31)     = Critical (<33%)
Cyan (36)    = Headers
Magenta (35) = Flooding critical
Gray (90)    = Offline/disabled
```

---

## Troubleshooting

### Q: Arrow keys still don't work
**A:** Make sure you're using the console mode (not tcod GUI). Use `legend` to verify the UI is working.

### Q: Dashboard is too long
**A:** Scroll up to see the beginning, or use individual commands:
- `legend` - Just the legend
- `status` - Just quick status
- `compartments` - Just compartment detail

### Q: Can't see colors?
**A:** Your terminal might not support ANSI colors. The game still works in grayscale.

### Q: Movement doesn't advance turn
**A:** Movement IS an action and automatically advances the turn. If it doesn't, check the logger output.

---

## Summary

The enhanced GUI provides complete tactical information at a glance while making the game more playable with working keyboard controls. All systems are color-coded for quick assessment, and compartment damage is immediately visible.

**Key improvements:**
- ✅ Arrow keys work
- ✅ WASD keys work  
- ✅ Complete submarine visualization
- ✅ All variables displayed
- ✅ Color-coded health
- ✅ Issue highlighting
- ✅ Visual legends

Enjoy commanding your submarine! 🚢
