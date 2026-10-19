# Visual System Quick Reference Card

## 🎨 Complete Tileset System (126 Tiles)

### Quick Start

```python
from ui.graphics_renderer import get_renderer
renderer = get_renderer()

# Render anything
renderer.render_<item>(console, x, y, [options])
```

## 📦 Tile Categories

| Category | Count | Tiles |
|----------|-------|-------|
| **Ocean** | 8 | surface, shallow, medium, deep, very_deep + 3 variants |
| **Submarine** | 16 | 8 angles × 2 states (surf/sub) |
| **Ships** | 7 | merchant, warship, destroyer (+ damaged) |
| **Torpedoes** | 9 | G7e, G7a, Mk14, Mk23, 21inch, Type93, Type95, generic, wake |
| **Mines** | 3 | contact, magnetic, acoustic |
| **Weather** | 6 | clear, fog, rain, storm, ice, night |
| **Periscope** | 4 | up, searching, locked, damaged |
| **Sonar/Radar** | 4 | active, passive, ping, scanning |
| **Systems** | 8 | battery×3, oxygen×3, hull×2 |
| **Aircraft** | 6 | bomber, patrol, fighter, recon, attacking, damaged |
| **Ports/Nav** | 6 | friendly, enemy, neutral, waypoint, objective, complete |
| **Depth Charges** | 4 | falling, armed, exploding, sonobuoy |
| **Convoys** | 4 | cargo, tanker, troopship, escort |
| **Damage** | 4 | light, moderate, heavy, critical |
| **Flags** | 6 | Germany, USA, UK, Japan, Italy, USSR |
| **Crew/Comp** | 8 | 4 crew states + 4 compartment states |
| **UI/Gauges** | 19 | horizontal, circular, battery gauges + borders |
| **Explosions** | 6 | small, medium, large + damage markers |

**Total:** 126/256 tiles (49% capacity, 130 remaining)

## 🚀 Common Operations

### Tactical Display

```python
# Ocean with depth
ocean_tile = renderer.get_ocean_tile_for_depth(250)
renderer.render_tile_to_console(console, ocean_tile, x, y)

# Submarine with heading
renderer.render_submarine(console, x, y, heading=90, depth=50)

# Ships
renderer.render_ship(console, x, y, 'destroyer', damaged=False)

# Torpedoes (specific type)
renderer.render_torpedo_type(console, x, y, 'Type_93')

# Mines
renderer.render_mine(console, x, y, 'magnetic')

# Weather overlay
renderer.render_weather(console, x, y, 'storm')

# Depth charges
renderer.render_depth_charge_state(console, x, y, 'exploding')
```

### HUD/UI Display

```python
# System status icons
renderer.render_battery(console, x, y, 0.75)  # 75% battery
renderer.render_oxygen(console, x, y, 0.50)   # 50% oxygen
renderer.render_hull_status(console, x, y, 0.90)  # 90% hull

# Sensors
renderer.render_periscope(console, x, y, 'searching')
renderer.render_sonar(console, x, y, 'active')
renderer.render_radar(console, x, y)

# Gauges (old system, still works)
renderer.render_gauge(console, x, y, 'horizontal', 0.80)

# Crew and compartments
renderer.render_crew_icon(console, x, y, 'stressed')
renderer.render_compartment(console, x, y, 'flooding')
```

### Strategic Map

```python
# Ports
renderer.render_port(console, x, y, 'friendly')
renderer.render_port(console, x, y, 'enemy')

# Navigation
renderer.render_waypoint(console, x, y)
renderer.render_mission(console, x, y, 'objective')

# Convoys
renderer.render_convoy(console, x, y, 'cargo')

# Flags/Territory
renderer.render_flag(console, x, y, 'Germany')

# Obstacles
renderer.render_obstacle(console, x, y, 'wreck')
```

### Combat

```python
# Aircraft
renderer.render_aircraft(console, x, y, 'bomber', damaged=False)

# Damage overlays
renderer.render_damage_overlay(console, x, y, 'heavy')

# Explosions
renderer.render_explosion(console, x, y, 'large')

# Sonobuoys
renderer.render_sonobuoy(console, x, y)
```

## 🔧 Helper Functions

### Dynamic Tile Selection

```python
# Ocean depth mapping
ocean_tile = renderer.get_ocean_tile_for_depth(depth)
# depth < 100 → surface
# depth < 200 → shallow
# depth < 300 → medium
# depth < 400 → deep
# depth >= 400 → very_deep

# Submarine angle mapping
sub_tile = renderer.get_submarine_tile_for_angle(angle, submerged)
# Snaps to nearest 45° (0, 45, 90, 135, 180, 225, 270, 315)

# Gauge level mapping
gauge_tile = renderer.get_gauge_tile('horizontal', level)
# level → percentage (100, 75, 50, 25)
```

### Tile Lookup

```python
# Get tile index
idx = renderer.get_tile_index('torpedo_type93')

# Get tile coordinates (col, row)
coords = renderer.get_tile_coords('mine_magnetic')

# Get pixel coordinates (x, y, width, height)
pixel_coords = renderer.get_tile_pixel_coords('aircraft_bomber')

# Check if tile exists
if renderer.get_tile_index('some_tile') is not None:
    # Tile available
    pass
```

## 🎮 Usage Patterns

### Pattern 1: Full Tactical Rendering

```python
def render_full_tactical(game, console):
    renderer = get_renderer()
    
    # 1. Ocean background
    for y in range(h):
        for x in range(w):
            depth = game.map.get_depth(x, y)
            ocean = renderer.get_ocean_tile_for_depth(depth)
            renderer.render_tile_to_console(console, ocean, x, y)
    
    # 2. Weather overlay
    if game.weather in ['fog', 'storm', 'rain']:
        for y in range(h):
            for x in range(w):
                if random.random() < 0.1:
                    renderer.render_weather(console, x, y, game.weather)
    
    # 3. Static objects
    for mine in game.mines:
        renderer.render_mine(console, mine.x, mine.y, mine.type)
    
    for wreck in game.wrecks:
        renderer.render_obstacle(console, wreck.x, wreck.y, 'wreck')
    
    # 4. Ships and contacts
    for contact in game.contacts:
        renderer.render_ship(console, contact.x, contact.y, 
                           contact.type, contact.damaged)
    
    # 5. Active weapons
    for torpedo in game.torpedoes:
        renderer.render_torpedo_type(console, torpedo.x, torpedo.y, 
                                    torpedo.type)
    
    for charge in game.depth_charges:
        state = 'armed' if charge.age > 3 else 'falling'
        renderer.render_depth_charge_state(console, charge.x, charge.y, state)
    
    # 6. Aircraft
    for aircraft in game.aircraft:
        renderer.render_aircraft(console, aircraft.x, aircraft.y,
                               aircraft.type, aircraft.damaged)
    
    # 7. Player submarine (on top)
    renderer.render_submarine(console, game.sub.x, game.sub.y,
                            game.sub.heading, game.sub.depth)
```

### Pattern 2: Status Panel

```python
def render_status_panel(game, console, x_start, y_start):
    renderer = get_renderer()
    y = y_start
    
    # Title
    console.print(x_start, y, "═══ SUBMARINE STATUS ═══")
    y += 2
    
    # Systems
    battery = game.sub.systems.battery
    renderer.render_battery(console, x_start, y, battery)
    console.print(x_start + 2, y, f"Battery: {int(battery*100)}%")
    y += 1
    
    oxygen = game.sub.systems.oxygen
    renderer.render_oxygen(console, x_start, y, oxygen)
    console.print(x_start + 2, y, f"Oxygen: {int(oxygen*100)}%")
    y += 1
    
    hull = game.sub.systems.hull_integrity
    renderer.render_hull_status(console, x_start, y, hull)
    console.print(x_start + 2, y, f"Hull: {int(hull*100)}%")
    y += 2
    
    # Sensors
    console.print(x_start, y, "─── SENSORS ───")
    y += 1
    
    periscope_state = 'locked' if game.sub.periscope.locked else 'searching'
    renderer.render_periscope(console, x_start, y, periscope_state)
    console.print(x_start + 2, y, "Periscope")
    y += 1
    
    sonar_state = 'active' if game.sub.sonar.pinging else 'passive'
    renderer.render_sonar(console, x_start, y, sonar_state)
    console.print(x_start + 2, y, "Sonar")
    y += 1
```

### Pattern 3: Strategic Overview

```python
def render_strategic_map(game, console):
    renderer = get_renderer()
    
    # Background (simplified ocean)
    for y in range(h):
        for x in range(w):
            renderer.render_tile_to_console(console, 'ocean_medium', x, y)
    
    # Ports
    for port in game.world.ports:
        if port.is_friendly():
            renderer.render_port(console, port.x, port.y, 'friendly')
        elif port.is_enemy():
            renderer.render_port(console, port.x, port.y, 'enemy')
        else:
            renderer.render_port(console, port.x, port.y, 'neutral')
        
        # Flag marker
        renderer.render_flag(console, port.x-1, port.y, port.nation)
    
    # Missions
    for mission in game.missions:
        if mission.completed:
            renderer.render_mission(console, mission.x, mission.y, 'complete')
        else:
            renderer.render_mission(console, mission.x, mission.y, 'objective')
    
    # Convoys
    for convoy in game.world.convoys:
        renderer.render_convoy(console, convoy.x, convoy.y, convoy.type)
    
    # Waypoints
    for wp in game.navigation.waypoints:
        renderer.render_waypoint(console, wp.x, wp.y)
    
    # Player position (small submarine)
    renderer.render_submarine(console, game.sub.x, game.sub.y, 0, 0)
```

## 🔍 Debugging

### Check Tileset Status

```python
from ui.graphics_renderer import get_renderer
renderer = get_renderer()

# Check total tiles
print(f"Total tiles: {len(renderer.atlas['map'])}")

# List all tiles
for name, idx in sorted(renderer.atlas['map'].items()):
    print(f"{idx:3d}: {name}")

# Check specific tile
tile = 'torpedo_type93'
idx = renderer.get_tile_index(tile)
if idx is not None:
    print(f"✅ {tile} found at index {idx}")
else:
    print(f"❌ {tile} not found")
```

### Regenerate Tileset

```bash
# Full tileset with all items
python tools/generate_expanded_tileset.py

# Output: submarine_tileset.png + atlas.json
```

## 📝 File Locations

```
assets/tilesets/
├── submarine_tileset.png    # 512×512 PNG (126 tiles)
└── atlas.json               # Tile mappings

tools/
├── generate_tileset.py           # Original (55 tiles)
└── generate_expanded_tileset.py  # Complete (126 tiles) ← USE THIS

ui/
├── graphics_renderer.py     # Graphics API
└── panels/panel_manager.py  # Rendering integration
```

## ⚠️ Common Pitfalls

1. **Wrong torpedo type format:**
   ```python
   # ❌ Wrong
   renderer.render_torpedo_type(console, x, y, 'torpedo_type93')
   
   # ✅ Correct
   renderer.render_torpedo_type(console, x, y, 'Type_93')
   ```

2. **Missing nation capitalization:**
   ```python
   # ❌ Wrong
   renderer.render_flag(console, x, y, 'germany')
   
   # ✅ Correct
   renderer.render_flag(console, x, y, 'Germany')
   ```

3. **Not checking return value:**
   ```python
   # ❌ Assumes success
   renderer.render_mine(console, x, y, 'contact')
   
   # ✅ Check success and fallback
   if not renderer.render_mine(console, x, y, 'contact'):
       console.print(x, y, '✱', fg=(50, 50, 50))
   ```

4. **Forgetting to import:**
   ```python
   # ❌ Error: renderer not defined
   renderer.render_submarine(console, x, y, 0, 0)
   
   # ✅ Import first
   from ui.graphics_renderer import get_renderer
   renderer = get_renderer()
   renderer.render_submarine(console, x, y, 0, 0)
   ```

## 🎯 Performance Tips

1. **Cache renderer instance:** Call `get_renderer()` once, reuse
2. **Batch tile lookups:** Use `get_ocean_tile_for_depth()` once per depth level
3. **Minimize fallbacks:** Ensure tileset is loaded to avoid ASCII rendering
4. **Render order:** Background → static → dynamic → player (painter's algorithm)

## 📚 Documentation

- **COMPLETE_VISUAL_OVERHAUL.md** - Full system guide (this doc's parent)
- **GRAPHICS_OVERHAUL.md** - Original 55-tile system
- **tools/generate_expanded_tileset.py** - Generator source code
- **ui/graphics_renderer.py** - API source code

---

**Quick Stats:**
- **126 tiles** (49% capacity)
- **20+ render methods**
- **12 categories**
- **130 slots remaining**

**Version:** 2.0  
**Last Updated:** December 2024
