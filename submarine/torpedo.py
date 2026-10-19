"""Simple torpedo model for tactical simulation.

Torpedoes move in continuous map-space (x,y) and check for contact collisions
with `TacticalMap.contacts`. This version includes historical torpedo defects
and realistic WWII-era failures.
"""
import math
import random
from world.sonar_systems import TORPEDO_DEFECTS


class Torpedo:
    def __init__(self, owner_id, x, y, dx, dy, speed=1.5, life=30, target_id=None, homing_strength=0.20, torpedo_type='G7e'):
        # owner_id: identifier of the firing sub (string)
        self.owner_id = owner_id
        self.x = float(x)
        self.y = float(y)
        # normalized direction vector
        mag = math.hypot(dx, dy) or 1.0
        self.dx = dx / mag
        self.dy = dy / mag
        self.speed = float(speed)  # cells per tick
        self.life = life  # ticks before self-destruct
        self.active = True
        self.exploded = False
        # homing target (contact id) and homing tuning
        self.target_id = target_id
        self.homing_strength = float(homing_strength)
        
        # Historical torpedo type and defects
        self.torpedo_type = torpedo_type
        self.defect = None  # Will be set if a historical defect occurs
        self.check_historical_defects()
        
        # Depth (for depth-based failures)
        self.depth = 0
    
    def check_historical_defects(self):
        """Check if this torpedo has a historical manufacturing defect."""
        for defect in TORPEDO_DEFECTS:
            if defect.torpedo_type == self.torpedo_type:
                if defect.occurs():
                    self.defect = defect
                    break

    def step(self, tactical_map):
        if not self.active:
            return None
        
        # Apply historical defects
        if self.defect:
            if self.defect.name == 'Mark 14 Deep Running':
                # Torpedo runs 3-6m deeper than set - for detection purposes
                self.depth += random.uniform(0.5, 1.0)  # Gradually goes deeper
            elif self.defect.name == 'G7a Hot Run':
                # Torpedo motor started in tube - runs erratically
                self.dx += random.uniform(-0.1, 0.1)
                self.dy += random.uniform(-0.1, 0.1)
                # Renormalize
                mag = math.hypot(self.dx, self.dy) or 1.0
                self.dx /= mag
                self.dy /= mag
        
        # homing adjustment toward target if present
        if self.target_id is not None:
            # find the contact by id
            tgt = None
            for c in tactical_map.contacts:
                if c.get('id') == self.target_id:
                    tgt = c
                    break
            if tgt is not None:
                to_dx = tgt['x'] - self.x
                to_dy = tgt['y'] - self.y
                mag = math.hypot(to_dx, to_dy) or 1.0
                ndx = to_dx / mag
                ndy = to_dy / mag
                # blend directions for smooth turning
                blend = self.homing_strength
                self.dx = (1.0 - blend) * self.dx + blend * ndx
                self.dy = (1.0 - blend) * self.dy + blend * ndy
                # renormalize
                mag2 = math.hypot(self.dx, self.dy) or 1.0
                self.dx /= mag2
                self.dy /= mag2

        # move
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.life -= 1

        # bounds check
        if self.x < 0 or self.y < 0 or self.x >= tactical_map.width or self.y >= tactical_map.height:
            self.active = False
            return {'type': 'wall', 'torpedo': self}

        # check for impact with contacts (simple distance threshold)
        hit_contact = None
        for c in list(tactical_map.contacts):
            # contact positions are integer grid coords
            dx = c['x'] - self.x
            dy = c['y'] - self.y
            if math.hypot(dx, dy) < 0.75:
                hit_contact = c
                break

        if hit_contact:
            # Check for defect-based miss
            miss = False
            if self.defect:
                if self.defect.name == 'Mark 14 Magnetic Detonator Failure':
                    # 35% additional failure chance beyond base defect
                    miss = random.random() < 0.35
                elif self.defect.name == 'Mark 14 Deep Running':
                    # Torpedo passed under target - miss
                    miss = True
            
            if not miss:
                # remove contact and mark explosion
                try:
                    tactical_map.contacts.remove(hit_contact)
                except ValueError:
                    pass
                self.active = False
                self.exploded = True
                return {'type': 'hit', 'contact': hit_contact, 'torpedo': self, 'defect': self.defect}
            else:
                # Defect caused miss - return as near-miss
                self.active = False
                return {'type': 'defect_miss', 'contact': hit_contact, 'torpedo': self, 'defect': self.defect}

        if self.life <= 0:
            self.active = False
            return {'type': 'timeout', 'torpedo': self}

        return None
