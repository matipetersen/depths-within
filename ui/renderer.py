# Handles rendering using libtcod, with console fallback
try:
    import tcod
    TCOD_AVAILABLE = True
except Exception:
    tcod = None
    TCOD_AVAILABLE = False
# Delay importing the ASCII renderer until render-time to avoid import-time
# failures due to environment differences. We'll attempt a dynamic import
# in `render()` so the module can fail gracefully at runtime.
draw_ascii_console = None


class Renderer:
    def __init__(self):
        self.use_tcod = TCOD_AVAILABLE

    def render(self, game):
        # Minimal rendering: if tcod available show a basic window, otherwise console prints
        header = f"Turn: {getattr(game, 'turn', 0)} | Depth: {game.submarine.systems.depth if hasattr(game.submarine, 'systems') else 'N/A'}"
        if self.use_tcod:
            # Placeholder: tcod rendering would go here. For now fall back to console prints.
            print('[tcod available] ' + header)
        else:
            # Console fallback rendering - use new dual-view display
            try:
                # Import dynamically to capture import errors at runtime
                try:
                    from ui.ascii_gui import draw_dual_view
                    draw_dual_view(game, cursor=getattr(game, 'ascii_cursor', None), use_color=getattr(game, 'ascii_use_color', True))
                except Exception as ex:
                    print('(dual view error:', str(ex)[:100], ')')
                    # Fallback to basic display if dual view fails
                    try:
                        from ui.ascii_gui import draw_ascii_console as _draw_fn
                        _draw_fn(game, cursor=getattr(game, 'ascii_cursor', None), use_color=getattr(game, 'ascii_use_color', True))
                    except Exception:
                        pass
                return
            except Exception:
                pass

            print('+' + '-' * 60 + '+')
            print('|', header.ljust(60), '|')
            print('+' + '-' * 60 + '+')
            # submarine quick status or compartments detail
            try:
                if getattr(game, 'show_compartments', False):
                    print('--- Compartments ---')
                    try:
                        for comp in game.submarine.compartments:
                            print(f"{comp.name}: integrity={comp.integrity:.2f} flooding={comp.flooding:.2f}")
                    except Exception:
                        print('Compartments unavailable')
                    print('--------------------')
                else:
                    status = game.submarine.status()
                    print(status)
            except Exception:
                print('Submarine status unavailable')
