"""
ASCII Glyph definitions for units, compartments, and UI elements.
Used for ASCII rendering in the game.
"""

# Submarine and Contact Glyphs
GLYPHS = {
    # Player submarine variants
    'submarine_player': '⊓',      # Player submarine (iconic sub shape)
    'submarine_player_alt': '◉',  # Alternative player sub marker
    'submarine_surfaced': '≈',    # Surfaced submarine
    
    # Contact types
    'contact_merchant': '⊞',      # Merchant ship
    'contact_warship': '⊕',       # Warship
    'contact_escort': '◄',        # Escort vessel
    'contact_submarine': '◇',     # Enemy submarine
    'contact_unknown': '?',       # Unknown contact
    
    # Convoy and Formation
    'convoy': '▲',                 # Convoy group
    'formation': 'ⓞ',              # Formation indicator
    
    # Aircraft
    'aircraft': '✈',              # Aircraft in flight
    'aircraft_patrol': '⚡',       # Patrol aircraft
    'aircraft_bomber': '☠',       # Bomber aircraft
    'aircraft_fighter': '◆',      # Fighter aircraft
    
    # Torpedoes and Weapons
    'torpedo': '→',               # Torpedo in flight
    'torpedo_homing': '↗',        # Homing torpedo (angled)
    'depth_charge': 'o',          # Depth charge
    
    # Compartment Roles (crew)
    'crew_captain': 'C',          # Captain
    'crew_sonar': 'S',            # Sonar operator
    'crew_torpedo': 'T',          # Torpedo specialist
    'crew_engineering': 'E',      # Engineer
    'crew_damage_control': 'D',   # Damage control
    'crew_navigator': 'N',        # Navigator
    'crew_radio': 'R',            # Radio operator
    'crew_gunner': 'G',           # Gunner
    
    # Map Features
    'depth_shallow': '~',         # Shallow water
    'depth_medium': '=',          # Medium depth
    'depth_deep': ',',            # Deep water
    'depth_very_deep': ':',       # Very deep water
    'depth_trench': '.',          # Trench/bottom
    
    'thermocline': '-',           # Thermocline (thermal layer)
    'minefield': '✱',             # Minefield
    'coast': '#',                 # Coastline/shallow
    'land': '█',                  # Land
    
    # Damage and Status
    'damaged': 'X',               # Damaged status
    'flooded': '▓',               # Flooded
    'on_fire': '▲',               # On fire
    'sinking': '↓',               # Sinking
    
    # Events
    'event_alert': '!',           # Alert/event marker
    'event_critical': '‼',        # Critical event
    'event_resolved': '✓',        # Event resolved
    
    # UI Elements
    'ui_border_h': '─',           # Horizontal border
    'ui_border_v': '│',           # Vertical border
    'ui_border_tl': '┌',          # Top-left corner
    'ui_border_tr': '┐',          # Top-right corner
    'ui_border_bl': '└',          # Bottom-left corner
    'ui_border_br': '┘',          # Bottom-right corner
    'ui_separator': '─',          # Separator line
    
    # Status Indicators
    'status_online': '●',         # Online/functional
    'status_damaged': '◐',        # Damaged
    'status_offline': '○',        # Offline/non-functional
    'status_unknown': '?',        # Unknown status
    
    # Skill/Expertise Markers
    'skill_novice': '◇',          # Novice (low skill)
    'skill_trained': '◆',         # Trained (medium skill)
    'skill_expert': '★',          # Expert (high skill)
    
    # Weather/Environment
    'weather_clear': '.',         # Clear weather
    'weather_fog': '≈',           # Fog
    'weather_storm': '⚑',         # Storm/rough sea
    'weather_rain': '∼',          # Rain
}


def get_glyph(glyph_name: str, default: str = '?') -> str:
    """Get glyph by name, with fallback to default."""
    return GLYPHS.get(glyph_name, default)


def get_contact_glyph(contact_type: str) -> str:
    """Get appropriate glyph for contact type."""
    type_map = {
        'merchant': 'contact_merchant',
        'cargo': 'contact_merchant',
        'tanker': 'contact_merchant',
        'warship': 'contact_warship',
        'destroyer': 'contact_warship',
        'cruiser': 'contact_warship',
        'escort': 'contact_escort',
        'submarine': 'contact_submarine',
    }
    glyph_name = type_map.get(contact_type.lower(), 'contact_unknown')
    return get_glyph(glyph_name)


def get_compartment_crew_glyph(role: str) -> str:
    """Get glyph for crew member by role."""
    role_map = {
        'captain': 'crew_captain',
        'sonar': 'crew_sonar',
        'sonar_operator': 'crew_sonar',
        'torpedo': 'crew_torpedo',
        'torpedo_specialist': 'crew_torpedo',
        'engineering': 'crew_engineering',
        'engineer': 'crew_engineering',
        'damage_control': 'crew_damage_control',
        'navigator': 'crew_navigator',
        'radio': 'crew_radio',
        'radio_operator': 'crew_radio',
        'gunner': 'crew_gunner',
    }
    glyph_name = role_map.get(role.lower(), 'crew_captain')
    return get_glyph(glyph_name)


def get_depth_glyph(depth: float, max_depth: float = 250) -> str:
    """Get glyph representing water depth."""
    ratio = depth / max_depth if max_depth > 0 else 0
    
    if ratio < 0.1:
        return get_glyph('depth_shallow')
    elif ratio < 0.35:
        return get_glyph('depth_medium')
    elif ratio < 0.65:
        return get_glyph('depth_deep')
    elif ratio < 0.95:
        return get_glyph('depth_very_deep')
    else:
        return get_glyph('depth_trench')


def get_damage_glyph(damage_level: float) -> str:
    """Get glyph representing damage level (0-1)."""
    if damage_level < 0.25:
        return get_glyph('status_online')
    elif damage_level < 0.6:
        return get_glyph('status_damaged')
    else:
        return get_glyph('status_offline')


def get_skill_glyph(skill_level: float) -> str:
    """Get glyph representing skill level (0-1)."""
    if skill_level < 0.33:
        return get_glyph('skill_novice')
    elif skill_level < 0.66:
        return get_glyph('skill_trained')
    else:
        return get_glyph('skill_expert')


def get_weather_glyph(visibility: float) -> str:
    """Get glyph representing weather conditions."""
    # visibility is 0-1 where 1 is clear
    if visibility > 0.8:
        return get_glyph('weather_clear')
    elif visibility > 0.5:
        return get_glyph('weather_rain')
    elif visibility > 0.2:
        return get_glyph('weather_fog')
    else:
        return get_glyph('weather_storm')


def render_health_bar(current: float, max_val: float, width: int = 10) -> str:
    """Render a health bar using Unicode block characters."""
    if max_val == 0:
        ratio = 0
    else:
        ratio = min(1.0, current / max_val)
    
    filled = int(ratio * width)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}]"


def render_status_bar(value: float, width: int = 10, threshold_warn: float = 0.7, 
                      threshold_crit: float = 0.95) -> str:
    """Render status bar with color coding (warn/crit levels)."""
    value = max(0.0, min(1.0, value))
    filled = int(value * width)
    
    if value >= threshold_crit:
        # Critical: use ▓
        bar = '▓' * filled + '░' * (width - filled)
    elif value >= threshold_warn:
        # Warning: use ▒
        bar = '▒' * filled + '░' * (width - filled)
    else:
        # Normal: use █
        bar = '█' * filled + '░' * (width - filled)
    
    return f"[{bar}]"


# Example usage
if __name__ == '__main__':
    print("ASCII Glyph Reference:")
    print(f"Player Submarine: {get_glyph('submarine_player')}")
    print(f"Merchant Ship: {get_contact_glyph('merchant')}")
    print(f"Sonar Operator: {get_compartment_crew_glyph('sonar')}")
    print(f"Damage Level (25%): {get_damage_glyph(0.25)}")
    print(f"Skill Level (80%): {get_skill_glyph(0.8)}")
    print(f"Health Bar: {render_health_bar(75, 100)}")
    print(f"Stress Bar: {render_status_bar(0.8)}")
