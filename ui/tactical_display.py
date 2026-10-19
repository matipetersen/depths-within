"""Enhanced tactical display system with real-time map, contacts, and HUD.

Provides a full graphical view using ASCII art with color, showing:
- Tactical map centered on submarine
- Contact positions with bearings and ranges
- Depth zones and thermocline
- Real-time submarine orientation
- HUD with speed, depth, heading
"""

import math
from enum import Enum

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_INVERSE = "\033[7m"

# Color codes (using 256-color terminal)
COLOR_DEEP_BLUE = "\033[38;5;17m"      # Deep ocean blue
COLOR_CYAN = "\033[38;5;51m"           # Cyan for thermocline
COLOR_LIGHT_BLUE = "\033[38;5;153m"    # Light blue for contacts
COLOR_RED = "\033[38;5;196m"           # Red for threats
COLOR_DARK_RED = "\033[38;5;52m"       # Dark red for critical
COLOR_GREEN = "\033[38;5;46m"          # Green for friendlies
COLOR_YELLOW = "\033[38;5;226m"        # Yellow for warnings
COLOR_GRAY = "\033[38;5;245m"          # Gray for text
COLOR_WHITE = "\033[38;5;255m"         # White for important


class DepthLevel(Enum):
    SURFACE = (0, 50, '~', COLOR_LIGHT_BLUE)
    SHALLOW = (50, 100, '≈', COLOR_CYAN)
    MODERATE = (100, 150, '=', COLOR_DEEP_BLUE)
    DEEP = (150, 250, '≡', COLOR_DEEP_BLUE)
    VERY_DEEP = (250, 400, '≋', COLOR_DEEP_BLUE)
    ABYSSAL = (400, float('inf'), '∿', COLOR_DEEP_BLUE)


class ContactType(Enum):
    MERCHANT = ('C', COLOR_YELLOW, 'Merchant vessel')
    WARSHIP = ('W', COLOR_RED, 'Warship/Destroyer')
    ESCORT = ('E', COLOR_RED, 'Escort')
    AIRCRAFT = ('A', COLOR_RED, 'Aircraft')
    SUBMARINE = ('S', COLOR_GREEN, 'Submarine')
    UNKNOWN = ('?', COLOR_GRAY, 'Unknown contact')


def get_depth_char(depth):
    """Get ASCII character and color for depth."""
    for level in DepthLevel:
        min_d, max_d, char, color = level.value
        if min_d <= depth < max_d:
            return char, color
    return '∿', COLOR_DEEP_BLUE


def bearing_to_vector(bearing_deg, distance):
    """Convert bearing and distance to x, y offset."""
    # Bearing: 0° = North (up), 90° = East (right), 180° = South, 270° = West
    rad = math.radians(bearing_deg)
    y = -int(distance * math.cos(rad) / 100)  # Negative because up is negative
    x = int(distance * math.sin(rad) / 100)
    return x, y


class TacticalDisplay:
    """Main tactical map display with real-time updates."""
    
    def __init__(self, width=120, height=35):
        self.width = width
        self.height = height
        self.map_width = width - 25  # Reserve right side for HUD
        self.map_height = height - 10  # Reserve bottom for details
        self.map_center_x = self.map_width // 2
        self.map_center_y = self.map_height // 2
        
    def _clear_map(self):
        """Create blank map filled with water."""
        return [[(' ', COLOR_DEEP_BLUE) for _ in range(self.map_width)] for _ in range(self.map_height)]
    
    def _get_depth_char_at(self, game, sub_depth):
        """Get character for background based on depth."""
        char, color = get_depth_char(sub_depth)
        return char, color
    
    def _render_background(self, game_map, game):
        """Fill map background with depth-appropriate characters."""
        char, color = self._get_depth_char_at(game, game.submarine.systems.depth)
        
        for y in range(self.map_height):
            for x in range(self.map_width):
                game_map[y][x] = (char, color)
        
        return game_map
    
    def _render_thermocline(self, game_map, game=None):
        """Draw thermocline line if relevant."""
        if game and hasattr(game, 'world') and hasattr(game.world, 'thermocline_depth'):
            # Simplified: draw as a visual indicator
            pass
        return game_map
    
    def _render_submarine(self, game_map, game):
        """Draw submarine at center of map with compartment visualization."""
        x, y = self.map_center_x, self.map_center_y
        
        # Draw submarine compartment layout (simplified)
        sub = game.submarine
        compartments = getattr(sub, 'compartments', [])
        
        # Create compartment visualization if available
        if compartments:
            # Draw submarine as a row of compartments
            comp_start_x = x - len(compartments) // 2
            for i, comp in enumerate(compartments[:7]):  # Show up to 7 compartments
                comp_x = comp_start_x + i
                
                if 0 <= y < self.map_height and 0 <= comp_x < self.map_width:
                    # Color based on integrity
                    integrity = getattr(comp, 'integrity', 1.0)
                    flooding = getattr(comp, 'flooding', 0.0)
                    
                    if flooding > 0.5:
                        # Flooded
                        char, color = '█', COLOR_RED
                    elif integrity < 0.3:
                        # Damaged
                        char, color = '▓', COLOR_RED
                    elif integrity < 0.7:
                        # Damaged but functional
                        char, color = '▒', COLOR_YELLOW
                    else:
                        # Operational
                        char, color = '█', COLOR_GREEN
                    
                    game_map[y][comp_x] = (char, color)
        else:
            # Fallback: simple submarine shape
            if 0 <= y < self.map_height and 0 <= x < self.map_width:
                game_map[y][x] = ('@', COLOR_GREEN)
        
        # Draw heading indicator
        heading = getattr(game.submarine.systems, 'heading', 0)
        rad = math.radians(heading)
        indicator_dist = 2
        ind_x = x + int(indicator_dist * math.sin(rad))
        ind_y = y - int(indicator_dist * math.cos(rad))
        
        if 0 <= ind_y < self.map_height and 0 <= ind_x < self.map_width:
            game_map[ind_y][ind_x] = ('▲', COLOR_GREEN)
        
        return game_map
    
    def _render_contacts(self, game_map, game):
        """Render sonar contacts on map."""
        if not hasattr(game, 'sonar_manager') or not game.sonar_manager:
            return game_map
        
        # Get contacts from sonar
        contacts = getattr(game.sonar_manager, 'detected_contacts', [])
        
        for contact in contacts:
            if not hasattr(contact, 'bearing') or not hasattr(contact, 'range'):
                continue
            
            # Calculate position relative to submarine
            offset_x, offset_y = bearing_to_vector(contact.bearing, contact.range)
            map_x = self.map_center_x + offset_x
            map_y = self.map_center_y + offset_y
            
            # Clamp to map bounds
            if 0 <= map_y < self.map_height and 0 <= map_x < self.map_width:
                contact_type = ContactType.UNKNOWN
                try:
                    if hasattr(contact, 'contact_type'):
                        contact_type = contact.contact_type
                except:
                    pass
                
                char, color = contact_type.value[0:2]
                game_map[map_y][map_x] = (char, color)
        
        return game_map
    
    def _render_torpedoes(self, game_map, game):
        """Render active torpedoes on map."""
        if not hasattr(game.submarine, 'active_torpedoes'):
            return game_map
        
        for torpedo in game.submarine.active_torpedoes:
            if not hasattr(torpedo, 'x') or not hasattr(torpedo, 'y'):
                continue
            
            offset_x = torpedo.x - game.submarine.x if hasattr(game.submarine, 'x') else 0
            offset_y = torpedo.y - game.submarine.y if hasattr(game.submarine, 'y') else 0
            
            map_x = self.map_center_x + offset_x // 100
            map_y = self.map_center_y + offset_y // 100
            
            if 0 <= map_y < self.map_height and 0 <= map_x < self.map_width:
                game_map[map_y][map_x] = ('T', COLOR_YELLOW)
        
        return game_map
    
    def _render_compartment_status_bar(self, game):
        """Render a status bar showing all compartments at a glance."""
        lines = []
        sub = game.submarine
        compartments = getattr(sub, 'compartments', [])
        
        if not compartments:
            return []
        
        # Compartment overview line
        comp_line = f"{COLOR_WHITE}{ANSI_BOLD}═ COMPARTMENTS ═{ANSI_RESET}  "
        
        for comp in compartments:
            integrity = getattr(comp, 'integrity', 1.0)
            flooding = getattr(comp, 'flooding', 0.0)
            crew = getattr(comp, 'crew', [])
            
            # Determine color and symbol
            if flooding > 0.5:
                color = COLOR_DARK_RED if flooding > 0.7 else COLOR_RED
                symbol = "⚠"
            elif integrity < 0.3:
                color = COLOR_RED
                symbol = "✕"
            elif integrity < 0.5:
                color = COLOR_YELLOW
                symbol = "◐"
            elif integrity < 0.8:
                color = COLOR_YELLOW
                symbol = "◑"
            else:
                color = COLOR_GREEN
                symbol = "◉"
            
            # Format compartment indicator
            comp_short = comp.name[:3].upper()
            crew_count = len(crew)
            comp_display = f"{color}{symbol} {comp_short}({crew_count}){ANSI_RESET}"
            comp_line += comp_display + " │ "
        
        lines.append(comp_line.rstrip(" │ "))
        
        # Details line: show issues
        issues = []
        for comp in compartments:
            integrity = getattr(comp, 'integrity', 1.0)
            flooding = getattr(comp, 'flooding', 0.0)
            
            if flooding > 0.3:
                issues.append(f"{COLOR_RED}{comp.name}: Flooding {flooding:.0%}{ANSI_RESET}")
            elif integrity < 0.5:
                issues.append(f"{COLOR_YELLOW}{comp.name}: Damage {(1-integrity):.0%}{ANSI_RESET}")
        
        if issues:
            lines.append(f"{COLOR_WHITE}{ANSI_BOLD}⚠ ISSUES:{ANSI_RESET}  " + " | ".join(issues))
        
        return lines
    
    def _render_legend(self):
        """Return formatted map legend."""
        lines = [
            f"{COLOR_WHITE}{ANSI_BOLD}═══ CONTACT LEGEND ═══{ANSI_RESET}",
            f"  {COLOR_GREEN}@{ANSI_RESET} Your U-Boat",
            f"  {COLOR_YELLOW}C{ANSI_RESET} Merchant ship",
            f"  {COLOR_RED}W{ANSI_RESET} Warship",
            f"  {COLOR_RED}E{ANSI_RESET} Escort",
            f"  {COLOR_RED}A{ANSI_RESET} Aircraft",
            f"  {COLOR_YELLOW}T{ANSI_RESET} Torpedo",
        ]
        return lines
    
    def _render_compass(self):
        """Return simple compass indicator."""
        return [
            "  N",
            "W + E",
            "  S"
        ]
    
    def render(self, game):
        """Render complete tactical display."""
        output = []
        
        # Get depth info
        depth = game.submarine.systems.depth
        depth_char, depth_color = get_depth_char(depth)
        
        # Calculate depth zone
        if depth < 50:
            depth_zone = "SURFACE"
        elif depth < 100:
            depth_zone = "SHALLOW"
        elif depth < 150:
            depth_zone = "MODERATE"
        elif depth < 250:
            depth_zone = "DEEP"
        elif depth < 400:
            depth_zone = "VERY DEEP"
        else:
            depth_zone = "ABYSSAL"
        
        output.append(f"{ANSI_BOLD}{'═' * self.width}{ANSI_RESET}")
        output.append(f"{COLOR_WHITE}{ANSI_BOLD}TACTICAL MAP{ANSI_RESET} - Turn {game.turn} | {depth_color}{ANSI_BOLD}Depth {depth:.0f}m ({depth_zone}){ANSI_RESET} | {depth_color}{depth_char}{ANSI_RESET}")
        output.append(f"{ANSI_BOLD}{'─' * self.width}{ANSI_RESET}")
        
        # Create and render map
        game_map = self._clear_map()
        game_map = self._render_background(game_map, game)
        game_map = self._render_thermocline(game_map, game)
        game_map = self._render_contacts(game_map, game)
        game_map = self._render_torpedoes(game_map, game)
        game_map = self._render_submarine(game_map, game)
        
        # Render map to string with right-side HUD
        hud_lines = self._render_hud(game)
        legend_lines = self._render_legend()
        compass_lines = self._render_compass()
        
        max_hud_lines = max(len(hud_lines), len(legend_lines) + len(compass_lines) + 5)
        
        # Combine map and HUD
        for y in range(self.map_height):
            line = ""
            # Map section
            for x in range(self.map_width):
                char, color = game_map[y][x]
                line += f"{color}{char}{ANSI_RESET}"
            
            # HUD section
            line += " "
            if y < len(hud_lines):
                line += hud_lines[y]
            
            output.append(line)
        
        # Add legend and compass below map
        output.append(f"{ANSI_BOLD}{'─' * self.width}{ANSI_RESET}")
        
        # Legend and compass side by side
        legend_start = len(output)
        for i, line in enumerate(legend_lines):
            if legend_start + i < len(output):
                output[legend_start + i] += "  " + line
            else:
                output.append("  " * (self.map_width // 2) + line)
        
        # Add compartment status bar
        output.append(f"{ANSI_BOLD}{'─' * self.width}{ANSI_RESET}")
        comp_lines = self._render_compartment_status_bar(game)
        output.extend(comp_lines)
        
        output.append(f"{ANSI_BOLD}{'═' * self.width}{ANSI_RESET}\n")
        
        return "\n".join(output)
    
    def _render_hud(self, game):
        """Render heads-up display with system status."""
        lines = []
        sub = game.submarine
        
        # Heading and speed
        heading = getattr(sub.systems, 'heading', 0)
        speed = getattr(sub.systems, 'speed', 0)
        depth = getattr(sub.systems, 'depth', 0)
        
        lines.append(f"{COLOR_WHITE}{ANSI_BOLD}═ SYSTEMS ═{ANSI_RESET}")
        lines.append(f"Heading: {heading:.0f}°")
        lines.append(f"Speed:   {speed:.1f} kt")
        lines.append(f"Depth:   {depth:.0f}m")
        lines.append("")
        
        # Compartment status
        lines.append(f"{COLOR_WHITE}{ANSI_BOLD}═ COMPARTMENTS ═{ANSI_RESET}")
        if hasattr(sub, 'compartments'):
            for comp in sub.compartments[:4]:  # Show first 4
                status_char = '✓' if comp.integrity >= 0.8 else '⚠' if comp.integrity >= 0.5 else '✗'
                status_color = COLOR_GREEN if comp.integrity >= 0.8 else COLOR_YELLOW if comp.integrity >= 0.5 else COLOR_RED
                lines.append(f"{status_color}{status_char}{ANSI_RESET} {comp.name}: {comp.integrity:.0%}")
        
        lines.append("")
        
        # Torpedoes
        lines.append(f"{COLOR_WHITE}{ANSI_BOLD}═ ARMAMENT ═{ANSI_RESET}")
        if hasattr(sub, 'torpedoes'):
            loaded = sum(1 for t in sub.torpedoes if getattr(t, 'loaded', False))
            lines.append(f"Torpedoes: {loaded}/{len(sub.torpedoes)}")
        
        if hasattr(sub, 'active_torpedoes'):
            lines.append(f"In Water: {len(sub.active_torpedoes)}")
        
        lines.append("")
        
        # Crew status
        lines.append(f"{COLOR_WHITE}{ANSI_BOLD}═ CREW ═{ANSI_RESET}")
        if hasattr(game, 'crew'):
            alive_count = sum(1 for c in game.crew if getattr(c, 'alive', True))
            lines.append(f"Personnel: {alive_count}/{len(game.crew)}")
        
        if hasattr(game, 'player'):
            xp = getattr(game.player, 'xp', 0)
            level = getattr(game.player, 'level', 1)
            lines.append(f"Cmdr Level: {level} ({xp} XP)")
        
        lines.append("")
        
        # Sonar status
        lines.append(f"{COLOR_WHITE}{ANSI_BOLD}═ SONAR ═{ANSI_RESET}")
        if hasattr(game, 'sonar_manager') and game.sonar_manager:
            contacts = len(getattr(game.sonar_manager, 'detected_contacts', []))
            lines.append(f"Contacts: {contacts}")
            sonar_type = getattr(game.sonar_manager, 'current_sonar', 'Unknown')
            if hasattr(sonar_type, 'name'):
                lines.append(f"System: {sonar_type.name}")
        
        return lines


class SonarView:
    """Circular sonar display (alternative tactical view)."""
    
    def __init__(self, width=40, height=25):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.max_range = 200  # Display range in km
    
    def render(self, game):
        """Render circular sonar view."""
        output = []
        
        # Create sonar display grid
        sonar_map = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw concentric circles (range rings)
        for ring_distance in [50, 100, 150, 200]:
            radius = int(ring_distance * self.width / (2 * self.max_range))
            for angle in range(0, 360, 15):
                x = int(self.center_x + radius * math.sin(math.radians(angle)))
                y = int(self.center_y - radius * math.cos(math.radians(angle)))
                if 0 <= y < self.height and 0 <= x < self.width:
                    sonar_map[y][x] = '·'
        
        # Draw cardinal directions
        sonar_map[1][self.center_x] = 'N'
        sonar_map[self.height - 2][self.center_x] = 'S'
        sonar_map[self.center_y][self.width - 2] = 'E'
        sonar_map[self.center_y][1] = 'W'
        
        # Place submarine at center
        sonar_map[self.center_y][self.center_x] = '@'
        
        # Plot contacts
        if hasattr(game, 'sonar_manager') and game.sonar_manager:
            contacts = getattr(game.sonar_manager, 'detected_contacts', [])
            for contact in contacts:
                if hasattr(contact, 'bearing') and hasattr(contact, 'range'):
                    radius = int(contact.range * self.width / (2 * self.max_range))
                    x = int(self.center_x + radius * math.sin(math.radians(contact.bearing)))
                    y = int(self.center_y - radius * math.cos(math.radians(contact.bearing)))
                    
                    if 0 <= y < self.height and 0 <= x < self.width:
                        sonar_map[y][x] = 'C'
        
        # Render to output
        output.append(f"{ANSI_BOLD}{'═' * self.width}{ANSI_RESET}")
        output.append(f"{COLOR_WHITE}{ANSI_BOLD}SONAR DISPLAY{ANSI_RESET} - {game.submarine.systems.depth:.0f}m")
        output.append(f"{ANSI_BOLD}{'─' * self.width}{ANSI_RESET}")
        
        for row in sonar_map:
            output.append(f"{COLOR_CYAN}{''.join(row)}{ANSI_RESET}")
        
        output.append(f"{ANSI_BOLD}{'═' * self.width}{ANSI_RESET}\n")
        
        return "\n".join(output)


def render_tactical_mode(game):
    """Main entry point for tactical display."""
    display = TacticalDisplay(width=120, height=35)
    return display.render(game)


def render_sonar_mode(game):
    """Entry point for sonar-only display."""
    display = SonarView(width=40, height=25)
    return display.render(game)
