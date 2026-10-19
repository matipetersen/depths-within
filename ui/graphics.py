"""Enhanced graphics rendering system with tilesheet support.

Provides multiple rendering backends:
1. Tilesheet rendering (pixel-based via tcod)
2. ASCII rendering (character-based fallback)
3. Color block rendering (graceful degradation)

Automatically detects available resources and uses the best available option.
"""

try:
    import tcod
    TCOD_AVAILABLE = True
except Exception:
    tcod = None
    TCOD_AVAILABLE = False

from ui.tileset import load_preferred_tileset, tile_coords_from_name, load_atlas


class GraphicsRenderer:
    """Enhanced graphics renderer with multi-backend support."""
    
    def __init__(self):
        self.use_tcod = TCOD_AVAILABLE
        self.tileset = None
        self.atlas = None
        self.console = None
        
        # Try to load tileset and atlas
        if self.use_tcod:
            try:
                self.tileset = load_preferred_tileset()
                self.atlas = load_atlas()
                print("[Graphics] Tileset loaded successfully")
            except Exception as e:
                print(f"[Graphics] Failed to load tileset: {e}")
                self.tileset = None
                self.atlas = None
    
    def get_render_backend(self):
        """Return the current render backend name."""
        if self.use_tcod and self.tileset:
            return "tilesheet"
        elif self.use_tcod:
            return "tcod_fallback"
        else:
            return "ascii_console"
    
    def has_tilesheet(self):
        """Check if tilesheet graphics are available."""
        return self.tileset is not None and self.atlas is not None
    
    def render_game(self, game):
        """Render the full game state."""
        backend = self.get_render_backend()
        
        if backend == "tilesheet":
            return self._render_tilesheet(game)
        elif backend == "tcod_fallback":
            return self._render_tcod_fallback(game)
        else:
            return self._render_ascii(game)
    
    def _render_tilesheet(self, game):
        """Render using tilesheet graphics."""
        # Initialize tcod context and console if needed
        if not hasattr(self, 'context') or self.context is None:
            self._init_graphics()
        
        # Clear console
        self.console.clear()
        
        # Render game to console
        self._render_game_to_console(game, self.console)
        
        # Present to screen
        self.context.present(self.console)
        
        # Handle events
        for event in tcod.event.get():
            if isinstance(event, tcod.event.Quit):
                print("\n[Graphics] Window closed by user")
                raise SystemExit()
    
    def _init_graphics(self):
        """Initialize tcod context and console."""
        if tcod is None or self.tileset is None:
            raise RuntimeError("Cannot initialize graphics: tcod or tileset not available")
        
        # Create context with tileset
        width_cells, height_cells = 80, 50
        tile_size = self.atlas.get('tile_size', 32) if self.atlas else 32
        
        self.context = tcod.context.new(
            width=width_cells * tile_size,
            height=height_cells * tile_size,
            tileset=self.tileset,
            title="Depths Within",
            vsync=True
        )
        self.console = tcod.Console(width_cells, height_cells)
        print(f"[Graphics] Initialized {width_cells}x{height_cells} console with {tile_size}px tiles")
    
    def _render_game_to_console(self, game, console):
        """Render game state to console using tiles."""
        # Render layers in order
        self._render_ocean(game, console)
        self._render_submarine(game, console)
        self._render_contacts(game, console)
        self._render_ui(game, console)
    
    def _render_ocean(self, game, console):
        """Render ocean background."""
        # For now, fill with ocean_surface tile (index 0)
        # In future, use tactical_map to vary depth
        console.print(0, 0, " " * (console.width * console.height), fg=(50, 100, 150))
    
    def _render_submarine(self, game, console):
        """Render submarine at current position."""
        if not game.submarine:
            return
        
        # Center submarine on screen
        x, y = console.width // 2, console.height // 2
        
        # Get heading and map to tile index (8 directions)
        heading = getattr(game.submarine, 'heading', 0)
        angle_idx = int((heading + 22.5) / 45) % 8
        
        # Choose surface or submerged tile
        depth = getattr(game.submarine.systems, 'depth', 0) if hasattr(game.submarine, 'systems') else 0
        if depth > 0:
            tile_idx = 16 + angle_idx  # sub_submerged_X
        else:
            tile_idx = 8 + angle_idx   # sub_angle_X
        
        # For now, use ASCII representation
        # TODO: Use actual tile indices when tile rendering is implemented
        console.print(x, y, "S", fg=(255, 255, 0))
    
    def _render_contacts(self, game, console):
        """Render contacts/ships."""
        # TODO: Get contacts from tactical_map or fog_of_war
        pass
    
    def _render_ui(self, game, console):
        """Render UI panels."""
        # Render header at top
        header = self._get_header(game)
        console.print(0, 0, header, fg=(255, 255, 255))
        
        # Render status at bottom
        if hasattr(game.submarine, 'status'):
            try:
                status = game.submarine.status()
                # Split status into lines and render at bottom
                lines = status.split('\n')[:5]  # Take first 5 lines
                for i, line in enumerate(lines):
                    console.print(0, console.height - 5 + i, line[:console.width], fg=(200, 200, 200))
            except Exception:
                pass
    
    def _render_tcod_fallback(self, game):
        """Render using tcod without full tilesheet support."""
        header = self._get_header(game)
        print(f"[TCOD] {header}")
        return self._render_ascii(game)
    
    def _render_ascii(self, game):
        """Render using ASCII console."""
        from ui.ascii_gui import draw_ascii_console
        
        try:
            draw_ascii_console(
                game,
                cursor=getattr(game, 'ascii_cursor', None),
                use_color=getattr(game, 'ascii_use_color', True)
            )
        except Exception as e:
            # Minimal fallback
            self._render_minimal(game)
    
    def _render_minimal(self, game):
        """Minimal fallback rendering."""
        header = self._get_header(game)
        print('┌' + '─' * 70 + '┐')
        print('│' + header.ljust(70) + '│')
        print('└' + '─' * 70 + '┘')
        
        try:
            print(game.submarine.status())
        except Exception:
            print("Submarine status unavailable")
    
    def _get_header(self, game):
        """Get the standard game header line."""
        turn = getattr(game, 'turn', 0)
        depth = 'N/A'
        try:
            if hasattr(game.submarine, 'systems'):
                depth = game.submarine.systems.depth
        except Exception:
            pass
        
        return f"Turn: {turn} | Depth: {depth}m"
    
    def get_tile_color(self, tile_name):
        """Get RGB color for a named tile (for color block rendering)."""
        if not self.atlas:
            return (100, 100, 100)  # Default gray
        
        from ui.tileset import tile_coords_from_name
        coords = tile_coords_from_name(tile_name, self.atlas)
        
        if coords is None:
            return (100, 100, 100)
        
        # TODO: Extract average color from tile
        return (100, 150, 200)  # Placeholder submarine blue
    
    def get_graphics_info(self):
        """Get information about available graphics."""
        return {
            'backend': self.get_render_backend(),
            'tcod_available': self.use_tcod,
            'tileset_loaded': self.has_tilesheet(),
            'atlas_loaded': self.atlas is not None,
            'features': {
                'tilesheet': self.has_tilesheet(),
                'pixel_rendering': self.use_tcod and self.tileset is not None,
                'ascii_rendering': True,
                'color_support': True,
            }
        }


class TilesheetManager:
    """Manages tilesheet assets and tile mapping."""
    
    def __init__(self):
        self.atlas = load_atlas()
        self.tile_cache = {}
        self.missing_tiles = set()
    
    def get_tile_code(self, tile_name):
        """Get the tile code for a named tile."""
        if self.atlas is None:
            return None
        
        mapping = self.atlas.get('map', {})
        return mapping.get(tile_name)
    
    def get_tile_coords(self, tile_name):
        """Get x,y coordinates of a tile in the sheet."""
        if self.atlas is None:
            return None
        
        coords = tile_coords_from_name(tile_name, self.atlas)
        return coords
    
    def get_all_tiles(self):
        """Get all available tiles."""
        if self.atlas is None:
            return {}
        
        return self.atlas.get('map', {})
    
    def list_tiles_by_prefix(self, prefix):
        """Get all tiles matching a prefix."""
        if self.atlas is None:
            return []
        
        mapping = self.atlas.get('map', {})
        return [name for name in mapping.keys() if name.startswith(prefix)]
    
    def get_tile_categories(self):
        """Get tile categories based on name prefixes."""
        if self.atlas is None:
            return {}
        
        categories = {}
        mapping = self.atlas.get('map', {})
        
        for tile_name in mapping.keys():
            prefix = tile_name.split('_')[0]
            if prefix not in categories:
                categories[prefix] = []
            categories[prefix].append(tile_name)
        
        return categories


class SonarDisplay:
    """Specialized rendering for sonar/tactical display with tiles."""
    
    def __init__(self, tileset_manager=None):
        self.tileset = tileset_manager or TilesheetManager()
    
    def render_contact(self, contact, use_tiles=True):
        """Render a sonar contact."""
        contact_type = contact.get('type', 'unknown').lower()
        
        if use_tiles:
            tile_map = {
                'submarine': 'sub_silhouette',
                'ship': 'ship_silhouette',
                'destroyer': 'ship_silhouette',
                'convoy': 'ship_silhouette',
                'contact': 'sonar_ping',
            }
            tile_name = tile_map.get(contact_type, 'sonar_ping')
            tile_code = self.tileset.get_tile_code(tile_name)
            return tile_code if tile_code is not None else '●'
        else:
            char_map = {
                'submarine': '◉',
                'ship': '⊞',
                'destroyer': '⊟',
                'convoy': '◈',
                'contact': '●',
            }
            return char_map.get(contact_type, '●')
    
    def render_sonar_screen(self, sonar_data, width=40, height=20, use_tiles=False):
        """Render a full sonar screen."""
        screen = [['.' for _ in range(width)] for _ in range(height)]
        
        contacts = sonar_data.get('contacts', [])
        center_x, center_y = width // 2, height // 2
        
        # Place contacts on screen
        for contact in contacts:
            bearing = contact.get('bearing', 0)
            range_m = contact.get('range', 0)
            
            # Convert bearing/range to screen coords (simple polar projection)
            import math
            angle_rad = math.radians(bearing)
            x = int(center_x + (range_m / 1000) * math.sin(angle_rad) * (width / 2))
            y = int(center_y - (range_m / 1000) * math.cos(angle_rad) * (height / 2))
            
            if 0 <= x < width and 0 <= y < height:
                char = self.render_contact(contact, use_tiles)
                screen[y][x] = char
        
        # Render center
        screen[center_y][center_x] = '⊙'
        
        # Format as string
        lines = [''.join(row) for row in screen]
        return '\n'.join(lines)
