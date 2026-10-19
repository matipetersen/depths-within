# Compartment status panel
class CompartmentPanel:
    def __init__(self):
        self.visible = False

    def draw(self, console, x, y, width, height=12, game=None):
        # Draw compartments vertically
        from ui.graphics_renderer import get_renderer
        graphics = get_renderer()
        graphics.render_ui_border(console, x, y, width, height, title="COMPARTMENTS")
        
        if game and hasattr(game, 'submarine'):
            comps = game.submarine.compartments
            for i, c in enumerate(comps[: (height - 2) ]):
                # Color coding
                if c.flooding > 0.5:
                    color = (80, 150, 255) # Blue for flood
                elif c.integrity < 0.5:
                    color = (255, 80, 80) # Red for damage
                else:
                    color = (100, 255, 100) # Green for ok
                    
                # Dynamic formatting based on width
                if width < 30:
                    # Compact format: "Name 100% 0%"
                    name_len = width - 12
                    if name_len < 5: name_len = 5
                    txt = f"{c.name[:name_len]:{name_len}} {int(c.integrity*100):3d}% {int(c.flooding*100):3d}%"
                else:
                    # Standard format
                    txt = f"{c.name[:15]:15} {int(c.integrity*100):3d}% {int(c.flooding*100):3d}%"
                
                console.print(x + 1, y + 1 + i, txt[:width-2], fg=color)
        else:
            console.print(x + 1, y + 1, 'No compartments')
