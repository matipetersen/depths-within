# Main display panel (map/sonar/periscope)
import math

class MainPanel:
    def __init__(self, width=41, height=21):
        # width/height are for simple ASCII sonar rendering (odd numbers preferred)
        self.width = width
        self.height = height

    def draw_sonar(self, submarine, contacts=None):
        # Render a simple ASCII sonar: submarine at center, contacts placed by bearing/range
        w = self.width
        h = self.height
        cx = w // 2
        cy = h // 2
        grid = [['.' for _ in range(w)] for _ in range(h)]
        grid[cy][cx] = 'S'  # our sub

        if not contacts:
            contacts = []

        # Map maximum display range to half of min(width,height)
        max_steps = min(cx, cy) - 1

        for c in contacts:
            try:
                bearing = float(c.get('bearing', 0))
                # normalize range -> 0..1 (if range not provided assume mid)
                r = c.get('range', None)
                if r is None:
                    rnorm = 0.5
                else:
                    # assume detection range ~ 6000m for normalization; clamp
                    rnorm = max(0.0, min(1.0, r / 6000.0))
                steps = max(1, int(rnorm * max_steps))
                angle = math.radians((90 - bearing) % 360)
                x = cx + int(round(math.cos(angle) * steps))
                y = cy + int(round(math.sin(angle) * steps))
                if 0 <= x < w and 0 <= y < h:
                    grid[y][x] = 'X'
            except Exception:
                continue

        # Convert grid to string
        lines = [''.join(row) for row in grid]
        return '\n'.join(lines)

    def draw(self, game):
        # use submarine sonar to get contacts
        try:
            contacts = game.submarine.sonar.detect()
        except Exception:
            contacts = []

        s = self.draw_sonar(game.submarine, contacts)
        print(s)
