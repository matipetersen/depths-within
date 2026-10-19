"""
Hotkey system for WWII Submarine Roguelike.
Provides keyboard shortcuts for common commands and easy game control.
"""

from enum import Enum
from typing import Dict, Callable, Optional, Any


class HotkeyCategory(Enum):
    """Categories for organizing hotkeys."""
    NAVIGATION = "Navigation"
    COMBAT = "Combat"
    SYSTEMS = "Systems"
    CREW = "Crew"
    INFO = "Info"
    SUPPLIES = "Supplies"
    ESPIONAGE = "Espionage"
    ENCOUNTERS = "Encounters"
    GAME = "Game"


class Hotkey:
    """Represents a single hotkey binding."""
    
    def __init__(self, key: str, command: str, description: str, category: HotkeyCategory, 
                 alternative_keys: Optional[list] = None):
        self.key = key
        self.command = command
        self.description = description
        self.category = category
        self.alternative_keys = alternative_keys or []
    
    def matches(self, input_key: str) -> bool:
        """Check if input matches this hotkey."""
        return input_key.lower() == self.key.lower() or any(
            input_key.lower() == alt.lower() for alt in self.alternative_keys
        )
    
    def __repr__(self) -> str:
        keys = f"{self.key}"
        if self.alternative_keys:
            keys += f"/{'/'.join(self.alternative_keys)}"
        return f"{keys:6s} - {self.description}"


class HotkeySystem:
    """Manages all hotkeys and command dispatching."""
    
    def __init__(self):
        self.hotkeys: Dict[str, Hotkey] = {}
        self._initialize_hotkeys()
    
    def _initialize_hotkeys(self):
        """Initialize default hotkeys."""
        
        # NAVIGATION
        self.register(Hotkey("t", "tick", "Wait/Advance turn", HotkeyCategory.NAVIGATION))
        self.register(Hotkey("w", "wait", "Wait one turn", HotkeyCategory.NAVIGATION, ["Space"]))
        self.register(Hotkey("d", "dive", "Dive/Change depth", HotkeyCategory.NAVIGATION))
        self.register(Hotkey("s", "surface", "Surface", HotkeyCategory.NAVIGATION))
        
        # COMBAT
        self.register(Hotkey("f", "fire", "Fire torpedo", HotkeyCategory.COMBAT, ["Space"]))
        self.register(Hotkey("a", "aim", "Aim at target", HotkeyCategory.COMBAT))
        self.register(Hotkey("r", "sonar", "Scan sonar contacts", HotkeyCategory.COMBAT))
        
        # SYSTEMS
        self.register(Hotkey("c", "compartments", "Show compartment status", HotkeyCategory.SYSTEMS, ["i"]))
        self.register(Hotkey("p", "player_status", "Show player stats", HotkeyCategory.SYSTEMS))
        self.register(Hotkey("j", "journal", "Show journal/logs", HotkeyCategory.INFO, ["l"]))
        
        # CREW
        self.register(Hotkey("cr", "crew_list", "Show crew roster", HotkeyCategory.CREW))
        self.register(Hotkey("m", "crew_morale", "Show crew morale", HotkeyCategory.CREW))
        
        # INFO
        self.register(Hotkey("st", "status", "Show game status", HotkeyCategory.INFO))
        self.register(Hotkey("lo", "lore", "Read random crew story", HotkeyCategory.INFO))
        
        # SUPPLIES
        self.register(Hotkey("su", "supplies", "Show supply status", HotkeyCategory.SUPPLIES))
        self.register(Hotkey("ra", "ration_level", "Change rationing", HotkeyCategory.SUPPLIES))
        
        # ESPIONAGE
        self.register(Hotkey("sp", "spy_status", "Check for spies", HotkeyCategory.ESPIONAGE))
        self.register(Hotkey("es", "eliminate_spy", "Execute exposed spy", HotkeyCategory.ESPIONAGE))
        
        # ENCOUNTERS
        self.register(Hotkey("en", "encounter_status", "Check encounters", HotkeyCategory.ENCOUNTERS))
        self.register(Hotkey("re", "resolve_encounter", "Try to resolve encounter", HotkeyCategory.ENCOUNTERS))
        
        # SYSTEMS - Statistics
        self.register(Hotkey("sa", "stats", "Show game statistics", HotkeyCategory.SYSTEMS))
        
        # GAME
        self.register(Hotkey("h", "help", "Show help/hotkeys", HotkeyCategory.GAME, ["?"]))
        self.register(Hotkey("q", "quit", "Quit game", HotkeyCategory.GAME, ["Esc"]))
    
    def register(self, hotkey: Hotkey) -> None:
        """Register a hotkey."""
        self.hotkeys[hotkey.key] = hotkey
        for alt in hotkey.alternative_keys:
            self.hotkeys[alt] = hotkey
    
    def find_hotkey(self, input_key: str) -> Optional[Hotkey]:
        """Find a hotkey by input key."""
        input_lower = input_key.lower()
        for key, hotkey in self.hotkeys.items():
            if hotkey.matches(input_key):
                return hotkey
        return None
    
    def get_by_category(self, category: HotkeyCategory) -> list:
        """Get all hotkeys in a category."""
        seen = set()
        result = []
        for hotkey in self.hotkeys.values():
            if hotkey.category == category and hotkey.key not in seen:
                seen.add(hotkey.key)
                result.append(hotkey)
        return sorted(result, key=lambda h: h.key)
    
    def get_all_categories(self) -> list:
        """Get all categories with hotkeys."""
        categories = set()
        for hotkey in self.hotkeys.values():
            categories.add(hotkey.category)
        return sorted(categories, key=lambda c: c.value)
    
    def print_hotkeys(self, category: Optional[HotkeyCategory] = None) -> str:
        """Generate formatted hotkey help text."""
        lines = []
        
        if category:
            # Show specific category
            hotkeys = self.get_by_category(category)
            lines.append(f"\n{category.value} Commands:")
            lines.append("─" * 60)
            for hotkey in hotkeys:
                lines.append(f"  {hotkey}")
        else:
            # Show all categories
            lines.append("\n╔════════════════════════════════════════════════════════════╗")
            lines.append("║              SUBMARINE ROGUELIKE HOTKEYS                    ║")
            lines.append("╚════════════════════════════════════════════════════════════╝")
            
            for cat in self.get_all_categories():
                hotkeys = self.get_by_category(cat)
                lines.append(f"\n{cat.value}:")
                lines.append("─" * 60)
                for hotkey in hotkeys:
                    lines.append(f"  {hotkey}")
        
        return "\n".join(lines)
    
    def get_quick_reference(self) -> str:
        """Get a quick reference of the most important hotkeys."""
        lines = [
            "QUICK REFERENCE:",
            "─" * 40,
            "  [T] Wait  [D] Dive  [S] Surface",
            "  [F] Fire  [R] Sonar  [C] Compartments",
            "  [J] Journal  [M] Morale  [SU] Supplies",
            "  [SP] Spy Status  [EN] Encounters",
            "  [H] Help  [Q] Quit",
        ]
        return "\n".join(lines)


class QuickCommandParser:
    """Parses user input into commands with hotkey support."""
    
    def __init__(self, hotkey_system: HotkeySystem):
        self.hotkeys = hotkey_system
    
    def parse(self, user_input: str) -> tuple[Optional[str], list[str]]:
        """
        Parse user input and return (command, args).
        Returns (None, []) if input is invalid.
        
        Examples:
            "t" -> ("tick", [])
            "d 300" -> ("dive", ["300"])
            "ra strict" -> ("ration_level", ["strict"])
            "help" -> ("help", [])
        """
        if not user_input or not user_input.strip():
            return None, []
        
        parts = user_input.strip().split()
        input_key = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Try to find hotkey match
        hotkey = self.hotkeys.find_hotkey(input_key)
        if hotkey:
            return hotkey.command, args
        
        # If no hotkey match, treat as command name directly
        return input_key, args
    
    def should_auto_tick(self, command: Optional[str]) -> bool:
        """Determine if we should auto-tick after a command."""
        # Commands that don't auto-tick
        no_tick_commands = {
            "help", "status", "lore", "sonar", "crew_list", "crew_info",
            "player_status", "upgrades", "mission", "journal", "log_search",
            "crew_loyalty", "crew_morale", "rebellion_check", "war_status",
            "supplies", "resource_summary", "spy_status", "encounter_status",
            "compartments", "ascii", "color"
        }
        return command not in no_tick_commands if command else True


class GameUIHelper:
    """Helper for displaying game UI with hotkey hints."""
    
    def __init__(self, hotkey_system: HotkeySystem):
        self.hotkeys = hotkey_system
    
    def show_status_with_hints(self, game: 'Game', show_quick_ref: bool = True) -> str:
        """Generate status display with hotkey hints."""
        lines = []
        
        # Basic status
        lines.append(f"Turn: {game.turn} | Depth: {game.submarine.current_depth}m")
        lines.append(f"Crew: {game.crew_roster.crew_count if game.crew_roster else 0}")
        
        # Supply summary
        if game.supply_inventory:
            summary = game.supply_inventory.get_summary()
            oxygen_pct = summary.get(list(summary.keys())[0], 50)
            lines.append(f"Oxygen: {oxygen_pct:.0f}%")
        
        # Add quick reference
        if show_quick_ref:
            lines.append("")
            lines.append(self.hotkeys.get_quick_reference())
        
        return "\n".join(lines)
    
    def format_command_help(self, category: Optional[HotkeyCategory] = None) -> str:
        """Format help text for commands."""
        return self.hotkeys.print_hotkeys(category)

