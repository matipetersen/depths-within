"""Weapon system for all units (ships, aircraft, submarines).

Implements:
- Depth charges (spawned by escorts/destroyers/aircraft)
- Ship gun fire (surface weapons with arc trajectory)
- Aircraft bombs and torpedoes
- Weapon-specific damage and evasion mechanics
"""
import random
import math


class DepthCharge:
    """Represents an active depth charge."""
    
    def __init__(self, x, y, depth, owner_id, charge_id, owner_type='ship'):
        """Initialize depth charge.
        
        Args:
            x, y: Surface position
            depth: Detonation depth (will explode when sub descends to this depth)
            owner_id: ID of ship/aircraft that deployed it
            charge_id: Unique charge ID
            owner_type: 'ship' or 'aircraft'
        """
        self.x = x
        self.y = y
        self.depth = depth  # Detonation depth
        self.active = True
        self.owner_id = owner_id
        self.id = charge_id
        self.owner_type = owner_type
        self.age = 0  # Ticks alive
        self.blast_radius = 4  # Map units for horizontal blast
        self.damage_at_depth = {  # Damage vs depth differential (0-1.0 scale)
            0: 0.30,     # At exact depth: 30% damage
            1: 0.25,
            2: 0.20,
            3: 0.15,
            4: 0.10,
            5: 0.05
        }
    
    def get_damage_at_depth(self, sub_depth):
        """Calculate damage based on submarine depth vs detonation depth."""
        depth_diff = abs(sub_depth - self.depth)
        if depth_diff > 5:
            return 0.0
        return self.damage_at_depth.get(depth_diff, 0.0)
    
    def is_in_blast_radius(self, sub_x, sub_y, sub_depth):
        """Check if submarine is in blast radius."""
        horizontal_dist = math.hypot(sub_x - self.x, sub_y - self.y)
        return horizontal_dist <= self.blast_radius


class ShellTrajectory:
    """Represents a surface ship's gun fire projectile."""
    
    def __init__(self, sx, sy, tx, ty, shell_id, owner_id, owner_type='merchant'):
        """Initialize shell trajectory.
        
        Args:
            sx, sy: Firing ship position
            tx, ty: Target position
            shell_id: Unique shell ID
            owner_id: ID of firing ship
            owner_type: 'merchant' or 'destroyer'
        """
        self.start_x = sx
        self.start_y = sy
        self.target_x = tx
        self.target_y = ty
        self.x = float(sx)
        self.y = float(sy)
        self.id = shell_id
        self.owner_id = owner_id
        self.owner_type = owner_type
        
        # Trajectory calculation
        dx = tx - sx
        dy = ty - sy
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = dx / dist * 0.5  # Speed: 0.5 units per tick
            self.vy = dy / dist * 0.5
        else:
            self.vx = 0
            self.vy = 0
        
        self.travel_dist = 0
        self.max_range = 15  # Maximum range
        self.active = True
        self.damage = 0.08  # 8% hull damage on hit (surface only)
    
    def tick(self):
        """Move shell one step along trajectory."""
        self.x += self.vx
        self.y += self.vy
        self.travel_dist += math.hypot(self.vx, self.vy)
        
        # Deactivate if traveled too far
        if self.travel_dist >= self.max_range:
            self.active = False
    
    def is_near_target(self, tolerance=0.5):
        """Check if shell has reached target."""
        dist = math.hypot(self.x - self.target_x, self.y - self.target_y)
        return dist <= tolerance


class AircraftAttack:
    """Represents an active aircraft attack run."""
    
    def __init__(self, aircraft_id, aircraft_name, nation, x, y, depth, attack_type='bomb'):
        """Initialize aircraft attack.
        
        Args:
            aircraft_id: Unique aircraft ID
            aircraft_name: Type of aircraft
            nation: Nation flying aircraft
            x, y: Current position
            depth: Operating depth of submarine (for calculation)
            attack_type: 'bomb', 'depth_charge', 'torpedo', 'gun'
        """
        self.id = aircraft_id
        self.name = aircraft_name
        self.nation = nation
        self.x = x
        self.y = y
        self.depth = depth
        self.attack_type = attack_type
        self.active = True
        self.progress = 0  # 0-1.0, how far through attack run
        self.duration = 8  # Ticks for full attack
        
        # Damage by weapon type
        self.damage_table = {
            'bomb': 0.25,           # 25% hull damage
            'depth_charge': 0.20,   # 20% hull damage
            'torpedo': 0.35,        # 35% hull damage (rarer)
            'gun': 0.10              # 10% hull damage
        }
    
    def get_damage(self):
        """Return damage for this attack type."""
        return self.damage_table.get(self.attack_type, 0.15)
    
    def tick(self):
        """Progress attack run."""
        self.progress = min(1.0, self.progress + 1.0 / self.duration)
        if self.progress >= 1.0:
            self.active = False


class WeaponManager:
    """Manages all active weapons on the tactical map."""
    
    def __init__(self):
        """Initialize weapon manager."""
        self.depth_charges = []
        self.shells = []
        self.aircraft_attacks = []
        self._next_charge_id = 1
        self._next_shell_id = 1
        self._next_aircraft_id = 1
    
    def spawn_depth_charge(self, x, y, depth, owner_id, owner_type='ship'):
        """Spawn a new depth charge."""
        charge = DepthCharge(x, y, depth, owner_id, self._next_charge_id, owner_type)
        self.depth_charges.append(charge)
        self._next_charge_id += 1
        return charge
    
    def spawn_shell(self, sx, sy, tx, ty, owner_id, owner_type='merchant'):
        """Spawn a new shell trajectory."""
        shell = ShellTrajectory(sx, sy, tx, ty, self._next_shell_id, owner_id, owner_type)
        self.shells.append(shell)
        self._next_shell_id += 1
        return shell
    
    def spawn_aircraft_attack(self, aircraft_id, aircraft_name, nation, x, y, depth, attack_type='bomb'):
        """Spawn a new aircraft attack."""
        attack = AircraftAttack(aircraft_id, aircraft_name, nation, x, y, depth, attack_type)
        self.aircraft_attacks.append(attack)
        self._next_aircraft_id += 1
        return attack
    
    def tick(self, submarine=None, tmap=None):
        """Update all weapons, check for hits.
        
        Args:
            submarine: Player submarine (for hit detection)
            tmap: Tactical map (for reference)
        
        Returns:
            List of (weapon_type, damage, location) hits on submarine
        """
        hits = []
        
        # Tick shells
        for shell in self.shells:
            if shell.active:
                shell.tick()
        self.shells = [s for s in self.shells if s.active]
        
        # Tick aircraft attacks
        for attack in self.aircraft_attacks:
            if attack.active:
                attack.tick()
        self.aircraft_attacks = [a for a in self.aircraft_attacks if a.active]
        
        # Check depth charges for submarine hit
        if submarine and hasattr(submarine, 'x') and hasattr(submarine, 'systems'):
            current_depth = getattr(submarine.systems, 'depth', 0)
            
            for charge in self.depth_charges:
                if charge.active and charge.is_in_blast_radius(submarine.x, submarine.y, current_depth):
                    damage = charge.get_damage_at_depth(current_depth)
                    if damage > 0:
                        hits.append(('depth_charge', damage, f"({charge.x},{charge.y})@{charge.depth}m"))
                        charge.active = False
            
            # Check aircraft attacks for hit
            for attack in self.aircraft_attacks:
                if attack.active and attack.progress >= 0.8:  # Hit only near end of run
                    dist = math.hypot(submarine.x - attack.x, submarine.y - attack.y)
                    if dist <= 2.0:  # Close range
                        damage = attack.get_damage()
                        hits.append(('aircraft_attack', damage, f"{attack.name} ({attack.attack_type})"))
                        attack.active = False
        
        # Remove inactive weapons
        self.depth_charges = [c for c in self.depth_charges if c.active or c.age < 20]
        for charge in self.depth_charges:
            charge.age += 1
        
        return hits
    
    def get_active_charges(self):
        """Get list of active depth charges."""
        return [c for c in self.depth_charges if c.active]
    
    def get_active_shells(self):
        """Get list of active shells."""
        return [s for s in self.shells if s.active]
    
    def get_active_aircraft_attacks(self):
        """Get list of active aircraft attacks."""
        return [a for a in self.aircraft_attacks if a.active]
