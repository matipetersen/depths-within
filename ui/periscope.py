"""
ASCII Periscope View Renderer
Generates a 2D visual representation of the horizon based on tactical map data.
"""

import math

def render_periscope_view(game, width=80, height=20):
    """
    Render the periscope view.
    
    Args:
        game: The game instance
        width: Width of the view in characters
        height: Height of the view in characters
        
    Returns:
        List of strings representing the view
    """
    # Constants
    FOV = 60.0  # Field of view in degrees
    CENTER_BEARING = getattr(game.submarine, 'heading', 0)
    
    # Initialize buffer with sky and ocean
    horizon_y = height // 2
    buffer = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Draw Sky (Day/Night cycle could affect this)
    sky_char = ' '
    if hasattr(game, 'time_system'):
        time_info = game.time_system.get_time_info()
        if time_info['time_of_day'] == 'night':
            sky_char = '.'  # Stars
        elif time_info['time_of_day'] in ['dawn', 'dusk']:
            sky_char = '-'
    
    for y in range(horizon_y):
        for x in range(width):
            if sky_char == '.':
                if (x * y * 13) % 97 == 0: # Pseudo-random stars
                    buffer[y][x] = '.'
            else:
                buffer[y][x] = sky_char

    # Draw Ocean
    for y in range(horizon_y, height):
        for x in range(width):
            buffer[y][x] = '~' if (x+y)%2==0 else ' '

    # Draw Horizon Line
    for x in range(width):
        buffer[horizon_y][x] = '-'

    # Get contacts
    contacts = []
    if game.tactical_map:
        contacts.extend(game.tactical_map.get_contacts())
        # Filter only surface contacts for periscope
        # (Submarines only if surfaced, but we'll simplify for now)
    
    # Process contacts for rendering
    visible_contacts = []
    
    sub_x = game.submarine.x
    sub_y = game.submarine.y
    
    for contact in contacts:
        cx = contact.get('x', 0)
        cy = contact.get('y', 0)
        
        # Calculate distance
        dx = cx - sub_x
        dy = cy - sub_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Max visual range (approx 20 tiles)
        if dist > 20:
            continue
            
        # Calculate bearing
        # Math angle: 0 is East, increases counter-clockwise
        # Compass bearing: 0 is North, increases clockwise
        # We need bearing from sub to target
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        bearing = (90 - angle_deg) % 360
        
        # Calculate relative bearing (-180 to +180)
        rel_bearing = (bearing - CENTER_BEARING + 180) % 360 - 180
        
        # Check if in FOV
        if abs(rel_bearing) <= FOV / 2:
            visible_contacts.append({
                'dist': dist,
                'rel_bearing': rel_bearing,
                'type': contact.get('type', 'merchant')
            })
            
    # Sort by distance (draw far objects first)
    visible_contacts.sort(key=lambda c: c['dist'], reverse=True)
    
    # Draw contacts
    for c in visible_contacts:
        # Horizontal position (0 to width-1)
        # rel_bearing maps from -FOV/2 to +FOV/2 -> 0 to width
        screen_x = int((c['rel_bearing'] + FOV/2) / FOV * width)
        
        # Scale based on distance (closer = bigger)
        # dist 1 = scale 1.0, dist 20 = scale 0.1
        scale = max(0.2, 1.0 - (c['dist'] / 20.0))
        
        ship_w = max(3, int(10 * scale))
        ship_h = max(2, int(5 * scale))
        
        # Vertical position (on horizon, slightly lower if closer)
        screen_y = horizon_y + int((1.0 - scale) * 2) 
        
        # Draw ship sprite
        draw_ship(buffer, screen_x, screen_y, ship_w, ship_h, c['type'])

    # Convert buffer to strings
    lines = ["".join(row) for row in buffer]
    
    # Add overlay info
    lines[0] = f"PERISCOPE VIEW - BEARING {int(CENTER_BEARING):03d}°".center(width)
    lines[height-1] = f"CONTACTS: {len(visible_contacts)}".center(width)
    
    return lines

def draw_ship(buffer, cx, bottom_y, w, h, ship_type):
    """Draw a simple ASCII ship centered at cx, sitting on bottom_y."""
    height = len(buffer)
    width = len(buffer[0])
    
    half_w = w // 2
    start_x = cx - half_w
    start_y = bottom_y - h + 1
    
    # Simple ship shapes
    if ship_type == 'destroyer':
        # Warship shape
        #      |
        #    _/_|__
        #  _/      \__
        # \___________/
        shape = [
            "      |      ",
            "    _/_|__   ",
            "  _/      \__",
            " \___________/"
        ]
    else:
        # Merchant shape
        #      __
        #    _|  |_
        #  _/      \__
        # \___________/
        shape = [
            "      __     ",
            "    _|  |_   ",
            "  _/      \__",
            " \___________/"
        ]
        
    # Scale/Crop shape to fit w, h roughly
    # For now, just center the fixed shape and clip
    
    for r, line in enumerate(shape):
        # Map to buffer coordinates
        # Align bottom of shape to bottom_y
        buf_y = bottom_y - (len(shape) - 1 - r)
        
        if 0 <= buf_y < height:
            # Center line at cx
            line_start_x = cx - len(line)//2
            
            for c_idx, char in enumerate(line):
                buf_x = line_start_x + c_idx
                if 0 <= buf_x < width and char != ' ':
                    buffer[buf_y][buf_x] = char

```