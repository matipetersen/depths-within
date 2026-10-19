"""Enhanced graphics renderer for tcod using the submarine tileset.

This module provides high-level rendering functions that use the generated
tileset to create a visually appealing submarine game display.
"""

import math
from typing import Optional, Tuple, List
import os
import json

try:
    import tcod
    from PIL import Image
    GRAPHICS_AVAILABLE = True
except ImportError:
    GRAPHICS_AVAILABLE = False
    tcod = None


class GraphicsRenderer:
    """High-level graphics renderer using the submarine tileset."""
    
    def __init__(self):
        self.atlas = None
        self.tileset_image = None
        self.tile_size = 32
        self.cols = 16
        self.rows = 16
        self._load_atlas()
        self._load_tileset_image()
    
    def _load_atlas(self):
        """Load the atlas.json file."""
        try:
            atlas_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tilesets', 'atlas.json')
            with open(atlas_path, 'r') as f:
                self.atlas = json.load(f)
                self.tile_size = self.atlas.get('tile_size', 32)
                self.cols = self.atlas.get('cols', 16)
                self.rows = self.atlas.get('rows', 16)
        except Exception as e:
            print(f"Warning: Could not load atlas.json: {e}")
            self.atlas = None
    
    def _load_tileset_image(self):
        """Load the tileset PNG for direct tile access."""
        if not GRAPHICS_AVAILABLE:
            return
        
        try:
            tileset_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tilesets', 'submarine_tileset.png')
            self.tileset_image = Image.open(tileset_path).convert('RGBA')
        except Exception as e:
            print(f"Warning: Could not load tileset image: {e}")
            self.tileset_image = None
    
    def get_tile_index(self, tile_name: str) -> Optional[int]:
        """Get tile index from name."""
        if not self.atlas:
            return None
        return self.atlas.get('map', {}).get(tile_name)
    
    def get_tile_coords(self, tile_name: str) -> Optional[Tuple[int, int]]:
        """Get tile coordinates (col, row) from name."""
        idx = self.get_tile_index(tile_name)
        if idx is None:
            return None
        
        col = idx % self.cols
        row = idx // self.cols
        return (col, row)
    
    def get_tile_pixel_coords(self, tile_name: str) -> Optional[Tuple[int, int, int, int]]:
        """Get pixel coordinates (x, y, width, height) for a tile."""
        coords = self.get_tile_coords(tile_name)
        if not coords:
            return None
        
        col, row = coords
        x = col * self.tile_size
        y = row * self.tile_size
        return (x, y, self.tile_size, self.tile_size)
    
    def get_ocean_tile_for_depth(self, depth: float) -> str:
        """Get appropriate ocean tile name for given depth."""
        if depth is None:
            return 'ocean_deep'  # Default for out-of-bounds
        if depth < 100:
            return 'ocean_surface'
        elif depth < 200:
            return 'ocean_shallow'
        elif depth < 300:
            return 'ocean_medium'
        elif depth < 400:
            return 'ocean_deep'
        else:
            return 'ocean_very_deep'
    
    def get_submarine_tile_for_angle(self, angle: float, submerged: bool = False) -> str:
        """Get submarine tile name for given angle and depth.
        
        Args:
            angle: Heading angle in degrees (0-360)
            submerged: True if submarine is submerged
        
        Returns:
            Tile name string
        """
        # Snap to nearest 45 degrees
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        closest_angle = min(angles, key=lambda x: abs(((angle - x + 180) % 360) - 180))
        
        if submerged:
            return f'sub_submerged_{closest_angle}'
        else:
            return f'sub_angle_{closest_angle}'
    
    def get_gauge_tile(self, gauge_type: str, level: float) -> str:
        """Get appropriate gauge tile for given level.
        
        Args:
            gauge_type: 'horizontal', 'circular', or 'battery'
            level: Value from 0.0 to 1.0
        
        Returns:
            Tile name string
        """
        # Snap to nearest available level
        if gauge_type == 'battery':
            if level > 0.83:
                return 'gauge_battery_100'
            elif level > 0.49:
                return 'gauge_battery_66'
            else:
                return 'gauge_battery_33'
        elif gauge_type == 'horizontal':
            if level > 0.875:
                return 'gauge_h_100'
            elif level > 0.625:
                return 'gauge_h_75'
            elif level > 0.375:
                return 'gauge_h_50'
            else:
                return 'gauge_h_25'
        else:  # circular
            if level > 0.875:
                return 'gauge_c_100'
            elif level > 0.625:
                return 'gauge_c_75'
            elif level > 0.375:
                return 'gauge_c_50'
            else:
                return 'gauge_c_25'
    
    def render_tile_to_console(self, console, tile_name: str, x: int, y: int, bg_color: Optional[Tuple[int, int, int]] = None):
        """Render a named tile to a tcod console at given position.
        
        Args:
            console: tcod.Console instance
            tile_name: Name of tile from atlas
            x, y: Console coordinates
            bg_color: Optional background color (R, G, B)
        """
        if not GRAPHICS_AVAILABLE or not tcod:
            return False
            
        # Check if we should use ASCII fallback (if tileset is disabled)
        use_tileset = os.environ.get('USE_TILESET', '0') == '1'
        
        if not use_tileset:
            # ASCII Fallback Mode
            char, fg_color = self._get_ascii_fallback(tile_name)
            try:
                if x < 0 or y < 0 or x >= console.width or y >= console.height:
                    return False
                console.print(x, y, char, fg=fg_color, bg=bg_color if bg_color else (0, 0, 0))
                return True
            except Exception:
                return False

        tile_idx = self.get_tile_index(tile_name)
        if tile_idx is None:
            return False
        
        try:
            # Check console bounds
            if x < 0 or y < 0 or x >= console.width or y >= console.height:
                return False
            
            # Use the Private Use Area offset where we loaded our sprites (0xE000)
            # This allows us to mix text (standard ASCII) and sprites (PUA)
            char_code = 0xE000 + tile_idx
            
            # Render using the character code
            # We use white fg so the texture colors are preserved
            # We use black bg (or transparent if supported)
            fg = (255, 255, 255)
            bg = bg_color if bg_color else (0, 0, 0)
            
            console.print(x, y, chr(char_code), fg=fg, bg=bg)
            return True
            
        except Exception as e:
            return False

    def _get_ascii_fallback(self, tile_name: str) -> Tuple[str, Tuple[int, int, int]]:
        """Get ASCII char and color for a tile name."""
        char = '?'
        color = (200, 200, 200)
        
        # Ocean / Depth
        if 'ocean' in tile_name:
            if 'surface' in tile_name: return '~', (50, 180, 255)
            if 'shallow' in tile_name: return '~', (30, 130, 220)
            if 'medium' in tile_name: return '.', (20, 80, 180)
            if 'deep' in tile_name: return '.', (10, 50, 140)
            if 'very_deep' in tile_name: return ' ', (5, 30, 80)
            return ' ', (0, 0, 0)
            
        # Entities
        if 'sub' in tile_name: return '@', (255, 255, 0)
        if 'merchant' in tile_name: return 'M', (200, 200, 200)
        if 'destroyer' in tile_name: return 'D', (255, 50, 50)
        if 'warship' in tile_name: return 'W', (200, 50, 50)
        if 'torpedo' in tile_name: return '!', (255, 255, 0)
        if 'aircraft' in tile_name: return '^', (255, 255, 255)
        if 'mine' in tile_name: return '*', (255, 0, 0)
        if 'wreck' in tile_name: return '#', (100, 100, 100)
        
        # UI
        if 'ui_border' in tile_name:
            if 'h' in tile_name: return '─', (100, 100, 100)
            if 'v' in tile_name: return '│', (100, 100, 100)
            if 'corner' in tile_name: return '+', (100, 100, 100)
            return '#', (100, 100, 100)
            
        # Gauges
        if 'gauge' in tile_name:
            if '100' in tile_name: return '█', (0, 255, 0)
            if '75' in tile_name: return '▓', (100, 255, 0)
            if '50' in tile_name: return '▒', (255, 255, 0)
            if '25' in tile_name: return '░', (255, 0, 0)
            return ' ', (50, 50, 50)
            
        # Status
        if 'hull_intact' in tile_name: return 'OK', (0, 255, 0)
        if 'hull_damaged' in tile_name: return 'DMG', (255, 0, 0)
        if 'battery' in tile_name: return 'BAT', (255, 255, 0)
        if 'oxygen' in tile_name: return 'O2', (0, 255, 255)
        
        # Ports
        if 'port' in tile_name:
            if 'friendly' in tile_name: return 'P', (100, 255, 100)
            if 'hostile' in tile_name: return 'P', (255, 100, 100)
            return 'P', (200, 200, 200)

        return char, color

    
    def render_ocean_background(self, console, width: int, height: int, depth_map=None):
        """Render ocean background with depth shading.
        
        Args:
            console: tcod.Console instance
            width, height: Size of area to render
            depth_map: Optional function(x, y) -> depth value
        """
        for y in range(height):
            for x in range(width):
                if depth_map:
                    depth = depth_map(x, y)
                else:
                    # Default depth gradient
                    depth = 100 + (y * 10)
                
                tile_name = self.get_ocean_tile_for_depth(depth)
                self.render_tile_to_console(console, tile_name, x, y)
    
    def render_submarine(self, console, x: int, y: int, heading: float, depth: float):
        """Render submarine sprite at position.
        
        Args:
            console: tcod.Console instance
            x, y: Console coordinates
            heading: Submarine heading in degrees
            depth: Current depth in meters
        """
        submerged = depth > 10  # Submerged if deeper than 10m
        tile_name = self.get_submarine_tile_for_angle(heading, submerged)
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_ship(self, console, x: int, y: int, ship_type: str = 'merchant', damaged: bool = False):
        """Render ship sprite at position.
        
        Args:
            console: tcod.Console instance
            x, y: Console coordinates
            ship_type: 'merchant', 'warship', or 'destroyer'
            damaged: Whether ship is damaged
        """
        if damaged:
            tile_name = f'{ship_type}_damaged'
        else:
            tile_name = f'{ship_type}_ship' if ship_type == 'merchant' else ship_type
        
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_torpedo(self, console, x: int, y: int):
        """Render torpedo sprite at position."""
        return self.render_tile_to_console(console, 'torpedo', x, y)
    
    def render_explosion(self, console, x: int, y: int, size: str = 'medium'):
        """Render explosion effect at position.
        
        Args:
            size: 'small', 'medium', or 'large'
        """
        tile_name = f'explosion_{size}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_gauge(self, console, x: int, y: int, gauge_type: str, level: float):
        """Render a UI gauge.
        
        Args:
            console: tcod.Console instance
            x, y: Console coordinates
            gauge_type: 'horizontal', 'circular', or 'battery'
            level: Value from 0.0 to 1.0
        """
        tile_name = self.get_gauge_tile(gauge_type, level)
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_crew_icon(self, console, x: int, y: int, status: str = 'ok'):
        """Render crew member icon.
        
        Args:
            status: 'ok', 'stressed', 'injured', or 'critical'
        """
        tile_name = f'crew_{status}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_compartment(self, console, x: int, y: int, status: str = 'ok'):
        """Render compartment status icon.
        
        Args:
            status: 'ok', 'damaged', 'critical', or 'flooding'
        """
        tile_name = f'compartment_{status}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    # === EXPANDED TILE RENDERING METHODS ===
    
    def render_torpedo_type(self, console, x: int, y: int, torpedo_type: str = 'G7e'):
        """Render specific historical torpedo type."""
        torpedo_map = {
            'G7e': 'torpedo_g7e',
            'G7a': 'torpedo_g7a',
            'Mk_14': 'torpedo_mk14',
            'Mk_23': 'torpedo_mk23',
            '21_inch': 'torpedo_21inch',
            'Type_93': 'torpedo_type93',
            'Type_95': 'torpedo_type95',
        }
        tile_name = torpedo_map.get(torpedo_type, 'torpedo')
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_mine(self, console, x: int, y: int, mine_type: str = 'contact'):
        """Render mine with type indication."""
        tile_name = f'mine_{mine_type}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_periscope(self, console, x: int, y: int, state: str = 'up'):
        """Render periscope state icon."""
        tile_name = f'periscope_{state}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_sonar(self, console, x: int, y: int, state: str = 'active'):
        """Render sonar state icon."""
        tile_name = f'sonar_{state}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_radar(self, console, x: int, y: int):
        """Render radar scanning icon."""
        return self.render_tile_to_console(console, 'radar_scanning', x, y)
    
    def render_battery(self, console, x: int, y: int, level: float = 1.0):
        """Render battery status based on level."""
        if level >= 0.8:
            tile_name = 'battery_full'
        elif level >= 0.4:
            tile_name = 'battery_med'
        else:
            tile_name = 'battery_low'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_oxygen(self, console, x: int, y: int, level: float = 1.0):
        """Render oxygen status based on level."""
        if level >= 0.8:
            tile_name = 'oxygen_full'
        elif level >= 0.4:
            tile_name = 'oxygen_med'
        else:
            tile_name = 'oxygen_low'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_hull_status(self, console, x: int, y: int, level: float = 1.0):
        """Render hull integrity status."""
        if level >= 0.8:
            tile_name = 'hull_intact'
        else:
            tile_name = 'hull_damaged'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_weather(self, console, x: int, y: int, weather_type: str = 'clear'):
        """Render weather effect."""
        tile_name = f'weather_{weather_type}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_port(self, console, x: int, y: int, status: str = 'neutral'):
        """Render port marker."""
        tile_name = f'port_{status}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_waypoint(self, console, x: int, y: int):
        """Render navigation waypoint."""
        return self.render_tile_to_console(console, 'waypoint', x, y)
    
    def render_mission(self, console, x: int, y: int, status: str = 'objective'):
        """Render mission marker."""
        tile_name = f'mission_{status}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_aircraft(self, console, x: int, y: int, aircraft_type: str = 'bomber', damaged: bool = False):
        """Render aircraft with type and status."""
        if damaged:
            tile_name = 'aircraft_damaged'
        else:
            tile_name = f'aircraft_{aircraft_type}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_depth_charge_state(self, console, x: int, y: int, state: str = 'falling'):
        """Render depth charge with specific state."""
        tile_name = f'depth_charge_{state}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_sonobuoy(self, console, x: int, y: int):
        """Render sonobuoy marker."""
        return self.render_tile_to_console(console, 'sonobuoy', x, y)
    
    def render_convoy(self, console, x: int, y: int, convoy_type: str = 'cargo'):
        """Render convoy formation marker."""
        tile_name = f'convoy_{convoy_type}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_damage_overlay(self, console, x: int, y: int, severity: str = 'light'):
        """Render damage indicator overlay."""
        tile_name = f'damage_{severity}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_flag(self, console, x: int, y: int, nation: str = 'Germany'):
        """Render nation flag marker."""
        tile_name = f'flag_{nation.lower()}'
        return self.render_tile_to_console(console, tile_name, x, y)
    
    def render_obstacle(self, console, x: int, y: int, obstacle_type: str = 'wreck'):
        """Render obstacle marker."""
        tile_name = f'obstacle_{obstacle_type}'
        return self.render_tile_to_console(console, tile_name, x, y)

    def render_ui_border(self, console, x: int, y: int, width: int, height: int, title: Optional[str] = None):
        """Render a UI border using tileset border pieces.
        
        Args:
            console: tcod.Console instance
            x, y: Top-left position
            width, height: Dimensions including border
            title: Optional title to display in top border
        """
        if width < 2 or height < 2:
            return

        # Draw corners
        self.render_tile_to_console(console, 'ui_corner_top_left', x, y)
        self.render_tile_to_console(console, 'ui_corner_top_right', x + width - 1, y)
        self.render_tile_to_console(console, 'ui_corner_bottom_left', x, y + height - 1)
        self.render_tile_to_console(console, 'ui_corner_bottom_right', x + width - 1, y + height - 1)
        
        # Draw horizontal borders
        for i in range(1, width - 1):
            self.render_tile_to_console(console, 'ui_border_h', x + i, y)
            self.render_tile_to_console(console, 'ui_border_h', x + i, y + height - 1)
            
        # Draw vertical borders
        for i in range(1, height - 1):
            self.render_tile_to_console(console, 'ui_border_v', x, y + i)
            self.render_tile_to_console(console, 'ui_border_v', x + width - 1, y + i)
            
        # Draw title if provided
        if title:
            # Center title
            title_len = len(title)
            if title_len < width - 2:
                start_x = x + (width - title_len) // 2
                console.print(start_x, y, title, fg=(255, 255, 255), bg=(0, 0, 0))


# Global renderer instance
_renderer = None

def get_renderer() -> GraphicsRenderer:
    """Get or create global graphics renderer instance."""
    global _renderer
    if _renderer is None:
        _renderer = GraphicsRenderer()
    return _renderer
