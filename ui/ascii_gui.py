"""ASCII GUI renderer for when tilesets are not available.

This draws a simple ASCII tactical map and HUD to stdout. It's intended as
an interim GUI while tileset art is being prepared.
"""
import os
import math


def draw_dual_view(game, cursor=None, use_color=True):
    """Draw dual-view display: top-down submarine view on left, depth map on right.
    
    Args:
        game: Game instance
        cursor: Optional targeting cursor
        use_color: Use ANSI colors
    """
    # Clear screen first to prevent multiple screens stacking
    print("\033[2J\033[H", end='')  # ANSI clear screen and move cursor to top
    
    # Layout
    tactical_w = 60
    tactical_h = 30
    depth_w = 40
    depth_h = 30
    
    tmap = getattr(game, 'tactical_map', None)
    sub = getattr(game, 'submarine', None)
    
    # ANSI helpers
    CSI = "\x1b["
    def ansi(code):
        return f"{CSI}{code}m" if use_color else ""
    
    HEADER = ansi('1;36')   # bold cyan
    SUBHEADER = ansi('36')  # cyan
    HINT = ansi('33')       # yellow
    GOOD = ansi('32')       # green
    WARN = ansi('31')       # red
    LAND = ansi('32')       # green for land
    WATER_S = ansi('36')    # cyan for shallow
    WATER_D = ansi('34')    # blue for deep
    RESET = ansi('0')
    
    # Header
    if sub and hasattr(sub, 'systems'):
        depth = getattr(sub.systems, 'depth', 'N/A')
        battery = getattr(sub.systems, 'battery', 1.0)
        oxygen = getattr(sub.systems, 'oxygen', 1.0)
        noise = getattr(sub.systems, 'noise_level', 1.0)
        
        batt_str = f"{battery:.0%}" if isinstance(battery, float) else str(battery)
        oxy_str = f"{oxygen:.0%}" if isinstance(oxygen, float) else str(oxygen)
        
        # Color code noise
        noise_col = GOOD
        if noise > 5.0: noise_col = WARN
        elif noise > 2.0: noise_col = ansi('33') # yellow
        
        header = f"Turn: {getattr(game, 'turn', 0):4d} | Depth: {depth}m | Battery: {batt_str} | O2: {oxy_str} | Noise: {noise_col}{noise:.1f}{RESET}"
    else:
        header = f"Turn: {getattr(game, 'turn', 0)}"
    
    total_w = tactical_w + depth_w + 5
    print('+' + '-' * (total_w - 2) + '+')
    print('| ' + (HEADER + header + RESET).ljust(total_w - 4 + (len(HEADER)+len(RESET) if use_color else 0)) + ' |')
    print('+' + '-' * (total_w - 2) + '+')
    
    # Camera logic for immense map
    sub_x = getattr(sub, 'x', 0) if sub else 0
    sub_y = getattr(sub, 'y', 0) if sub else 0
    
    cam_x = max(0, min(tmap.width - tactical_w, sub_x - tactical_w // 2))
    cam_y = max(0, min(tmap.height - tactical_h, sub_y - tactical_h // 2))
    
    # Draw both maps side by side
    for y in range(tactical_h):
        # LEFT: Tactical map with submarine and contacts (Viewport)
        tactical_line = []
        if tmap:
            row_chars = [' '] * tactical_w
            
            # Draw terrain
            for x in range(tactical_w):
                world_x = cam_x + x
                world_y = cam_y + y
                
                if 0 <= world_x < tmap.width and 0 <= world_y < tmap.height:
                    d = tmap.get_depth(world_x, world_y)
                    if d is not None:
                        if d <= 0:
                            row_chars[x] = LAND + '#' + RESET
                        elif d < 50:
                            row_chars[x] = WATER_S + '~' + RESET
                        elif d < 150:
                            row_chars[x] = WATER_D + '.' + RESET
                        elif d < 300:
                            row_chars[x] = WATER_D + ':' + RESET
                        else:
                            row_chars[x] = ' '
            
            # Draw visible contacts (Fog of War)
            visible_contacts = game.get_visible_contacts() if hasattr(game, 'get_visible_contacts') else []
            
            # If game doesn't support FoW yet (fallback), use truth data
            if not hasattr(game, 'get_visible_contacts'):
                # ... (This fallback is complex to reconstruct inline, so we assume game has the method now)
                # But for safety, let's just use the truth data if the list is empty AND FoW is missing
                pass

            for contact in visible_contacts:
                cx = contact.get('x', -1)
                cy = contact.get('y', -1)
                screen_x = cx - cam_x
                screen_y = cy - cam_y
                
                if 0 <= screen_x < tactical_w and screen_y == y:
                    c_type = contact.get('type', 'unknown')
                    
                    # Determine char and color based on type
                    char = '?'
                    color = ansi('37') # white
                    
                    if c_type == 'merchant':
                        char = 'M'
                        color = ansi('37')
                    elif c_type == 'warship':
                        char = 'D'
                        color = WARN
                    elif c_type == 'submarine':
                        char = 'E'
                        color = WARN
                    elif c_type == 'biological':
                        char = 'W'
                        color = ansi('34')
                    elif c_type == 'ghost':
                        char = '?'
                        color = ansi('35') # Magenta
                    elif c_type == 'unknown':
                        char = '?'
                        color = ansi('33') # yellow
                    
                    # Mark stale contacts (ghosts)
                    if contact.get('stale', False):
                        color = ansi('90') # dark grey
                    
                    row_chars[screen_x] = color + char + RESET
            
            # Draw torpedoes
            torpedoes = getattr(tmap, 'torpedoes', [])
            for torp in torpedoes:
                if getattr(torp, 'active', False):
                    tx = getattr(torp, 'x', -1)
                    ty = getattr(torp, 'y', -1)
                    screen_x = int(tx) - cam_x
                    screen_y = int(ty) - cam_y
                    
                    if 0 <= screen_x < tactical_w and screen_y == y:
                        is_homing = getattr(torp, 'homing_strength', 0) > 0
                        torp_glyph = '↗' if is_homing else '→'
                        row_chars[screen_x] = ansi('33') + torp_glyph + RESET
            
            # Draw player submarine
            if sub:
                sx = getattr(sub, 'x', -1)
                sy = getattr(sub, 'y', -1)
                screen_x = sx - cam_x
                screen_y = sy - cam_y
                
                if 0 <= screen_x < tactical_w and screen_y == y:
                    row_chars[screen_x] = GOOD + '@' + RESET
            
            tactical_line = ''.join(row_chars)
        else:
            tactical_line = ' ' * tactical_w
        
        # RIGHT: Depth map (Slice View centered on Submarine)
        depth_line = []
        if tmap:
            row_chars = [' '] * depth_w
            max_depth = 500
            
            # Calculate slice range (X axis relative to sub)
            slice_start_x = sub_x - depth_w // 2
            
            # SURFACE LAYER
            if y == 0:
                row_chars = [WATER_S + '~' + RESET] * depth_w
                # Overlay visible contacts in slice
                visible_contacts = game.get_visible_contacts() if hasattr(game, 'get_visible_contacts') else []
                
                for contact in visible_contacts:
                    cx = contact.get('x', -1)
                    cy = contact.get('y', -1)
                    cdepth = contact.get('depth', 0)
                    
                    # Only show if within Y range of sub (e.g. +/- 5 tiles)
                    if abs(cy - sub_y) < 5 and cdepth <= 10: # Surface contacts
                        slice_x = cx - slice_start_x
                        if 0 <= slice_x < depth_w:
                            c_type = contact.get('type', 'unknown')
                            char = '?'
                            color = ansi('37')
                            
                            if c_type == 'merchant': char = 'M'; color = ansi('37')
                            elif c_type == 'warship': char = 'D'; color = WARN
                            elif c_type == 'biological': char = 'W'; color = ansi('34')
                            elif c_type == 'submarine': char = 'E'; color = WARN
                            
                            row_chars[slice_x] = color + char + RESET
            else:
                # UNDERWATER LAYERS
                # Get thermal layer depth
                thermal_layer = 150
                if hasattr(game, 'fog_of_war') and game.fog_of_war:
                    thermal_layer = game.fog_of_war.thermal_layer_depth
                
                thermal_row = int((thermal_layer / max_depth) * depth_h)

                for x in range(depth_w):
                    world_x = slice_start_x + x
                    # Sample depth at sub's Y (or average of nearby Ys?)
                    # Let's use sub's Y for a true slice
                    d = tmap.get_depth(world_x, sub_y)
                    
                    if d is not None:
                        # Calculate if this pixel is "ground"
                        # y goes from 0 (top) to depth_h (bottom)
                        # Map y to depth
                        pixel_depth = (y / depth_h) * max_depth
                        
                        if pixel_depth > d:
                            # Below sea floor
                            row_chars[x] = ansi('30') + '#' + RESET # Dark grey ground
                        else:
                            # Water column
                            char = ' '
                            color = ''
                            
                            # Draw thermal layer
                            if y == thermal_row:
                                char = '-'
                                color = ansi('90') # Dark grey dashed line
                            
                            if pixel_depth < 50:
                                char = '.' if char == ' ' else char
                                color = WATER_S if color == '' else color
                            elif pixel_depth < 200:
                                char = '.' if char == ' ' else char
                                color = WATER_D if color == '' else color
                            
                            row_chars[x] = color + char + RESET
                
                # Overlay visible underwater contacts
                visible_contacts = game.get_visible_contacts() if hasattr(game, 'get_visible_contacts') else []
                # Add player sub manually as it's always visible to self
                if sub:
                    visible_contacts.append({
                        'x': sub.x, 'y': sub.y, 
                        'depth': getattr(sub.systems, 'depth', 0), 
                        'type': 'player'
                    })
                
                for contact in visible_contacts:
                    cx = contact.get('x', -1)
                    cy = contact.get('y', -1)
                    cdepth = contact.get('depth', 0)
                    
                    if abs(cy - sub_y) < 5 and cdepth > 10: # Underwater contacts
                        slice_x = cx - slice_start_x
                        depth_row = int((cdepth / max_depth) * depth_h)
                        
                        if 0 <= slice_x < depth_w and depth_row == y:
                            c_type = contact.get('type', 'unknown')
                            char = '?'
                            color = ansi('37')
                            
                            if c_type == 'player': char = '@'; color = GOOD
                            elif c_type == 'submarine': char = 'E'; color = WARN
                            elif c_type == 'biological': char = 'w'; color = ansi('34')
                            elif c_type == 'ghost': char = '?'; color = ansi('35') # Magenta for ghosts
                            
                            row_chars[slice_x] = color + char + RESET

            depth_line = '|' + ''.join(row_chars) + '|'
        else:
            depth_line = '|' + ' ' * depth_w + '|'
        
        # Calculate padding to align right panel
        # tactical_line contains ANSI codes, so len() is misleading.
        # We know the visible width is tactical_w.
        # We print tactical_line, then padding, then depth_line.
        
        print('| ' + tactical_line + ' | ' + depth_line)
    
    # Bottom separator
    print('+' + '-' * (total_w - 2) + '+')
    
    # Info line
    if sub:
        sx = getattr(sub, 'x', None)
        sy = getattr(sub, 'y', None)
        if sx is not None and sy is not None:
            contacts = tmap.get_contacts() if tmap else []
            submarines = tmap.get_submarines() if tmap else []
            info = f"Pos: ({sx:3d},{sy:3d}) | Ships: {len(contacts)} | Subs: {len(submarines)} | Map: {tmap.width}x{tmap.height}"
            print('| ' + HINT + info.ljust(total_w - 4 + (len(HINT)+len(RESET) if use_color else 0)) + RESET + ' |')
    
    # Check for pending decision
    if hasattr(game, 'decision_manager') and game.decision_manager and game.decision_manager.pending_decision:
        decision = game.decision_manager.pending_decision
        
        # Draw decision box
        print('+' + '=' * (total_w - 2) + '+')
        print('| ' + (ansi('1;33') + "CAPTAIN'S DECISION REQUIRED" + RESET).center(total_w - 4 + (len(ansi('1;33'))+len(RESET) if use_color else 0)) + ' |')
        print('+' + '-' * (total_w - 2) + '+')
        
        # Title and description
        print('| ' + (ansi('1;37') + decision.title + RESET).ljust(total_w - 4 + (len(ansi('1;37'))+len(RESET) if use_color else 0)) + ' |')
        
        # Wrap description
        desc_words = decision.description.split()
        current_line = ""
        for word in desc_words:
            if len(current_line) + len(word) + 1 < total_w - 4:
                current_line += word + " "
            else:
                print('| ' + current_line.ljust(total_w - 4) + ' |')
                current_line = word + " "
        if current_line:
            print('| ' + current_line.ljust(total_w - 4) + ' |')
            
        print('| ' + ' ' * (total_w - 4) + ' |')
        
        # Options
        for opt in decision.options:
            opt_str = f"[{opt.key}] {opt.text}"
            if opt.tooltip:
                opt_str += f" ({opt.tooltip})"
            print('| ' + (ansi('36') + opt_str + RESET).ljust(total_w - 4 + (len(ansi('36'))+len(RESET) if use_color else 0)) + ' |')
            
        print('+' + '=' * (total_w - 2) + '+')
        return  # Skip normal log/hints when decision is pending

    # Log
    print('+' + '-' * (total_w - 2) + '+')
    recent = []
    if hasattr(game, 'logger'):
        try:
            recent = list(game.logger.recent())
        except Exception:
            recent = []
    
    print('| Log:')
    for l in recent[-5:]:
        msg = l.get('text', str(l))
        # Truncate to fit
        max_len = total_w - 6
        if len(msg) > max_len:
            msg = msg[:max_len]
        print('| ' + msg.ljust(total_w - 4) + ' |')
    
    # Fill empty log space
    for _ in range(max(0, 6 - len(recent[-5:]))):
        print('|' + ' ' * (total_w - 2) + '|')
    
    print('+' + '-' * (total_w - 2) + '+')
    print(HINT + '  ARROWS: move  P: ping  T: fire  N: next-target  S: surface  D: dive  C: compartments  Q: quit' + RESET)


def draw_ascii_console(game, cursor=None, use_color=True):
    """Draw full ASCII GUI to stdout (Fallback/Single View)."""
    # Reuse dual view for now as it's superior
    draw_dual_view(game, cursor, use_color)



def draw_enhanced_tactical_gui(game, show_compartments=False, show_status=False, show_legend=False, use_color=True):
    """Draw enhanced tactical GUI with legend, status, and compartments.
    
    Args:
        game: Game instance
        show_compartments: If True, show compartment status
        show_status: If True, show control status dashboard
        show_legend: If True, show tactical legend
        use_color: If True, use ANSI colors
    """
    from ui.enhanced_gui import (
        ASCIILegend, 
        SubmarineVisual, 
        ControlStatusDashboard, 
        CompartmentHighlighter
    )
    
    # Always draw main tactical map first
    draw_ascii_console(game, use_color=use_color)
    
    print()  # Blank line separator
    
    # Draw requested components
    if show_legend:
        print(ASCIILegend.draw_tile_legend())
        print()
    
    if show_compartments:
        print(CompartmentHighlighter.draw_compartment_status(game.submarine))
        print()
    
    if show_status:
        supplies = getattr(game, 'supply_inventory', None)
        crew = getattr(game, 'crew_roster', None)
        print(ControlStatusDashboard.draw_control_panel(game.submarine, supplies, crew))
        print()


def draw_full_dashboard(game, use_color=True):
    """Draw complete dashboard with everything visible.
    
    Useful for:
    - Initial game startup
    - Status/help commands
    - Full information display
    """
    from ui.enhanced_gui import (
        ASCIILegend, 
        SubmarineVisual, 
        ControlStatusDashboard, 
        CompartmentHighlighter
    )
    
    # Clear screen
    try:
        os.system('clear' if os.name != 'nt' else 'cls')
    except:
        pass
    
    # Title
    CSI = "\x1b[" if use_color else ""
    BOLD = f"{CSI}1m" if use_color else ""
    CYAN = f"{CSI}36m" if use_color else ""
    RESET = f"{CSI}0m" if use_color else ""
    
    print(f"\n{BOLD}{CYAN}═══════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{CYAN}    DEPTHS WITHIN - SUBMARINE COMMAND INTERFACE{RESET}")
    print(f"{BOLD}{CYAN}═══════════════════════════════════════════════════════════{RESET}\n")
    
    # Draw each section
    try:
        draw_ascii_console(game, use_color=use_color)
        print()
    except Exception as e:
        print(f"Error drawing map: {e}")
    
    try:
        print(ASCIILegend.draw_tile_legend())
        print()
    except Exception as e:
        print(f"Error drawing legend: {e}")
    
    try:
        print(SubmarineVisual.draw_submarine_status(game.submarine))
        print()
    except Exception as e:
        print(f"Error drawing submarine status: {e}")
    
    try:
        supplies = getattr(game, 'supply_inventory', None)
        crew = getattr(game, 'crew_roster', None)
        print(ControlStatusDashboard.draw_control_panel(game.submarine, supplies, crew))
        print()
    except Exception as e:
        print(f"Error drawing control panel: {e}")
    
    try:
        print(CompartmentHighlighter.draw_compartment_status(game.submarine))
        print()
    except Exception as e:
        print(f"Error drawing compartment status: {e}")
    
    try:
        print(ASCIILegend.draw_command_legend())
    except Exception as e:
        print(f"Error drawing command legend: {e}")


