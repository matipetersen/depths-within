"""Submarine compartment map display - visual representation of all compartments and their status."""

import math

# ANSI color codes
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"

# Colors for status
COLOR_GREEN = "\033[38;5;46m"       # Operational
COLOR_YELLOW = "\033[38;5;226m"     # Warning
COLOR_RED = "\033[38;5;196m"        # Critical/Danger
COLOR_DARK_RED = "\033[38;5;52m"    # Very critical
COLOR_GRAY = "\033[38;5;245m"       # Neutral
COLOR_BLUE = "\033[38;5;51m"        # Water/Flooding
COLOR_WHITE = "\033[38;5;255m"      # Text
COLOR_ORANGE = "\033[38;5;214m"     # Alert


def get_compartment_status_color(integrity: float, flooding: float) -> str:
    """Determine color based on compartment state."""
    if flooding > 0.7:
        # Critical flooding
        return COLOR_DARK_RED
    elif flooding > 0.4:
        # Severe flooding
        return COLOR_RED
    elif integrity < 0.3:
        # Heavily damaged
        return COLOR_RED
    elif integrity < 0.5:
        # Moderately damaged
        return COLOR_YELLOW
    elif flooding > 0.1:
        # Minor flooding
        return COLOR_YELLOW
    elif integrity < 0.8:
        # Minor damage
        return COLOR_YELLOW
    else:
        # Operational
        return COLOR_GREEN


def get_compartment_status_char(integrity: float, flooding: float) -> str:
    """Get a character representing compartment status."""
    if flooding > 0.7:
        return "⚠"  # Critical flooding
    elif flooding > 0.4:
        return "≈"  # Significant flooding
    elif flooding > 0.1:
        return "~"  # Minor flooding
    elif integrity < 0.3:
        return "✕"  # Heavily damaged
    elif integrity < 0.5:
        return "◐"  # Damaged
    elif integrity < 0.8:
        return "◑"  # Minor damage
    else:
        return "◉"  # Operational


class CompartmentMapDisplay:
    """Displays submarine compartment status in a visual map."""
    
    def __init__(self, width: int = 80):
        self.width = width
        self.compartment_width = 10
        self.compartment_height = 5
    
    def render(self, game) -> str:
        """Render the submarine compartment map."""
        output = []
        sub = game.submarine
        compartments = getattr(sub, 'compartments', [])
        
        if not compartments:
            return "No compartment data available"
        
        # Header
        output.append(f"{ANSI_BOLD}{'═' * self.width}{ANSI_RESET}")
        output.append(f"{COLOR_WHITE}{ANSI_BOLD}SUBMARINE COMPARTMENT MAP{ANSI_RESET} - {len(compartments)} compartments")
        output.append(f"{ANSI_BOLD}{'─' * self.width}{ANSI_RESET}")
        
        # Display compartments horizontally
        comp_lines = self._render_compartments_horizontal(compartments)
        output.extend(comp_lines)
        
        # Legend and status
        output.append(f"{ANSI_BOLD}{'─' * self.width}{ANSI_RESET}")
        legend_lines = self._render_legend()
        output.extend(legend_lines)
        
        # Statistics
        stats_lines = self._render_statistics(compartments)
        output.extend(stats_lines)
        
        output.append(f"{ANSI_BOLD}{'═' * self.width}{ANSI_RESET}\n")
        
        return "\n".join(output)
    
    def _render_compartments_horizontal(self, compartments: list) -> list:
        """Render compartments in a horizontal layout."""
        lines = []
        
        # Build the compartment boxes
        comp_box_lines = [[] for _ in range(self.compartment_height)]
        
        for comp in compartments:
            integrity = getattr(comp, 'integrity', 1.0)
            flooding = getattr(comp, 'flooding', 0.0)
            crew = getattr(comp, 'crew', [])
            
            color = get_compartment_status_color(integrity, flooding)
            status_char = get_compartment_status_char(integrity, flooding)
            
            # Build compartment box
            box = self._build_compartment_box(comp, color, status_char, integrity, flooding, crew)
            
            # Add to each line
            for i, line in enumerate(box):
                comp_box_lines[i].append(line)
        
        # Combine lines
        for line_parts in comp_box_lines:
            lines.append(" ".join(line_parts))
        
        # Add crew assignment indicators
        lines.append("")
        crew_line = self._render_crew_assignment(compartments)
        lines.append(crew_line)
        
        return lines
    
    def _build_compartment_box(self, comp, color: str, status_char: str, integrity: float, flooding: float, crew: list) -> list:
        """Build a single compartment display box."""
        box = []
        
        comp_name = comp.name[:10].ljust(10)[:10]
        
        # Line 1: Top border with status
        box.append(f"{color}┌─ {status_char} ─┐{ANSI_RESET}")
        
        # Line 2: Compartment name
        box.append(f"{color}│{ANSI_RESET}{COLOR_WHITE}{comp_name}{ANSI_RESET}{color}│{ANSI_RESET}")
        
        # Line 3: Integrity bar
        int_bar = self._build_bar(integrity, 8)
        box.append(f"{color}│{ANSI_RESET}{int_bar}{color}│{ANSI_RESET}")
        
        # Line 4: Flooding indicator
        flood_bar = self._build_flood_bar(flooding, 8)
        box.append(f"{color}│{ANSI_RESET}{flood_bar}{color}│{ANSI_RESET}")
        
        # Line 5: Crew count
        crew_str = f"Crew:{len(crew)}".ljust(8)
        crew_color = COLOR_GREEN if len(crew) > 0 else COLOR_GRAY
        box.append(f"{color}└{crew_color}{crew_str}{color}┘{ANSI_RESET}")
        
        return box
    
    def _build_bar(self, value: float, width: int) -> str:
        """Build a status bar."""
        filled = int(value * width)
        empty = width - filled
        
        if value >= 0.8:
            fill_color = COLOR_GREEN
        elif value >= 0.5:
            fill_color = COLOR_YELLOW
        else:
            fill_color = COLOR_RED
        
        bar = f"{fill_color}{'█' * filled}{ANSI_RESET}{COLOR_GRAY}{'░' * empty}{ANSI_RESET}"
        return bar
    
    def _build_flood_bar(self, value: float, width: int) -> str:
        """Build a flooding indicator bar."""
        filled = int(value * width)
        empty = width - filled
        
        if value <= 0.0:
            fill_color = COLOR_GREEN
        elif value <= 0.2:
            fill_color = COLOR_YELLOW
        else:
            fill_color = COLOR_RED
        
        bar = f"{fill_color}{'∿' * filled}{ANSI_RESET}{COLOR_GRAY}{'·' * empty}{ANSI_RESET}"
        return bar
    
    def _render_crew_assignment(self, compartments: list) -> str:
        """Show crew assignments per compartment."""
        line = "Crew Assignments: "
        for comp in compartments:
            crew = getattr(comp, 'crew', [])
            if crew:
                comp_short = comp.name[:4].upper()
                crew_count = len(crew)
                crew_names = ", ".join([getattr(c, 'name', f'Crew{i}')[:4] for i, c in enumerate(crew)])
                line += f"{comp_short}({crew_count}: {crew_names}) | "
        
        if line == "Crew Assignments: ":
            line += "No crew assigned to compartments"
        
        return line.rstrip(" | ")
    
    def _render_legend(self) -> list:
        """Render legend for compartment status."""
        lines = []
        lines.append("")
        lines.append(f"{ANSI_BOLD}STATUS INDICATORS:{ANSI_RESET}")
        lines.append(f"  {COLOR_GREEN}◉{ANSI_RESET} Operational (80%+)  |  {COLOR_YELLOW}◑{ANSI_RESET} Minor Damage  |  {COLOR_RED}◐{ANSI_RESET} Moderate Damage  |  {COLOR_RED}✕{ANSI_RESET} Heavy Damage")
        lines.append(f"  {COLOR_GREEN}·{ANSI_RESET} No Flooding  |  {COLOR_YELLOW}~{ANSI_RESET} Minor Flooding  |  {COLOR_RED}≈{ANSI_RESET} Moderate Flooding  |  {COLOR_DARK_RED}⚠{ANSI_RESET} Critical Flooding")
        lines.append("")
        
        return lines
    
    def _render_statistics(self, compartments: list) -> list:
        """Render overall submarine statistics."""
        lines = []
        
        total_integrity = sum(getattr(c, 'integrity', 1.0) for c in compartments) / len(compartments) if compartments else 1.0
        total_flooding = sum(getattr(c, 'flooding', 0.0) for c in compartments) / len(compartments) if compartments else 0.0
        total_crew = sum(len(getattr(c, 'crew', [])) for c in compartments)
        
        # Color based on overall status
        hull_color = COLOR_GREEN if total_integrity >= 0.8 else COLOR_YELLOW if total_integrity >= 0.5 else COLOR_RED
        flood_color = COLOR_GREEN if total_flooding <= 0.1 else COLOR_YELLOW if total_flooding <= 0.3 else COLOR_RED
        
        lines.append(f"{ANSI_BOLD}OVERALL SUBMARINE STATUS:{ANSI_RESET}")
        lines.append(f"  {ANSI_BOLD}Hull Integrity:{ANSI_RESET} {hull_color}{total_integrity:.0%}{ANSI_RESET}  |  {ANSI_BOLD}Average Flooding:{ANSI_RESET} {flood_color}{total_flooding:.0%}{ANSI_RESET}  |  {ANSI_BOLD}Crew Assigned:{ANSI_RESET} {total_crew}")
        
        # Show critical compartments
        critical = [c for c in compartments if getattr(c, 'integrity', 1.0) < 0.5 or getattr(c, 'flooding', 0.0) > 0.3]
        if critical:
            lines.append(f"")
            lines.append(f"  {COLOR_RED}{ANSI_BOLD}⚠ CRITICAL ISSUES:{ANSI_RESET}")
            for comp in critical:
                integrity = getattr(comp, 'integrity', 1.0)
                flooding = getattr(comp, 'flooding', 0.0)
                issues = []
                if integrity < 0.5:
                    issues.append(f"Damage {integrity:.0%}")
                if flooding > 0.3:
                    issues.append(f"Flooding {flooding:.0%}")
                if issues:
                    lines.append(f"    {COLOR_RED}→{ANSI_RESET} {comp.name}: {', '.join(issues)}")
        
        return lines


def render_compartment_map(game) -> str:
    """Convenience function to render compartment map."""
    display = CompartmentMapDisplay(width=120)
    return display.render(game)
