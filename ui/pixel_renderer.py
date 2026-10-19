"""Modern pixel-based renderer using SDL and the submarine tileset.

This renderer uses actual 32x32 pixel tiles instead of console characters,
providing a modern graphical roguelike experience.
"""

import os
import math
from typing import Optional, Tuple
try:
    import tcod
    import tcod.sdl.render
    from PIL import Image
    import numpy as np
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

from ui.graphics_renderer import GraphicsRenderer


class PixelRenderer:
    """Pixel-based renderer that draws actual tile graphics."""
    
    def __init__(self, window_width: int = 1920, window_height: int = 1080):
        if not AVAILABLE:
            raise RuntimeError("tcod and PIL required for pixel rendering")
        
        self.tile_size = 32
        self.window_width = window_width
        self.window_height = window_height
        
        # Calculate how many tiles fit on screen
        self.tiles_x = window_width // self.tile_size
        self.tiles_y = window_height // self.tile_size
        
        # Load graphics system
        self.graphics = GraphicsRenderer()
        
        # Load tileset image
        tileset_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tilesets', 'submarine_tileset.png')
        self.tileset_img = Image.open(tileset_path).convert('RGBA')
        self.tileset_array = np.array(self.tileset_img)
        
        # Create SDL texture for tileset
        self.context = None
        self.renderer = None
        self.tileset_texture = None
        
        print(f"[PixelRenderer] Initialized {self.tiles_x}x{self.tiles_y} tile grid ({window_width}x{window_height}px)")
    
    def init_sdl(self):
        """Initialize SDL context and renderer."""
        self.context = tcod.context.new(
            width=self.window_width,
            height=self.window_height,
            title="Depths Within",
            vsync=True,
            sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE
        )
        self.renderer = self.context.sdl_renderer
        
        # Create texture from tileset
        surface = tcod.sdl.render.load_bmp(
            os.path.join(os.path.dirname(__file__), '..', 'assets', 'tilesets', 'submarine_tileset.png')
        )
        self.tileset_texture = self.renderer.create_texture_from_surface(surface)
        
        print("[PixelRenderer] SDL initialized")
    
    def get_tile_rect(self, tile_name: str) -> Optional[Tuple[int, int, int, int]]:
        """Get source rectangle for a tile in the tileset."""
        coords = self.graphics.get_tile_coords(tile_name)
        if not coords:
            return None
        
        col, row = coords
        x = col * self.tile_size
        y = row * self.tile_size
        return (x, y, self.tile_size, self.tile_size)
    
    def draw_tile(self, tile_name: str, screen_x: int, screen_y: int):
        """Draw a tile at the given screen position."""
        if not self.renderer or not self.tileset_texture:
            return False
        
        src_rect = self.get_tile_rect(tile_name)
        if not src_rect:
            return False
        
        src_x, src_y, w, h = src_rect
        dst_x = screen_x * self.tile_size
        dst_y = screen_y * self.tile_size
        
        # Copy tile from tileset to screen
        self.renderer.copy(
            self.tileset_texture,
            srcrect=(src_x, src_y, w, h),
            dstrect=(dst_x, dst_y, self.tile_size, self.tile_size)
        )
        return True
    
    def render_map(self, game):
        """Render the tactical map."""
        if not self.renderer:
            return
        
        # Clear screen
        self.renderer.draw_color = (0, 0, 0, 255)
        self.renderer.clear()
        
        # Get submarine position for camera
        try:
            sub_x = int(getattr(game.submarine, 'x', 0))
            sub_y = int(getattr(game.submarine, 'y', 0))
        except:
            sub_x, sub_y = 0, 0
        
        # Calculate camera offset to center submarine
        camera_x = sub_x - self.tiles_x // 2
        camera_y = sub_y - self.tiles_y // 2
        
        # Render ocean tiles
        tmap = getattr(game, 'tactical_map', None)
        if not tmap:
            return
        
        for screen_y in range(self.tiles_y):
            for screen_x in range(self.tiles_x):
                world_x = screen_x + camera_x
                world_y = screen_y + camera_y
                
                # Get depth and appropriate tile
                depth = tmap.get_depth(world_x, world_y)
                if depth is None:
                    depth = 500
                
                tile_name = self.graphics.get_ocean_tile_for_depth(depth)
                self.draw_tile(tile_name, screen_x, screen_y)
        
        # Draw submarine
        sub_screen_x = self.tiles_x // 2
        sub_screen_y = self.tiles_y // 2
        heading = getattr(game.submarine, 'heading', 0)
        depth = getattr(game.submarine.systems, 'depth', 0) if hasattr(game.submarine, 'systems') else 0
        
        sub_tile = self.graphics.get_submarine_tile_for_angle(heading, depth > 10)
        self.draw_tile(sub_tile, sub_screen_x, sub_screen_y)
        
        # Draw contacts
        try:
            contacts = game.submarine.sonar.detect()
            for contact in contacts:
                bearing = float(contact.get('bearing', 0))
                rng = contact.get('range', 1000)
                
                # Convert to screen position
                angle_rad = math.radians(90 - bearing)
                tiles_away = int(rng / 1000)  # Rough conversion
                
                contact_world_x = sub_x + int(math.cos(angle_rad) * tiles_away)
                contact_world_y = sub_y + int(math.sin(angle_rad) * tiles_away)
                
                contact_screen_x = contact_world_x - camera_x
                contact_screen_y = contact_world_y - camera_y
                
                if 0 <= contact_screen_x < self.tiles_x and 0 <= contact_screen_y < self.tiles_y:
                    contact_type = contact.get('type', 'merchant')
                    if 'destroyer' in contact_type.lower():
                        ship_tile = 'ship_destroyer'
                    elif 'cruiser' in contact_type.lower():
                        ship_tile = 'ship_cruiser'
                    else:
                        ship_tile = 'ship_merchant'
                    
                    self.draw_tile(ship_tile, contact_screen_x, contact_screen_y)
        except:
            pass
        
        # Present
        self.renderer.present()
    
    def cleanup(self):
        """Clean up SDL resources."""
        if self.tileset_texture:
            self.tileset_texture.destroy()
        if self.context:
            self.context.close()
