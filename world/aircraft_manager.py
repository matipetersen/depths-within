"""
Aircraft Manager - Load and manage aircraft data.
Handles aircraft spawning, threat simulation, and combat resolution.
"""

import json
import os
import random
from typing import Dict, List, Optional


class Aircraft:
    """Represents an aircraft type."""
    
    def __init__(self, data: dict):
        """Initialize aircraft from data dict."""
        self.id = data.get('id', 'unknown')
        self.nation = data.get('nation', 'unknown')
        self.type = data.get('type', 'fighter')  # flying_boat, fighter_bomber, etc.
        self.description = data.get('description', '')
        self.role = data.get('role', 'fighter_defense')  # maritime_patrol, anti_ship, etc.
        self.engine_type = data.get('engine_type', 'radial')
        self.crew = data.get('crew', 1)
        self.speed = data.get('speed', 300)  # knots
        self.endurance_hours = data.get('endurance_hours', 3)
        self.armament = data.get('armament', [])
        self.radar = data.get('radar', False)
        self.bomb_load = data.get('bomb_load', 0)  # lbs
        self.depth_charges = data.get('depth_charges', 0)
        self.range_nm = data.get('range_nm', 500)
        self.year = data.get('year', 1940)
        self.threat_level = data.get('threat_level', 'medium')  # low, medium, high
    
    def is_anti_submarine(self) -> bool:
        """Check if aircraft has ASW capability."""
        return self.depth_charges > 0 or self.role == 'maritime_patrol'
    
    def is_anti_ship(self) -> bool:
        """Check if aircraft has anti-ship capability."""
        return self.role == 'anti_ship' or self.bomb_load > 0
    
    def get_damage_range(self) -> tuple:
        """Get min/max damage this aircraft can inflict (0-10 scale)."""
        if self.role == 'maritime_patrol':
            return (2, 4)  # Depth charges/bombs
        elif self.role == 'anti_ship':
            return (3, 7)  # Dedicated anti-ship
        elif self.role == 'fighter_defense':
            return (1, 3)  # Light armament
        else:
            return (1, 2)
    
    def __repr__(self):
        return f"<{self.id} ({self.nation}) - {self.role}>"


class AircraftManager:
    """Manages all aircraft types and spawning."""
    
    def __init__(self, data_dir: str = 'data'):
        """Initialize aircraft manager."""
        self.data_dir = data_dir
        self.aircraft: Dict[str, Aircraft] = {}
        self.aircraft_by_nation: Dict[str, List[Aircraft]] = {}
        self.aircraft_by_role: Dict[str, List[Aircraft]] = {}
        self._load_aircraft()
    
    def _load_aircraft(self):
        """Load aircraft from JSON file."""
        try:
            aircraft_file = os.path.join(self.data_dir, 'aircraft.json')
            with open(aircraft_file, 'r') as f:
                data = json.load(f)
            
            for aircraft_data in data:
                ac = Aircraft(aircraft_data)
                self.aircraft[ac.id] = ac
                
                # Index by nation
                if ac.nation not in self.aircraft_by_nation:
                    self.aircraft_by_nation[ac.nation] = []
                self.aircraft_by_nation[ac.nation].append(ac)
                
                # Index by role
                if ac.role not in self.aircraft_by_role:
                    self.aircraft_by_role[ac.role] = []
                self.aircraft_by_role[ac.role].append(ac)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load aircraft: {e}")
    
    def get_aircraft(self, aircraft_id: str) -> Optional[Aircraft]:
        """Get aircraft by ID."""
        return self.aircraft.get(aircraft_id)
    
    def get_aircraft_by_nation(self, nation: str) -> List[Aircraft]:
        """Get all aircraft from a nation."""
        return self.aircraft_by_nation.get(nation, [])
    
    def get_aircraft_by_role(self, role: str) -> List[Aircraft]:
        """Get all aircraft with a given role."""
        return self.aircraft_by_role.get(role, [])
    
    def get_random_aircraft(self, nation: Optional[str] = None, 
                           role: Optional[str] = None) -> Optional[Aircraft]:
        """Get random aircraft, optionally filtered by nation and/or role."""
        candidates = list(self.aircraft.values())
        
        if nation:
            candidates = [a for a in candidates if a.nation == nation]
        
        if role:
            candidates = [a for a in candidates if a.role == role]
        
        return random.choice(candidates) if candidates else None
    
    def get_patrol_aircraft(self, nation: str) -> List[Aircraft]:
        """Get all maritime patrol aircraft from a nation."""
        return [a for a in self.get_aircraft_by_nation(nation) 
                if a.role == 'maritime_patrol']
    
    def get_fighter_aircraft(self, nation: str) -> List[Aircraft]:
        """Get all fighter aircraft from a nation."""
        return [a for a in self.get_aircraft_by_nation(nation) 
                if 'fighter' in a.role or a.type == 'fighter']
    
    def spawn_patrol_flight(self, nation: str, count: int = 1) -> List[Aircraft]:
        """Spawn patrol aircraft for a nation."""
        patrol_ac = self.get_patrol_aircraft(nation)
        if not patrol_ac:
            return []
        
        return [random.choice(patrol_ac) for _ in range(min(count, len(patrol_ac)))]
    
    def spawn_combat_flight(self, nation: str, role: str = 'anti_ship', 
                           count: int = 1) -> List[Aircraft]:
        """Spawn combat aircraft for a nation."""
        candidates = [a for a in self.get_aircraft_by_nation(nation) 
                     if role in a.role or a.role == role]
        if not candidates:
            return []
        
        return [random.choice(candidates) for _ in range(min(count, len(candidates)))]
    
    def list_all(self) -> str:
        """Get formatted list of all aircraft."""
        result = "Aircraft:\n"
        for nation in sorted(self.aircraft_by_nation.keys()):
            ac_list = self.aircraft_by_nation[nation]
            result += f"\n{nation}:\n"
            for ac in ac_list:
                result += f"  {ac.id:20s} - {ac.role:20s} (Range: {ac.range_nm} nm, Threat: {ac.threat_level})\n"
        return result
