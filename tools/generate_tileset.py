import json
import os
import math
import random
from PIL import Image, ImageDraw, ImageFont

def generate_tileset():
    # Load atlas to get the full list of required tiles
    atlas_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tilesets', 'atlas.json')
    with open(atlas_path, 'r') as f:
        atlas = json.load(f)
    
    tile_size = atlas['tile_size']
    cols = atlas['cols']
    rows = atlas['rows']
    mapping = atlas['map']
    
    # Scale factor relative to original 32x32 design
    S = tile_size / 32.0
    
    # Create blank image
    width = cols * tile_size
    height = rows * tile_size
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    print(f"Generating {len(mapping)} tiles based on atlas.json (size={tile_size}x{tile_size})...")
    
    for name, idx in mapping.items():
        col = idx % cols
        row = idx // cols
        x = col * tile_size
        y = row * tile_size
        
        # Create tile image
        tile = Image.new('RGBA', (tile_size, tile_size), (0, 0, 0, 0))
        tdraw = ImageDraw.Draw(tile)
        
        # Helper for scaled coordinates
        def sc(coords):
            if isinstance(coords, (int, float)):
                return int(coords * S)
            return [int(c * S) for c in coords]
            
        def sc_rect(x1, y1, x2, y2):
            return [int(x1 * S), int(y1 * S), int(x2 * S), int(y2 * S)]

        # --- DRAWING LOGIC BASED ON NAME ---
        
        # 1. Ocean Tiles
        if name.startswith('ocean_'):
            if 'surface' in name:
                color = (30, 100, 180, 255)
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=color)
                # Waves
                tdraw.line(sc_rect(0, 5, 31, 5), fill=(50, 120, 200, 255), width=1)
                tdraw.line(sc_rect(5, 15, 25, 15), fill=(50, 120, 200, 255), width=1)
                tdraw.line(sc_rect(2, 25, 20, 25), fill=(50, 120, 200, 255), width=1)
            elif 'shallow' in name:
                color = (20, 80, 160, 255)
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=color)
            elif 'medium' in name:
                color = (10, 60, 140, 255)
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=color)
            elif 'deep' in name:
                color = (5, 40, 100, 255)
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=color)
            elif 'very_deep' in name:
                color = (0, 20, 60, 255)
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=color)
            elif 'variant' in name:
                color = (30, 100, 180, 255)
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=color)
                for _ in range(5):
                    rx = random.randint(0, tile_size-1)
                    ry = random.randint(0, tile_size-1)
                    tdraw.point((rx, ry), fill=(50, 120, 200, 255))

        # 2. Submarine Tiles (Rotated)
        elif name.startswith('sub_angle_') or name.startswith('sub_submerged_'):
            try:
                angle = int(name.split('_')[-1])
            except ValueError:
                angle = 0
            is_submerged = 'submerged' in name
            
            sub_img = Image.new('RGBA', (tile_size, tile_size), (0, 0, 0, 0))
            sdraw = ImageDraw.Draw(sub_img)
            
            color = (60, 60, 60, 255) if not is_submerged else (40, 60, 80, 200)
            outline = (200, 200, 200, 255) if not is_submerged else (100, 150, 200, 150)
            
            # Distinct Submarine Shape (Cigar shape)
            # Main Hull
            sdraw.ellipse(sc_rect(12, 2, 20, 30), fill=color, outline=outline)
            # Conning tower (distinct box)
            sdraw.rectangle(sc_rect(10, 12, 22, 18), fill=(100, 100, 100, 255), outline=outline)
            # Periscope/Snorkel
            if not is_submerged:
                sdraw.line(sc_rect(16, 12, 16, 6), fill=(255, 255, 0, 255), width=max(1, int(2*S)))
            
            # Rotate
            rotated = sub_img.rotate(-angle, resample=Image.BICUBIC)
            tile.paste(rotated, (0, 0), rotated)

        # 3. Ships
        elif 'ship' in name or 'destroyer' in name or 'contact_merchant' in name or 'contact_warship' in name:
            color = (100, 100, 100, 255)
            if 'merchant' in name:
                # Rectangular shape with distinct bow/stern
                # Hull
                tdraw.polygon([(8*S, 8*S), (24*S, 8*S), (28*S, 16*S), (24*S, 24*S), (8*S, 24*S), (4*S, 16*S)], fill=(120, 100, 80, 255), outline=(50, 50, 50, 255))
                # Superstructure
                tdraw.rectangle(sc_rect(12, 12, 20, 20), fill=(150, 130, 110, 255))
            elif 'warship' in name:
                # Sharp, aggressive shape
                points = [(16*S, 2*S), (28*S, 28*S), (16*S, 24*S), (4*S, 28*S)]
                tdraw.polygon(points, fill=(80, 80, 90, 255), outline=(200, 50, 50, 255))
                # Turret
                tdraw.ellipse(sc_rect(14, 14, 18, 18), fill=(200, 200, 200, 255))
            elif 'destroyer' in name:
                # Sleek, fast shape
                points = [(16*S, 2*S), (22*S, 30*S), (16*S, 26*S), (10*S, 30*S)]
                tdraw.polygon(points, fill=(70, 70, 80, 255), outline=(200, 100, 100, 255))
            
            if 'damaged' in name:
                # Add fire/smoke
                tdraw.ellipse(sc_rect(10, 10, 22, 22), fill=(255, 100, 0, 180))
                tdraw.ellipse(sc_rect(12, 8, 20, 16), fill=(50, 50, 50, 180))

        # 4. Weapons / Effects
        elif 'torpedo' in name:
            if 'wake' in name:
                tdraw.line(sc_rect(16, 0, 16, 32), fill=(200, 200, 255, 150), width=max(1, int(2*S)))
            else:
                # Small tube
                tdraw.rectangle(sc_rect(14, 8, 18, 24), fill=(50, 50, 50, 255), outline=(200, 200, 200, 255))
                # Red tip
                tdraw.rectangle(sc_rect(14, 8, 18, 12), fill=(255, 0, 0, 255))
        
        elif 'explosion' in name:
            size = 10 * S
            if 'medium' in name: size = 20 * S
            if 'large' in name: size = 30 * S
            center = 16 * S
            tdraw.ellipse([center-size/2, center-size/2, center+size/2, center+size/2], fill=(255, 150, 0, 255), outline=(255, 255, 0, 255))
        
        elif 'depth_charge' in name:
            tdraw.ellipse(sc_rect(10, 10, 22, 22), fill=(50, 50, 50, 255), outline=(0, 0, 0, 255))
            if 'exploding' in name:
                tdraw.ellipse(sc_rect(8, 8, 24, 24), outline=(255, 100, 0, 255), width=max(1, int(2*S)))

        elif 'mine' in name:
            tdraw.ellipse(sc_rect(10, 10, 22, 22), fill=(30, 30, 30, 255))
            # Spikes
            tdraw.line(sc_rect(16, 6, 16, 26), fill=(30, 30, 30, 255), width=max(1, int(2*S)))
            tdraw.line(sc_rect(6, 16, 26, 16), fill=(30, 30, 30, 255), width=max(1, int(2*S)))

        # 5. UI Elements
        elif 'gauge' in name:
            # Background
            tdraw.ellipse(sc_rect(2, 2, 30, 30), outline=(200, 200, 200, 255))
            # Needle based on value
            val = 0
            if '100' in name: val = 1.0
            elif '75' in name or '66' in name: val = 0.75
            elif '50' in name: val = 0.5
            elif '25' in name or '33' in name: val = 0.25
            
            angle = 180 + (val * 180) # 180 to 360 (semi circle)
            rad = math.radians(angle)
            ex = 16*S + 12*S * math.cos(rad)
            ey = 16*S + 12*S * math.sin(rad)
            tdraw.line([16*S, 16*S, ex, ey], fill=(255, 0, 0, 255), width=max(1, int(2*S)))

        elif 'battery' in name:
            # Battery shape
            tdraw.rectangle(sc_rect(8, 6, 24, 26), outline=(200, 200, 200, 255))
            tdraw.rectangle(sc_rect(12, 2, 20, 6), fill=(200, 200, 200, 255))
            # Fill level
            fill_h = 0
            color = (0, 255, 0, 255)
            if 'full' in name: fill_h = 18
            elif 'med' in name: 
                fill_h = 10
                color = (255, 255, 0, 255)
            elif 'low' in name: 
                fill_h = 4
                color = (255, 0, 0, 255)
            
            if fill_h > 0:
                tdraw.rectangle(sc_rect(9, 25-fill_h, 23, 25), fill=color)

        elif 'oxygen' in name:
            # O2 Tank
            tdraw.rectangle(sc_rect(8, 4, 24, 28), outline=(100, 200, 255, 255))
            color = (100, 200, 255, 255)
            if 'low' in name: color = (255, 100, 100, 255)
            # Text is too small at 16x16, draw symbol instead
            if tile_size >= 24:
                tdraw.text((10*S, 10*S), "O2", fill=color)
            else:
                tdraw.line(sc_rect(12, 10, 20, 10), fill=color)
                tdraw.line(sc_rect(12, 16, 20, 16), fill=color)

        elif 'hull' in name:
            # Shield shape
            points = [(6*S, 6*S), (26*S, 6*S), (26*S, 16*S), (16*S, 28*S), (6*S, 16*S)]
            tdraw.polygon(points, outline=(200, 200, 200, 255))
            if 'damaged' in name:
                tdraw.line(sc_rect(10, 10, 22, 22), fill=(255, 0, 0, 255), width=max(1, int(2*S)))

        # 6. Crew / Compartments
        elif 'crew' in name:
            # Stick figure head
            color = (200, 200, 200, 255)
            if 'stressed' in name: color = (255, 255, 0, 255)
            if 'injured' in name: color = (255, 100, 0, 255)
            if 'critical' in name: color = (255, 0, 0, 255)
            
            tdraw.ellipse(sc_rect(10, 4, 22, 16), fill=color) # Head
            tdraw.rectangle(sc_rect(8, 18, 24, 30), fill=(50, 50, 100, 255)) # Uniform

        elif 'compartment' in name:
            # Box
            color = (100, 100, 100, 255)
            if 'damaged' in name: color = (150, 100, 50, 255)
            if 'critical' in name: color = (150, 50, 50, 255)
            if 'flooding' in name: color = (50, 50, 150, 255)
            
            tdraw.rectangle(sc_rect(2, 8, 30, 24), fill=color, outline=(200, 200, 200, 255))
            if 'flooding' in name:
                tdraw.rectangle(sc_rect(2, 18, 30, 24), fill=(0, 0, 255, 200))

        # 7. Weather
        elif 'weather' in name:
            if 'rain' in name or 'storm' in name:
                # Rain drops
                tdraw.line(sc_rect(10, 10, 8, 16), fill=(100, 100, 255, 255))
                tdraw.line(sc_rect(20, 14, 18, 20), fill=(100, 100, 255, 255))
                if 'storm' in name:
                    # Lightning
                    points = [(16*S, 2*S), (12*S, 12*S), (20*S, 12*S), (16*S, 22*S)]
                    tdraw.line(points, fill=(255, 255, 0, 255), width=1)
            elif 'fog' in name:
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=(200, 200, 200, 100))
            elif 'night' in name:
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=(0, 0, 50, 150))
                tdraw.point((10*S, 10*S), fill=(255, 255, 255, 255))
                tdraw.point((25*S, 20*S), fill=(255, 255, 255, 255))

        # 8. Flags
        elif 'flag' in name:
            # Flag pole
            tdraw.line(sc_rect(4, 4, 4, 28), fill=(150, 100, 50, 255), width=max(1, int(2*S)))
            # Flag rect
            rect = sc_rect(6, 4, 26, 16)
            if 'germany' in name:
                tdraw.rectangle(rect, fill=(200, 0, 0, 255))
                tdraw.ellipse(sc_rect(12, 6, 20, 14), fill=(255, 255, 255, 255))
            elif 'usa' in name:
                tdraw.rectangle(rect, fill=(0, 0, 200, 255))
                tdraw.rectangle(sc_rect(6, 4, 26, 8), fill=(200, 0, 0, 255)) # Stripes
            elif 'uk' in name:
                tdraw.rectangle(rect, fill=(0, 0, 150, 255))
                tdraw.line(sc_rect(6, 4, 26, 16), fill=(200, 0, 0, 255)) # Cross
                tdraw.line(sc_rect(6, 16, 26, 4), fill=(200, 0, 0, 255))
            elif 'japan' in name:
                tdraw.rectangle(rect, fill=(255, 255, 255, 255))
                tdraw.ellipse(sc_rect(12, 6, 20, 14), fill=(200, 0, 0, 255))
            else:
                tdraw.rectangle(rect, fill=(150, 150, 150, 255))

        # 9. Aircraft
        elif 'aircraft' in name:
            # Plane shape
            points = [(16*S, 4*S), (28*S, 20*S), (4*S, 20*S)]
            tdraw.polygon(points, fill=(200, 200, 200, 255)) # Wings
            tdraw.rectangle(sc_rect(14, 4, 18, 28), fill=(150, 150, 150, 255)) # Fuselage
            if 'damaged' in name:
                tdraw.ellipse(sc_rect(10, 10, 20, 20), fill=(255, 100, 0, 150))

        # 10. Divers
        elif 'diver' in name:
            # Diver shape
            tdraw.ellipse(sc_rect(12, 4, 20, 12), fill=(50, 50, 50, 255)) # Head
            tdraw.rectangle(sc_rect(10, 12, 22, 24), fill=(30, 30, 30, 255)) # Body
            tdraw.line(sc_rect(8, 14, 24, 14), fill=(30, 30, 30, 255), width=max(1, int(2*S))) # Arms
            tdraw.line(sc_rect(12, 24, 12, 30), fill=(30, 30, 30, 255), width=max(1, int(2*S))) # Legs
            tdraw.line(sc_rect(20, 24, 20, 30), fill=(30, 30, 30, 255), width=max(1, int(2*S)))
            
            if 'swimming' in name:
                tdraw.line(sc_rect(6, 28, 12, 30), fill=(100, 100, 100, 255), width=max(1, int(2*S))) # Fins
            if 'combat' in name:
                tdraw.line(sc_rect(24, 14, 28, 10), fill=(100, 100, 100, 255), width=1) # Knife

        # 11. Sensors
        elif 'sensor' in name or 'radar' in name or 'sonar' in name:
            if 'radar' in name:
                # Dish
                tdraw.arc(sc_rect(4, 10, 28, 26), 180, 360, fill=(200, 200, 200, 255), width=max(1, int(2*S)))
                tdraw.line(sc_rect(16, 26, 16, 30), fill=(100, 100, 100, 255))
            elif 'sonar' in name:
                # Waves
                tdraw.arc(sc_rect(4, 4, 28, 28), 0, 360, fill=(0, 255, 0, 100), width=1)
                tdraw.arc(sc_rect(10, 10, 22, 22), 0, 360, fill=(0, 255, 0, 150), width=1)
                tdraw.point((16*S, 16*S), fill=(0, 255, 0, 255))
        
        # 12. Periscope
        elif 'periscope' in name:
            # Crosshair
            tdraw.line(sc_rect(16, 0, 16, 32), fill=(0, 255, 0, 150), width=1)
            tdraw.line(sc_rect(0, 16, 32, 16), fill=(0, 255, 0, 150), width=1)
            tdraw.ellipse(sc_rect(4, 4, 28, 28), outline=(0, 255, 0, 150), width=1)
            if 'locked' in name:
                tdraw.rectangle(sc_rect(14, 14, 18, 18), outline=(255, 0, 0, 255), width=max(1, int(2*S)))

        # 13. Time / Moon
        elif 'time' in name or 'moon' in name or 'sun' in name:
            if 'sun' in name or 'noon' in name:
                tdraw.ellipse(sc_rect(8, 8, 24, 24), fill=(255, 255, 0, 255))
            elif 'moon' in name or 'night' in name:
                tdraw.ellipse(sc_rect(8, 8, 24, 24), fill=(200, 200, 200, 255))
                if 'crescent' in name:
                    tdraw.ellipse(sc_rect(12, 8, 28, 24), fill=(0, 0, 0, 0)) # Mask
            elif 'dawn' in name or 'dusk' in name:
                tdraw.rectangle([0, 16*S, 32*S, 32*S], fill=(255, 100, 50, 100))
                tdraw.ellipse(sc_rect(10, 10, 22, 22), fill=(255, 200, 0, 255))

        # 14. UI Borders and Buttons
        elif 'ui_' in name:
            if 'border' in name:
                if 'h' in name:
                    tdraw.line(sc_rect(0, 16, 32, 16), fill=(100, 100, 100, 255), width=max(1, int(2*S)))
                elif 'v' in name:
                    tdraw.line(sc_rect(16, 0, 16, 32), fill=(100, 100, 100, 255), width=max(1, int(2*S)))
            elif 'corner' in name:
                if 'top_left' in name:
                    tdraw.line(sc_rect(16, 16, 32, 16), fill=(100, 100, 100, 255), width=max(1, int(2*S)))
                    tdraw.line(sc_rect(16, 16, 16, 32), fill=(100, 100, 100, 255), width=max(1, int(2*S)))
                elif 'top_right' in name:
                    tdraw.line(sc_rect(0, 16, 16, 16), fill=(100, 100, 100, 255), width=max(1, int(2*S)))
                    tdraw.line(sc_rect(16, 16, 16, 32), fill=(100, 100, 100, 255), width=max(1, int(2*S)))
                elif 'bottom_left' in name:
                    tdraw.line(sc_rect(16, 16, 32, 16), fill=(100, 100, 100, 255), width=max(1, int(2*S)))
                    tdraw.line(sc_rect(16, 0, 16, 16), fill=(100, 100, 100, 255), width=max(1, int(2*S)))
                elif 'bottom_right' in name:
                    tdraw.line(sc_rect(0, 16, 16, 16), fill=(100, 100, 100, 255), width=max(1, int(2*S)))
                    tdraw.line(sc_rect(16, 0, 16, 16), fill=(100, 100, 100, 255), width=max(1, int(2*S)))
            elif 'button' in name:
                tdraw.rectangle(sc_rect(2, 2, 30, 30), outline=(150, 150, 150, 255))
                if 'pressed' in name:
                    tdraw.rectangle(sc_rect(4, 4, 28, 28), fill=(100, 100, 100, 255))
                else:
                    tdraw.rectangle(sc_rect(4, 4, 28, 28), fill=(50, 50, 50, 255))

        # 15. Contacts
        elif 'contact_' in name:
            if 'unknown' in name:
                tdraw.rectangle(sc_rect(10, 10, 22, 22), outline=(255, 255, 0, 255))
                tdraw.text((12*S, 10*S), "?", fill=(255, 255, 0, 255))
            elif 'aircraft' in name:
                tdraw.polygon([(16*S, 4*S), (28*S, 20*S), (4*S, 20*S)], outline=(255, 0, 0, 255))
            elif 'coastal' in name:
                tdraw.rectangle(sc_rect(8, 12, 24, 20), fill=(100, 100, 50, 255))
            elif 'uncertain' in name:
                tdraw.ellipse(sc_rect(8, 8, 24, 24), outline=(255, 255, 0, 150))
            elif 'probable' in name:
                tdraw.ellipse(sc_rect(8, 8, 24, 24), outline=(255, 150, 0, 200))
            elif 'certain' in name:
                tdraw.ellipse(sc_rect(8, 8, 24, 24), outline=(255, 0, 0, 255))

        # 16. Missions & Intel
        elif 'mission_' in name:
            if 'objective' in name:
                tdraw.ellipse(sc_rect(8, 8, 24, 24), outline=(255, 255, 0, 255), width=max(1, int(2*S)))
                tdraw.line(sc_rect(16, 8, 16, 24), fill=(255, 255, 0, 255))
                tdraw.line(sc_rect(8, 16, 24, 16), fill=(255, 255, 0, 255))
            elif 'complete' in name or 'success' in name:
                tdraw.line([(8*S, 16*S), (14*S, 22*S), (24*S, 8*S)], fill=(0, 255, 0, 255), width=max(1, int(2*S)))
            elif 'failed' in name:
                tdraw.line([(8*S, 8*S), (24*S, 24*S)], fill=(255, 0, 0, 255), width=max(1, int(2*S)))
                tdraw.line([(24*S, 8*S), (8*S, 24*S)], fill=(255, 0, 0, 255), width=max(1, int(2*S)))
            else:
                # Generic mission icon
                tdraw.rectangle(sc_rect(8, 8, 24, 24), outline=(200, 200, 0, 255))

        elif 'intel_' in name:
            # Folder shape
            tdraw.polygon([(4*S, 4*S), (12*S, 4*S), (14*S, 8*S), (28*S, 8*S), (28*S, 28*S), (4*S, 28*S)], fill=(200, 180, 100, 255))

        # 17. Visibility / Detection / Fog
        elif 'visibility_' in name:
            # Eye icon
            tdraw.ellipse(sc_rect(4, 10, 28, 22), outline=(200, 200, 200, 255))
            tdraw.ellipse(sc_rect(12, 12, 20, 20), fill=(200, 200, 200, 255))
            if 'low' in name:
                tdraw.line(sc_rect(4, 22, 28, 10), fill=(255, 0, 0, 255), width=1)

        elif 'detection_' in name:
            # Exclamation mark
            color = (0, 255, 0, 255)
            if 'caution' in name: color = (255, 255, 0, 255)
            if 'danger' in name: color = (255, 0, 0, 255)
            tdraw.rectangle(sc_rect(14, 4, 18, 20), fill=color)
            tdraw.rectangle(sc_rect(14, 24, 18, 28), fill=color)

        elif 'fog_' in name:
            if 'unexplored' in name:
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=(0, 0, 0, 255))
            elif 'explored' in name:
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=(50, 50, 60, 150))
            elif 'visible' in name:
                pass # Transparent
            elif 'sonar' in name:
                tdraw.rectangle([0, 0, tile_size-1, tile_size-1], fill=(0, 50, 0, 100))

        # 18. Misc UI (Clock, Compass, etc)
        elif 'clock_face' in name:
            tdraw.ellipse(sc_rect(2, 2, 30, 30), outline=(200, 200, 200, 255))
            tdraw.line(sc_rect(16, 16, 16, 6), fill=(200, 200, 200, 255))
            tdraw.line(sc_rect(16, 16, 22, 16), fill=(200, 200, 200, 255))
        elif 'compass_rose' in name:
            tdraw.polygon([(16*S, 2*S), (20*S, 16*S), (16*S, 30*S), (12*S, 16*S)], fill=(200, 200, 200, 255))
        elif 'calendar' in name:
            tdraw.rectangle(sc_rect(4, 6, 28, 28), fill=(200, 200, 200, 255))
            tdraw.line(sc_rect(4, 10, 28, 10), fill=(0, 0, 0, 255))

        # 19. Indicators (Stealth, Alert, Fatigue, Skill)
        elif 'stealth_indicator' in name:
            tdraw.polygon([(16*S, 4*S), (28*S, 16*S), (16*S, 28*S), (4*S, 16*S)], fill=(50, 50, 50, 255))
        elif 'alert_indicator' in name:
            tdraw.polygon([(16*S, 4*S), (28*S, 28*S), (4*S, 28*S)], fill=(255, 0, 0, 255))
        elif 'fatigue_' in name:
            color = (0, 255, 0, 255)
            if 'medium' in name: color = (255, 255, 0, 255)
            if 'high' in name: color = (255, 0, 0, 255)
            tdraw.text((8*S, 8*S), "Zzz", fill=color)
        elif 'skill_' in name:
            color = (200, 200, 200, 255)
            if 'master' in name: color = (255, 215, 0, 255)
            tdraw.polygon([(16*S, 4*S), (20*S, 14*S), (30*S, 14*S), (22*S, 20*S), (25*S, 30*S), (16*S, 24*S), (7*S, 30*S), (10*S, 20*S), (2*S, 14*S), (12*S, 14*S)], fill=color)

        # 20. ELDRITCH HORRORS
        elif 'horror_' in name:
            if 'tentacle' in name:
                # Wavy purple line
                points = [(16*S, 32*S), (20*S, 24*S), (12*S, 16*S), (20*S, 8*S), (16*S, 0*S)]
                tdraw.line(points, fill=(150, 0, 200, 255), width=max(1, int(3*S)))
            elif 'eye' in name:
                # Red eye
                tdraw.ellipse(sc_rect(4, 10, 28, 22), fill=(50, 0, 50, 255))
                tdraw.ellipse(sc_rect(12, 10, 20, 22), fill=(255, 0, 0, 255))
                tdraw.line(sc_rect(16, 12, 16, 20), fill=(0, 0, 0, 255))
            elif 'maw' in name:
                # Toothy mouth
                tdraw.ellipse(sc_rect(4, 4, 28, 28), fill=(50, 0, 0, 255))
                tdraw.polygon([(16*S, 28*S), (12*S, 20*S), (20*S, 20*S)], fill=(255, 255, 255, 255))
                tdraw.polygon([(16*S, 4*S), (12*S, 12*S), (20*S, 12*S)], fill=(255, 255, 255, 255))
            elif 'shadow' in name:
                # Amorphous blob
                tdraw.ellipse(sc_rect(4, 8, 20, 24), fill=(20, 0, 40, 200))
                tdraw.ellipse(sc_rect(12, 4, 28, 20), fill=(20, 0, 40, 200))
            elif 'portal' in name:
                # Swirl
                tdraw.ellipse(sc_rect(2, 2, 30, 30), outline=(100, 0, 200, 255), width=max(1, int(2*S)))
                tdraw.ellipse(sc_rect(8, 8, 24, 24), outline=(150, 0, 255, 255), width=max(1, int(2*S)))
            elif 'boss' in name:
                # Big scary shape
                tdraw.rectangle(sc_rect(4, 4, 28, 28), fill=(50, 0, 50, 255))
                tdraw.ellipse(sc_rect(8, 8, 12, 12), fill=(255, 0, 0, 255))
                tdraw.ellipse(sc_rect(20, 8, 24, 12), fill=(255, 0, 0, 255))

        # 21. Default / Fallback (Missing Texture)
        else:
            # Magenta/Black checkerboard to make missing tiles obvious
            tdraw.rectangle([0, 0, tile_size//2, tile_size//2], fill=(255, 0, 255, 255))
            tdraw.rectangle([tile_size//2, tile_size//2, tile_size, tile_size], fill=(255, 0, 255, 255))
            tdraw.rectangle([tile_size//2, 0, tile_size, tile_size//2], fill=(0, 0, 0, 255))
            tdraw.rectangle([0, tile_size//2, tile_size//2, tile_size], fill=(0, 0, 0, 255))

        # Paste tile into main image
        img.paste(tile, (x, y))

    # Save
    out_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tilesets', 'submarine_tileset.png')
    img.save(out_path)
    print(f"Saved tileset to {out_path}")

if __name__ == "__main__":
    generate_tileset()