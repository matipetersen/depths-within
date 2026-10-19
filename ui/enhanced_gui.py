"""Enhanced GUI with tactical map, submarine visualization, status dashboard, and legends.

This module provides comprehensive visualization of:
1. ASCII tile legend (depth zones, terrain, etc.)
2. Submarine compartment layout with status indicators
3. Control status dashboard (all controllable variables)
4. Visual feedback for compartment damage/issues
"""
import os
from enum import Enum


class DepthZone(Enum):
    """ASCII character mapping for depth zones."""
    SHALLOW = ('~', 'Shallow water (50-100m)')
    MODERATE = ('=', 'Moderate depth (100-150m)')
    DEEP = (',', 'Deep water (150-250m)')
    VERY_DEEP = (':', 'Very deep (250-400m)')
    ABYSSAL = ('.', 'Abyssal trench (400m+)')
    THERMOCLINE = ('*', 'Thermocline boundary')
    CONTACT = ('C', 'Ship/contact detected')
    AIRCRAFT = ('A', 'Aircraft')
    SUBMARINE = ('S', 'Your submarine')
    TORPEDO = ('T', 'Torpedo in water')


class CompartmentStatus(Enum):
    """Status indicators for compartments."""
    NORMAL = ('✓', '32', 'Normal operation')  # (symbol, ANSI color, description)
    DAMAGED = ('!', '31', 'Damaged - reduced capacity')  # red
    FLOODED = ('X', '35', 'Flooding - CRITICAL')  # magenta
    OFFLINE = ('-', '90', 'Offline - not operational')  # dark gray
    WARNING = ('⚠', '33', 'Warning - issues detected')  # yellow
    OVERLOAD = ('⬆', '31', 'Overload - reduce load')  # red


def get_ansi_color(code):
    """Return ANSI color escape sequence."""
    return f"\033[{code}m" if code else ""


ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"


class ASCIILegend:
    """Displays the ASCII tile legend for players."""
    
    @staticmethod
    def draw_tile_legend():
        """Return formatted tile legend."""
        lines = [
            f"{ANSI_BOLD}═══ TACTICAL MAP LEGEND ═══{ANSI_RESET}",
            "",
            f"  Depth Zones:",
            f"    {get_ansi_color('36')}~{ANSI_RESET} = Shallow (50-100m)",
            f"    {get_ansi_color('36')}={ANSI_RESET} = Moderate (100-150m)",
            f"    {get_ansi_color('36')},{ANSI_RESET} = Deep (150-250m)",
            f"    {get_ansi_color('36')}:{ANSI_RESET} = Very Deep (250-400m)",
            f"    {get_ansi_color('36')}·{ANSI_RESET} = Abyss (400m+)",
            "",
            f"  Contacts & Objects:",
            f"    {get_ansi_color('32')}C{ANSI_RESET} = Ship/Merchant contact",
            f"    {get_ansi_color('33')}E{ANSI_RESET} = Escort/Destroyer",
            f"    {get_ansi_color('31')}A{ANSI_RESET} = Aircraft",
            f"    {get_ansi_color('34')}S{ANSI_RESET} = Your Submarine",
            f"    {get_ansi_color('31')}T{ANSI_RESET} = Torpedo",
            f"    {get_ansi_color('35')}*{ANSI_RESET} = Thermocline",
            "",
            f"  Cursor Navigation:",
            f"    {get_ansi_color('33')}+{ANSI_RESET} = Your cursor position",
        ]
        return "\n".join(lines)
    
    @staticmethod
    def draw_command_legend():
        """Return formatted command reference for tactical mode."""
        lines = [
            f"{ANSI_BOLD}═══ HOTKEY REFERENCE ═══{ANSI_RESET}",
            "",
            f"  Navigation & Movement:",
            f"    {get_ansi_color('33')}↑/↓/←/→{ANSI_RESET} = Move cursor on map",
            f"    {get_ansi_color('33')}WASD{ANSI_RESET} = Move submarine (if enabled)",
            f"    {get_ansi_color('33')}D{ANSI_RESET} = Dive to depth",
            f"    {get_ansi_color('33')}S{ANSI_RESET} = Surface immediately",
            "",
            f"  Combat & Sonar:",
            f"    {get_ansi_color('33')}R{ANSI_RESET} = Active sonar ping",
            f"    {get_ansi_color('33')}F{ANSI_RESET} = Fire torpedo at cursor",
            f"    {get_ansi_color('33')}N{ANSI_RESET} = Cycle to next target",
            "",
            f"  Systems & Info:",
            f"    {get_ansi_color('33')}C{ANSI_RESET} = Show compartments",
            f"    {get_ansi_color('33')}P{ANSI_RESET} = Show status",
            f"    {get_ansi_color('33')}J{ANSI_RESET} = Show journal",
            f"    {get_ansi_color('33')}H{ANSI_RESET} = Show this help",
            "",
            f"  Volume Control:",
            f"    {get_ansi_color('33')}[{ANSI_RESET} = Decrease sonar sensitivity",
            f"    {get_ansi_color('33')}]{ANSI_RESET} = Increase sonar sensitivity",
        ]
        return "\n".join(lines)


class SubmarineVisual:
    """ASCII visualization of submarine compartments with status."""
    
    # Standard U-boat compartment layout (simplified for display)
    COMPARTMENT_LAYOUT = [
        ('Bow', 'Forward torpedo room'),
        ('Control', 'Central control room'),
        ('Engine', 'Diesel/electric engines'),
        ('Aft', 'Aft torpedo/storage'),
    ]
    
    @staticmethod
    def draw_submarine_status(submarine):
        """Return ASCII art of submarine with compartment status."""
        lines = []
        lines.append(f"{ANSI_BOLD}═══ SUBMARINE STATUS ═══{ANSI_RESET}")
        lines.append("")
        
        # Submarine name and stats
        sub_name = getattr(submarine, 'id', 'U-???')
        sub_class = getattr(submarine, 'class_name', 'Type VIIC')
        lines.append(f"  {ANSI_BOLD}Vessel: {sub_name} ({sub_class}){ANSI_RESET}")
        
        # Position and depth
        x = getattr(submarine, 'x', 0)
        y = getattr(submarine, 'y', 0)
        depth = getattr(submarine.systems, 'depth', 0) if hasattr(submarine, 'systems') else 0
        lines.append(f"  Position: ({x}, {y}) | Depth: {depth}m")
        lines.append("")
        
        # Draw submarine profile
        lines.append("  ┌─────────────────────────────────────────┐")
        
        # Get compartment statuses
        if hasattr(submarine, 'compartments'):
            compartments = submarine.compartments
            comp_display = []
            
            for comp in compartments:
                name = getattr(comp, 'name', 'Unknown')[:10]
                integrity = getattr(comp, 'integrity', 1.0)
                flooding = getattr(comp, 'flooding', 0.0)
                
                # Determine status
                if flooding > 0.5:
                    status_char = f"{get_ansi_color('35')}X{ANSI_RESET}"
                elif integrity < 0.3:
                    status_char = f"{get_ansi_color('31')}!{ANSI_RESET}"
                elif integrity < 0.6:
                    status_char = f"{get_ansi_color('33')}⚠{ANSI_RESET}"
                else:
                    status_char = f"{get_ansi_color('32')}✓{ANSI_RESET}"
                
                bar_len = 8
                filled = int((integrity / 1.0) * bar_len)
                bar = '█' * filled + '░' * (bar_len - filled)
                
                comp_line = f"  │ {status_char} {name:10s} │{bar}│"
                comp_display.append(comp_line)
            
            # Display compartments
            for comp_line in comp_display[:4]:  # Show first 4 compartments
                lines.append(comp_line)
            
            if len(comp_display) > 4:
                lines.append(f"  │  ... and {len(comp_display) - 4} more compartments")
        else:
            lines.append("  │  (Compartment system unavailable)")
        
        lines.append("  └─────────────────────────────────────────┘")
        lines.append("")
        
        return "\n".join(lines)


class ControlStatusDashboard:
    """Display all controllable submarine variables."""
    
    @staticmethod
    def draw_control_panel(submarine, supplies=None, crew_roster=None):
        """Return formatted control status dashboard."""
        lines = []
        lines.append(f"{ANSI_BOLD}═══ CONTROL STATUS DASHBOARD ═══{ANSI_RESET}")
        lines.append("")
        
        # Propulsion
        lines.append(f"  {ANSI_BOLD}PROPULSION{ANSI_RESET}")
        if hasattr(submarine, 'systems'):
            depth = getattr(submarine.systems, 'depth', 0)
            heading = getattr(submarine.systems, 'heading_deg', 0)
            speed = getattr(submarine.systems, 'speed', 0)
            battery = getattr(submarine.systems, 'battery', 0)
            
            # Depth indicator with visual
            depth_bar = SubmarineVisual._draw_bar(depth, max_val=400, width=15)
            lines.append(f"    Depth: {depth:3.0f}m  {depth_bar}")
            
            # Heading (compass)
            heading_compass = SubmarineVisual._heading_to_compass(heading)
            lines.append(f"    Heading: {heading_compass} ({heading:3.0f}°)")
            
            # Speed
            speed_bar = SubmarineVisual._draw_bar(speed, max_val=20, width=15)
            lines.append(f"    Speed: {speed:5.1f} kt  {speed_bar}")
            
            # Battery
            batt_color = get_ansi_color('32') if battery > 50 else get_ansi_color('33') if battery > 25 else get_ansi_color('31')
            batt_bar = SubmarineVisual._draw_bar(battery, max_val=100, width=15)
            lines.append(f"    Battery: {batt_color}{battery:6.1f}%{ANSI_RESET}  {batt_bar}")
        
        lines.append("")
        
        # Supplies (if available)
        if supplies:
            lines.append(f"  {ANSI_BOLD}SUPPLIES{ANSI_RESET}")
            if hasattr(supplies, 'oxygen_liters'):
                ox = supplies.oxygen_liters
                ox_bar = SubmarineVisual._draw_bar(ox, max_val=supplies.oxygen_capacity if hasattr(supplies, 'oxygen_capacity') else 1000, width=12)
                ox_color = get_ansi_color('32') if ox > 500 else get_ansi_color('33') if ox > 250 else get_ansi_color('31')
                lines.append(f"    O₂: {ox_color}{ox:6.0f}L{ANSI_RESET}  {ox_bar}")
            
            if hasattr(supplies, 'food_rations'):
                food = supplies.food_rations
                food_bar = SubmarineVisual._draw_bar(food, max_val=supplies.max_food_rations if hasattr(supplies, 'max_food_rations') else 100, width=12)
                food_color = get_ansi_color('32') if food > 50 else get_ansi_color('33') if food > 25 else get_ansi_color('31')
                lines.append(f"    Food: {food_color}{food:5.0f}{ANSI_RESET}  {food_bar}")
            
            if hasattr(supplies, 'fuel_liters'):
                fuel = supplies.fuel_liters
                fuel_bar = SubmarineVisual._draw_bar(fuel, max_val=supplies.fuel_capacity if hasattr(supplies, 'fuel_capacity') else 500, width=12)
                fuel_color = get_ansi_color('32') if fuel > 250 else get_ansi_color('33') if fuel > 100 else get_ansi_color('31')
                lines.append(f"    Fuel: {fuel_color}{fuel:6.0f}L{ANSI_RESET}  {fuel_bar}")
            
            if hasattr(supplies, 'ammunition'):
                ammo = supplies.ammunition
                ammo_bar = SubmarineVisual._draw_bar(ammo, max_val=supplies.max_ammunition if hasattr(supplies, 'max_ammunition') else 24, width=12)
                lines.append(f"    Ammo: {ammo:2.0f} torpedoes  {ammo_bar}")
        
        lines.append("")
        
        # Crew status (if available)
        if crew_roster:
            lines.append(f"  {ANSI_BOLD}CREW STATUS{ANSI_RESET}")
            crew_count = getattr(crew_roster, 'current_crew_count', 0) if hasattr(crew_roster, 'current_crew_count') else len(getattr(crew_roster, 'crew', []))
            max_crew = getattr(crew_roster, 'max_crew', 50)
            crew_bar = SubmarineVisual._draw_bar(crew_count, max_val=max_crew, width=12)
            lines.append(f"    Personnel: {crew_count}/{max_crew}  {crew_bar}")
            
            # Morale summary (if available)
            if hasattr(crew_roster, 'crew'):
                avg_morale = 0
                stress_count = 0
                try:
                    for crew_member in crew_roster.crew:
                        avg_morale += getattr(crew_member, 'morale', 50)
                        if getattr(crew_member, 'stress', 0) > 75:
                            stress_count += 1
                    if crew_roster.crew:
                        avg_morale /= len(crew_roster.crew)
                    
                    morale_color = get_ansi_color('32') if avg_morale > 60 else get_ansi_color('33') if avg_morale > 40 else get_ansi_color('31')
                    lines.append(f"    Morale: {morale_color}{avg_morale:5.1f}{ANSI_RESET}  (Stressed: {stress_count})")
                except Exception:
                    pass
        
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _draw_bar(current, max_val=100, width=20, filled_char='█', empty_char='░'):
        """Draw a progress bar."""
        if max_val <= 0:
            return ""
        percentage = min(100, (current / max_val) * 100)
        filled = int((percentage / 100) * width)
        empty = width - filled
        
        # Color based on percentage
        if percentage > 66:
            color = get_ansi_color('32')  # green
        elif percentage > 33:
            color = get_ansi_color('33')  # yellow
        else:
            color = get_ansi_color('31')  # red
        
        bar = f"{color}{filled_char * filled}{ANSI_RESET}{empty_char * empty}"
        return f"[{bar}] {percentage:5.1f}%"
    
    @staticmethod
    def _heading_to_compass(degrees):
        """Convert heading degrees to compass direction."""
        compass = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                   'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        idx = int((degrees + 11.25) / 22.5) % 16
        return compass[idx]


class CompartmentHighlighter:
    """Highlights compartment issues in the main display."""
    
    @staticmethod
    def get_compartment_status_line(compartment):
        """Return colored status line for a single compartment."""
        name = getattr(compartment, 'name', 'Unknown')
        integrity = getattr(compartment, 'integrity', 1.0)
        flooding = getattr(compartment, 'flooding', 0.0)
        pressure = getattr(compartment, 'pressure', 0.0)
        
        # Determine status and color
        if flooding > 0.5:
            status = f"{get_ansi_color('35')}FLOODING CRITICAL{ANSI_RESET}"
            icon = "⚠⚠⚠"
        elif integrity < 0.3:
            status = f"{get_ansi_color('31')}SEVERELY DAMAGED{ANSI_RESET}"
            icon = "!!!"
        elif integrity < 0.6:
            status = f"{get_ansi_color('33')}DAMAGED{ANSI_RESET}"
            icon = "! !"
        elif flooding > 0:
            status = f"{get_ansi_color('33')}MINOR LEAK{ANSI_RESET}"
            icon = "..."
        elif pressure > 100:
            status = f"{get_ansi_color('33')}HIGH PRESSURE{ANSI_RESET}"
            icon = "⬆⬆"
        else:
            status = f"{get_ansi_color('32')}NOMINAL{ANSI_RESET}"
            icon = "✓"
        
        # Build status line
        line = f"  {icon} {name:15s} | Integrity: {integrity*100:5.1f}% | Flooding: {flooding*100:5.1f}% | Status: {status}"
        return line
    
    @staticmethod
    def draw_compartment_status(submarine):
        """Return formatted compartment status with all issues highlighted."""
        lines = []
        lines.append(f"{ANSI_BOLD}═══ COMPARTMENT STATUS REPORT ═══{ANSI_RESET}")
        lines.append("")
        
        if hasattr(submarine, 'compartments'):
            for comp in submarine.compartments:
                lines.append(CompartmentHighlighter.get_compartment_status_line(comp))
            
            # Summary section
            lines.append("")
            total_flooding = sum(getattr(c, 'flooding', 0) for c in submarine.compartments)
            avg_integrity = sum(getattr(c, 'integrity', 1.0) for c in submarine.compartments) / max(1, len(submarine.compartments))
            
            if total_flooding > 0.5:
                lines.append(f"{get_ansi_color('31')}{ANSI_BOLD}WARNING: CRITICAL FLOODING IN MULTIPLE COMPARTMENTS{ANSI_RESET}")
            elif avg_integrity < 0.5:
                lines.append(f"{get_ansi_color('33')}{ANSI_BOLD}CAUTION: STRUCTURAL DAMAGE DETECTED{ANSI_RESET}")
            else:
                lines.append(f"{get_ansi_color('32')}All systems nominal{ANSI_RESET}")
        else:
            lines.append("  (No compartment data available)")
        
        return "\n".join(lines)


def draw_full_enhanced_gui(game, cursor=None, use_color=True):
    """Draw complete enhanced GUI with all components.
    
    Shows in sequence:
    1. Tactical map with depth visualization
    2. ASCII tile legend
    3. Submarine compartment visualization
    4. Control status dashboard
    5. Compartment status with issues highlighted
    6. Command reference
    """
    import os
    
    # Clear screen on Unix
    try:
        os.system('clear' if os.name != 'nt' else 'cls')
    except:
        pass
    
    CSI = "\x1b[" if use_color else ""
    HEADER = f"{CSI}1;36m" if use_color else ""
    RESET = f"{CSI}0m" if use_color else ""
    
    sections = []
    
    # 1. Tactical Map (from original ASCII GUI)
    try:
        from ui.ascii_gui import draw_ascii_console
        # Capture the original tactical map
        sections.append(f"{HEADER}╔═══ TACTICAL MAP ═══╗{RESET}")
        sections.append("")
        # We'll render this separately via draw_ascii_console
    except:
        pass
    
    # 2. Tile Legend
    sections.append(ASCIILegend.draw_tile_legend())
    sections.append("")
    
    # 3. Submarine Status
    if hasattr(game, 'submarine'):
        sections.append(SubmarineVisual.draw_submarine_status(game.submarine))
    
    # 4. Control Panel
    supplies = getattr(game, 'supply_inventory', None)
    crew = getattr(game, 'crew_roster', None)
    if hasattr(game, 'submarine'):
        sections.append(ControlStatusDashboard.draw_control_panel(game.submarine, supplies, crew))
    
    # 5. Compartment Issues
    if hasattr(game, 'submarine'):
        sections.append(CompartmentHighlighter.draw_compartment_status(game.submarine))
    
    sections.append("")
    
    # 6. Command Reference
    sections.append(ASCIILegend.draw_command_legend())
    
    # Print all sections
    print("\n".join(sections))
