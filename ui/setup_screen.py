"""Initial game setup screen for faction and crew selection."""

import json
import os
import random
from typing import List, Dict, Tuple, Optional

try:
    import tcod
    import tcod.event
    TCOD_AVAILABLE = True
except ImportError:
    TCOD_AVAILABLE = False
    tcod = None


def load_factions() -> List[Dict]:
    """Load faction data from JSON file."""
    try:
        factions_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'factions.json')
        with open(factions_path, 'r') as f:
            factions = json.load(f)
        # Only return primary factions (playable)
        return [f for f in factions if f.get('primary_faction', False)]
    except Exception as e:
        # Fallback factions if file not found
        return [
            {"id": "Germany", "name": "Nazi Germany", "alignment": "axis", "primary_navy": "Kriegsmarine"},
            {"id": "USA", "name": "United States", "alignment": "allies", "primary_navy": "United States Navy"},
            {"id": "UK", "name": "British Empire", "alignment": "allies", "primary_navy": "Royal Navy"},
            {"id": "Japan", "name": "Empire of Japan", "alignment": "axis", "primary_navy": "Imperial Japanese Navy"},
        ]


def load_crew_names(faction_id: str) -> List[str]:
    """Load crew names for a specific faction."""
    try:
        names_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'crew_names.json')
        with open(names_path, 'r') as f:
            all_names = json.load(f)
        
        # Get names for the faction, or use generic names
        if faction_id in all_names:
            return all_names[faction_id]
        elif 'default' in all_names:
            return all_names['default']
        else:
            # Fallback names
            return ["John", "Mike", "Steve", "Hans", "Klaus", "Fritz", "Ivan", "Boris", "Jean", "Pierre"]
    except Exception:
        # Fallback names
        return ["John", "Mike", "Steve", "Hans", "Klaus", "Fritz", "Ivan", "Boris", "Jean", "Pierre"]


def generate_crew_member(name: str, rank: str = 'Seaman', specialization: Optional[str] = None) -> Dict:
    """Generate a crew member with randomized skills."""
    skills = {
        'sonar': random.uniform(0.4, 0.8),
        'torpedoes': random.uniform(0.4, 0.8),
        'navigation': random.uniform(0.4, 0.8),
        'engineering': random.uniform(0.4, 0.8),
        'medical': random.uniform(0.4, 0.8),
    }
    
    # Boost specialized skill
    if specialization and specialization in skills:
        skills[specialization] = min(1.0, skills[specialization] + 0.2)
    
    traits = random.sample(['brave', 'cautious', 'calm', 'hotheaded', 'methodical', 'quick'], k=random.randint(1, 2))
    
    return {
        'name': name,
        'rank': rank,
        'skills': skills,
        'traits': traits,
        'specialization': specialization
    }


def render_faction_selection(factions: List[Dict], selected_index: int) -> str:
    """Render the faction selection screen."""
    output = []
    output.append("╔" + "═" * 78 + "╗")
    output.append("║" + " " * 27 + "DEPTHS WITHIN" + " " * 38 + "║")
    output.append("║" + " " * 25 + "FACTION SELECTION" + " " * 36 + "║")
    output.append("╠" + "═" * 78 + "╣")
    output.append("║" + " " * 78 + "║")
    output.append("║  Select your faction (↑/↓ to navigate, ENTER to select):" + " " * 18 + "║")
    output.append("║" + " " * 78 + "║")
    
    for i, faction in enumerate(factions):
        is_selected = (i == selected_index)
        marker = "►" if is_selected else " "
        name = faction.get('name', 'Unknown')
        navy = faction.get('primary_navy', '')
        alignment = faction.get('alignment', '').upper()
        
        # Truncate if too long
        name_display = f"{name[:25]:<25}"
        navy_display = f"{navy[:20]:<20}"
        align_display = f"{alignment[:6]:>6}"
        
        line = f"║  {marker} {name_display} | {navy_display} | {align_display}   ║"
        output.append(line)
    
    output.append("║" + " " * 78 + "║")
    output.append("╠" + "═" * 78 + "╣")
    output.append("║  Commands: [↑] Up  [↓] Down  [ENTER] Select  [Q] Quit" + " " * 24 + "║")
    output.append("╚" + "═" * 78 + "╝")
    
    return '\n'.join(output)


def render_crew_selection(faction_name: str, crew_list: List[Dict], crew_count: int, max_crew: int) -> str:
    """Render the crew selection/confirmation screen."""
    output = []
    output.append("╔" + "═" * 78 + "╗")
    output.append("║" + " " * 27 + "DEPTHS WITHIN" + " " * 38 + "║")
    output.append("║" + " " * 26 + "CREW ROSTER" + " " * 41 + "║")
    output.append("╠" + "═" * 78 + "╣")
    output.append(f"║  Faction: {faction_name[:50]:<50}              ║")
    output.append(f"║  Crew Size: {crew_count}/{max_crew}" + " " * (63 - len(str(crew_count)) - len(str(max_crew))) + "║")
    output.append("║" + " " * 78 + "║")
    
    # Show first 10 crew members (or all if less)
    output.append("║  Starting Crew:" + " " * 63 + "║")
    output.append("║" + " " * 78 + "║")
    
    for i, crew in enumerate(crew_list[:10]):
        # Handle None crew members
        if crew is None:
            continue
        
        name = crew.get('name', 'Unknown')[:15]
        rank = crew.get('rank', 'Seaman')[:12]
        spec = (crew.get('specialization') or 'General')[:12]
        
        line = f"║  {i+1:2d}. {name:<15} | {rank:<12} | {spec:<12}              ║"
        output.append(line)
    
    if len(crew_list) > 10:
        output.append(f"║      ... and {len(crew_list) - 10} more crew members" + " " * (78 - 30 - len(str(len(crew_list) - 10))) + "║")
    
    output.append("║" + " " * 78 + "║")
    output.append("╠" + "═" * 78 + "╣")
    output.append("║  Commands: [ENTER] Start Game  [R] Re-roll Crew  [Q] Back" + " " * 19 + "║")
    output.append("╚" + "═" * 78 + "╝")
    
    return '\n'.join(output)


def render_faction_selection_tcod(console, factions: List[Dict], selected_index: int, frame: int = 0):
    """Render faction selection screen to a tcod console with animations."""
    # Create varied ocean background - Deep Blue Theme
    for y in range(console.height):
        depth_factor = y / console.height
        # Deep blue gradient (darker at bottom)
        bg_r = int(5 + depth_factor * 5)
        bg_g = int(10 + depth_factor * 10)
        bg_b = int(20 + depth_factor * 20)
        for x in range(console.width):
            # Animated wave pattern
            wave_offset = (frame // 3) % 5
            wave = int((x + wave_offset) % 6 == 0)
            if wave and y < 3:
                console.print(x, y, '~', fg=(100, 200, 255), bg=(bg_r, bg_g, bg_b))
            elif random.random() < 0.002 and y > 5:  # Random floating particles
                console.print(x, y, '·', fg=(150, 200, 255), bg=(bg_r, bg_g, bg_b))
            else:
                console.print(x, y, ' ', bg=(bg_r, bg_g, bg_b))
    
    # Enhanced ASCII art submarine with metallic colors
    sub_art = [
        "                    ___________________",
        "               ____|                   |____",
        "          ____|                             |____",
        "      ====|  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  |====",
        "      ====|  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  |====",
        "          |__|_______________________________|__|",
        "             o    o    o    o    o    o    o",
    ]
    art_x = console.width // 2 - 22
    # Brighter metallic colors
    art_colors = [
        (200, 200, 200),  # White/Grey
        (180, 180, 180),  # Light grey
        (160, 160, 160),  # Grey
        (140, 140, 140),  # Dark grey hull
        (120, 120, 120),  # Darker hull
        (160, 160, 160),  # Medium grey
        (100, 200, 255),  # Portholes (Blue light)
    ]
    for i, line in enumerate(sub_art):
        console.print(art_x, 1 + i, line, fg=art_colors[i])
    
    # Add ANIMATED bubbles rising from submarine
    bubble_chars = ['·', '°', '○', '◦']
    bubble_base = [(10, 8), (20, 8), (30, 8), (15, 8), (25, 8)]
    for idx, (bx_offset, by) in enumerate(bubble_base):
        bx = art_x + bx_offset
        # Animate bubbles rising based on frame
        rise = (frame // 2 + idx) % 6
        bubble_y = by - rise
        if bubble_y >= 0:
            bubble_char = bubble_chars[(frame + idx) % len(bubble_chars)]
            bubble_color = (200, 240, 255)
            console.print(bx, bubble_y, bubble_char, fg=bubble_color)
    
    # Title with depth gauge aesthetic
    depth_marker = "▼ 0m"
    console.print(2, 9, depth_marker, fg=(255, 100, 100))
    
    title = "╔═══════════════════════════════════════╗"
    title2 = "║     D E P T H S   W I T H I N         ║"
    title3 = "║  ~ Submarine Warfare Simulator ~      ║"
    title4 = "╚═══════════════════════════════════════╝"
    
    title_x = console.width // 2 - 20
    # Bright White/Cyan title
    console.print(title_x, 10, title, fg=(200, 220, 255))
    console.print(title_x, 11, title2, fg=(255, 255, 255))
    console.print(title_x, 12, title3, fg=(180, 220, 255))
    console.print(title_x, 13, title4, fg=(200, 220, 255))
    
    # Add ANIMATED sonar ping effect
    ping_phase = (frame // 4) % 3
    if ping_phase == 0:
        sonar_line = "~·~·~·~·~·~·~ S O N A R   A C T I V E ~·~·~·~·~·~·~"
        sonar_color = (100, 255, 150)
    elif ping_phase == 1:
        sonar_line = "·~·~·~·~·~·~· S O N A R   A C T I V E ·~·~·~·~·~·~·"
        sonar_color = (150, 255, 200)
    else:
        sonar_line = "~·~·~·~·~·~·~ S O N A R   A C T I V E ~·~·~·~·~·~·~"
        sonar_color = (100, 255, 150)
    console.print(console.width // 2 - len(sonar_line) // 2, 15, sonar_line, fg=sonar_color)
    
    # Decorative border with depth indicators
    border_y = 17
    console.print(2, border_y, "╔" + "═" * 75 + "╗", fg=(150, 200, 255))
    console.print(2, border_y + 1, "║ ⚓ SELECT YOUR NATION ⚓" + " " * 51 + "║", fg=(255, 255, 255))
    console.print(2, border_y + 2, "╠" + "═" * 75 + "╣", fg=(150, 200, 255))
    
    # Add ANIMATED pressure depth markers on sides
    for i in range(5):
        # Pulsing depth markers
        pulse = abs(((frame + i * 10) % 30) - 15)
        marker_brightness = 150 + pulse * 3
        console.print(0, border_y + 4 + i * 2, f"{20 + i * 50}m", fg=(marker_brightness, marker_brightness, marker_brightness + 20))
    
    # Faction list with styling and ship icons
    start_y = border_y + 3
    ship_icons = ["▓▓▓", "═══", "███", "▒▒▒", "░░░", "≡≡≡", "━━━", "▬▬▬"]
    
    for i, faction in enumerate(factions):
        y = start_y + i * 3  # More spacing
        name = faction.get('name', 'Unknown')[:22]
        navy = faction.get('primary_navy', 'Navy')[:18]
        alignment = faction.get('alignment', '').upper()[:7]
        
        # Alignment indicator
        if alignment == 'AXIS':
            align_symbol = "⚔"
            align_color = (255, 100, 100)
            ship_color = (255, 80, 80)
        else:
            align_symbol = "★"
            align_color = (100, 200, 255)
            ship_color = (100, 180, 255)
        
        if i == selected_index:
            # ANIMATED highlight for selected faction
            pulse = int(abs(((frame * 2) % 40) - 20))
            select_color = (255, 255, 100 + pulse)
            
            console.print(2, y, "║", fg=(150, 200, 255))
            console.print(4, y, "►►", fg=select_color)
            console.print(7, y, align_symbol, fg=align_color)
            console.print(9, y, f"{name:<22}", fg=(255, 255, 255))
            console.print(32, y, "│", fg=(150, 200, 255))
            console.print(34, y, f"{navy:<18}", fg=(220, 230, 240))
            console.print(54, y, "│", fg=(150, 200, 255))
            console.print(56, y, f"{alignment:<7}", fg=align_color)
            console.print(65, y, ship_icons[i % len(ship_icons)], fg=select_color)
            console.print(77, y, "║", fg=(150, 200, 255))
            
            # Add animated selection indicator line below
            console.print(2, y + 1, "║", fg=(150, 200, 255))
            indicator_char = ["─", "═", "─"][frame % 3]
            console.print(4, y + 1, "  └" + indicator_char * 68 + "┘", fg=(200, 220, 255))
            console.print(77, y + 1, "║", fg=(150, 200, 255))
        else:
            console.print(2, y, "║", fg=(100, 150, 200))
            console.print(7, y, align_symbol, fg=align_color)
            console.print(9, y, f"{name:<22}", fg=(180, 180, 180))
            console.print(32, y, "│", fg=(100, 150, 200))
            console.print(34, y, f"{navy:<18}", fg=(150, 160, 170))
            console.print(54, y, "│", fg=(100, 150, 200))
            console.print(56, y, f"{alignment:<7}", fg=(150, 150, 150))
            console.print(65, y, ship_icons[i % len(ship_icons)], fg=ship_color)
            console.print(77, y, "║", fg=(100, 150, 200))
            
            # Divider line
            console.print(2, y + 1, "║", fg=(100, 150, 200))
            console.print(4, y + 1, " " * 72, fg=(60, 75, 85))
            console.print(77, y + 1, "║", fg=(100, 150, 200))
    
    # Close border
    close_y = start_y + len(factions) * 3
    console.print(2, close_y, "╚" + "═" * 75 + "╝", fg=(150, 200, 255))
    
    # Commands with decorative elements
    commands_y = console.height - 5
    
    # Add ANIMATED depth charges and mines at bottom
    mine_chars = ['◉', '◎', '○']
    for i in range(0, console.width, 8):
        mine_char = mine_chars[(frame // 5 + i // 8) % len(mine_chars)]
        console.print(i, commands_y - 1, mine_char, fg=(100, 120, 140))
    
    # ANIMATED wave decoration
    wave_chars = ['～', '~', '≈']
    wave_str = ""
    for i in range(40):
        wave_str += wave_chars[(frame // 2 + i) % len(wave_chars)] + " "
    console.print(2, commands_y, wave_str, fg=(100, 200, 255))
    
    # ANIMATED torpedo indicators on sides
    torpedo_x = (frame // 3) % 3
    console.print(torpedo_x, commands_y + 1, "──►", fg=(255, 255, 0))
    console.print(console.width - 3 - torpedo_x, commands_y + 1, "◄──", fg=(255, 255, 0))
    
    # Commands box with warmer colors
    cmd_box = "╔═══════════════════════════════════════════════╗"
    cmd_text = "║  ↑/↓ Navigate  │  ENTER Select  │  Q Quit  ║"
    cmd_close = "╚═══════════════════════════════════════════════╝"
    cmd_x = console.width // 2 - 24
    console.print(cmd_x, commands_y + 1, cmd_box, fg=(150, 200, 255))
    console.print(cmd_x, commands_y + 2, cmd_text, fg=(255, 255, 255))
    console.print(cmd_x, commands_y + 3, cmd_close, fg=(150, 200, 255))


def render_crew_selection_tcod(console, faction_name: str, crew_list: List[Dict], frame: int = 0):
    """Render crew selection screen to a tcod console with animations."""
    # Ocean background with Deep Blue Theme
    for y in range(console.height):
        depth_factor = y / console.height
        # Deep blue gradient
        bg_r = int(5 + depth_factor * 5)
        bg_g = int(10 + depth_factor * 10)
        bg_b = int(20 + depth_factor * 20)
        for x in range(console.width):
            # Add animated floating bubbles
            bubble_chance = 0.008 if (y + frame // 3) % 40 < 20 else 0.004
            if random.random() < bubble_chance:
                console.print(x, y, '°', fg=(150, 200, 255), bg=(bg_r, bg_g, bg_b))
            else:
                console.print(x, y, ' ', bg=(bg_r, bg_g, bg_b))
    
    # Add submarine conning tower on left
    tower_art = [
        "   ║",
        "   ║",
        "  ╔╩╗",
        "  ║ ║",
        "  ║ ║",
        " ╔╩═╩╗",
        "╔╩═══╩╗",
        "║▓▓▓▓▓║",
    ]
    for i, line in enumerate(tower_art):
        console.print(2, 10 + i, line, fg=(150, 180, 200))
    
    # Add crew walking icon
    console.print(3, 18, "☺☺☺", fg=(255, 255, 255))
    
    # Periscope view border with enhanced styling
    title_art = [
        "          ╔═══════════════════════════════════════════════════════════════════╗",
        "          ║                                                                   ║",
        "          ║               ⚓  C R E W   M A N I F E S T  ⚓                   ║",
        "          ║                                                                   ║",
        f"          ║                    {faction_name[:35]:^35}                      ║",
        "          ║                                                                   ║",
        "          ╠═══════════════════════════════════════════════════════════════════╣",
    ]
    for i, line in enumerate(title_art):
        if i == 2:
            console.print(0, 1 + i, line, fg=(255, 255, 255))
        else:
            console.print(0, 1 + i, line, fg=(150, 200, 255))
    
    # Add rank insignia decorations
    insignia = ["◆", "◈", "◇", "◊"]
    for i, ins in enumerate(insignia):
        console.print(12 + i * 3, 2, ins, fg=(255, 215, 0))
        console.print(console.width - 15 + i * 3, 2, ins, fg=(255, 215, 0))
    
    # Column headers with naval styling and icons
    header_y = 9
    console.print(12, header_y, "  #  │  NAME            │  RANK            │ SPECIALTY   │ STATUS", fg=(200, 220, 255))
    console.print(12, header_y + 1, "═════╪══════════════════╪══════════════════╪═════════════╪════════", fg=(150, 200, 255))
    
    # Show crew members in organized list with enhanced visuals
    start_y = header_y + 2
    max_display = min(16, len(crew_list))
    
    # Specialty icons
    specialty_icons = {
        'sonar': '◈',
        'torpedoes': '◆',
        'navigation': '☆',
        'engineering': '⚙',
        'medical': '♥',
        'command': '★',
    }
    
    for i, crew in enumerate(crew_list[:max_display]):
        if crew is None:
            continue
        
        y = start_y + i
        name = crew.get('name', 'Unknown')[:14]
        rank = crew.get('rank', 'Seaman')[:14]
        spec = (crew.get('specialization') or 'General')[:13]
        
        # Rank-based color coding
        if 'Commander' in rank or 'Officer' in rank:
            rank_color = (255, 215, 0)
        else:
            rank_color = (200, 220, 255)
        
        # Specialty icons
        spec_icon = {
            'sonar': '◈',
            'torpedoes': '◆',
            'navigation': '☆',
            'engineering': '⚙',
            'medical': '♥',
        }.get(crew.get('specialization'), '•')
        
        # Add alternating row background for readability
        if i % 2 == 0:
            row_marker = "▓"
            row_color = (20, 40, 60)
        else:
            row_marker = "▒"
            row_color = (15, 30, 50)
        
        console.print(11, y, row_marker, fg=row_color)
        console.print(10, y, f" {i+1:2d}  │", fg=(180, 200, 220))
        console.print(17, y, f"{name:<16} │", fg=(255, 255, 255))
        console.print(36, y, f"{rank:<16} │", fg=rank_color)
        console.print(55, y, spec_icon, fg=(100, 255, 100))
        console.print(57, y, f"{spec:<11}", fg=(200, 220, 255))
        
        # Status indicator (all ready)
        console.print(69, y, "│ ✓", fg=(100, 255, 100))
    
    # Total crew count with decorations
    total_y = start_y + max_display + 1
    console.print(12, total_y, "═════╧═══════════════════╧═══════════════════╧═════════════╧════════", fg=(150, 200, 255))
    
    # Add submarine silhouette at bottom
    console.print(12, total_y + 1, "        ╔══════════════════════════════════════════╗", fg=(150, 200, 255))
    console.print(12, total_y + 2, f"        ║  Total Crew: {len(crew_list)} sailors ready for duty  ║", fg=(255, 255, 255))
    console.print(12, total_y + 3, "        ╚══════════════════════════════════════════╝", fg=(150, 200, 255))
    
    if len(crew_list) > max_display:
        console.print(12, total_y + 4, f"        (Showing first {max_display} of {len(crew_list)} crew members)", fg=(180, 200, 220))
    
    # Add crew readiness indicators
    readiness_icons = ["⚓", "⚙", "◆", "☆"]
    console.print(12, total_y + 5, "        Readiness: ", fg=(200, 220, 255))
    for idx, icon in enumerate(readiness_icons):
        console.print(31 + idx * 3, total_y + 5, icon, fg=(100, 255, 100))
    
    # Commands with enhanced styling
    commands_y = console.height - 5
    
    # Add ocean floor decoration
    ocean_floor = "~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~"
    console.print(2, commands_y - 1, ocean_floor, fg=(50, 100, 150))
    
    # Add depth marker
    console.print(0, commands_y, "▼ 300m", fg=(255, 100, 100))
    
    console.print(10, commands_y, "╠════════════════════════════════════════════════════════════════════╣", fg=(150, 200, 255))
    console.print(10, commands_y + 1, "║                                                                    ║", fg=(100, 150, 200))
    console.print(10, commands_y + 2, "║  ENTER: Begin Mission  │  R: Re-roll  │  Q: Change Faction       ║", fg=(255, 255, 255))
    console.print(10, commands_y + 3, "║                                                                    ║", fg=(100, 150, 200))
    console.print(10, commands_y + 4, "╚════════════════════════════════════════════════════════════════════╝", fg=(150, 200, 255))


def run_setup_screen_terminal() -> Optional[Tuple[Dict, List[Dict]]]:
    """Fallback terminal version of setup screen."""
    import sys
    from ui.term_input import getkey
    
    factions = load_factions()
    selected_faction_index = 0
    
    # Phase 1: Faction Selection
    while True:
        # Clear screen
        print("\033[2J\033[H", end='')
        
        # Render faction selection
        screen = render_faction_selection(factions, selected_faction_index)
        print(screen)
        
        # Get input
        try:
            key = getkey()
            
            if key == 'UP':
                selected_faction_index = (selected_faction_index - 1) % len(factions)
            elif key == 'DOWN':
                selected_faction_index = (selected_faction_index + 1) % len(factions)
            elif key == '\r' or key == '\n':  # Enter
                break
            elif key.lower() == 'q':
                return None
        except KeyboardInterrupt:
            return None
    
    # Get selected faction
    selected_faction = factions[selected_faction_index]
    faction_id = selected_faction['id']
    faction_name = selected_faction['name']
    
    # Phase 2: Crew Generation
    crew_count = 20  # Starting crew size
    
    def generate_crew():
        """Generate a new random crew."""
        names = load_crew_names(faction_id)
        random.shuffle(names)
        
        new_crew = []
        
        # Add command staff
        if len(names) > 0:
            new_crew.append(generate_crew_member(names[0], 'Commander', 'navigation'))
        if len(names) > 1:
            new_crew.append(generate_crew_member(names[1], 'Executive Officer', 'torpedoes'))
        if len(names) > 2:
            new_crew.append(generate_crew_member(names[2], 'Chief Engineer', 'engineering'))
        if len(names) > 3:
            new_crew.append(generate_crew_member(names[3], 'Sonar Operator', 'sonar'))
        if len(names) > 4:
            new_crew.append(generate_crew_member(names[4], 'Medical Officer', 'medical'))
        
        # Add regular crew
        specializations = ['sonar', 'torpedoes', 'navigation', 'engineering', 'medical', None]
        for i in range(5, min(crew_count, len(names))):
            spec = random.choice(specializations)
            new_crew.append(generate_crew_member(names[i], 'Seaman', spec))
        
        # Fill remaining slots with generated names if needed
        while len(new_crew) < crew_count:
            generic_name = f"Sailor {len(new_crew) + 1}"
            spec = random.choice(specializations)
            new_crew.append(generate_crew_member(generic_name, 'Seaman', spec))
        
        # Filter out any None entries (defensive)
        return [c for c in new_crew if c is not None]
    
    # Generate initial crew
    crew_list = generate_crew()
    
    # Phase 3: Crew Confirmation
    while True:
        # Clear screen
        print("\033[2J\033[H", end='')
        
        # Render crew screen
        screen = render_crew_selection(faction_name, crew_list, len(crew_list), 50)
        print(screen)
        
        # Get input
        try:
            key = getkey()
            
            if key == '\r' or key == '\n':  # Enter - start game
                return (selected_faction, crew_list)
            elif key.lower() == 'r':  # Re-roll crew
                crew_list = generate_crew()
            elif key.lower() == 'q':  # Back to faction selection
                return run_setup_screen_terminal()
        except KeyboardInterrupt:
            return None


def run_setup_screen() -> Optional[Tuple[Dict, List[Dict]]]:
    """Run the interactive setup screen using tcod.
    
    Returns:
        Tuple of (selected_faction, crew_list) or None if cancelled
    """
    if not TCOD_AVAILABLE:
        # Fallback to terminal mode
        return run_setup_screen_terminal()
    
    factions = load_factions()
    selected_faction_index = 0
    
    # Use a text-compatible font for setup screen with tighter spacing
    # Try to load a truetype font for text rendering
    try:
        # Menlo is often better/bolder than Monaco on macOS - Match game.py style
        tileset = tcod.tileset.load_truetype_font('/System/Library/Fonts/Menlo.ttc', 16, 16)
    except:
        try:
            tileset = tcod.tileset.load_truetype_font('/System/Library/Fonts/Monaco.ttf', 16, 16)
        except:
            try:
                # Fallback to Courier with tighter spacing
                tileset = tcod.tileset.load_truetype_font('/System/Library/Fonts/Courier New.ttf', 16, 16)
            except:
                # Last resort: use our custom tileset (text won't render properly)
                from ui.tileset import load_preferred_tileset
                tileset = load_preferred_tileset()
    
    SCREEN_W, SCREEN_H = 80, 50
    
    # Animation state
    frame = 0
    
    with tcod.context.new_terminal(
        SCREEN_W, SCREEN_H,
        tileset=tileset,
        title="Depths Within - Setup",
        vsync=True
    ) as context:
        console = tcod.console.Console(SCREEN_W, SCREEN_H, order="F")
        
        # Phase 1: Faction Selection
        running = True
        while running:
            console.clear()
            
            # Render faction selection to console with animation frame
            render_faction_selection_tcod(console, factions, selected_faction_index, frame)
            frame += 1
            
            context.present(console)
            
            # Handle input
            for event in tcod.event.wait():
                if event.type == "QUIT":
                    return None
                elif event.type == "KEYDOWN":
                    if event.sym == tcod.event.KeySym.UP:
                        selected_faction_index = (selected_faction_index - 1) % len(factions)
                    elif event.sym == tcod.event.KeySym.DOWN:
                        selected_faction_index = (selected_faction_index + 1) % len(factions)
                    elif event.sym == tcod.event.KeySym.RETURN:
                        running = False
                        break
                    elif event.sym == tcod.event.KeySym.Q:
                        return None
        
        # Get selected faction
        selected_faction = factions[selected_faction_index]
        faction_id = selected_faction['id']
        faction_name = selected_faction['name']
        
        # Phase 2: Crew Generation
        crew_count = 20  # Starting crew size
        
        def generate_crew():
            """Generate a new random crew."""
            names = load_crew_names(faction_id)
            random.shuffle(names)
            
            new_crew = []
            
            # Add command staff
            if len(names) > 0:
                new_crew.append(generate_crew_member(names[0], 'Commander', 'navigation'))
            if len(names) > 1:
                new_crew.append(generate_crew_member(names[1], 'Executive Officer', 'torpedoes'))
            if len(names) > 2:
                new_crew.append(generate_crew_member(names[2], 'Chief Engineer', 'engineering'))
            if len(names) > 3:
                new_crew.append(generate_crew_member(names[3], 'Sonar Operator', 'sonar'))
            if len(names) > 4:
                new_crew.append(generate_crew_member(names[4], 'Medical Officer', 'medical'))
            
            # Add regular crew
            specializations = ['sonar', 'torpedoes', 'navigation', 'engineering', 'medical', None]
            for i in range(5, min(crew_count, len(names))):
                spec = random.choice(specializations)
                new_crew.append(generate_crew_member(names[i], 'Seaman', spec))
            
            # Fill remaining slots with generated names if needed
            while len(new_crew) < crew_count:
                generic_name = f"Sailor {len(new_crew) + 1}"
                spec = random.choice(specializations)
                new_crew.append(generate_crew_member(generic_name, 'Seaman', spec))
            
            # Filter out any None entries (defensive)
            return [c for c in new_crew if c is not None]
        
        # Generate initial crew
        crew_list = generate_crew()
        
        # Phase 3: Crew Confirmation
        running = True
        while running:
            console.clear()
            
            # Render crew selection to console with animation frame
            render_crew_selection_tcod(console, faction_name, crew_list, frame)
            frame += 1
            
            context.present(console)
            
            # Handle input
            for event in tcod.event.wait():
                if event.type == "QUIT":
                    return None
                elif event.type == "KEYDOWN":
                    if event.sym == tcod.event.KeySym.RETURN:
                        return (selected_faction, crew_list)
                    elif event.sym == tcod.event.KeySym.R:
                        crew_list = generate_crew()
                    elif event.sym == tcod.event.KeySym.Q:
                        return run_setup_screen()  # Back to faction selection


def quick_setup(faction_id: str = "Germany") -> Tuple[Dict, List[Dict]]:
    """Quick setup without interactive screen (for testing)."""
    factions = load_factions()
    selected_faction = next((f for f in factions if f['id'] == faction_id), factions[0])
    
    # Generate crew
    names = load_crew_names(faction_id)
    random.shuffle(names)
    
    crew_list = []
    specializations = ['sonar', 'torpedoes', 'navigation', 'engineering', 'medical', None]
    
    for i in range(min(20, len(names))):
        rank = 'Commander' if i == 0 else 'Officer' if i < 5 else 'Seaman'
        spec = specializations[i % len(specializations)]
        crew_list.append(generate_crew_member(names[i], rank, spec))
    
    return (selected_faction, crew_list)
