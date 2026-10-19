"""Tileset loader helpers for tcod.

This module attempts to load a user-provided tilesheet from
`assets/tilesets/` using common tile sizes (32,24,16). If none is found
or loading fails, it falls back to `tcod.tileset.load_default()`.
"""
import os

try:
    import tcod
except Exception:
    tcod = None

import json


def load_atlas():
    """Load atlas.json from assets/tilesets if present.

    Returns a dict with keys: tile_size, cols, rows, map (name->index)
    or None if no atlas found or parse failed.
    """
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    atlas_path = os.path.join(root, 'assets', 'tilesets', 'atlas.json')
    if not os.path.exists(atlas_path):
        return None
    try:
        with open(atlas_path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            return data
    except Exception:
        return None


def tile_coords_from_name(name, atlas=None):
    """Return (col, row, tile_size, cols, rows) for a named tile in atlas.

    If `atlas` is None, this will attempt to load the atlas.json automatically.
    Returns None if the name is not found or atlas missing.
    """
    if atlas is None:
        atlas = load_atlas()
    if not atlas:
        return None
    mapping = atlas.get('map', {})
    idx = mapping.get(name)
    if idx is None:
        return None
    cols = atlas.get('cols', 8)
    rows = atlas.get('rows', 4)
    tile_size = atlas.get('tile_size', 32)
    col = int(idx % cols)
    row = int(idx // cols)
    return (col, row, tile_size, cols, rows)


# simple cache for opened tilesheet images
_TILE_IMAGE_CACHE = {}


def blit_tile_as_color_block(console, name, tx, ty, atlas=None):
    """Approximate blit: compute average color of the named tile and print
    a single cell on `console` with that background color.

    This is a graceful interim fallback when pixel-level blitting is not
    available or when portability across tcod versions is desired.

    Args:
        console: tcod.Console-like object with a `print(x,y, text, bg=...)` API.
        name: tile name from atlas.json
        tx, ty: target console cell coordinates (integers)
        atlas: optional atlas dict to avoid reloading
    Returns True on success, False otherwise.
    """
    try:
        import os
        from PIL import Image
    except Exception:
        return False

    if atlas is None:
        atlas = load_atlas()
    if not atlas:
        return False

    coords = tile_coords_from_name(name, atlas=atlas)
    if not coords:
        return False
    col, row, tile_size, cols, rows = coords

    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    candidates = [
        os.path.join(root, 'assets', 'tilesets', 'submarine_tileset.png'),  # 512x512 matches atlas
        os.path.join(root, 'assets', 'tilesets', 'modern_tileset.png'),
        os.path.join(root, 'assets', 'tilesets', 'tileset.png'),
    ]
    path = None
    for p in candidates:
        if os.path.exists(p):
            path = p
            break
    if path is None:
        return False

    key = (path, col, row, tile_size)
    img = _TILE_IMAGE_CACHE.get(key)
    try:
        if img is None:
            full = Image.open(path).convert('RGB')
            left = int(col * tile_size)
            upper = int(row * tile_size)
            right = left + int(tile_size)
            lower = upper + int(tile_size)
            tile = full.crop((left, upper, right, lower))
            # resize to 1x1 to get average color quickly
            avg = tile.resize((1, 1), resample=Image.BILINEAR).getpixel((0, 0))
            _TILE_IMAGE_CACHE[key] = avg
            img = avg
        else:
            img = _TILE_IMAGE_CACHE[key]
    except Exception:
        return False

    # console.print supports bg=(r,g,b) in modern tcod; use a space with bg color
    try:
        console.print(tx, ty, ' ', bg=img)
        return True
    except Exception:
        try:
            # fallback: use a block char with fg color
            console.print(tx, ty, '█', fg=img)
            return True
        except Exception:
            return False


def load_preferred_tileset():
    if tcod is None:
        return None

    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Load atlas to get the correct tile size
    atlas = load_atlas()
    tile_size = atlas.get('tile_size', 32) if atlas else 32
    cols = atlas.get('cols', 16) if atlas else 16
    rows = atlas.get('rows', 16) if atlas else 16
    
    # 1. Load the base font for text
    # We need a font that looks good at 32x32 (or whatever the tile size is)
    font_path = '/System/Library/Fonts/Monaco.ttf'
    if not os.path.exists(font_path):
        font_path = '/System/Library/Fonts/Courier New.ttf'
    
    tileset = None
    try:
        # Load font with the SAME tile size as our graphics
        # This is crucial: tcod tilesets must have uniform tile size
        if os.path.exists(font_path):
            tileset = tcod.tileset.load_truetype_font(font_path, tile_size, tile_size)
            print(f"[Tileset] Loaded base font: {font_path}")
        else:
            print("[Tileset] No system font found, creating empty tileset")
            tileset = tcod.tileset.Tileset(tile_size, tile_size)
    except Exception as e:
        print(f"[Tileset] Failed to load font: {e}")
        tileset = tcod.tileset.Tileset(tile_size, tile_size)

    # 2. Load the sprites into the Private Use Area (0xE000+)
    candidates = [
        os.path.join(root, 'assets', 'tilesets', 'submarine_tileset.png'),
        os.path.join(root, 'assets', 'tilesets', 'modern_tileset.png'),
        os.path.join(root, 'assets', 'tilesets', 'tileset.png'),
    ]

    for path in candidates:
        if os.path.exists(path):
            try:
                from PIL import Image
                import numpy as np
                
                img = Image.open(path).convert('RGBA')
                img_array = np.array(img)
                
                # Load tiles starting at 0xE000
                max_tiles = min(256, cols * rows)
                base_char = 0xE000
                
                for tile_idx in range(max_tiles):
                    col = tile_idx % cols
                    row = tile_idx // cols
                    
                    x = col * tile_size
                    y = row * tile_size
                    
                    # Extract tile data
                    tile_data = img_array[y:y+tile_size, x:x+tile_size]
                    
                    # Register tile at custom codepoint
                    tileset.set_tile(base_char + tile_idx, tile_data)
                
                print(f"[Tileset] Loaded sprites from {os.path.basename(path)} starting at U+E000")
                return tileset
            except Exception as e:
                print(f"[Tileset] Failed to load sprites: {e}")
                continue

    return tileset


def blit_tile_exact(console, name, tx, ty, atlas=None):
    """Attempt pixel-accurate blit of a named tile into a tcod `console`.

    This function tries several strategies and falls back gracefully to the
    simpler `blit_tile_as_color_block` when true pixel blitting is not
    supported in the current environment (missing tcod features or numpy).

    Note: full pixel-perfect blitting depends on tcod version and console
    internals. This helper attempts to use numpy + console.tiles_rgb when
    available; otherwise it will render an average-color block.
    """
    try:
        from PIL import Image
    except Exception:
        return blit_tile_as_color_block(console, name, tx, ty, atlas=atlas)

    if atlas is None:
        atlas = load_atlas()
    if not atlas:
        return blit_tile_as_color_block(console, name, tx, ty, atlas=atlas)

    coords = tile_coords_from_name(name, atlas=atlas)
    if not coords:
        return blit_tile_as_color_block(console, name, tx, ty, atlas=atlas)
    col, row, tile_size, cols, rows = coords

    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    candidates = [
        os.path.join(root, 'assets', 'tilesets', 'submarine_tileset.png'),  # 512x512 matches atlas
        os.path.join(root, 'assets', 'tilesets', 'modern_tileset.png'),
        os.path.join(root, 'assets', 'tilesets', 'tileset.png'),
    ]
    path = None
    for p in candidates:
        if os.path.exists(p):
            path = p
            break
    if path is None:
        return blit_tile_as_color_block(console, name, tx, ty, atlas=atlas)

    try:
        full = Image.open(path).convert('RGBA')
        left = int(col * tile_size)
        upper = int(row * tile_size)
        right = left + int(tile_size)
        lower = upper + int(tile_size)
        tile = full.crop((left, upper, right, lower))
    except Exception:
        return blit_tile_as_color_block(console, name, tx, ty, atlas=atlas)

    # Try numpy + tcod.tiles_rgb approach if available
    try:
        import numpy as _np
        if hasattr(console, 'tiles_rgb'):
            # Resize tile to tile cell size if console provides tile size info
            try:
                tw = getattr(console, 'tile_width', tile_size)
                th = getattr(console, 'tile_height', tile_size)
                tile_rs = tile.resize((tw, th), resample=Image.BILINEAR)
            except Exception:
                tile_rs = tile

            arr = _np.array(tile_rs)
            # Ensure RGB shape (h,w,3)
            if arr.shape[2] == 4:
                arr = arr[:, :, :3]

            # Attempt to write into console.tiles_rgb at the target cell.
            # API differs across tcod versions; try a few common conventions.
            try:
                # console.tiles_rgb[y, x] = arr  (row-major)
                console.tiles_rgb[ty, tx] = arr
                return True
            except Exception:
                try:
                    # some consoles expect (x,y) indexing
                    console.tiles_rgb[tx, ty] = arr
                    return True
                except Exception:
                    pass
    except Exception:
        pass

    # Last-resort fallback: draw average color block
    return blit_tile_as_color_block(console, name, tx, ty, atlas=atlas)
