"""
Faction Manager - Load and manage faction data.
Tracks faction relationships, alignments, and capabilities.
"""

import json
import os
from typing import Dict, List, Optional


class Faction:
    """Represents a faction (nation) in the game."""
    
    def __init__(self, data: dict):
        """Initialize a faction from data dict."""
        self.id = data.get('id', 'unknown')
        self.name = data.get('name', 'Unknown Faction')
        self.color = data.get('color', 'white')
        self.primary_faction = data.get('primary_faction', False)
        self.alignment = data.get('alignment', 'neutral')  # axis, allies, neutral
        self.primary_navy = data.get('primary_navy', 'Unknown Navy')
        self.description = data.get('description', '')
        self.headquarters = data.get('headquarters', '')
        self.founded = data.get('founded', 0)
    
    def is_axis(self) -> bool:
        """Check if faction is Axis aligned."""
        return self.alignment == 'axis'
    
    def is_allied(self) -> bool:
        """Check if faction is Allied aligned."""
        return self.alignment == 'allies'
    
    def is_hostile_to(self, other: 'Faction') -> bool:
        """Check if this faction is hostile to another."""
        # Same alignment = friendly, different = hostile
        return self.alignment != other.alignment and self.alignment != 'neutral'
    
    def __repr__(self):
        return f"<Faction {self.name} ({self.alignment})>"


class FactionManager:
    """Manages all factions and their relationships."""
    
    def __init__(self, data_dir: str = 'data'):
        """Initialize faction manager."""
        self.data_dir = data_dir
        self.factions: Dict[str, Faction] = {}
        self.factions_by_alignment: Dict[str, List[Faction]] = {
            'axis': [],
            'allies': [],
            'neutral': []
        }
        self._load_factions()
    
    def _load_factions(self):
        """Load factions from JSON file."""
        try:
            factions_file = os.path.join(self.data_dir, 'factions.json')
            with open(factions_file, 'r') as f:
                data = json.load(f)
            
            for faction_data in data:
                faction = Faction(faction_data)
                self.factions[faction.id] = faction
                self.factions_by_alignment[faction.alignment].append(faction)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load factions: {e}")
    
    def get_faction(self, faction_id: str) -> Optional[Faction]:
        """Get a faction by ID."""
        return self.factions.get(faction_id)
    
    def get_factions_by_alignment(self, alignment: str) -> List[Faction]:
        """Get all factions with a given alignment."""
        return self.factions_by_alignment.get(alignment, [])
    
    def get_axis_factions(self) -> List[Faction]:
        """Get all Axis factions."""
        return self.factions_by_alignment['axis']
    
    def get_allied_factions(self) -> List[Faction]:
        """Get all Allied factions."""
        return self.factions_by_alignment['allies']
    
    def get_primary_factions(self) -> List[Faction]:
        """Get all primary factions (playable/major powers)."""
        return [f for f in self.factions.values() if f.primary_faction]
    
    def get_random_faction(self, alignment: Optional[str] = None) -> Optional[Faction]:
        """Get a random faction, optionally filtered by alignment."""
        import random
        if alignment:
            candidates = self.factions_by_alignment.get(alignment, [])
        else:
            candidates = list(self.factions.values())
        
        return random.choice(candidates) if candidates else None
    
    def are_hostile(self, faction1_id: str, faction2_id: str) -> bool:
        """Check if two factions are hostile to each other."""
        f1 = self.get_faction(faction1_id)
        f2 = self.get_faction(faction2_id)
        
        if not f1 or not f2:
            return False
        
        return f1.is_hostile_to(f2)
    
    def get_hostile_factions(self, faction_id: str) -> List[Faction]:
        """Get all factions hostile to the given faction."""
        faction = self.get_faction(faction_id)
        if not faction:
            return []
        
        return [f for f in self.factions.values() if faction.is_hostile_to(f)]
    
    def get_friendly_factions(self, faction_id: str) -> List[Faction]:
        """Get all factions friendly to the given faction."""
        faction = self.get_faction(faction_id)
        if not faction:
            return []
        
        return [f for f in self.factions.values() 
                if f.alignment == faction.alignment and f.id != faction_id]
    
    def list_all(self) -> str:
        """Get formatted list of all factions."""
        result = "Factions:\n"
        for alignment in ['axis', 'allies', 'neutral']:
            factions = self.factions_by_alignment[alignment]
            if factions:
                result += f"\n{alignment.upper()}:\n"
                for faction in factions:
                    status = " (Primary)" if faction.primary_faction else ""
                    result += f"  {faction.name}{status} - {faction.primary_navy}\n"
        return result
