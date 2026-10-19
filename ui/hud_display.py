"""Enhanced HUD and dashboard displays for game status visualization.

Provides multiple view modes:
- Full dashboard (comprehensive system status)
- Quick status bar
- Detailed panel for specific systems
"""

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_INVERSE = "\033[7m"

COLOR_GREEN = "\033[38;5;46m"
COLOR_YELLOW = "\033[38;5;226m"
COLOR_RED = "\033[38;5;196m"
COLOR_CYAN = "\033[38;5;51m"
COLOR_WHITE = "\033[38;5;255m"
COLOR_GRAY = "\033[38;5;245m"
COLOR_BLUE = "\033[38;5;33m"


def get_status_color(value, thresholds=(0.5, 0.75)):
    """Return color based on value (0.0 to 1.0)."""
    low, high = thresholds
    if value >= high:
        return COLOR_GREEN
    elif value >= low:
        return COLOR_YELLOW
    else:
        return COLOR_RED


def get_status_bar(value, width=20, label=""):
    """Create a filled bar for status display."""
    filled = int(value * width)
    bar = '█' * filled + '░' * (width - filled)
    color = get_status_color(value)
    return f"{label}: {color}[{bar}]{ANSI_RESET} {value*100:.0f}%"


class DashboardView:
    """Comprehensive dashboard showing all game systems."""
    
    def render(self, game):
        """Render full dashboard."""
        lines = []
        
        lines.append(f"{ANSI_BOLD}{'═' * 120}{ANSI_RESET}")
        lines.append(f"{COLOR_WHITE}{ANSI_BOLD}COMMAND CENTER DASHBOARD{ANSI_RESET} - Turn {game.turn}")
        lines.append(f"{ANSI_BOLD}{'═' * 120}{ANSI_RESET}")
        lines.append("")
        
        # Top row: 3 columns
        col1 = self._render_submarine_status(game)
        col2 = self._render_compartment_status(game)
        col3 = self._render_crew_status(game)
        
        max_lines = max(len(col1), len(col2), len(col3))
        col_width = 38
        
        for i in range(max_lines):
            line = ""
            line += (col1[i] if i < len(col1) else "").ljust(col_width)
            line += " | "
            line += (col2[i] if i < len(col2) else "").ljust(col_width)
            line += " | "
            line += (col3[i] if i < len(col3) else "").ljust(col_width)
            lines.append(line)
        
        lines.append("")
        lines.append(f"{ANSI_BOLD}{'─' * 120}{ANSI_RESET}")
        lines.append("")
        
        # Bottom row: 2 columns
        col4 = self._render_weapons_status(game)
        col5 = self._render_sonar_contacts(game)
        
        max_lines = max(len(col4), len(col5))
        col_width = 58
        
        for i in range(max_lines):
            line = ""
            line += (col4[i] if i < len(col4) else "").ljust(col_width)
            line += " | "
            line += (col5[i] if i < len(col5) else "").ljust(col_width)
            lines.append(line)
        
        lines.append(f"{ANSI_BOLD}{'═' * 120}{ANSI_RESET}\n")
        
        return "\n".join(lines)
    
    def _render_submarine_status(self, game):
        """Submarine control status."""
        lines = []
        sub = game.submarine
        
        lines.append(f"{COLOR_CYAN}{ANSI_BOLD}SUBMARINE{ANSI_RESET}")
        lines.append(f"{'─' * 35}")
        
        heading = getattr(sub.systems, 'heading', 0)
        speed = getattr(sub.systems, 'speed', 0)
        depth = getattr(sub.systems, 'depth', 0)
        
        sub_name = getattr(sub, 'name', getattr(sub, 'submarine_name', 'U-Boat'))
        sub_nation = getattr(sub, 'nation', 'Unknown')
        
        lines.append(f"Name: {sub_name}")
        lines.append(f"Nation: {sub_nation}")
        lines.append("")
        
        lines.append(f"Heading: {heading:.0f}°")
        lines.append(f"Speed: {speed:.1f} knots")
        lines.append(f"Depth: {depth:.0f} meters")
        lines.append("")
        
        # Hull integrity
        if hasattr(sub, 'hull_integrity'):
            lines.append(get_status_bar(sub.hull_integrity, label="Hull"))
        
        # Engine status
        if hasattr(sub.systems, 'engine_power'):
            engine_health = getattr(sub.systems, 'engine_power', 1.0)
            lines.append(get_status_bar(engine_health, label="Engine"))
        
        # Battery
        if hasattr(sub.systems, 'battery_charge'):
            battery = getattr(sub.systems, 'battery_charge', 1.0)
            lines.append(get_status_bar(battery, label="Battery"))
        
        return lines
    
    def _render_compartment_status(self, game):
        """Compartment damage status."""
        lines = []
        
        lines.append(f"{COLOR_YELLOW}{ANSI_BOLD}COMPARTMENTS{ANSI_RESET}")
        lines.append(f"{'─' * 35}")
        
        if not hasattr(game.submarine, 'compartments'):
            lines.append("No compartment data")
            return lines
        
        total_compartments = len(game.submarine.compartments)
        damaged = sum(1 for c in game.submarine.compartments if c.integrity < 0.8)
        flooded = sum(1 for c in game.submarine.compartments if c.flooding > 0.1)
        
        lines.append(f"Total: {total_compartments}")
        lines.append(f"Damaged: {damaged}")
        lines.append(f"Flooded: {flooded}")
        lines.append("")
        
        # Show top 5 compartments
        for comp in game.submarine.compartments[:5]:
            status = '✓' if comp.integrity >= 0.8 else '⚠' if comp.integrity >= 0.5 else '✗'
            status_color = COLOR_GREEN if comp.integrity >= 0.8 else COLOR_YELLOW if comp.integrity >= 0.5 else COLOR_RED
            
            name = comp.name[:15].ljust(15)
            lines.append(f"{status_color}{status}{ANSI_RESET} {name} {comp.integrity*100:.0f}%")
        
        return lines
    
    def _render_crew_status(self, game):
        """Crew and personnel status."""
        lines = []
        
        lines.append(f"{COLOR_BLUE}{ANSI_BOLD}CREW{ANSI_RESET}")
        lines.append(f"{'─' * 35}")
        
        crew_list = getattr(game, 'crew', []) or (getattr(game.crew_roster, 'crew_members', {}) if hasattr(game, 'crew_roster') else [])
        if isinstance(crew_list, dict):
            crew_list = list(crew_list.values())
        
        if crew_list:
            total_crew = len(crew_list)
            alive_crew = sum(1 for c in crew_list if getattr(c, 'alive', True))
            injured_crew = sum(1 for c in crew_list if getattr(c, 'health', 1.0) < 0.8)
            
            lines.append(f"Total: {total_crew}")
            lines.append(f"Alive: {alive_crew}/{total_crew}")
            lines.append(f"Injured: {injured_crew}")
            lines.append("")
            
            # Crew morale
            if hasattr(game, 'crew_morale'):
                morale = game.crew_morale
                lines.append(get_status_bar(morale, label="Morale"))
            
            # Loyalty
            if hasattr(game, 'crew_loyalty'):
                loyalty = game.crew_loyalty
                lines.append(get_status_bar(loyalty, label="Loyalty"))
        
        # Commander status
        if hasattr(game, 'player'):
            lines.append("")
            lines.append(f"{COLOR_WHITE}Commander{ANSI_RESET}")
            
            level = getattr(game.player, 'level', 1)
            xp = getattr(game.player, 'xp', 0)
            lines.append(f"Level: {level}")
            lines.append(f"Experience: {xp} XP")
        
        return lines
    
    def _render_weapons_status(self, game):
        """Torpedo and ammunition status."""
        lines = []
        
        lines.append(f"{COLOR_RED}{ANSI_BOLD}WEAPONS{ANSI_RESET}")
        lines.append(f"{'─' * 55}")
        
        if hasattr(game.submarine, 'torpedoes'):
            torpedoes = game.submarine.torpedoes
            # Handle both list and dict formats
            if isinstance(torpedoes, dict):
                torpedo_list = list(torpedoes.values())
            else:
                torpedo_list = torpedoes if isinstance(torpedoes, list) else []
            
            total_torpedoes = len(torpedo_list)
            loaded_torpedoes = sum(1 for t in torpedo_list if getattr(t, 'loaded', False))
            ready_torpedoes = sum(1 for t in torpedo_list if getattr(t, 'ready', False))
            
            lines.append(f"Torpedoes: {loaded_torpedoes}/{total_torpedoes} loaded")
            lines.append(f"Ready to fire: {ready_torpedoes}")
            lines.append("")
            
            # Show torpedo types (first 6)
            torpedo_types = {}
            for t in torpedo_list[:8]:
                t_type = getattr(t, 'torpedo_type', 'Unknown')
                if t_type not in torpedo_types:
                    torpedo_types[t_type] = {'total': 0, 'loaded': 0}
                torpedo_types[t_type]['total'] += 1
                if getattr(t, 'loaded', False):
                    torpedo_types[t_type]['loaded'] += 1
            
            for t_type, counts in list(torpedo_types.items())[:6]:
                lines.append(f"  {t_type}: {counts['loaded']}/{counts['total']}")
        
        if hasattr(game.submarine, 'active_torpedoes'):
            in_water = len(game.submarine.active_torpedoes)
            if in_water > 0:
                lines.append("")
                lines.append(f"{COLOR_RED}In water: {in_water} torpedo(es){ANSI_RESET}")
        
        return lines
    
    def _render_sonar_contacts(self, game):
        """Detected sonar contacts."""
        lines = []
        
        lines.append(f"{COLOR_CYAN}{ANSI_BOLD}SONAR CONTACTS{ANSI_RESET}")
        lines.append(f"{'─' * 55}")
        
        if not hasattr(game, 'sonar_manager') or not game.sonar_manager:
            lines.append("Sonar system offline")
            return lines
        
        contacts = getattr(game.sonar_manager, 'detected_contacts', [])
        
        if not contacts:
            lines.append("No contacts detected")
        else:
            lines.append(f"Total contacts: {len(contacts)}")
            lines.append("")
            
            # Show each contact
            for i, contact in enumerate(contacts[:8]):
                bearing = getattr(contact, 'bearing', 0)
                range_m = getattr(contact, 'range', 0)
                quality = getattr(contact, 'quality', 0.5)
                
                contact_str = f"  {bearing:.0f}° | {range_m:.0f}m | "
                if hasattr(contact, 'contact_type'):
                    contact_str += str(contact.contact_type.name)[:10]
                
                quality_color = get_status_color(quality)
                contact_str += f" {quality_color}[{quality*100:.0f}%]{ANSI_RESET}"
                lines.append(contact_str)
        
        return lines


class StatusBar:
    """Quick one-line status bar."""
    
    @staticmethod
    def render(game):
        """Render compact status bar."""
        sub = game.submarine
        
        depth = getattr(sub.systems, 'depth', 0)
        speed = getattr(sub.systems, 'speed', 0)
        heading = getattr(sub.systems, 'heading', 0)
        
        # Torpedo count
        torpedoes = "0/0"
        if hasattr(sub, 'torpedoes'):
            loaded = sum(1 for t in sub.torpedoes if getattr(t, 'loaded', False))
            torpedoes = f"{loaded}/{len(sub.torpedoes)}"
        
        # Contact count
        contacts = 0
        if hasattr(game, 'sonar_manager') and game.sonar_manager:
            contacts = len(getattr(game.sonar_manager, 'detected_contacts', []))
        
        status = f"Turn {game.turn} | Depth {depth:.0f}m | Speed {speed:.1f}kt | Heading {heading:.0f}° | Torpedoes {torpedoes} | Contacts {contacts}"
        
        return f"{COLOR_CYAN}{status}{ANSI_RESET}"


class DetailedPanel:
    """Detailed view for a specific system."""
    
    @staticmethod
    def render_compartment_details(game):
        """Show detailed compartment breakdown."""
        lines = []
        
        lines.append(f"{ANSI_BOLD}{'═' * 80}{ANSI_RESET}")
        lines.append(f"{COLOR_YELLOW}{ANSI_BOLD}COMPARTMENT DAMAGE REPORT{ANSI_RESET}")
        lines.append(f"{ANSI_BOLD}{'─' * 80}{ANSI_RESET}")
        lines.append("")
        
        if not hasattr(game.submarine, 'compartments'):
            lines.append("No compartment data available")
            return "\n".join(lines)
        
        for comp in game.submarine.compartments:
            status = '✓ NORMAL' if comp.integrity >= 0.8 else '⚠ DAMAGED' if comp.integrity >= 0.5 else '✗ CRITICAL'
            status_color = COLOR_GREEN if comp.integrity >= 0.8 else COLOR_YELLOW if comp.integrity >= 0.5 else COLOR_RED
            
            lines.append(f"{status_color}{ANSI_BOLD}{comp.name}{ANSI_RESET}")
            lines.append(get_status_bar(comp.integrity, width=30, label="  Integrity"))
            
            if hasattr(comp, 'flooding') and comp.flooding > 0:
                lines.append(get_status_bar(min(comp.flooding, 1.0), width=30, label="  Flooding"))
            
            if hasattr(comp, 'crew'):
                lines.append(f"  Crew: {len(comp.crew)} personnel")
            
            lines.append("")
        
        lines.append(f"{ANSI_BOLD}{'═' * 80}{ANSI_RESET}\n")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_crew_details(game):
        """Show detailed crew roster."""
        lines = []
        
        lines.append(f"{ANSI_BOLD}{'═' * 80}{ANSI_RESET}")
        lines.append(f"{COLOR_BLUE}{ANSI_BOLD}CREW ROSTER{ANSI_RESET}")
        lines.append(f"{ANSI_BOLD}{'─' * 80}{ANSI_RESET}")
        lines.append("")
        
        crew_list = getattr(game, 'crew', []) or (getattr(game.crew_roster, 'crew_members', {}) if hasattr(game, 'crew_roster') else [])
        if isinstance(crew_list, dict):
            crew_list = list(crew_list.values())
        
        if not crew_list:
            lines.append("No crew data available")
            return "\n".join(lines)
        
        for crew_member in crew_list[:20]:  # Show first 20
            name = getattr(crew_member, 'name', 'Unknown')
            role = getattr(crew_member, 'role', 'Sailor')
            alive = getattr(crew_member, 'alive', True)
            health = getattr(crew_member, 'health', 1.0)
            
            status_symbol = '✓' if alive and health >= 0.8 else '⚠' if alive else '✗'
            status_color = COLOR_GREEN if (alive and health >= 0.8) else COLOR_YELLOW if alive else COLOR_RED
            
            lines.append(f"{status_color}{status_symbol}{ANSI_RESET} {name:20} | {role:15} | Health {health*100:.0f}%")
        
        lines.append(f"{ANSI_BOLD}{'═' * 80}{ANSI_RESET}\n")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_sonar_details(game):
        """Show detailed sonar info."""
        lines = []
        
        lines.append(f"{ANSI_BOLD}{'═' * 80}{ANSI_RESET}")
        lines.append(f"{COLOR_CYAN}{ANSI_BOLD}SONAR SYSTEM DETAILS{ANSI_RESET}")
        lines.append(f"{ANSI_BOLD}{'─' * 80}{ANSI_RESET}")
        lines.append("")
        
        if not hasattr(game, 'sonar_manager') or not game.sonar_manager:
            lines.append("Sonar system offline")
            return "\n".join(lines)
        
        sonar_mgr = game.sonar_manager
        lines.append(f"Active System: {getattr(sonar_mgr, 'current_sonar', 'Unknown')}")
        
        if hasattr(sonar_mgr, 'sonar_operator'):
            op = sonar_mgr.sonar_operator
            lines.append(f"Operator: {getattr(op, 'name', 'Unknown')}")
            lines.append(f"Fatigue: {getattr(op, 'fatigue', 0.0)*100:.1f}%")
            lines.append("")
        
        lines.append(f"{COLOR_CYAN}{ANSI_BOLD}DETECTED CONTACTS:{ANSI_RESET}")
        contacts = getattr(sonar_mgr, 'detected_contacts', [])
        
        if not contacts:
            lines.append("  No contacts")
        else:
            for contact in contacts:
                bearing = getattr(contact, 'bearing', 0)
                range_m = getattr(contact, 'range', 0)
                quality = getattr(contact, 'quality', 0.5)
                contact_type = getattr(contact, 'contact_type', 'Unknown')
                
                lines.append(f"  Bearing {bearing:3.0f}° | Range {range_m:6.0f}m | {contact_type.name:10} | Quality {quality*100:3.0f}%")
        
        lines.append(f"{ANSI_BOLD}{'═' * 80}{ANSI_RESET}\n")
        
        return "\n".join(lines)


def render_dashboard_mode(game):
    """Main entry point for dashboard display."""
    dashboard = DashboardView()
    return dashboard.render(game)


def render_status_bar(game):
    """Render quick status bar."""
    return StatusBar.render(game)
