"""
Expanded tileset generator for WWII Submarine Roguelike.
Creates a comprehensive PNG tileset with all game items, systems, and visual elements.
Now includes: torpedoes, mines, weather, ports, aircraft, depth charges, convoys, etc.
"""
from PIL import Image, ImageDraw
import os
import math

# Tileset configuration
TILE_SIZE = 32
COLS = 16
ROWS = 16
TOTAL_TILES = COLS * ROWS  # 256 tiles

# Comprehensive color palette
COLORS = {
    # Ocean depths
    'ocean_surface': (30, 80, 120),
    'ocean_shallow': (25, 70, 110),
    'ocean_medium': (20, 60, 100),
    'ocean_deep': (15, 50, 90),
    'ocean_very_deep': (10, 40, 80),
    
    # Submarine
    'sub_hull': (60, 65, 70),
    'sub_conning': (50, 55, 60),
    'sub_highlight': (80, 85, 90),
    'sub_shadow': (40, 45, 50),
    'sub_periscope': (70, 75, 80),
    
    # Ships
    'ship_merchant': (90, 80, 70),
    'ship_warship': (70, 70, 75),
    'ship_destroyer': (75, 75, 80),
    
    # Weapons and effects
    'torpedo_body': (180, 190, 200),
    'torpedo_propeller': (160, 170, 180),
    'torpedo_electric': (100, 200, 255),  # Blue glow
    'torpedo_oxygen': (255, 200, 100),  # Orange glow (Type 93)
    'torpedo_homing': (255, 150, 255),  # Pink glow (acoustic)
    'explosion': (255, 150, 50),
    'damage': (200, 80, 60),
    'water_splash': (200, 220, 240),
    'mine_body': (50, 50, 50),
    'mine_spikes': (70, 70, 70),
    
    # Weather
    'fog': (200, 210, 220, 180),
    'rain': (180, 190, 200, 200),
    'storm': (100, 110, 120, 220),
    'ice': (240, 250, 255),
    'night': (10, 15, 30, 200),
    
    # UI
    'ui_gauge_good': (80, 200, 100),
    'ui_gauge_warn': (255, 200, 50),
    'ui_gauge_bad': (255, 80, 60),
    'ui_bg': (40, 50, 60),
    'ui_border': (100, 120, 140),
    'ui_text': (220, 230, 240),
    
    # Systems
    'battery': (255, 200, 50),
    'oxygen': (100, 200, 255),
    'hull': (80, 85, 90),
    'sonar_ping': (100, 255, 150),
    'radar_sweep': (255, 255, 100),
    
    # Factions
    'germany': (40, 40, 40),
    'usa': (0, 40, 100),
    'uk': (150, 30, 30),
    'japan': (180, 0, 0),
    'italy': (0, 120, 50),
    'ussr': (180, 0, 0),
    
    # Ports and objectives
    'port_friendly': (100, 200, 100),
    'port_enemy': (200, 80, 80),
    'port_neutral': (150, 150, 150),
    'waypoint': (255, 200, 50),
    'objective': (255, 150, 255),
    
    # Aircraft
    'aircraft_body': (120, 120, 130),
    'aircraft_wing': (110, 110, 120),
    'aircraft_damaged': (180, 80, 60),
}


def create_ocean_tile(size, depth_level='medium', **kwargs):
    """Create ocean tile with wave pattern."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Base color
    color = COLORS.get(f'ocean_{depth_level}', COLORS['ocean_medium'])
    draw.rectangle([0, 0, size, size], fill=color)
    
    # Wave lines
    for i in range(3):
        y = size // 4 + i * size // 8
        wave_color = tuple(min(255, c + 10) for c in color[:3])
        for x in range(size):
            wave_y = y + int(2 * math.sin(x * 0.3 + i))
            draw.point((x, wave_y), fill=wave_color)
    
    return img


def create_submarine_tile(size, angle=0, surfaced=True, **kwargs):
    """Create submarine tile at specific angle."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Convert angle to radians
    rad = math.radians(angle)
    
    # Submarine hull (ellipse pointing in direction)
    length = size * 0.7
    width = size * 0.25
    
    # Draw hull rotated
    for offset in range(-int(width//2), int(width//2)):
        x1 = cx + offset * math.sin(rad) - length/2 * math.cos(rad)
        y1 = cy - offset * math.cos(rad) - length/2 * math.sin(rad)
        x2 = cx + offset * math.sin(rad) + length/2 * math.cos(rad)
        y2 = cy - offset * math.cos(rad) + length/2 * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=COLORS['sub_hull'], width=2)
    
    # Conning tower (only if surfaced)
    if surfaced:
        tower_x = cx
        tower_y = cy - width
        draw.rectangle([tower_x-2, tower_y-4, tower_x+2, tower_y], fill=COLORS['sub_conning'])
        # Periscope
        draw.line([(tower_x, tower_y-4), (tower_x, tower_y-8)], fill=COLORS['sub_periscope'])
    
    return img


def create_ship_tile(size, ship_type='merchant', **kwargs):
    """Create ship tile with type-specific design."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    color = COLORS.get(f'ship_{ship_type}', COLORS['ship_merchant'])
    cx, cy = size // 2, size // 2
    
    if ship_type == 'merchant':
        # Boxy cargo ship
        draw.rectangle([cx-10, cy-6, cx+10, cy+6], fill=color)
        draw.rectangle([cx+6, cy-10, cx+10, cy-6], fill=tuple(max(0, c-20) for c in color))  # Smokestack
    elif ship_type == 'warship':
        # Sleek warship with gun turret
        draw.ellipse([cx-12, cy-5, cx+12, cy+5], fill=color)
        draw.ellipse([cx-4, cy-8, cx+4, cy-2], fill=tuple(max(0, c-30) for c in color))  # Turret
    elif ship_type == 'destroyer':
        # Fast destroyer
        draw.polygon([(cx-14, cy), (cx+14, cy-3), (cx+14, cy+3)], fill=color)
        draw.rectangle([cx, cy-6, cx+4, cy+6], fill=tuple(max(0, c-20) for c in color))  # Bridge
    
    return img


def create_torpedo_type_tile(size, torpedo_id='G7e', propulsion='electric', **kwargs):
    """Create torpedo tile with propulsion-specific glow."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Torpedo body
    draw.ellipse([cx-12, cy-3, cx+12, cy+3], fill=COLORS['torpedo_body'])
    
    # Propulsion glow
    if propulsion == 'electric':
        glow_color = COLORS['torpedo_electric']
    elif propulsion == 'oxygen':
        glow_color = COLORS['torpedo_oxygen']
    elif propulsion == 'homing':
        glow_color = COLORS['torpedo_homing']
    else:
        glow_color = COLORS['torpedo_propeller']
    
    # Glow at rear
    for radius in range(4, 0, -1):
        alpha = 50 * (5 - radius)
        glow = glow_color[:3] + (alpha,)
        draw.ellipse([cx-14-radius, cy-radius, cx-14+radius, cy+radius], fill=glow)
    
    # Propeller
    draw.line([(cx-10, cy), (cx-14, cy)], fill=COLORS['torpedo_propeller'], width=2)
    
    # Type indicator (small letter)
    if torpedo_id == 'Type_93':  # Long Lance - make it longer
        draw.rectangle([cx-14, cy-2, cx+14, cy+2], fill=COLORS['torpedo_oxygen'])
    
    return img


def create_mine_tile(size, mine_type='contact', **kwargs):
    """Create mine tile with type-specific features."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Mine body (sphere)
    draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill=COLORS['mine_body'])
    
    if mine_type == 'contact':
        # Spikes for contact detonation
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = cx + 8 * math.cos(rad)
            y1 = cy + 8 * math.sin(rad)
            x2 = cx + 12 * math.cos(rad)
            y2 = cy + 12 * math.sin(rad)
            draw.line([(x1, y1), (x2, y2)], fill=COLORS['mine_spikes'], width=2)
    elif mine_type == 'magnetic':
        # Magnetic indicator (M)
        draw.text((cx-3, cy-4), 'M', fill=COLORS['ui_text'])
    elif mine_type == 'acoustic':
        # Acoustic indicator (sound waves)
        for radius in [10, 12, 14]:
            draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], 0, 360, fill=COLORS['sonar_ping'])
    
    return img


def create_periscope_tile(size, state='up', **kwargs):
    """Create periscope UI icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    if state == 'up':
        # Periscope viewing
        draw.rectangle([cx-2, cy-8, cx+2, cy+8], fill=COLORS['sub_periscope'])
        draw.ellipse([cx-5, cy-10, cx+5, cy-6], fill=COLORS['sub_highlight'])  # Lens
    elif state == 'searching':
        # Sweeping arc
        draw.rectangle([cx-2, cy-8, cx+2, cy+8], fill=COLORS['sub_periscope'])
        draw.arc([cx-10, cy-10, cx+10, cy+10], 270, 360, fill=COLORS['radar_sweep'], width=2)
    elif state == 'locked':
        # Target locked
        draw.rectangle([cx-2, cy-8, cx+2, cy+8], fill=COLORS['sub_periscope'])
        draw.ellipse([cx-5, cy-10, cx+5, cy-6], fill=(255, 0, 0))  # Red lens
    elif state == 'damaged':
        # Broken
        draw.rectangle([cx-2, cy, cx+2, cy+8], fill=COLORS['sub_periscope'])
        draw.line([(cx-5, cy), (cx+5, cy-8)], fill=COLORS['damage'], width=2)
    
    return img


def create_sonar_tile(size, state='active', **kwargs):
    """Create sonar UI icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Sonar dome
    draw.arc([cx-10, cy-10, cx+10, cy+10], 180, 360, fill=COLORS['sonar_ping'], width=3)
    
    if state == 'active':
        # Pinging (concentric arcs)
        for radius in [12, 14]:
            draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], 180, 360, fill=COLORS['sonar_ping'], width=1)
    elif state == 'passive':
        # Listening (single arc)
        draw.arc([cx-12, cy-12, cx+12, cy+12], 180, 360, fill=COLORS['ui_gauge_good'], width=2)
    elif state == 'ping':
        # Active ping burst
        for radius in range(10, 16, 2):
            alpha = 255 - (radius - 10) * 40
            color = COLORS['sonar_ping'][:3] + (alpha,)
            draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], 180, 360, fill=color, width=2)
    
    return img


def create_radar_tile(size, state='scanning', **kwargs):
    """Create radar UI icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Radar dish
    draw.ellipse([cx-10, cy-10, cx+10, cy+10], outline=COLORS['ui_border'], width=2)
    
    # Scanning beam
    draw.line([(cx, cy), (cx+10, cy-10)], fill=COLORS['radar_sweep'], width=2)
    
    return img


def create_battery_icon(size, level=1.0, **kwargs):
    """Create battery status icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Battery outline
    draw.rectangle([cx-8, cy-6, cx+8, cy+6], outline=COLORS['ui_border'], width=2)
    draw.rectangle([cx+8, cy-2, cx+10, cy+2], fill=COLORS['ui_border'])  # Terminal
    
    # Fill level
    fill_width = int(14 * level)
    if level > 0.7:
        color = COLORS['ui_gauge_good']
    elif level > 0.3:
        color = COLORS['ui_gauge_warn']
    else:
        color = COLORS['ui_gauge_bad']
    draw.rectangle([cx-7, cy-5, cx-7+fill_width, cy+5], fill=color)
    
    return img


def create_oxygen_icon(size, level=1.0, **kwargs):
    """Create oxygen status icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # O2 text
    draw.text((cx-6, cy-6), 'O2', fill=COLORS['oxygen'])
    
    # Level bar
    bar_height = int(12 * level)
    if level > 0.7:
        color = COLORS['ui_gauge_good']
    elif level > 0.3:
        color = COLORS['ui_gauge_warn']
    else:
        color = COLORS['ui_gauge_bad']
    draw.rectangle([cx-2, cy+6-bar_height, cx+2, cy+6], fill=color)
    
    return img


def create_hull_icon(size, level=1.0, **kwargs):
    """Create hull integrity icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Hull silhouette
    if level > 0.7:
        color = COLORS['ui_gauge_good']
    elif level > 0.3:
        color = COLORS['ui_gauge_warn']
    else:
        color = COLORS['ui_gauge_bad']
    
    draw.ellipse([cx-10, cy-4, cx+10, cy+4], fill=color)
    
    # Damage cracks if low
    if level < 0.5:
        draw.line([(cx-5, cy-2), (cx+5, cy+2)], fill=COLORS['damage'], width=2)
    
    return img


def create_weather_tile(size, weather_type='clear', **kwargs):
    """Create weather effect tile."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if weather_type == 'clear':
        # Sun
        cx, cy = size // 2, size // 2
        draw.ellipse([cx-6, cy-6, cx+6, cy+6], fill=(255, 255, 100))
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = cx + 8 * math.cos(rad)
            y1 = cy + 8 * math.sin(rad)
            x2 = cx + 12 * math.cos(rad)
            y2 = cy + 12 * math.sin(rad)
            draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 100), width=2)
    elif weather_type == 'fog':
        # Fog clouds
        for y in range(0, size, 8):
            for x in range(0, size, 8):
                draw.ellipse([x, y, x+10, y+6], fill=COLORS['fog'])
    elif weather_type == 'rain':
        # Rain lines
        for x in range(0, size, 4):
            for y in range(0, size, 8):
                draw.line([(x, y), (x+2, y+6)], fill=COLORS['rain'], width=1)
    elif weather_type == 'storm':
        # Lightning bolt
        cx = size // 2
        draw.line([(cx, 0), (cx-3, size//3), (cx+2, size//3), (cx-2, size)], fill=(255, 255, 100), width=3)
    elif weather_type == 'ice':
        # Ice crystal
        cx, cy = size // 2, size // 2
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            x2 = cx + 10 * math.cos(rad)
            y2 = cy + 10 * math.sin(rad)
            draw.line([(cx, cy), (x2, y2)], fill=COLORS['ice'], width=2)
    elif weather_type == 'night':
        # Moon and stars
        draw.ellipse([size-12, 4, size-4, 12], fill=(200, 200, 220))
        for x, y in [(6, 8), (10, 4), (4, 14)]:
            draw.point((x, y), fill=(255, 255, 255))
    
    return img


def create_port_tile(size, status='friendly', **kwargs):
    """Create port marker tile."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    color = COLORS[f'port_{status}']
    
    # Port building
    draw.rectangle([cx-10, cy-8, cx+10, cy+8], fill=color)
    # Dock
    draw.rectangle([cx-12, cy+8, cx+12, cy+12], fill=tuple(max(0, c-40) for c in color))
    # Flag
    draw.line([(cx, cy-8), (cx, cy-14)], fill=(100, 100, 100), width=2)
    draw.polygon([(cx, cy-14), (cx+6, cy-11), (cx, cy-8)], fill=color)
    
    return img


def create_waypoint_tile(size, **kwargs):
    """Create waypoint marker."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Target circles
    for radius in [14, 10, 6]:
        draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], 0, 360, fill=COLORS['waypoint'], width=2)
    
    return img


def create_mission_tile(size, status='objective', **kwargs):
    """Create mission marker."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    if status == 'objective':
        # Exclamation mark
        draw.rectangle([cx-2, cy-10, cx+2, cy-2], fill=COLORS['objective'])
        draw.rectangle([cx-2, cy, cx+2, cy+4], fill=COLORS['objective'])
    elif status == 'complete':
        # Checkmark
        draw.line([(cx-6, cy), (cx-2, cy+6), (cx+8, cy-6)], fill=COLORS['ui_gauge_good'], width=3)
    
    return img


def create_aircraft_tile(size, aircraft_type='bomber', **kwargs):
    """Create aircraft tile."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Wings
    draw.line([(cx-12, cy), (cx+12, cy)], fill=COLORS['aircraft_wing'], width=4)
    # Fuselage
    draw.ellipse([cx-4, cy-8, cx+4, cy+8], fill=COLORS['aircraft_body'])
    
    if aircraft_type == 'attacking':
        # Bombs falling
        draw.ellipse([cx-2, cy+10, cx+2, cy+14], fill=(50, 50, 50))
    elif aircraft_type == 'damaged':
        # Smoke trail
        for i in range(3):
            y = cy - 8 - i * 3
            draw.ellipse([cx-2-i, y-2, cx+2-i, y+2], fill=COLORS['aircraft_damaged'])
    
    return img


def create_depth_charge_tile(size, state='falling', **kwargs):
    """Create depth charge tile."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Barrel shape
    draw.ellipse([cx-6, cy-8, cx+6, cy+8], fill=(60, 60, 60))
    
    if state == 'falling':
        # Motion lines
        for i in range(3):
            y = cy - 10 - i * 3
            draw.line([(cx-2, y), (cx+2, y)], fill=(150, 150, 150), width=1)
    elif state == 'armed':
        # Red light
        draw.ellipse([cx-2, cy-2, cx+2, cy+2], fill=(255, 0, 0))
    elif state == 'exploding':
        # Explosion rings
        for radius in [8, 12, 16]:
            alpha = 255 - (radius - 8) * 30
            color = COLORS['explosion'][:3] + (alpha,)
            draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], 0, 360, fill=color, width=2)
    
    return img


def create_sonobuoy_tile(size, **kwargs):
    """Create sonobuoy marker."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Float
    draw.ellipse([cx-4, cy-8, cx+4, cy-4], fill=(255, 150, 0))
    # Cable
    draw.line([(cx, cy-4), (cx, cy+8)], fill=(100, 100, 100), width=1)
    # Hydrophone
    draw.ellipse([cx-3, cy+8, cx+3, cy+14], fill=COLORS['sonar_ping'])
    
    return img


def create_convoy_marker_tile(size, convoy_type='cargo', **kwargs):
    """Create convoy formation marker."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    if convoy_type == 'cargo':
        # Multiple merchant ships
        for x_off in [-6, 0, 6]:
            draw.rectangle([cx+x_off-2, cy-3, cx+x_off+2, cy+3], fill=COLORS['ship_merchant'])
    elif convoy_type == 'tanker':
        # Tanker with tanks
        draw.rectangle([cx-8, cy-4, cx+8, cy+4], fill=(80, 70, 60))
        draw.ellipse([cx-6, cy-2, cx-2, cy+2], fill=(100, 90, 80))
        draw.ellipse([cx+2, cy-2, cx+6, cy+2], fill=(100, 90, 80))
    elif convoy_type == 'troopship':
        # Large passenger ship
        draw.rectangle([cx-10, cy-6, cx+10, cy+6], fill=(120, 110, 100))
        for x_off in [-6, 0, 6]:
            draw.rectangle([cx+x_off-1, cy-8, cx+x_off+1, cy-6], fill=(50, 50, 50))  # Smokestacks
    elif convoy_type == 'escort':
        # Destroyer pattern
        draw.polygon([(cx-8, cy), (cx+8, cy-2), (cx+8, cy+2)], fill=COLORS['ship_destroyer'])
    
    return img


def create_damage_indicator_tile(size, severity='light', **kwargs):
    """Create damage indicator overlay."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    if severity == 'light':
        # Small crack
        draw.line([(cx-4, cy-4), (cx+4, cy+4)], fill=COLORS['damage'], width=2)
    elif severity == 'moderate':
        # X pattern
        draw.line([(cx-6, cy-6), (cx+6, cy+6)], fill=COLORS['damage'], width=2)
        draw.line([(cx-6, cy+6), (cx+6, cy-6)], fill=COLORS['damage'], width=2)
    elif severity == 'heavy':
        # Multiple cracks
        for angle in [0, 45, 90, 135]:
            rad = math.radians(angle)
            x2 = cx + 8 * math.cos(rad)
            y2 = cy + 8 * math.sin(rad)
            draw.line([(cx, cy), (x2, y2)], fill=COLORS['damage'], width=2)
    elif severity == 'critical':
        # Explosion-like pattern
        for radius in [6, 10, 14]:
            alpha = 200 - (radius - 6) * 40
            color = COLORS['explosion'][:3] + (alpha,)
            draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], 0, 360, fill=color, width=2)
    
    return img


def create_flag_tile(size, nation='Germany', **kwargs):
    """Create nation flag marker."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    color = COLORS.get(nation.lower(), (100, 100, 100))
    
    # Flag pole
    draw.line([(cx-8, cy+8), (cx-8, cy-12)], fill=(100, 100, 100), width=2)
    # Flag
    draw.polygon([(cx-8, cy-12), (cx+6, cy-8), (cx-8, cy-4)], fill=color)
    
    return img


def create_ui_border_tile(size, direction='horizontal', **kwargs):
    """Create UI border element."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if direction == 'horizontal':
        draw.line([(0, size//2), (size, size//2)], fill=COLORS['ui_border'], width=2)
    elif direction == 'vertical':
        draw.line([(size//2, 0), (size//2, size)], fill=COLORS['ui_border'], width=2)
    
    return img


def create_ui_corner_tile(size, corner='top-left', **kwargs):
    """Create UI corner element."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    if corner == 'top-left':
        draw.arc([0, 0, size, size], 180, 270, fill=COLORS['ui_border'], width=2)
    elif corner == 'top-right':
        draw.arc([0, 0, size, size], 270, 360, fill=COLORS['ui_border'], width=2)
    elif corner == 'bottom-left':
        draw.arc([0, 0, size, size], 90, 180, fill=COLORS['ui_border'], width=2)
    elif corner == 'bottom-right':
        draw.arc([0, 0, size, size], 0, 90, fill=COLORS['ui_border'], width=2)
    
    return img


def create_button_tile(size, state='normal', **kwargs):
    """Create UI button."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if state == 'normal':
        draw.rectangle([2, 2, size-2, size-2], fill=COLORS['ui_bg'], outline=COLORS['ui_border'])
    elif state == 'pressed':
        draw.rectangle([2, 2, size-2, size-2], fill=tuple(max(0, c-20) for c in COLORS['ui_bg']), outline=COLORS['ui_border'])
    
    return img


def create_obstacle_tile(size, obstacle_type='wreck', **kwargs):
    """Create obstacle marker."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    if obstacle_type == 'wreck':
        # Sunken ship silhouette
        draw.rectangle([cx-8, cy-4, cx+8, cy+4], fill=(80, 80, 80))
        draw.line([(cx, cy-4), (cx, cy-10)], fill=(60, 60, 60), width=2)  # Mast
        # Tilted angle
        draw.line([(cx-8, cy+4), (cx-4, cy+8)], fill=(100, 100, 100), width=2)
    
    return img


# Import existing tile creators from original file
def create_torpedo_tile(size, **kwargs):
    """Simple torpedo tile."""
    return create_torpedo_type_tile(size, 'generic', 'electric', **kwargs)


def create_explosion_tile(size, **kwargs):
    """Create explosion effect."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Layered explosion circles
    for radius in [4, 8, 12]:
        alpha = 255 - (radius - 4) * 30
        color = COLORS['explosion'][:3] + (alpha,)
        draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=color)
    
    # Debris particles
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x = cx + 14 * math.cos(rad)
        y = cy + 14 * math.sin(rad)
        draw.ellipse([x-2, y-2, x+2, y+2], fill=(255, 200, 100))
    
    return img


def create_ui_gauge(size, gauge_type='horizontal', level=1.0, **kwargs):
    """Create UI gauge."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Determine color based on level
    if level > 0.7:
        color = COLORS['ui_gauge_good']
    elif level > 0.3:
        color = COLORS['ui_gauge_warn']
    else:
        color = COLORS['ui_gauge_bad']
    
    if gauge_type == 'horizontal':
        # Horizontal bar gauge
        bar_width = 20
        bar_height = 6
        draw.rectangle([cx-bar_width//2, cy-bar_height//2, cx+bar_width//2, cy+bar_height//2], 
                      outline=COLORS['ui_border'], width=1)
        fill_width = int(bar_width * level)
        draw.rectangle([cx-bar_width//2, cy-bar_height//2, 
                       cx-bar_width//2+fill_width, cy+bar_height//2], fill=color)
    elif gauge_type == 'circular':
        # Circular arc gauge
        radius = 10
        draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], 180, 180 + int(180 * level), 
                fill=color, width=3)
    
    return img


def create_crew_icon(size, status='ok', **kwargs):
    """Create crew status icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Head
    draw.ellipse([cx-4, cy-8, cx+4, cy], fill=(200, 180, 160))
    # Body
    draw.rectangle([cx-5, cy, cx+5, cy+8], fill=(100, 100, 120))
    
    # Status indicator
    if status == 'ok':
        indicator_color = COLORS['ui_gauge_good']
    elif status == 'stressed':
        indicator_color = COLORS['ui_gauge_warn']
    elif status == 'injured':
        indicator_color = (255, 150, 50)
    elif status == 'critical':
        indicator_color = COLORS['ui_gauge_bad']
    else:
        indicator_color = (150, 150, 150)
    
    draw.ellipse([cx+6, cy-8, cx+10, cy-4], fill=indicator_color)
    
    return img


def create_compartment_tile(size, status='ok', **kwargs):
    """Create compartment status tile."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2
    
    # Compartment box
    if status == 'ok':
        color = COLORS['ui_gauge_good']
        symbol = '✓'
    elif status == 'damaged':
        color = COLORS['ui_gauge_warn']
        symbol = '!'
    elif status == 'critical':
        color = COLORS['ui_gauge_bad']
        symbol = 'X'
    elif status == 'flooding':
        color = (100, 150, 255)
        symbol = '~'
    else:
        color = (150, 150, 150)
        symbol = '?'
    
    draw.rectangle([cx-10, cy-8, cx+10, cy+8], outline=color, width=2)
    
    # Grid pattern
    for i in range(-8, 10, 4):
        draw.line([(cx+i, cy-8), (cx+i, cy+8)], fill=color, width=1)
        draw.line([(cx-10, cy+i), (cx+10, cy+i)], fill=color, width=1)
    
    return img


def generate_tileset():
    """Generate complete tileset with all tiles."""
    tileset = Image.new('RGBA', (COLS * TILE_SIZE, ROWS * TILE_SIZE), (0, 0, 0, 0))
    
    # Tile list: (name, create_function, kwargs)
    tiles = []
    
    # === ORIGINAL TILES (0-54) ===
    
    # Ocean tiles (0-7)
    for depth in ['surface', 'shallow', 'medium', 'deep', 'very_deep']:
        tiles.append((f'ocean_{depth}', create_ocean_tile, {'depth_level': depth}))
    tiles.append(('ocean_variant_1', create_ocean_tile, {'depth_level': 'medium'}))
    tiles.append(('ocean_variant_2', create_ocean_tile, {'depth_level': 'deep'}))
    tiles.append(('ocean_variant_3', create_ocean_tile, {'depth_level': 'surface'}))
    
    # Submarine tiles (8-23)
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        tiles.append((f'sub_angle_{angle}', create_submarine_tile, {'angle': angle, 'surfaced': True}))
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        tiles.append((f'sub_submerged_{angle}', create_submarine_tile, {'angle': angle, 'surfaced': False}))
    
    # Ship tiles (24-29)
    tiles.append(('merchant_ship', create_ship_tile, {'ship_type': 'merchant'}))
    tiles.append(('warship', create_ship_tile, {'ship_type': 'warship'}))
    tiles.append(('destroyer', create_ship_tile, {'ship_type': 'destroyer'}))
    tiles.append(('merchant_damaged', create_ship_tile, {'ship_type': 'merchant'}))
    tiles.append(('warship_damaged', create_ship_tile, {'ship_type': 'warship'}))
    tiles.append(('destroyer_damaged', create_ship_tile, {'ship_type': 'destroyer'}))
    
    # Torpedoes and effects (30-35)
    tiles.append(('torpedo', create_torpedo_tile, {}))
    tiles.append(('torpedo_wake', create_torpedo_tile, {}))
    tiles.append(('explosion_small', create_explosion_tile, {}))
    tiles.append(('explosion_medium', create_explosion_tile, {}))
    tiles.append(('explosion_large', create_explosion_tile, {}))
    tiles.append(('damage_marker', create_explosion_tile, {}))
    
    # UI gauges (36-47)
    for level in [1.0, 0.75, 0.5, 0.25]:
        tiles.append((f'gauge_h_{int(level*100)}', create_ui_gauge, {'gauge_type': 'horizontal', 'level': level}))
    for level in [1.0, 0.75, 0.5, 0.25]:
        tiles.append((f'gauge_c_{int(level*100)}', create_ui_gauge, {'gauge_type': 'circular', 'level': level}))
    for level in [1.0, 0.66, 0.33]:
        tiles.append((f'gauge_battery_{int(level*100)}', create_ui_gauge, {'gauge_type': 'horizontal', 'level': level}))
    
    # Crew icons (48-51)
    for status in ['ok', 'stressed', 'injured', 'critical']:
        tiles.append((f'crew_{status}', create_crew_icon, {'status': status}))
    
    # Compartment tiles (52-55)
    for status in ['ok', 'damaged', 'critical', 'flooding']:
        tiles.append((f'compartment_{status}', create_compartment_tile, {'status': status}))
    
    # === NEW ITEMS AND SYSTEMS (56+) ===
    
    # Periscope icons (56-59)
    for state in ['up', 'searching', 'locked', 'damaged']:
        tiles.append((f'periscope_{state}', create_periscope_tile, {'state': state}))
    
    # Sonar/Radar icons (60-63)
    for state in ['active', 'passive', 'ping']:
        tiles.append((f'sonar_{state}', create_sonar_tile, {'state': state}))
    tiles.append(('radar_scanning', create_radar_tile, {'state': 'scanning'}))
    
    # System status icons (64-71)
    for level, suffix in [(1.0, 'full'), (0.5, 'med'), (0.2, 'low')]:
        tiles.append((f'battery_{suffix}', create_battery_icon, {'level': level}))
    for level, suffix in [(1.0, 'full'), (0.5, 'med'), (0.2, 'low')]:
        tiles.append((f'oxygen_{suffix}', create_oxygen_icon, {'level': level}))
    for level, suffix in [(1.0, 'intact'), (0.5, 'damaged')]:
        tiles.append((f'hull_{suffix}', create_hull_icon, {'level': level}))
    
    # Torpedo types (72-78)
    torpedo_types = [
        ('torpedo_g7e', 'G7e', 'electric'),
        ('torpedo_g7a', 'G7a', 'air-fuel'),
        ('torpedo_mk14', 'Mk_14', 'air-fuel'),
        ('torpedo_mk23', 'Mk_23', 'homing'),
        ('torpedo_21inch', '21_inch', 'electric'),
        ('torpedo_type93', 'Type_93', 'oxygen'),
        ('torpedo_type95', 'Type_95', 'electric'),
    ]
    for name, tid, prop in torpedo_types:
        tiles.append((name, create_torpedo_type_tile, {'torpedo_id': tid, 'propulsion': prop}))
    
    # Mines and obstacles (79-82)
    for mine_type in ['contact', 'magnetic', 'acoustic']:
        tiles.append((f'mine_{mine_type}', create_mine_tile, {'mine_type': mine_type}))
    tiles.append(('obstacle_wreck', create_obstacle_tile, {'obstacle_type': 'wreck'}))
    
    # Weather effects (83-88)
    for weather in ['clear', 'fog', 'rain', 'storm', 'ice', 'night']:
        tiles.append((f'weather_{weather}', create_weather_tile, {'weather_type': weather}))
    
    # Port and strategic map (89-94)
    for status in ['friendly', 'enemy', 'neutral']:
        tiles.append((f'port_{status}', create_port_tile, {'status': status}))
    tiles.append(('waypoint', create_waypoint_tile, {}))
    for status in ['objective', 'complete']:
        tiles.append((f'mission_{status}', create_mission_tile, {'status': status}))
    
    # Aircraft types (95-100)
    for aircraft_type in ['bomber', 'patrol', 'fighter', 'recon', 'attacking', 'damaged']:
        tiles.append((f'aircraft_{aircraft_type}', create_aircraft_tile, {'aircraft_type': aircraft_type}))
    
    # Depth charges variants (101-104)
    for state in ['falling', 'armed', 'exploding']:
        tiles.append((f'depth_charge_{state}', create_depth_charge_tile, {'state': state}))
    tiles.append(('sonobuoy', create_sonobuoy_tile, {}))
    
    # Convoy markers (105-108)
    for convoy_type in ['cargo', 'tanker', 'troopship', 'escort']:
        tiles.append((f'convoy_{convoy_type}', create_convoy_marker_tile, {'convoy_type': convoy_type}))
    
    # Damage indicators (109-112)
    for severity in ['light', 'moderate', 'heavy', 'critical']:
        tiles.append((f'damage_{severity}', create_damage_indicator_tile, {'severity': severity}))
    
    # Signal flags (113-118)
    for nation in ['germany', 'usa', 'uk', 'japan', 'italy', 'ussr']:
        tiles.append((f'flag_{nation}', create_flag_tile, {'nation': nation}))
    
    # UI decorative elements (119-126)
    tiles.append(('ui_border_h', create_ui_border_tile, {'direction': 'horizontal'}))
    tiles.append(('ui_border_v', create_ui_border_tile, {'direction': 'vertical'}))
    for corner in ['top-left', 'top-right', 'bottom-left', 'bottom-right']:
        tiles.append((f'ui_corner_{corner.replace("-", "_")}', create_ui_corner_tile, {'corner': corner}))
    for state in ['normal', 'pressed']:
        tiles.append((f'ui_button_{state}', create_button_tile, {'state': state}))
    
    # Generate and place tiles
    atlas_map = {}
    for idx, (name, func, kwargs) in enumerate(tiles):
        if idx >= TOTAL_TILES:
            break
        
        row = idx // COLS
        col = idx % COLS
        
        # Generate tile
        tile = func(size=TILE_SIZE, **kwargs)
        
        # Paste into tileset
        x = col * TILE_SIZE
        y = row * TILE_SIZE
        tileset.paste(tile, (x, y), tile)
        
        # Add to atlas
        atlas_map[name] = idx
    
    return tileset, atlas_map


def main():
    """Generate tileset and atlas."""
    print("=" * 80)
    print("EXPANDED TILESET GENERATOR - WWII Submarine Roguelike")
    print("=" * 80)
    print()
    print("Generating comprehensive tileset with all game items...")
    
    # Generate tileset
    tileset, atlas_map = generate_tileset()
    
    # Save tileset PNG
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tilesets')
    os.makedirs(output_dir, exist_ok=True)
    
    tileset_path = os.path.join(output_dir, 'submarine_tileset.png')
    tileset.save(tileset_path)
    print(f"✅ Saved tileset: {tileset_path}")
    print(f"   Size: {tileset.width}x{tileset.height}")
    print(f"   Tiles: {len(atlas_map)}/{TOTAL_TILES} ({len(atlas_map)*100//TOTAL_TILES}% capacity)")
    
    # Generate atlas.json
    import json
    atlas = {
        "tile_size": TILE_SIZE,
        "cols": COLS,
        "rows": ROWS,
        "map": atlas_map
    }
    
    atlas_path = os.path.join(output_dir, 'atlas.json')
    with open(atlas_path, 'w') as f:
        json.dump(atlas, f, indent=2)
    print(f"✅ Saved atlas: {atlas_path}")
    
    # Print tile categories
    print("\n📊 Tile Breakdown by Category:")
    categories = {
        'Ocean': [n for n in atlas_map if n.startswith('ocean_')],
        'Submarine': [n for n in atlas_map if n.startswith('sub_')],
        'Ships': [n for n in atlas_map if 'ship' in n or n.startswith('destroyer') or n.startswith('merchant') or n.startswith('warship')],
        'Torpedoes': [n for n in atlas_map if n.startswith('torpedo')],
        'Weapons': [n for n in atlas_map if 'depth_charge' in n or n.startswith('mine_') or n == 'sonobuoy'],
        'Explosions': [n for n in atlas_map if 'explosion' in n or 'damage' in n],
        'Aircraft': [n for n in atlas_map if n.startswith('aircraft_')],
        'Weather': [n for n in atlas_map if n.startswith('weather_')],
        'Ports/Nav': [n for n in atlas_map if 'port' in n or 'waypoint' in n or 'mission' in n],
        'Convoys': [n for n in atlas_map if n.startswith('convoy_')],
        'Systems': [n for n in atlas_map if n.startswith('battery_') or n.startswith('oxygen_') or n.startswith('hull_')],
        'Sensors': [n for n in atlas_map if n.startswith('sonar_') or n.startswith('radar_') or n.startswith('periscope_')],
        'Crew/Comp': [n for n in atlas_map if n.startswith('crew_') or n.startswith('compartment_')],
        'UI/Gauges': [n for n in atlas_map if n.startswith('gauge_') or n.startswith('ui_')],
        'Flags': [n for n in atlas_map if n.startswith('flag_')],
        'Obstacles': [n for n in atlas_map if 'obstacle' in n or 'wreck' in n],
    }
    
    for category, tile_list in categories.items():
        if tile_list:
            print(f"  {category:15s}: {len(tile_list):3d} tiles")
    
    # Print tile mapping (condensed)
    print("\n📝 Sample Tile Mapping (first 20):")
    for name, idx in sorted(list(atlas_map.items())[:20], key=lambda x: x[1]):
        row = idx // COLS
        col = idx % COLS
        print(f"  {idx:3d} ({row:2d},{col:2d}): {name}")
    print(f"  ... ({len(atlas_map)-20} more tiles)")
    
    print()
    print("=" * 80)
    print(f"✅ TILESET GENERATION COMPLETE!")
    print(f"   Total: {len(atlas_map)}/{TOTAL_TILES} tiles")
    print(f"   Remaining capacity: {TOTAL_TILES - len(atlas_map)} tiles")
    print("=" * 80)


if __name__ == '__main__':
    main()
