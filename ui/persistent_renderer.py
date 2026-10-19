"""Persistent screen-based rendering system for the game.

Replaces the old print-based approach with a true screen management system
that clears and updates in place, preventing visual clutter.
"""

import os
import sys
import subprocess
from typing import Optional

# Try to import graphics renderer with tileset support
try:
    from ui.graphics import GraphicsRenderer
    GRAPHICS_AVAILABLE = True
except Exception:
    GraphicsRenderer = None
    GRAPHICS_AVAILABLE = False

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_CLEAR = "\033[2J"           # Clear entire screen
ANSI_HOME = "\033[H"             # Move cursor to home (top-left)
ANSI_CLEAR_LINE = "\033[2K"      # Clear current line
ANSI_HIDE_CURSOR = "\033[?25l"   # Hide cursor
ANSI_SHOW_CURSOR = "\033[?25h"   # Show cursor


class ScreenManager:
    """Manages persistent screen rendering with ANSI escape sequences."""
    
    def __init__(self):
        self.current_view = 'status_bar'
        self.buffer = []
        self.last_render_size = 0
        self.has_clear_support = self._check_clear_support()
        
    def _check_clear_support(self) -> bool:
        """Check if terminal supports ANSI clear codes."""
        try:
            # Try to detect terminal capability
            term = os.environ.get('TERM', '')
            return 'xterm' in term or 'screen' in term or 'linux' in term or 'rxvt' in term or 'gnome' in term or 'konsole' in term or 'iterm' in term
        except:
            return True
    
    def clear_screen(self):
        """Clear the screen using platform-appropriate method."""
        if not self.has_clear_support:
            # Fallback: print many newlines
            print('\n' * 50)
            return
        
        # Use ANSI codes
        try:
            sys.stdout.write(ANSI_CLEAR + ANSI_HOME)
            sys.stdout.flush()
        except:
            # Fallback if ANSI doesn't work
            try:
                os.system('clear' if os.name != 'nt' else 'cls')
            except:
                pass
    
    def hide_cursor(self):
        """Hide the cursor."""
        try:
            sys.stdout.write(ANSI_HIDE_CURSOR)
            sys.stdout.flush()
        except:
            pass
    
    def show_cursor(self):
        """Show the cursor."""
        try:
            sys.stdout.write(ANSI_SHOW_CURSOR)
            sys.stdout.flush()
        except:
            pass
    
    def render_frame(self, content: str):
        """Render a frame of content, updating in place."""
        # Clear screen
        self.clear_screen()
        
        # Write new content
        print(content, end='', flush=True)
        
        sys.stdout.flush()
    
    def render_tactical_persistent(self, game):
        """Render tactical display persistently."""
        if game.tactical_display:
            try:
                output = game.tactical_display.render(game)
                self.render_frame(output)
                return True
            except Exception as e:
                print(f"Tactical display error: {e}")
                return False
        return False
    
    def render_sonar_persistent(self, game):
        """Render sonar display persistently."""
        if game.sonar_view:
            try:
                output = game.sonar_view.render(game)
                self.render_frame(output)
                return True
            except Exception as e:
                print(f"Sonar display error: {e}")
                return False
        return False
    
    def render_dashboard_persistent(self, game):
        """Render dashboard persistently."""
        if game.dashboard_view:
            try:
                output = game.dashboard_view.render(game)
                self.render_frame(output)
                return True
            except Exception as e:
                print(f"Dashboard display error: {e}")
                return False
        return False
    
    def render_status_bar(self, game):
        """Render a minimal status bar showing submarine state."""
        try:
            from ui.hud_display import render_status_bar as render_status
            output = render_status(game)
            self.render_frame(output)
            return True
        except Exception as e:
            # Fallback status display
            try:
                sub = game.submarine
                depth = getattr(sub, 'current_depth', 0)
                heading = getattr(sub, 'heading', 0)
                speed = getattr(sub, 'speed', 0)
                
                status = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ SUBMARINE STATUS BAR                                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Depth: {depth:6.1f}m  | Heading: {heading:6.1f}°  | Speed: {speed:6.1f} knots          ║
║ Hull Integrity: [████████░░] 85%  | Flooding: [░░░░░░░░░░]  0%               ║
║ Sonar Contacts: 0  | Torpedoes: 6  | Batteries: 95%                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
                self.render_frame(status)
                return True
            except:
                return False
    
    def render_compartment_map_persistent(self, game):
        """Render compartment map persistently."""
        try:
            from ui.compartment_map import render_compartment_map
            output = render_compartment_map(game)
            self.render_frame(output)
            return True
        except Exception as e:
            print(f"Compartment map error: {e}")
            return False
    
    def render_game_persistent(self, game):
        """Main persistent rendering based on current view."""
        view = getattr(game, 'current_view', 'tactical')
        
        if view == 'tactical':
            return self.render_tactical_persistent(game)
        elif view == 'sonar':
            return self.render_sonar_persistent(game)
        elif view == 'dashboard':
            return self.render_dashboard_persistent(game)
        elif view == 'compartment_map':
            return self.render_compartment_map_persistent(game)
        elif view == 'status_bar':
            return self.render_status_bar(game)
        else:
            # Default: render status bar
            return self.render_status_bar(game)


class PersistentRenderer:
    """Wrapper for persistent screen-based rendering."""
    
    def __init__(self):
        self.screen_manager = ScreenManager()
        self.last_turn = -1
        self.render_count = 0
        
        # Try to initialize graphics renderer with tileset support
        self.graphics_renderer = None
        if GRAPHICS_AVAILABLE:
            try:
                self.graphics_renderer = GraphicsRenderer()
                print(f"[Renderer] Graphics backend: {self.graphics_renderer.get_render_backend()}")
                if self.graphics_renderer.has_tilesheet():
                    print(f"[Renderer] Tileset loaded with {len(self.graphics_renderer.atlas.get('map', {}))} tiles")
            except Exception as e:
                print(f"[Renderer] Graphics initialization failed: {e}")
                self.graphics_renderer = None
    
    def render(self, game):
        """Render the game state persistently."""
        # Always render but track turn to avoid duplicate renders
        current_turn = getattr(game, 'turn', 0)
        
        # Check if we have graphics renderer with tilesheet
        use_graphics = self.graphics_renderer and self.graphics_renderer.has_tilesheet()
        
        # Force render on first call or when explicitly requested
        if self.render_count == 0:
            if use_graphics:
                self._render_with_graphics(game)
            else:
                self.screen_manager.render_game_persistent(game)
            self.last_turn = current_turn
            self.render_count += 1
            return True
        
        # For subsequent calls, only render if turn actually changed
        if current_turn != self.last_turn:
            if use_graphics:
                self._render_with_graphics(game)
            else:
                self.screen_manager.render_game_persistent(game)
            self.last_turn = current_turn
            return True
        
        # Don't render if turn hasn't changed
        return False
    
    def _render_with_graphics(self, game):
        """Render using graphics renderer with tileset."""
        try:
            self.graphics_renderer.render_game(game)
        except Exception as e:
            print(f"[Renderer] Graphics render failed: {e}")
            # Fall back to screen manager
            self.screen_manager.render_game_persistent(game)
    
    def render_forced(self, game):
        """Force a render regardless of turn."""
        self.screen_manager.render_game_persistent(game)
        self.render_count += 1
        return True
    
    def switch_view(self, game, view_name: str):
        """Switch to a different view and render immediately."""
        game.current_view = view_name
        return self.render_forced(game)
    
    def clear(self):
        """Clear the screen."""
        self.screen_manager.clear_screen()


def create_persistent_renderer():
    """Factory function to create appropriate renderer."""
    return PersistentRenderer()
