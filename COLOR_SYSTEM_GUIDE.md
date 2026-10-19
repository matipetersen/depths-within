# Color System Integration Guide

## Overview
The game now features a **centralized color system** (`ui/color_system.py`) that provides consistent, theme-based ANSI color output throughout the game.

## Color System Components

### 1. Color Enum
Defines 24 colors across three categories:
- **Basic Colors** (8): black, red, green, yellow, blue, magenta, cyan, white
- **Bright Colors** (8): bright_red, bright_green, bright_yellow, bright_blue, bright_magenta, bright_cyan, bright_white
- **Background Colors** (8): bg_black, bg_red, bg_green, bg_blue, etc.

```python
from ui.color_system import Color
color = Color.bright_green
```

### 2. Style Enum
Defines text styling options:
- bold
- dim
- italic
- underline
- reverse

### 3. ColorTheme Enum
Pre-defined themes for common game elements (20+ themes):

| Theme | Use Case |
|-------|----------|
| `alert` | Critical warnings/errors |
| `warning` | Caution/attention needed |
| `success` | Positive outcomes |
| `info` | Informational messages |
| `debug` | Debug output |
| `crew_thought` | Normal crew thoughts |
| `crew_stress` | Stressed crew messages |
| `crew_happy` | Happy crew messages |
| `crew_injured` | Injured crew messages |
| `sonar` | Sonar contacts/data |
| `torpedo` | Torpedo status |
| `damage` | Damage messages |
| `repairs` | Repair operations |
| `supplies` | Supply status |
| `heading` | Navigation headings |
| `depth` | Depth changes |
| `position` | Position/coordinates |
| `header` | Section headers |
| `label` | Label text |
| `value` | Numeric values |

### 4. ColorSystem Class
Central color management with global instance.

```python
from ui.color_system import _color_system

# Basic colorization
text = _color_system.colorize("Hello", Color.red, Style.bold)

# Theme-based coloring
text = _color_system.theme("Critical Error!", ColorTheme.alert)

# Convenience methods
text = _color_system.header("SUBMARINE STATUS")
text = _color_system.success("Torpedo fired successfully")
text = _color_system.alert("Hull integrity critical!")
text = _color_system.crew_thought("I wonder if we'll make it home...")
```

## Using Colors in Code

### Method 1: Direct Colorization
```python
from ui.color_system import _color_system, Color, Style

message = _color_system.colorize("Depth: 250m", Color.bright_cyan)
print(message)

# With styling
message = _color_system.colorize(
    "WARNING", 
    Color.bright_red, 
    Style.bold
)
print(message)
```

### Method 2: Theme-Based (Recommended)
```python
from ui.color_system import _color_system, ColorTheme

# Status messages
print(_color_system.theme("All systems nominal", ColorTheme.success))

# Crew communications
print(_color_system.theme("I'm getting nervous...", ColorTheme.crew_thought))

# Alerts
print(_color_system.theme("Hull breach!", ColorTheme.alert))
```

### Method 3: Convenience Methods
```python
from ui.color_system import _color_system

# Headers for sections
print(_color_system.header("CREW ROSTER"))

# Labels for data
print(_color_system.label("Sonar Status:"))

# Values to display
print(_color_system.value("5/50 contacts"))

# Status messages
print(_color_system.success("Torpedo reload complete"))
print(_color_system.warning("Low oxygen reserves"))
print(_color_system.alert("Engine failure!"))
print(_color_system.info("Entering patrol zone"))

# Crew-specific
print(_color_system.crew_thought("Crew morale is high"))
print(_color_system.crew_stressed("Crew stress rising"))
print(_color_system.crew_happy("Crew celebrating victory"))

# Tactical
print(_color_system.sonar("Contact detected"))
print(_color_system.torpedo("Torpedo armed"))
print(_color_system.damage("Compartment flooding"))
```

## Integration Points

### 1. Game Engine (engine/game.py)
- Color system imported and used for logging
- Crew management commands use colors for status displays

### 2. Crew Management (engine/crew_management.py)
- `CrewManagementUI` uses colors for:
  - Crew roster display (rank, skills, status)
  - Morale reports with color-coded health/stress
  - Assignment displays
  - Status management tips

### 3. Logger (engine/logger.py)
- Can be enhanced to use colored output
- Color-codes by message type (info, warning, error)

### 4. UI Panels (ui/panels/)
- Can use ColorSystem for consistent theming
- Particularly useful for status displays

## Disabling Colors

Colors can be disabled globally (useful for tests or text logs):

```python
from ui.color_system import _color_system

# Disable colors
_color_system.enabled = False

# Re-enable colors
_color_system.enabled = True

# Check if enabled
if _color_system.enabled:
    print("Colors are active")
```

When disabled, `colorize()` and `theme()` methods return the input text unchanged.

## Color Palette Reference

### Game State Colors
- **Success**: bright_green
- **Warning**: bright_yellow  
- **Alert**: bright_red
- **Info**: bright_cyan
- **Debug**: bright_magenta

### Crew State Colors
- **Happy**: bright_green
- **Normal**: cyan
- **Stressed**: bright_yellow
- **Injured**: bright_red
- **Anxious**: bright_magenta

### Tactical Colors
- **Sonar**: bright_cyan (for contacts)
- **Torpedo**: bright_yellow (for projectiles)
- **Damage**: bright_red (for hazards)
- **Repairs**: bright_green (for recovery)
- **Supplies**: bright_blue (for resources)

## Examples in Game

### Crew Management Display
```
╔════════════════════════════════════════════════════════════╗
║                    CREW ROSTER                            ║
╚════════════════════════════════════════════════════════════╝
Personnel: 47/50

 1. Captain Anderson | Lieutenant | Skill: Command | Health: 98.5%
 2. Chief Peterson | Chief | Skill: Engineering | Health: 95.2%
 3. Sonarman Jones | Specialist | Skill: Sonar | Health: 100.0%

    Stress: 45.0% | Morale: 85.0% | Fatigue: 12.3%
    Personality: Steady | Level: 5 | Missions: 23
```

### Status Messages
```
[SUCCESS] Torpedo reload complete
[WARNING] Low oxygen reserves (3 days)
[ALERT] Hull integrity below 50%!
[INFO] Entering patrol zone Delta-7
[CREW THOUGHT] "I wonder if we'll ever see port again..."
```

## Best Practices

1. **Use themes for consistency**: Rather than mixing colors, use appropriate ColorTheme values
2. **Semantic coloring**: Let colors convey meaning (red=danger, green=success)
3. **Accessibility**: Avoid color combinations that are hard to distinguish
4. **Disable for logs**: Set `_color_system.enabled = False` for plain text logs
5. **Group related elements**: Keep related messages using the same theme

## Performance Notes

- Color strings are generated on-demand (minimal overhead)
- No performance impact when colors are disabled
- ANSI codes add ~10-20 bytes per colored string
- Suitable for real-time game output

## Testing with Colors

For unit tests that need colored output verification:

```python
from ui.color_system import _color_system

# In test setup
_color_system.enabled = True

# Test color output
colored_text = _color_system.theme("test", ColorTheme.success)
assert "\033[" in colored_text  # Contains ANSI codes

# In test teardown
_color_system.enabled = False  # Disable for clean logs
```

## Future Enhancements

Possible additions:
- Custom color themes for user preferences
- Color profiles (accessibility modes)
- Dynamic theme switching based on game difficulty
- Color gradients for progress bars
- Terminal detection for color support
