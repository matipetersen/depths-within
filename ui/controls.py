"""Input handling: console fallback and tcod controls stub."""
try:
    import tcod
except Exception:
    tcod = None

from ui.term_input import getkey


class Controls:
    def __init__(self, enable_raw_input=False):
        """Initialize controls.
        
        Args:
            enable_raw_input: If True, use raw terminal input for arrow keys/movement.
                             If False (default), use regular input() for compatibility.
        """
        self.enable_raw_input = enable_raw_input

    def get_command(self):
        """Get user command input.
        
        Supports:
        - Regular typed commands
        - Arrow keys (converted to up/down/left/right commands)
        - WASD keys (converted to movement commands)
        - Escape/Ctrl+C for quit
        
        Returns:
            Command string or 'quit'
        """
        try:
            if self.enable_raw_input:
                # Use raw terminal input for immediate key detection
                return self._get_raw_command()
            else:
                # Standard input() for backward compatibility
                cmd = input('> ')
                return cmd
        except EOFError:
            return 'quit'
        except KeyboardInterrupt:
            return 'quit'
    
    def _get_raw_command(self):
        """Get command using raw terminal input (allows arrow keys, etc)."""
        try:
            key = getkey()
            
            # Map arrow keys to movement commands
            if key == 'UP':
                return 'move 0 -1'
            elif key == 'DOWN':
                return 'move 0 1'
            elif key == 'LEFT':
                return 'move -1 0'
            elif key == 'RIGHT':
                return 'move 1 0'
            
            # Map WASD keys to movement
            elif key.lower() == 'w':
                return 'move 0 -1'
            elif key.lower() == 's':
                return 'move 0 1'
            elif key.lower() == 'a':
                return 'move -1 0'
            elif key.lower() == 'd':
                return 'move 1 0'
            
            # Escape key
            elif key == '\x1b':
                return 'quit'
            
            # Regular command - collect full line
            else:
                # Put the first key back into stdin stream and use input()
                import sys
                sys.stdin = open('/dev/tty' if hasattr(sys.stdin, 'name') else None, 'r')
                return input(key + '> ')
        except Exception:
            # Fall back to regular input on error
            return input('> ')


class TcodControls:
    """Stub for tcod-based input handling. For now the main loop
    handles basic key events; this class is a placeholder for future
    mapping of tcod events to in-game commands."""

    def __init__(self):
        pass

    def handle_event(self, event):
        # return a command string or None
        try:
            if event.type == 'KEYDOWN':
                k = event.sym
                if k in (tcod.event.K_q, tcod.event.K_ESCAPE):
                    return 'quit'
                # map other keys as needed
        except Exception:
            pass
        return None
