"""
Scenario Generator - Create dynamic game scenarios based on parameters.
Generates matched scenarios for region, faction, difficulty, and year.
"""

import random
from typing import Dict, Optional, Tuple
from world.faction_manager import FactionManager
from world.convoy_manager import ConvoyManager
from world.aircraft_manager import AircraftManager


class ScenarioGenerator:
    """Generates game scenarios with matched difficulty and context."""
    
    def __init__(self):
        """Initialize scenario generator with managers."""
        self.faction_manager = FactionManager()
        self.convoy_manager = ConvoyManager()
        self.aircraft_manager = AircraftManager()
    
    def generate_scenario(self, 
                         region: Optional[str] = None,
                         faction: Optional[str] = None,
                         difficulty: Optional[str] = None,
                         year: int = 1943) -> Dict:
        """Generate a complete scenario."""
        
        # Pick region
        if not region:
            regions = ['north_atlantic', 'arctic', 'mediterranean', 'western_pacific', 'indian_ocean']
            region = random.choice(regions)
        
        # Pick player faction
        if not faction:
            # Player usually takes a major submarine power
            primary_factions = self.faction_manager.get_primary_factions()
            faction_obj = random.choice(primary_factions)
        else:
            faction_obj = self.faction_manager.get_faction(faction)
        
        # Pick difficulty
        if not difficulty:
            difficulty = random.choice(['easy', 'medium', 'hard', 'very_hard'])
        
        # Get region metadata (simplified)
        region_meta = {
            'north_atlantic': {
                'threat_nation': 'Germany',
                'dominant_convoy_nation': 'USA',
                'weather_hazard': 'high',
                'year_active_start': 1941,
                'year_active_end': 1945,
            },
            'arctic': {
                'threat_nation': 'Germany',
                'dominant_convoy_nation': 'UK',
                'weather_hazard': 'extreme',
                'year_active_start': 1941,
                'year_active_end': 1944,
            },
            'mediterranean': {
                'threat_nation': 'Italy',
                'dominant_convoy_nation': 'UK',
                'weather_hazard': 'medium',
                'year_active_start': 1941,
                'year_active_end': 1943,
            },
            'western_pacific': {
                'threat_nation': 'Japan',
                'dominant_convoy_nation': 'USA',
                'weather_hazard': 'high',
                'year_active_start': 1942,
                'year_active_end': 1945,
            },
            'indian_ocean': {
                'threat_nation': 'Japan',
                'dominant_convoy_nation': 'UK',
                'weather_hazard': 'low',
                'year_active_start': 1942,
                'year_active_end': 1944,
            }
        }
        
        region_info = region_meta.get(region, region_meta['north_atlantic'])
        
        # Build scenario dict
        scenario = {
            'id': f"scenario_{random.randint(10000, 99999)}",
            'region': region,
            'player_faction': faction_obj.id,
            'player_faction_name': faction_obj.name,
            'difficulty': difficulty,
            'year': year,
            'threat_nation': region_info['threat_nation'],
            'dominant_convoy_nation': region_info['dominant_convoy_nation'],
            'weather_hazard': region_info['weather_hazard'],
            'briefing': self._generate_briefing(region, faction_obj, difficulty, year),
            'objectives': self._generate_objectives(region, difficulty),
            'enemy_forces': self._generate_enemy_forces(region, year, difficulty),
            'friendly_convoys': self._generate_convoys(region, year, difficulty),
            'aircraft_threat': self._generate_aircraft_threat(region, year, difficulty),
            'victory_conditions': self._generate_victory_conditions(difficulty)
        }
        
        return scenario
    
    def _generate_briefing(self, region: str, faction_obj, difficulty: str, year: int) -> str:
        """Generate scenario briefing text."""
        briefings = {
            'north_atlantic': f"You are commanding a {faction_obj.name} submarine in the North Atlantic. "
                            f"German U-boats are conducting commerce warfare against Allied convoys. "
                            f"Your mission: hunt merchant shipping and warships.",
            'arctic': f"Arctic patrol assigned to {faction_obj.name} submarine. "
                     f"Extremely dangerous conditions with German and Norwegian opposition. "
                     f"Protect convoys to Soviet Union from U-boat and air attacks.",
            'mediterranean': f"{faction_obj.name} submarine deployed to Mediterranean. "
                            f"Italian Navy and Luftwaffe present. Intercept British and American convoys. "
                            f"High civilian traffic presents targeting challenges.",
            'western_pacific': f"{faction_obj.name} submarine on patrol in Western Pacific. "
                             f"Japanese merchant fleet and Navy present. "
                             f"Conduct commerce raiding and support fleet operations.",
            'indian_ocean': f"{faction_obj.name} submarine deployed to Indian Ocean. "
                           f"Remote waters but active Japanese trade routes. "
                           f"Limited resupply—plan extended patrol carefully."
        }
        return briefings.get(region, "You are assigned to patrol this region.")
    
    def _generate_objectives(self, region: str, difficulty: str) -> list:
        """Generate mission objectives based on difficulty."""
        base_objectives = {
            'easy': [
                "Survive for 30 game days",
                "Sink at least 1 merchant vessel",
                "Return to port with >20% battery"
            ],
            'medium': [
                "Sink merchant shipping totaling 20,000 tons",
                "Avoid sinking 3 torpedoes' worth of damage",
                "Complete patrol without crew casualties"
            ],
            'hard': [
                "Sink shipping totaling 50,000 tons",
                "Engage and damage at least 1 escort vessel",
                "Survive extended patrol (60+ days)"
            ],
            'very_hard': [
                "Sink 100,000+ tons of merchant shipping",
                "Sink or heavily damage 1+ escort vessel",
                "Avoid all aircraft encounters",
                "Return with >50% crew alive"
            ]
        }
        return base_objectives.get(difficulty, base_objectives['medium'])
    
    def _generate_enemy_forces(self, region: str, year: int, difficulty: str) -> Dict:
        """Generate enemy forces for the scenario."""
        difficulty_map = {
            'easy': {'patrol_aircraft': 1, 'escort_ships': 2, 'merchant_ships': 3},
            'medium': {'patrol_aircraft': 2, 'escort_ships': 4, 'merchant_ships': 6},
            'hard': {'patrol_aircraft': 3, 'escort_ships': 6, 'merchant_ships': 8},
            'very_hard': {'patrol_aircraft': 5, 'escort_ships': 8, 'merchant_ships': 12}
        }
        return difficulty_map.get(difficulty, difficulty_map['medium'])
    
    def _generate_convoys(self, region: str, year: int, difficulty: str) -> list:
        """Generate friendly convoys for the scenario."""
        # Get active templates for this region
        templates = self.convoy_manager.get_templates_active_in_year(year)
        
        # Filter by difficulty
        if difficulty in ['easy', 'medium']:
            templates = [t for t in templates if t.difficulty in ['easy', 'medium']]
        else:
            # Hard/very_hard can have all difficulties
            pass
        
        if not templates:
            return []
        
        # Pick 1-3 convoys
        num_convoys = {'easy': 1, 'medium': 2, 'hard': 3, 'very_hard': 3}.get(difficulty, 2)
        selected = random.sample(templates, min(num_convoys, len(templates)))
        
        return [
            {
                'template_id': t.id,
                'route': t.route,
                'nation': t.nation,
                'ships': t.get_total_ships(),
                'tonnage': t.get_total_cargo(),
                'difficulty': t.difficulty,
                'frequency_days': t.frequency_days
            }
            for t in selected
        ]
    
    def _generate_aircraft_threat(self, region: str, year: int, difficulty: str) -> Dict:
        """Generate aircraft threat parameters."""
        threat_levels = {
            'easy': 'low',
            'medium': 'medium',
            'hard': 'high',
            'very_hard': 'extreme'
        }
        
        return {
            'threat_level': threat_levels.get(difficulty, 'medium'),
            'patrol_frequency': {'easy': 5, 'medium': 3, 'hard': 2, 'very_hard': 1}.get(difficulty, 3),
            'bases_in_region': {'north_atlantic': 2, 'arctic': 2, 'mediterranean': 3, 'western_pacific': 4, 'indian_ocean': 1}.get(region, 1)
        }
    
    def _generate_victory_conditions(self, difficulty: str) -> Dict:
        """Generate victory conditions."""
        return {
            'minimum_tonnage_sunk': {
                'easy': 10000,
                'medium': 25000,
                'hard': 50000,
                'very_hard': 100000
            }.get(difficulty, 25000),
            'crew_survival_pct': {
                'easy': 50,
                'medium': 70,
                'hard': 80,
                'very_hard': 90
            }.get(difficulty, 70),
            'patrol_days': {
                'easy': 30,
                'medium': 45,
                'hard': 60,
                'very_hard': 90
            }.get(difficulty, 45)
        }
    
    def list_scenarios(self, count: int = 5) -> str:
        """Generate and list example scenarios."""
        result = "Generated Scenarios:\n"
        for i in range(count):
            scenario = self.generate_scenario()
            result += f"\n{i+1}. {scenario['id']}\n"
            result += f"   Region: {scenario['region']}\n"
            result += f"   Player: {scenario['player_faction_name']}\n"
            result += f"   Difficulty: {scenario['difficulty']}\n"
            result += f"   Year: {scenario['year']}\n"
            result += f"   Objectives: {len(scenario['objectives'])} goals\n"
        return result
