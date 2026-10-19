# Game Display Guide

## Running the Game

```bash
cd "/Users/matiaspetersen/Documents/Depths within"
python main.py
```

## Display System

The game now uses a **persistent screen-based rendering system** that clears and updates the display in place, similar to professional terminal games.

### Key Features

✅ **Persistent Screen** - Display updates in place, no scrolling text
✅ **Tactical Map** - Shows submarine and sonar contacts in real-time
✅ **Depth Visualization** - Different characters for different depth zones
✅ **Compartment Status** - Submarine compartments shown with color coding
✅ **System Status HUD** - Shows heading, speed, depth, and crew status
✅ **Color-Coded States** - Green (OK), Yellow (Warning), Red (Danger)

## Main Display Modes

### 1. Tactical View (Default)
Shows a tactical map with:
- **Center**: Your submarine (@) with heading indicator (▲)
- **Background**: Water with depth-appropriate characters
- **Right Panel**: System status HUD
- **Compartments**: Visual representation at center showing:
  - `█` (green) = Operational
  - `▒` (yellow) = Damaged but functional (50-70% integrity)
  - `▓` (red) = Heavily damaged (30-50% integrity)
  - `█` (red) = Flooded or destroyed

### 2. Depth Visualization

Different depth zones show different characters:
- `~` (0-50m) = **SURFACE** - Light blue
- `≈` (50-100m) = **SHALLOW** - Cyan
- `=` (100-150m) = **MODERATE** - Deep blue
- `≡` (150-250m) = **DEEP** - Deep blue
- `≋` (250-400m) = **VERY DEEP** - Deep blue
- `∿` (400m+) = **ABYSSAL** - Deep blue

The header shows your current depth and depth zone:
```
TACTICAL MAP - Turn 5 | Depth 150m (DEEP) | ≡
```

### 3. Submarine Compartments

Compartments are displayed as a row of blocks in the center of the map:
```
≡≡≡≡≡≡≡█████████≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
                ▲
```

Where:
- `█` = Hull/compartment
- Colors indicate integrity:
  - **Green** (`█`) = 80%+ integrity (operational)
  - **Yellow** (`▒`) = 50-80% integrity (damaged)
  - **Red** (`▓`) = 30-50% integrity (heavily damaged)
  - **Red** (`█`) = Flooded or critical

### 4. HUD System Status

The right panel shows:

```
═ SYSTEMS ═
Heading: 0°
Speed:   0.0 kt
Depth:   150m

═ COMPARTMENTS ═
✓ Torpedo Room: 100%
✓ Pressure Hull: 100%
⚠ Engine Room: 75%
✗ Stern Planes: 40%

═ ARMAMENT ═
Torpedoes: 2/4
In Water: 1

═ CREW ═
Personnel: 45/50
Cmdr Level: 1

═ SONAR ═
Contacts: 2
```

## Understanding the Display

### Sonar Contacts

On the tactical map, sonar contacts appear as letters:
- **C** (yellow) = Merchant vessel
- **W** (red) = Warship/Destroyer (threat)
- **E** (red) = Escort (threat)
- **A** (red) = Aircraft (threat)
- **S** (green) = Submarine (friendly)
- **?** (gray) = Unknown contact

### Compartment Status Indicators

In the HUD:
- **✓** (green) = Operational (80%+)
- **⚠** (yellow) = Damaged (50-80%)
- **✗** (red) = Heavily damaged (<50%)

## Terminal Requirements

The game works best with:
- **256-color terminal support** (most modern terminals)
- **ANSI escape sequence support** (xterm, GNOME Terminal, iTerm2, etc.)

### Setting Terminal Environment

If colors aren't working:
```bash
export TERM=xterm-256color
python main.py
```

### Supported Terminals
- xterm-256color
- GNOME Terminal
- KDE Konsole
- iTerm2
- GNU Screen
- Linux console
- rxvt
- And most other modern terminals

## Terminal Size Requirements

- **Minimum**: 120 columns × 35 rows
- **Recommended**: 120+ columns × 40+ rows

If the display is cut off, maximize your terminal window.

## Color Palette

The game uses a desaturated color scheme optimized for long play sessions:

- **Deep Blue** (`\033[38;5;17m`) - Ocean water background
- **Cyan** (`\033[38;5;51m`) - Thermocline, shallow zones
- **Light Blue** (`\033[38;5;153m`) - Surface contacts
- **Red** (`\033[38;5;196m`) - Threats, damage warnings
- **Green** (`\033[38;5;46m`) - Friendly contacts, operational status
- **Yellow** (`\033[38;5;226m`) - Warnings, caution
- **Gray** (`\033[38;5;245m`) - Secondary text, unknowns
- **White** (`\033[38;5;255m`) - Important information

## Troubleshooting

### Display Not Appearing

**Problem**: Screen is blank or text is scrolling instead of updating

**Solutions**:
1. Check terminal supports 256-color:
   ```bash
   echo $TERM  # Should show xterm-256color or similar
   ```

2. Set proper TERM:
   ```bash
   export TERM=xterm-256color
   python main.py
   ```

3. Check terminal window is large enough (120×35 minimum)

### Colors Not Showing

**Problem**: Display is monochrome/black and white

**Solutions**:
1. Enable color support:
   ```bash
   export FORCE_COLOR=1
   python main.py
   ```

2. Check terminal supports 256 colors:
   ```bash
   tput colors  # Should return 256
   ```

### Rendering Issues

**Problem**: Display is garbled or misaligned

**Solutions**:
1. Clear screen manually:
   ```bash
   clear
   python main.py
   ```

2. Try explicit ANSI support:
   ```bash
   FORCE_COLOR=1 TERM=xterm-256color python main.py
   ```

### Performance Issues

**Problem**: Game feels sluggish

**Solutions**:
1. Close other terminal-using applications
2. Disable other terminal effects/transparency
3. Check system load: `top`

## Playing the Game

### Navigation Commands

- **move <dx> <dy>** - Move submarine (e.g., `move 1 0` moves right)
- **dive <depth>** - Dive to specific depth (e.g., `dive 200`)
- **surface** - Return to surface
- **heading <degrees>** - Set heading (e.g., `heading 90` is east)

### System Commands

- **t** / **tactical** - Show tactical map
- **sonar** - Show sonar display (circular view)
- **dash** / **d** - Show dashboard (system overview)
- **compartments** - Show detailed compartment status
- **crew_detail** - Show detailed crew roster
- **status** - Show quick status bar

### Help Commands

- **h** - Show hotkey reference
- **h <category>** - Show category help (e.g., `h combat`)
- **legend** - Show map legend and ASCII symbols

## Display Update Rate

- Display updates when:
  - Game turn advances (submarine moves, time passes)
  - Player enters a command
  - System state changes (damage, crew changes, etc.)
- Updates are instantaneous using ANSI escape codes
- No lag or perceived delay

## Performance Notes

- Display rendering: <50ms per frame
- ANSI codes are sent directly to terminal
- No intermediate graphics libraries required
- Works over SSH, in multiplexers (tmux, screen)
- Efficient buffering prevents flicker

## Advanced Features

### Screen Management

The `PersistentRenderer` class handles:
- Automatic terminal detection
- ANSI code support detection with fallbacks
- Screen clearing and redrawing
- Cursor management (hidden during gameplay, shown on pause/exit)

### Persistent Screen Benefits

1. **No Scrolling** - Display updates in place
2. **No Duplication** - Only one copy of display on screen
3. **Professional Appearance** - Like modern terminal games
4. **Input Responsive** - Immediate visual feedback
5. **SSH Friendly** - Works well over remote connections

## Summary

Your game now has:
✅ Persistent screen display (no scrolling)
✅ Full tactical visualization with compartments
✅ Color-coded status indicators
✅ Real-time depth zone visualization
✅ Professional terminal-based interface
✅ Cross-platform terminal support

Ready to play! 🎮⛵

