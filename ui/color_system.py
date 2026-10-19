"""
Centralized color system for the entire game.
Provides consistent ANSI color codes and styling across all modules.
"""

from enum import Enum
from typing import Optional


class Color(Enum):
    """Standard color palette for the game."""
    # Basic colors
    BLACK = "30"
    RED = "31"
    GREEN = "32"
    YELLOW = "33"
    BLUE = "34"
    MAGENTA = "35"
    CYAN = "36"
    WHITE = "37"
    
    # Bright colors
    BRIGHT_BLACK = "90"
    BRIGHT_RED = "91"
    BRIGHT_GREEN = "92"
    BRIGHT_YELLOW = "93"
    BRIGHT_BLUE = "94"
    BRIGHT_MAGENTA = "95"
    BRIGHT_CYAN = "96"
    BRIGHT_WHITE = "97"
    
    # Background colors
    BG_BLACK = "40"
    BG_RED = "41"
    BG_GREEN = "42"
    BG_YELLOW = "43"
    BG_BLUE = "44"
    BG_MAGENTA = "45"
    BG_CYAN = "46"
    BG_WHITE = "47"


class Style(Enum):
    """Text styling options."""
    RESET = "0"
    BOLD = "1"
    DIM = "2"
    ITALIC = "3"
    UNDERLINE = "4"
    BLINK = "5"
    REVERSE = "7"
    HIDDEN = "8"
    STRIKETHROUGH = "9"


class ColorTheme(Enum):
    """Predefined color themes for different message types."""
    # Game events
    ALERT = ("bright_red", "bold")           # Critical warnings
    WARNING = ("yellow", "bold")              # Warnings
    SUCCESS = ("bright_green", "bold")        # Positive events
    INFO = ("cyan", None)                     # Information
    DEBUG = ("bright_black", "dim")           # Debug messages
    
    # Crew interactions
    CREW_THOUGHT = ("bright_cyan", None)      # Crew member thought/dialogue
    CREW_STRESS = ("bright_yellow", None)     # Stressed crew
    CREW_HAPPY = ("bright_green", None)       # Happy crew
    CREW_INJURED = ("bright_red", None)       # Injured crew
    
    # Game systems
    SONAR = ("bright_blue", None)             # Sonar contacts
    TORPEDO = ("bright_red", None)            # Torpedo activity
    DAMAGE = ("red", "bold")                  # Damage reports
    REPAIRS = ("green", None)                 # Repair activity
    SUPPLIES = ("yellow", None)               # Supply info
    
    # Navigation
    HEADING = ("bright_cyan", None)           # Heading/navigation
    DEPTH = ("blue", None)                    # Depth info
    POSITION = ("cyan", None)                 # Position info
    
    # UI Elements
    HEADER = ("bright_cyan", "bold")          # Section headers
    LABEL = ("white", "bold")                 # Labels
    VALUE = ("bright_white", None)            # Values/stats


class ColorSystem:
    """Central color management system."""
    
    def __init__(self, enabled: bool = True):
        """Initialize color system.
        
        Args:
            enabled: If False, colors are disabled (useful for logging/testing)
        """
        self.enabled = enabled
        self._color_map = {
            "black": Color.BLACK.value,
            "red": Color.RED.value,
            "green": Color.GREEN.value,
            "yellow": Color.YELLOW.value,
            "blue": Color.BLUE.value,
            "magenta": Color.MAGENTA.value,
            "cyan": Color.CYAN.value,
            "white": Color.WHITE.value,
            "bright_black": Color.BRIGHT_BLACK.value,
            "bright_red": Color.BRIGHT_RED.value,
            "bright_green": Color.BRIGHT_GREEN.value,
            "bright_yellow": Color.BRIGHT_YELLOW.value,
            "bright_blue": Color.BRIGHT_BLUE.value,
            "bright_magenta": Color.BRIGHT_MAGENTA.value,
            "bright_cyan": Color.BRIGHT_CYAN.value,
            "bright_white": Color.BRIGHT_WHITE.value,
        }
        self._style_map = {
            "bold": Style.BOLD.value,
            "dim": Style.DIM.value,
            "italic": Style.ITALIC.value,
            "underline": Style.UNDERLINE.value,
            "reverse": Style.REVERSE.value,
        }
    
    def colorize(self, text: str, color: Optional[str] = None, 
                 style: Optional[str] = None, bg_color: Optional[str] = None) -> str:
        """Apply color and styling to text.
        
        Args:
            text: Text to colorize
            color: Color name (e.g., "red", "bright_green")
            style: Style name (e.g., "bold", "dim")
            bg_color: Background color name
            
        Returns:
            Colored text with ANSI codes, or plain text if colors disabled
        """
        if not self.enabled or not text:
            return text
        
        codes = []
        
        if color and color in self._color_map:
            codes.append(self._color_map[color])
        
        if style and style in self._style_map:
            codes.append(self._style_map[style])
        
        if bg_color and bg_color in self._color_map:
            bg_code = bg_color.replace("bright_", "10")
            codes.append(bg_code)
        
        if not codes:
            return text
        
        code_str = ";".join(codes)
        return f"\033[{code_str}m{text}\033[0m"
    
    def theme(self, text: str, theme: ColorTheme) -> str:
        """Apply a predefined color theme to text.
        
        Args:
            text: Text to colorize
            theme: ColorTheme enum value
            
        Returns:
            Themed text with ANSI codes
        """
        # Parse theme (color, style) tuples
        color_name = theme.value[0] if theme.value else None
        style_name = theme.value[1] if len(theme.value) > 1 else None
        
        return self.colorize(text, color=color_name, style=style_name)
    
    def header(self, text: str) -> str:
        """Format text as a header."""
        return self.theme(text, ColorTheme.HEADER)
    
    def label(self, text: str) -> str:
        """Format text as a label."""
        return self.theme(text, ColorTheme.LABEL)
    
    def value(self, text: str) -> str:
        """Format text as a value."""
        return self.theme(text, ColorTheme.VALUE)
    
    def alert(self, text: str) -> str:
        """Format text as an alert."""
        return self.theme(text, ColorTheme.ALERT)
    
    def warning(self, text: str) -> str:
        """Format text as a warning."""
        return self.theme(text, ColorTheme.WARNING)
    
    def success(self, text: str) -> str:
        """Format text as success."""
        return self.theme(text, ColorTheme.SUCCESS)
    
    def info(self, text: str) -> str:
        """Format text as info."""
        return self.theme(text, ColorTheme.INFO)
    
    def crew_thought(self, text: str) -> str:
        """Format crew thought/dialogue."""
        return self.theme(text, ColorTheme.CREW_THOUGHT)
    
    def crew_stressed(self, text: str) -> str:
        """Format stressed crew message."""
        return self.theme(text, ColorTheme.CREW_STRESS)
    
    def crew_happy(self, text: str) -> str:
        """Format happy crew message."""
        return self.theme(text, ColorTheme.CREW_HAPPY)
    
    def sonar(self, text: str) -> str:
        """Format sonar message."""
        return self.theme(text, ColorTheme.SONAR)
    
    def torpedo(self, text: str) -> str:
        """Format torpedo message."""
        return self.theme(text, ColorTheme.TORPEDO)
    
    def damage(self, text: str) -> str:
        """Format damage message."""
        return self.theme(text, ColorTheme.DAMAGE)


# Global color system instance
_color_system = ColorSystem(enabled=True)


def colorize(text: str, color: Optional[str] = None, 
             style: Optional[str] = None) -> str:
    """Convenience function for coloring text."""
    return _color_system.colorize(text, color=color, style=style)


def get_color_system() -> ColorSystem:
    """Get the global color system instance."""
    return _color_system


def set_color_enabled(enabled: bool):
    """Enable or disable colors globally."""
    _color_system.enabled = enabled


def theme(text: str, theme_enum: ColorTheme) -> str:
    """Apply a theme to text."""
    return _color_system.theme(text, theme_enum)
