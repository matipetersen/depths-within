# Depths Within - Rendering Modes

## Two Ways to Play

### 🎮 MODERN PIXEL MODE (Recommended)
**Actual 32x32 pixel graphics** - Uses your tileset PNG with full graphical rendering

```bash
./run_pixel.sh
# OR
PIXEL_MODE=1 python main.py
```

**Features:**
- ✨ Full pixel art graphics (32x32 tiles)
- 🖼️ Actual submarine sprites with rotation
- 🌊 Detailed ocean depth visualization  
- 🎨 Uses submarine_tileset.png directly
- 💻 Hardware accelerated (SDL2)
- 📏 Default: 1280x800 window (40x25 tiles)

**Customize window size:**
```bash
WINDOW_WIDTH=1920 WINDOW_HEIGHT=1080 ./run_pixel.sh
```

---

### 📟 CONSOLE MODE (Classic Roguelike)
**Text-based ASCII/Unicode** - Traditional roguelike style

```bash
python main.py
# OR
PIXEL_MODE=0 python main.py
```

**Features:**
- 📝 Console-based rendering (80-120x40-50 characters)
- 🎯 Each tile = one character position
- 🔤 Works on any terminal
- 🎨 Colored Unicode characters (█ ▓ ░ etc.)
- ⚡ Lightweight, runs anywhere

---

## Current Status

**Console Mode:** ✅ Fully working
- Ocean renders as colored blocks (blue █)
- Each position = one character
- Classic roguelike aesthetic

**Pixel Mode:** 🚧 In development
- SDL rendering implemented
- Uses actual tileset graphics
- Full 32x32 pixel tiles

---

## Technical Details

**Your Tileset:**
- File: `assets/tilesets/submarine_tileset.png`
- Size: 512x512 pixels (16x16 grid)
- Tiles: 256 total tiles (32x32 each)
- Format: RGBA PNG

**Tiles Include:**
- Ocean depths (surface → abyss)
- Submarine angles (0°-315°, surfaced/submerged)
- Ships (merchant, destroyer, cruiser, battleship)
- Torpedoes, mines, depth charges
- UI elements (gauges, indicators)
- Effects (explosions, sonar pings)

**Console Mode** extracts average color from each tile and renders as a single colored character.

**Pixel Mode** renders the full 32x32 pixel tile directly to screen using SDL2.

---

## Controls

Both modes support the same controls:
- **Arrow Keys** - Move submarine
- **Space** - Wait/skip turn
- **P** - Active ping
- **T** - Fire torpedo
- **Q** - Quit

(See in-game HUD for full controls)
