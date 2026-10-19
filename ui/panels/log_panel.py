# Multi-tab log/message panel
class LogPanel:
    def __init__(self):
        self.tabs = ['Sonar', 'Captain', 'Crew', 'Navigation', 'Combat', 'System']
        self.active_tab = 0

    def draw(self, console, x, y, width, height, game=None):
        # Draw a simple log box using recent entries from game.logger
        from ui.graphics_renderer import get_renderer
        graphics = get_renderer()
        graphics.render_ui_border(console, x, y, width, height, title="LOG")
        
        if game and hasattr(game, 'logger'):
            entries = game.logger.recent(limit=height - 2)
            for i, e in enumerate(entries[-(height - 2):]):
                txt = e.get('text', '')
                # Truncate text to fit inside border
                max_len = width - 2
                console.print(x + 1, y + 1 + i, txt[:max_len], fg=(200, 200, 200))
        else:
            console.print(x + 1, y + 1, 'No logs available')
