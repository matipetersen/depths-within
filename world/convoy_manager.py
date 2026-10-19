"""
Convoy Manager - Load and manage convoy templates and spawning.
Generates dynamic convoys based on routes and templates.
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple


class ConvoyTemplate:
    """Represents a convoy template/route."""
    
    def __init__(self, data: dict):
        """Initialize convoy from data dict."""
        self.id = data.get('id', 'unknown')
        self.route = data.get('route', 'Unknown')
        self.nation = data.get('nation', 'unknown')
        self.description = data.get('description', '')
        
        # Composition
        composition = data.get('composition', {})
        self.merchant_count = composition.get('merchant', 0)
        self.tanker_count = composition.get('tanker', 0)
        self.troopship_count = composition.get('troopship', 0)
        
        # Escort
        self.escort_types = data.get('escort', [])
        self.escort_count = len(self.escort_types)
        
        # Operation
        self.departure_month = data.get('departure_month', 'all')
        self.frequency_days = data.get('frequency_days', 7)
        self.speed = data.get('speed', 10)
        self.difficulty = data.get('difficulty', 'medium')
        self.year_start = data.get('year_start', 1941)
        self.year_end = data.get('year_end', 1945)
    
    def get_total_ships(self) -> int:
        """Get total number of ships in convoy."""
        return self.merchant_count + self.tanker_count + self.troopship_count + self.escort_count
    
    def get_total_cargo(self) -> int:
        """Get total cargo tonnage (merchant + tanker + troopship)."""
        # Rough estimates for value
        merchant_tonnage = self.merchant_count * 7000
        tanker_tonnage = self.tanker_count * 15000
        troopship_tonnage = self.troopship_count * 12000
        return merchant_tonnage + tanker_tonnage + troopship_tonnage
    
    def is_high_value(self) -> bool:
        """Check if convoy is high-value target."""
        return self.get_total_cargo() > 50000 or self.troopship_count > 0
    
    def get_difficulty_multiplier(self) -> float:
        """Get difficulty multiplier (for damage/threat scaling)."""
        multipliers = {
            'easy': 0.5,
            'medium': 1.0,
            'hard': 1.5,
            'very_hard': 2.0
        }
        return multipliers.get(self.difficulty, 1.0)
    
    def __repr__(self):
        return f"<Convoy {self.id} ({self.route}) - {self.get_total_ships()} ships>"


class ConvoyManager:
    """Manages convoy templates and dynamic generation."""
    
    def __init__(self, data_dir: str = 'data'):
        """Initialize convoy manager."""
        self.data_dir = data_dir
        self.templates: Dict[str, ConvoyTemplate] = {}
        self.templates_by_nation: Dict[str, List[ConvoyTemplate]] = {}
        self.templates_by_difficulty: Dict[str, List[ConvoyTemplate]] = {}
        self._load_convoys()
    
    def _load_convoys(self):
        """Load convoy templates from JSON file."""
        try:
            convoys_file = os.path.join(self.data_dir, 'convoys.json')
            with open(convoys_file, 'r') as f:
                data = json.load(f)
            
            for convoy_data in data:
                convoy = ConvoyTemplate(convoy_data)
                self.templates[convoy.id] = convoy
                
                # Index by nation
                if convoy.nation not in self.templates_by_nation:
                    self.templates_by_nation[convoy.nation] = []
                self.templates_by_nation[convoy.nation].append(convoy)
                
                # Index by difficulty
                if convoy.difficulty not in self.templates_by_difficulty:
                    self.templates_by_difficulty[convoy.difficulty] = []
                self.templates_by_difficulty[convoy.difficulty].append(convoy)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load convoys: {e}")
    
    def get_template(self, template_id: str) -> Optional[ConvoyTemplate]:
        """Get convoy template by ID."""
        return self.templates.get(template_id)
    
    def get_templates_by_nation(self, nation: str) -> List[ConvoyTemplate]:
        """Get all convoy templates from a nation."""
        return self.templates_by_nation.get(nation, [])
    
    def get_templates_by_difficulty(self, difficulty: str) -> List[ConvoyTemplate]:
        """Get all templates with given difficulty."""
        return self.templates_by_difficulty.get(difficulty, [])
    
    def get_random_template(self, nation: Optional[str] = None, 
                           difficulty: Optional[str] = None) -> Optional[ConvoyTemplate]:
        """Get random convoy template, optionally filtered."""
        candidates = list(self.templates.values())
        
        if nation:
            candidates = [c for c in candidates if c.nation == nation]
        
        if difficulty:
            candidates = [c for c in candidates if c.difficulty == difficulty]
        
        return random.choice(candidates) if candidates else None
    
    def get_high_value_templates(self) -> List[ConvoyTemplate]:
        """Get all high-value convoy templates."""
        return [c for c in self.templates.values() if c.is_high_value()]
    
    def get_templates_active_in_year(self, year: int) -> List[ConvoyTemplate]:
        """Get all templates active in a given year."""
        return [c for c in self.templates.values() 
                if c.year_start <= year <= c.year_end]
    
    def spawn_convoy(self, template: ConvoyTemplate, 
                    position: Tuple[int, int] = (0, 0)) -> Dict:
        """Spawn a dynamic convoy from a template."""
        convoy = {
            'id': f"{template.id}_{random.randint(1000, 9999)}",
            'template_id': template.id,
            'position': position,
            'route': template.route,
            'nation': template.nation,
            'speed': template.speed,
            'difficulty': template.difficulty,
            'ships': []
        }
        
        # Add merchant ships
        for _ in range(template.merchant_count):
            convoy['ships'].append({
                'type': 'merchant',
                'ship_id': random.choice(['Liberty_Ship', 'Victory_Ship', 'Japanese_Maru', 'Italian_Freighter']),
                'x': position[0] + random.randint(-5, 5),
                'y': position[1] + random.randint(-5, 5),
                'health': 100
            })
        
        # Add tankers
        for _ in range(template.tanker_count):
            convoy['ships'].append({
                'type': 'tanker',
                'ship_id': 'HC_Tanker',
                'x': position[0] + random.randint(-5, 5),
                'y': position[1] + random.randint(-5, 5),
                'health': 100
            })
        
        # Add troopships
        for _ in range(template.troopship_count):
            convoy['ships'].append({
                'type': 'troopship',
                'ship_id': 'Troopship',
                'x': position[0] + random.randint(-5, 5),
                'y': position[1] + random.randint(-5, 5),
                'health': 100
            })
        
        # Add escort ships
        for escort_type in template.escort_types:
            convoy['ships'].append({
                'type': 'escort',
                'ship_id': escort_type,
                'x': position[0] + random.randint(-3, 3),
                'y': position[1] + random.randint(-3, 3),
                'health': 100
            })
        
        return convoy
    
    def list_all(self) -> str:
        """Get formatted list of all convoy templates."""
        result = "Convoy Templates:\n"
        for nation in sorted(self.templates_by_nation.keys()):
            templates = self.templates_by_nation[nation]
            result += f"\n{nation}:\n"
            for template in templates:
                result += f"  {template.id:10s} - {template.route:30s} ({template.difficulty})\n"
                result += f"             Composition: {template.merchant_count}x merchant, {template.tanker_count}x tanker, {template.troopship_count}x troop, {template.escort_count}x escort\n"
        return result
