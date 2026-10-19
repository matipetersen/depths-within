"""Enhanced PanelManager for tcod rendering with graphics.

This manager composes panels (main sonar panel, HUD, log) and renders
them to the provided tcod Console using the new tileset system.
"""
try:
    import tcod
except Exception:
    tcod = None

from ui.panels.main_panel import MainPanel
from ui.panels.log_panel import LogPanel
from ui.panels.compartment_panel import CompartmentPanel
from ui.panels.lore_panel import LorePanel
from world.tactical_map import TacticalMap
from ui.graphics_renderer import get_renderer


class PanelManager:
    def __init__(self):
        self.main = MainPanel(width=41, height=21)
        self.log = LogPanel()
        self.comp = CompartmentPanel()
        self.lore = LorePanel()
        # create a tactical map for rendering and link to submarine when available
        self.tmap = TacticalMap(width=60, height=30)
        self.show_compartments = False
        self.show_log = True
        # Get graphics renderer
        self.graphics = get_renderer()

    def render(self, console, game):
        # === LAYOUT CONSTANTS ===
        HEADER_H = 3
        LOG_H = 8
        
        # Calculate main area dimensions
        main_w = console.width
        main_h = console.height - HEADER_H - LOG_H
        
        # Split main area: 60% Tactical Map, 40% Depth Map
        tactical_w = int(main_w * 0.6)
        depth_w = main_w - tactical_w
        
        # === 1. HEADER (Top Bar) ===
        self.graphics.render_ui_border(console, 0, 0, main_w, HEADER_H + 1, title="DEPTHS WITHIN")
        
        # Stats
        turn = getattr(game, 'turn', 0)
        depth = getattr(game.submarine.systems, 'depth', 0)
        battery = getattr(game.submarine.systems, 'battery', 1.0)
        oxygen = getattr(game.submarine.systems, 'oxygen', 1.0)
        noise = getattr(game.submarine.systems, 'noise_level', 1.0)
        
        # Horror Stage
        horror_stage = "NORMAL"
        if hasattr(game, 'horror_manager') and game.horror_manager:
            horror_stage = game.horror_manager.current_stage.name
        
        # Colors
        c_good = (100, 255, 100)
        c_warn = (255, 255, 0)
        c_bad = (255, 50, 50)
        
        # Render Stats
        y_stat = 1
        x_cursor = 2
        
        console.print(x_cursor, y_stat, f"Turn: {turn}", fg=(255, 255, 255))
        x_cursor += 12
        
        console.print(x_cursor, y_stat, f"Depth: {depth}m", fg=(150, 220, 255))
        x_cursor += 15
        
        bat_col = c_good if battery > 0.5 else c_warn if battery > 0.2 else c_bad
        console.print(x_cursor, y_stat, f"Bat: {int(battery*100)}%", fg=bat_col)
        x_cursor += 12
        
        oxy_col = c_good if oxygen > 0.5 else c_warn if oxygen > 0.2 else c_bad
        console.print(x_cursor, y_stat, f"O2: {int(oxygen*100)}%", fg=oxy_col)
        x_cursor += 12
        
        noise_col = c_good if noise < 2.0 else c_warn if noise < 5.0 else c_bad
        console.print(x_cursor, y_stat, f"Noise: {noise:.1f}", fg=noise_col)
        x_cursor += 15
        
        console.print(x_cursor, y_stat, f"Stage: {horror_stage}", fg=(255, 150, 255))

        # === 2. TACTICAL MAP (Left) ===
        map_x = 0
        map_y = HEADER_H
        # Leave border space
        view_w = tactical_w - 2
        view_h = main_h - 2
        
        self.graphics.render_ui_border(console, map_x, map_y, tactical_w, main_h, title="TACTICAL")
        
        # Camera centering
        sub_x = getattr(game.submarine, 'x', 0)
        sub_y = getattr(game.submarine, 'y', 0)
        cam_x = int(sub_x - view_w // 2)
        cam_y = int(sub_y - view_h // 2)
        
        # Use game map if available, else fallback to local
        current_map = getattr(game, 'tactical_map', self.tmap)
        
        # Draw Ocean & Fog of War
        for sy in range(view_h):
            for sx in range(view_w):
                wx = cam_x + sx
                wy = cam_y + sy
                
                # Check visibility
                visible = True
                explored = True
                
                if hasattr(game, 'fog_of_war') and game.fog_of_war:
                    visible = game.fog_of_war.is_visible((wx, wy))
                    explored = game.fog_of_war.is_explored((wx, wy))
                
                screen_x = map_x + 1 + sx
                screen_y = map_y + 1 + sy
                
                if visible:
                    depth_val = current_map.get_depth(wx, wy)
                    tile = self.graphics.get_ocean_tile_for_depth(depth_val)
                    self.graphics.render_tile_to_console(console, tile, screen_x, screen_y)
                elif explored:
                    # Dimmed / Greyed out - Brightened significantly for visibility
                    console.print(screen_x, screen_y, '.', fg=(100, 150, 200))
                else:
                    # Unexplored (Black) - Use dark blue background to avoid pure black void
                    console.print(screen_x, screen_y, ' ', bg=(5, 10, 20))

        # Draw Submarine (Always visible to self)
        sub_sx = int(sub_x - cam_x)
        sub_sy = int(sub_y - cam_y)
        if 0 <= sub_sx < view_w and 0 <= sub_sy < view_h:
            heading = getattr(game.submarine, 'heading', 0)
            self.graphics.render_submarine(console, map_x + 1 + sub_sx, map_y + 1 + sub_sy, heading, depth)

        # Draw Visible Contacts
        visible_contacts = game.get_visible_contacts() if hasattr(game, 'get_visible_contacts') else []
        
        # Draw Ports
        if hasattr(current_map, 'get_ports'):
            for port in current_map.get_ports():
                px, py = port.get('x'), port.get('y')
                psx = int(px - cam_x)
                psy = int(py - cam_y)
                
                if 0 <= psx < view_w and 0 <= psy < view_h:
                    screen_x = map_x + 1 + psx
                    screen_y = map_y + 1 + psy
                    
                    status = port.get('status', 'neutral')
                    
                    # Draw port symbol using graphics renderer
                    self.graphics.render_port(console, screen_x, screen_y, status)
                    
                    # Draw name if mouse hovered (or just always for now if space permits)
                    # console.print(screen_x + 1, screen_y, port.get('name', 'Port')[:5], fg=color)

        for c in visible_contacts:
            cx, cy = c.get('x'), c.get('y')
            csx = int(cx - cam_x)
            csy = int(cy - cam_y)
            
            if 0 <= csx < view_w and 0 <= csy < view_h:
                c_type = c.get('type', 'unknown')
                is_ghost = c.get('is_ghost', False)
                
                screen_x = map_x + 1 + csx
                screen_y = map_y + 1 + csy
                
                if is_ghost:
                    console.print(screen_x, screen_y, '?', fg=(255, 0, 255)) # Magenta Ghost
                elif c_type == 'merchant':
                    self.graphics.render_ship(console, screen_x, screen_y, 'merchant')
                elif c_type == 'warship':
                    self.graphics.render_ship(console, screen_x, screen_y, 'warship')
                elif c_type == 'submarine':
                    console.print(screen_x, screen_y, 'E', fg=(255, 50, 50))
                elif c_type == 'biological':
                    console.print(screen_x, screen_y, 'w', fg=(100, 200, 255))
                else:
                    console.print(screen_x, screen_y, '?', fg=(255, 255, 0))

        # === 3. DEPTH MAP (Right) ===
        depth_x = tactical_w
        depth_y = HEADER_H
        d_view_w = depth_w - 2
        d_view_h = main_h - 2
        
        self.graphics.render_ui_border(console, depth_x, depth_y, depth_w, main_h, title="DEPTH MAP")
        
        # Slice view logic
        slice_start_x = int(sub_x - d_view_w // 2)
        max_depth_scale = 500.0
        
        # Thermal Layer
        thermal_layer = 150
        if hasattr(game, 'fog_of_war') and game.fog_of_war:
            thermal_layer = game.fog_of_war.thermal_layer_depth
        thermal_row = int((thermal_layer / max_depth_scale) * d_view_h)

        for sy in range(d_view_h):
            # Calculate depth for this row
            row_depth = (sy / d_view_h) * max_depth_scale
            
            for sx in range(d_view_w):
                wx = slice_start_x + sx
                # Sample terrain depth at sub's Y
                terrain_depth = current_map.get_depth(wx, sub_y)
                
                screen_x = depth_x + 1 + sx
                screen_y = depth_y + 1 + sy
                
                if terrain_depth is not None and row_depth > terrain_depth:
                    # Ground - Brightened
                    console.print(screen_x, screen_y, '#', fg=(80, 80, 80))
                else:
                    # Water
                    # Draw Thermal Layer
                    if sy == thermal_row:
                        console.print(screen_x, screen_y, '-', fg=(200, 200, 200))
                    elif sy == 0:
                        # Surface
                        console.print(screen_x, screen_y, '~', fg=(150, 220, 255))
                    else:
                        # Water column - darker as it goes deeper, but minimum brightness increased significantly
                        col_val = max(40, 140 - int(row_depth/3))
                        console.print(screen_x, screen_y, ' ', bg=(0, 10, col_val))

        # Draw Submarine on Depth Map
        sub_dsx = int(sub_x - slice_start_x)
        sub_dsy = int((depth / max_depth_scale) * d_view_h)
        
        if 0 <= sub_dsx < d_view_w and 0 <= sub_dsy < d_view_h:
            console.print(depth_x + 1 + sub_dsx, depth_y + 1 + sub_dsy, '@', fg=(255, 255, 0))

        # Draw Contacts on Depth Map
        for c in visible_contacts:
            cx = c.get('x')
            cy = c.get('y')
            cdepth = c.get('depth', 0)
            
            # Only show if near sub's Y plane (slice thickness)
            if abs(cy - sub_y) < 5:
                dsx = int(cx - slice_start_x)
                dsy = int((cdepth / max_depth_scale) * d_view_h)
                
                if 0 <= dsx < d_view_w and 0 <= dsy < d_view_h:
                    c_type = c.get('type', 'unknown')
                    char = '?'
                    color = (255, 255, 255)
                    
                    if c_type == 'merchant': char = 'M'
                    elif c_type == 'warship': char = 'D'; color = (255, 50, 50)
                    elif c_type == 'submarine': char = 'E'; color = (255, 0, 0)
                    elif c_type == 'ghost': char = '?'; color = (255, 0, 255)
                    
                    console.print(depth_x + 1 + dsx, depth_y + 1 + dsy, char, fg=color)

        # === 4. LOG / CONTROLS (Bottom) ===
        log_y = main_h + HEADER_H
        self.graphics.render_ui_border(console, 0, log_y, main_w, LOG_H, title="LOG & CONTROLS")
        
        # Controls Hint (Left side of bottom panel)
        hints = [
            "ARROWS: Move",
            "P: Active Ping",
            "X: Silent Run",
            "-/=: Dive/Rise",
            "T: Target",
            "F: Fire Torp",
            "H: Help (All Cmds)",
            "Q: Quit"
        ]
        for i, hint in enumerate(hints):
            console.print(2, log_y + 1 + i, hint, fg=(255, 255, 255))
            
        # Log (Right side of bottom panel)
        log_x = 25
        log_w = main_w - log_x - 2
        
        if hasattr(game, 'logger'):
            recent = list(game.logger.recent())[-5:]
            for i, msg in enumerate(recent):
                text = msg.get('text', str(msg))
                console.print(log_x, log_y + 1 + i, text[:log_w], fg=(255, 255, 255))

        # === 5. OVERLAYS ===
        
        # Help Overlay
        if getattr(game, 'show_help', False):
            help_w = 60
            help_h = 24
            help_x = (main_w - help_w) // 2
            help_y = (main_h - help_h) // 2
            
            # Draw box
            self.graphics.render_ui_border(console, help_x, help_y, help_w, help_h, title="COMMAND REFERENCE")
            
            # Clear background
            for y in range(help_y + 1, help_y + help_h):
                console.print(help_x + 1, y, " " * (help_w - 2), bg=(10, 10, 20))
            
            commands = [
                ("NAVIGATION", ""),
                ("Arrows", "Move Submarine"),
                ("- / =", "Dive / Surface (25m increments)"),
                ("Space", "Wait / Hold Position"),
                ("", ""),
                ("COMBAT", ""),
                ("T", "Cycle Targets"),
                ("F", "Fire Torpedo (at Target or Cursor)"),
                ("P", "Active Sonar Ping (Reveals contacts)"),
                ("X", "Toggle Silent Running"),
                ("", ""),
                ("SYSTEMS", ""),
                ("R", "Repair Damaged Compartment"),
                ("V", "Periscope View"),
                ("C", "Toggle Compartment Status"),
                ("1-4", "Speed: Slow/Std/Full/Flank"),
                ("", ""),
                ("GAME", ""),
                ("H", "Toggle This Help"),
                ("Q", "Quit Game")
            ]
            
            for i, (cmd, desc) in enumerate(commands):
                if desc == "":
                    console.print(help_x + 2, help_y + 2 + i, cmd, fg=(255, 255, 0)) # Header
                else:
                    console.print(help_x + 4, help_y + 2 + i, f"{cmd:10} : {desc}", fg=(200, 200, 200))

        # Target Line Visualization
        if hasattr(game, 'selected_target_id') and game.selected_target_id:
            # Find target
            contacts = game.get_visible_contacts()
            target = next((c for c in contacts if c.get('id') == game.selected_target_id), None)
            
            if target:
                # Draw line from sub to target
                tx, ty = target.get('x'), target.get('y')
                sx, sy = game.submarine.x, game.submarine.y
                
                # Convert to screen coords
                cam_x = int(sx - view_w // 2)
                cam_y = int(sy - view_h // 2)
                
                screen_tx = map_x + 1 + int(tx - cam_x)
                screen_ty = map_y + 1 + int(ty - cam_y)
                screen_sx = map_x + 1 + int(sx - cam_x)
                screen_sy = map_y + 1 + int(sy - cam_y)
                
                # Only draw if both on screen (simple check)
                if (0 <= int(tx - cam_x) < view_w and 0 <= int(ty - cam_y) < view_h):
                    # Draw target reticle
                    console.print(screen_tx, screen_ty, 'X', fg=(255, 0, 0), bg=(50, 0, 0))
                    
                    # Draw line (bresenham or tcod line)
                    points = tcod.los.bresenham((screen_sx, screen_sy), (screen_tx, screen_ty)).tolist()
                    for px, py in points[1:-1]: # Skip start/end
                        if map_x < px < map_x + tactical_w and map_y < py < map_y + main_h:
                            console.print(px, py, '.', fg=(255, 100, 100))

    def _old_render(self, console, game):
        # ...existing code...
        pass
