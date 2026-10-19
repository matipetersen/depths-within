# Graphical Display System - Developer Extension Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│          Game Main Loop (engine/game.py)            │
│  - process_command()                                │
│  - _tick()                                          │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        │            │            │              │
        ▼            ▼            ▼              ▼
   ┌────────┐   ┌────────┐  ┌────────┐  ┌────────────┐
   │Tactical│   │ Sonar  │  │ Dash   │  │ Detailed   │
   │Display │   │ Display│  │ Board  │  │ Panels     │
   │(120x35)│   │(40x25) │  │        │  │            │
   └────────┘   └────────┘  └────────┘  └────────────┘
   (800+ chars)  (300 chars) (2000+ chars) (1000+ chars)
        │            │            │              │
        └────────────┴────────────┴──────────────┘
                     │
          ┌──────────▼───────────┐
          │  ANSI Color Output   │
          │ (256-color terminal) │
          └──────────────────────┘
```

## Class Hierarchy

### Base Classes
```python
class DisplayView:
    """Abstract base for all display views"""
    def render(self, game) -> str:
        """Render the view and return string"""
        pass

class HUDElement:
    """Abstract base for dashboard elements"""
    def render_column(self, game) -> List[str]:
        """Render a column of text"""
        pass
```

### Concrete Implementations

#### TacticalDisplay (ui/tactical_display.py)
```python
class TacticalDisplay(DisplayView):
    def __init__(self, width=120, height=35)
    def render(self, game) -> str
    def _render_background(self, game_map, game)
    def _render_submarine(self, game_map, game)
    def _render_contacts(self, game_map, game)
    def _render_torpedoes(self, game_map, game)
    def _render_thermocline(self, game_map, game)
    def _render_legend(self) -> List[str]
    def _render_compass(self) -> List[str]
    def _render_hud(self, game) -> List[str]
```

**Key Methods:**
- `_clear_map()` - Initialize blank map grid
- `bearing_to_vector()` - Convert bearing/distance to x,y coordinates
- `_get_depth_char_at()` - Get ASCII char for depth level

#### SonarView (ui/tactical_display.py)
```python
class SonarView(DisplayView):
    def __init__(self, width=40, height=25)
    def render(self, game) -> str
    # Renders concentric circles for range rings
    # Places submarine at center
    # Plots contacts based on bearing/range
```

#### DashboardView (ui/hud_display.py)
```python
class DashboardView(DisplayView):
    def render(self, game) -> str
    def _render_submarine_status(self, game) -> List[str]
    def _render_compartment_status(self, game) -> List[str]
    def _render_crew_status(self, game) -> List[str]
    def _render_weapons_status(self, game) -> List[str]
    def _render_sonar_contacts(self, game) -> List[str]
```

#### DetailedPanel (ui/hud_display.py)
```python
class DetailedPanel:
    @staticmethod
    def render_compartment_details(game) -> str
    @staticmethod
    def render_crew_details(game) -> str
    @staticmethod
    def render_sonar_details(game) -> str
```

## Adding New Display Modes

### Step 1: Create New Display Class

```python
# In ui/new_display.py
class MyCustomDisplay(DisplayView):
    def __init__(self, width=80, height=30):
        self.width = width
        self.height = height
    
    def render(self, game) -> str:
        lines = []
        
        # Render your custom display
        lines.append(f"═══ MY CUSTOM DISPLAY ═══")
        lines.append(f"Turn {game.turn}")
        
        # Your custom rendering logic here
        for i in range(10):
            lines.append(f"Line {i}")
        
        lines.append(f"═" * 80)
        
        return "\n".join(lines)
```

### Step 2: Add to Game Initialization

```python
# In engine/game.py __init__()

try:
    from ui.new_display import MyCustomDisplay
    self.custom_display = MyCustomDisplay()
except Exception as e:
    self.custom_display = None
```

### Step 3: Add Command Handler

```python
# In engine/game.py process_command()

elif cmd in ('custom', 'my_display'):
    self.current_view = 'custom'
    if self.custom_display:
        try:
            print(self.custom_display.render(self))
        except Exception as e:
            print(f'Custom display error: {e}')
    return True
```

### Step 4: Test

```bash
python main.py
custom  # Will show your new display
```

## Common Patterns

### Pattern 1: Rendering a Grid

```python
# Create 2D grid
grid = [[' ' for _ in range(width)] for _ in range(height)]

# Fill with characters
for y in range(height):
    for x in range(width):
        grid[y][x] = get_character(game, x, y)

# Render to string
output = "\n".join("".join(row) for row in grid)
```

### Pattern 2: Converting Coordinates

```python
import math

def bearing_to_vector(bearing_deg, distance):
    """Convert bearing and distance to x, y offset"""
    rad = math.radians(bearing_deg)
    y = -int(distance * math.cos(rad) / 100)  # Negative because up is negative
    x = int(distance * math.sin(rad) / 100)
    return x, y

# Usage
bearing = 45  # Northeast
distance = 1000  # 1000m
dx, dy = bearing_to_vector(bearing, distance)
map_x = center_x + dx
map_y = center_y + dy
```

### Pattern 3: Status Bar Rendering

```python
def get_status_bar(value, width=20, label=""):
    """Create a filled bar for status display"""
    filled = int(value * width)
    bar = '█' * filled + '░' * (width - filled)
    color = get_status_color(value)
    return f"{label}: {color}[{bar}]{ANSI_RESET} {value*100:.0f}%"

# Output: "Health: [██████░░░░] 60%"
```

### Pattern 4: Color Management

```python
# Define color constants
COLOR_RED = "\033[38;5;196m"
COLOR_GREEN = "\033[38;5;46m"
COLOR_BLUE = "\033[38;5;33m"
ANSI_RESET = "\033[0m"

# Apply color
output = f"{COLOR_GREEN}Status: OK{ANSI_RESET}"

# Get color based on value
def get_status_color(value):
    if value >= 0.75:
        return COLOR_GREEN
    elif value >= 0.5:
        return COLOR_YELLOW
    else:
        return COLOR_RED
```

## Extending Existing Displays

### Add New Column to Dashboard

```python
# In DashboardView class

def _render_new_column(self, game):
    """Render a new system column"""
    lines = []
    lines.append(f"{COLOR_CYAN}{ANSI_BOLD}NEW SYSTEM{ANSI_RESET}")
    lines.append(f"{'─' * 35}")
    
    # Your logic here
    lines.append("Status: Active")
    
    return lines

# Modify render() to include new column
def render(self, game):
    # ... existing code ...
    col_new = self._render_new_column(game)
    
    # Add to output alongside existing columns
    # ... existing code ...
```

### Add New Contact Type

```python
# In TacticalDisplay class

class ContactType(Enum):
    MERCHANT = ('C', COLOR_YELLOW, 'Merchant vessel')
    WARSHIP = ('W', COLOR_RED, 'Warship/Destroyer')
    # ADD NEW TYPE:
    TANKER = ('K', COLOR_ORANGE, 'Oil tanker')
    TRANSPORT = ('L', COLOR_CYAN, 'Transport ship')
```

### Add New Depth Zone

```python
# In tactical_display.py

class DepthLevel(Enum):
    SURFACE = (0, 50, '~', COLOR_LIGHT_BLUE)
    SHALLOW = (50, 100, '≈', COLOR_CYAN)
    # ADD NEW ZONE:
    TWILIGHT = (200, 350, '◆', COLOR_PURPLE)  # Twilight zone
```

## Performance Optimization

### Caching Strategy
```python
class OptimizedTacticalDisplay(TacticalDisplay):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_map = None
        self.cached_turn = -1
    
    def render(self, game) -> str:
        # Only re-render if turn changed
        if game.turn != self.cached_turn:
            self.cached_map = self._render_full(game)
            self.cached_turn = game.turn
        return self.cached_map
```

### Incremental Rendering
```python
def render_incremental(self, game, changes_only=False):
    """Only update changed elements"""
    if not changes_only:
        return self.render(game)  # Full render
    
    # Calculate deltas
    old_contacts = self.last_contacts
    new_contacts = game.sonar_manager.detected_contacts
    
    # Only re-render changed contacts
    # ... delta logic ...
```

## Debugging Display Issues

### Enable Debug Output
```python
class DebugDisplay(DisplayView):
    def __init__(self):
        self.debug_enabled = True
    
    def debug(self, msg):
        if self.debug_enabled:
            print(f"[DEBUG] {msg}")
    
    def render(self, game):
        self.debug(f"Rendering with turn {game.turn}")
        # ... rest of render logic ...
```

### Validate Output
```python
def validate_render_output(output: str) -> bool:
    """Check output is valid"""
    lines = output.split('\n')
    
    # Check line width consistency
    max_width = max(len(line) for line in lines)
    if max_width > 200:
        print(f"Warning: Output line too long ({max_width} chars)")
        return False
    
    # Check for color codes
    if '\033[' not in output:
        print("Warning: No ANSI colors in output")
    
    return True
```

## Testing Framework

```python
# test_displays.py
import pytest
from engine.game import Game
from ui.tactical_display import TacticalDisplay

class TestTacticalDisplay:
    def test_render_empty_game(self):
        game = Game()
        display = TacticalDisplay()
        output = display.render(game)
        
        assert output is not None
        assert len(output) > 0
        assert "TACTICAL MAP" in output
    
    def test_submarine_position(self):
        game = Game()
        display = TacticalDisplay()
        output = display.render(game)
        
        # Check submarine symbol is present
        assert '@' in output
    
    def test_contact_rendering(self):
        game = Game()
        # Add mock contact
        display = TacticalDisplay()
        output = display.render(game)
        
        assert output is not None
```

## Future Extension Points

1. **3D Visualization** - Add depth-aware rendering
2. **Animation** - Frame-based animations for effects
3. **Interactive Maps** - Mouse/keyboard navigation
4. **Weather Integration** - Display weather effects
5. **Historical Accuracy** - Time-period specific visuals
6. **Crew Portraits** - Visual crew representation
7. **Map Legends** - Dynamic legend generation
8. **Recording/Playback** - Record displays for replay
9. **Multiplayer** - Network sync of displays
10. **VR/AR Support** - Virtual reality integration

## Resources

- **ANSI Color Codes:** [https://en.wikipedia.org/wiki/ANSI_escape_code](256 colors)
- **Terminal Capabilities:** Use `tput colors` to check terminal support
- **Unicode Symbols:** ═ ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ● ◆ ● ▀ ▄ █ ░
- **Math Functions:** `math.sin()`, `math.cos()`, `math.radians()`

## Contributing

To contribute new display modes:

1. Create new file in `ui/` directory
2. Implement display class with `render(game)` method
3. Add to `engine/game.py` initialization
4. Add command handler in `process_command()`
5. Create unit tests
6. Update documentation
7. Submit pull request

---

**Happy coding!** Your game now has a powerful, extensible graphical display system ready for further enhancement.
