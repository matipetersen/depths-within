"""Generate a simple placeholder 32x32 tileset atlas using Pillow.

This produces `assets/tilesets/modern_tileset.png` and
`assets/tilesets/atlas.json`. The generated tiles are simple shapes
meant as placeholders for later replacement with a professional
tileset (M4CRO, Kenney, etc.).

Run: `python scripts/generate_tileset.py`
"""
from PIL import Image, ImageDraw, ImageFont
import os
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT_DIR = os.path.join(ROOT, 'assets', 'tilesets')
os.makedirs(OUT_DIR, exist_ok=True)

TILE = 32
COLS = 8
ROWS = 4
W = TILE * COLS
H = TILE * ROWS

atlas = {}

img = Image.new('RGBA', (W, H), (10, 16, 22, 255))
draw = ImageDraw.Draw(img)

def cell_xy(i):
    x = (i % COLS) * TILE
    y = (i // COLS) * TILE
    return x, y

# palette
navy = (10, 16, 22, 255)
sonar = (24, 200, 120, 255)
amber = (255, 204, 102, 255)
steel = (136, 142, 150, 255)
red = (200, 80, 80, 255)

for i in range(COLS * ROWS):
    x, y = cell_xy(i)
    # cell background subtle circle
    draw.rectangle([x, y, x+TILE-1, y+TILE-1], fill=navy)

    cx = x + TILE//2
    cy = y + TILE//2

    # simple icon set
    if i == 0:
        # sonar ping (concentric circles)
        for r, c in [(12, sonar), (8, (20,120,80,255)), (3, (40,200,140,255))]:
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=c)
        atlas['sonar_ping'] = i
    elif i == 1:
        # submarine silhouette (triangle)
        draw.polygon([(cx-8, cy+6), (cx+8, cy+6), (cx, cy-8)], fill=steel)
        atlas['sub_silhouette'] = i
    elif i == 2:
        # ship silhouette (rectangle + mast)
        draw.rectangle([cx-10, cy-4, cx+10, cy+6], fill=steel)
        draw.line([(cx, cy-4), (cx, cy-12)], fill=amber, width=2)
        atlas['ship_silhouette'] = i
    elif i == 3:
        # damage icon (fire)
        draw.polygon([(cx, cy-6), (cx-4, cy+4), (cx+4, cy+4)], fill=red)
        atlas['damage'] = i
    elif i == 4:
        # battery icon
        draw.rectangle([cx-8, cy-6, cx+8, cy+6], outline=steel)
        draw.rectangle([cx-6, cy-4, cx+6, cy+4], fill=amber)
        atlas['battery'] = i
    elif i == 5:
        # O2 icon (circle with O2)
        draw.ellipse([cx-8, cy-8, cx+8, cy+8], outline=sonar)
        atlas['o2'] = i
    elif i == 6:
        # depth icon (down arrow)
        draw.polygon([(cx, cy+8), (cx-6, cy-2), (cx+6, cy-2)], fill=steel)
        atlas['depth'] = i
    else:
        # filler dots / UI glyph
        draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=steel)
        atlas[f'ui_{i}'] = i

out_png = os.path.join(OUT_DIR, 'modern_tileset.png')
img.save(out_png)

atlas_path = os.path.join(OUT_DIR, 'atlas.json')
with open(atlas_path, 'w', encoding='utf-8') as f:
    json.dump({'tile_size': TILE, 'cols': COLS, 'rows': ROWS, 'map': atlas}, f, indent=2)

print('Generated tileset:', out_png)
print('Atlas saved:', atlas_path)
