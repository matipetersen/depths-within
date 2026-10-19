"""
Player Progression and Submarine Upgrade System.
Tracks player XP, skills, and submarine improvements over career.
"""

import json
from typing import Dict, List, Optional, Tuple


class PlayerStats:
    """Tracks overall player skill and progression."""
    
    def __init__(self):
        """Initialize player stats."""
        self.level = 1
        self.total_xp = 0
        self.skills = {
            'sonar_operation': 0,
            'torpedo_accuracy': 0,
            'evasion': 0,
            'resource_management': 0,
            'crew_leadership': 0,
            'navigation': 0,
            'damage_control': 0
        }
        self.career_stats = {
            'ships_sunk': 0,
            'tonnage_sunk': 0,
            'contacts_detected': 0,
            'torpedoes_fired': 0,
            'successful_hits': 0,
            'patrol_days': 0,
            'crew_trained': 0,
            'narrow_escapes': 0,
            'compartments_repaired': 0
        }
    
    def gain_xp(self, skill: str, amount: int = 10):
        """Gain experience in a skill."""
        if skill in self.skills:
            self.skills[skill] += amount
            self.total_xp += amount
            
            # Check for level up (every 500 total XP)
            new_level = 1 + (self.total_xp // 500)
            if new_level > self.level:
                self.level = new_level
    
    def get_skill_bonus(self, skill: str) -> float:
        """Get skill bonus as percentage (0-1)."""
        if skill not in self.skills:
            return 0.0
        return min(1.0, self.skills[skill] / 500.0)
    
    def record_event(self, event_type: str, value: int = 1):
        """Record career event."""
        if event_type in self.career_stats:
            self.career_stats[event_type] += value
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'level': self.level,
            'total_xp': self.total_xp,
            'skills': self.skills,
            'career_stats': self.career_stats
        }
    
    def __repr__(self):
        return f"<PlayerStats Level {self.level}, {self.total_xp} XP>"


class SubmariueUpgrade:
    """Represents a single submarine upgrade."""
    
    def __init__(self, data: Dict):
        """Initialize upgrade."""
        self.id = data.get('id', 'upgrade_unknown')
        self.name = data.get('name', 'Unknown Upgrade')
        self.category = data.get('category', 'general')  # sonar, torpedo, hull, engine, etc.
        self.description = data.get('description', '')
        self.cost = data.get('cost', 1000)  # In campaign currency/points
        self.tier = data.get('tier', 1)
        self.effects = data.get('effects', {})
        self.installed = False
        self.xp_required = data.get('xp_required', 0)
    
    def apply_effect(self, target, effect_type: str):
        """Apply upgrade effect to submarine."""
        if effect_type in self.effects:
            effect_value = self.effects[effect_type]
            # Implementation depends on target system
            pass
    
    def __repr__(self):
        return f"<Upgrade {self.name} (Tier {self.tier})>"


class SubmariueUpgradeTree:
    """Manages available submarine upgrades."""
    
    UPGRADES = [
        # Sonar Upgrades
        {
            'id': 'sonar_improved_range',
            'name': 'Extended Sonar Range',
            'category': 'sonar',
            'description': 'Increases sonar detection range by 20%',
            'cost': 500,
            'tier': 1,
            'effects': {'sonar_range': 1.2},
            'xp_required': 100
        },
        {
            'id': 'sonar_silent_mode',
            'name': 'Silent Sonar Mode',
            'category': 'sonar',
            'description': 'Reduce sonar noise signature by 30%',
            'cost': 800,
            'tier': 2,
            'effects': {'sonar_signature': 0.7},
            'xp_required': 300
        },
        {
            'id': 'sonar_target_classification',
            'name': 'Target Classification',
            'category': 'sonar',
            'description': 'Sonar identifies ship type automatically',
            'cost': 1000,
            'tier': 3,
            'effects': {'sonar_detail': 1},
            'xp_required': 500
        },
        
        # Torpedo Upgrades
        {
            'id': 'torpedo_faster_reloading',
            'name': 'Quick Reload Mechanism',
            'category': 'torpedo',
            'description': 'Torpedo tube reload time -25%',
            'cost': 600,
            'tier': 1,
            'effects': {'reload_speed': 1.25},
            'xp_required': 150
        },
        {
            'id': 'torpedo_improved_guidance',
            'name': 'Enhanced Homing',
            'category': 'torpedo',
            'description': 'Torpedo homing strength +50%',
            'cost': 900,
            'tier': 2,
            'effects': {'homing_strength': 1.5},
            'xp_required': 350
        },
        {
            'id': 'torpedo_magnetic_warhead',
            'name': 'Magnetic Detonators',
            'category': 'torpedo',
            'description': 'Magnetic warheads detonate near hulls (20% damage boost)',
            'cost': 1200,
            'tier': 3,
            'effects': {'damage_bonus': 1.2},
            'xp_required': 600
        },
        
        # Hull Upgrades
        {
            'id': 'hull_reinforcement',
            'name': 'Hull Reinforcement',
            'category': 'hull',
            'description': 'Increase hull integrity by 15%',
            'cost': 700,
            'tier': 1,
            'effects': {'hull_integrity': 1.15},
            'xp_required': 200
        },
        {
            'id': 'hull_deeper_diving',
            'name': 'Deep Diving Hull',
            'category': 'hull',
            'description': 'Maximum depth increased to 300m (+50m)',
            'cost': 1100,
            'tier': 2,
            'effects': {'max_depth': 300},
            'xp_required': 400
        },
        {
            'id': 'hull_pressure_resistance',
            'name': 'Advanced Hull Material',
            'category': 'hull',
            'description': 'Pressure damage resistance +25%',
            'cost': 1500,
            'tier': 3,
            'effects': {'pressure_resistance': 1.25},
            'xp_required': 700
        },
        
        # Engine Upgrades
        {
            'id': 'engine_improved_surface_speed',
            'name': 'Tuned Diesel Engines',
            'category': 'engine',
            'description': 'Surface speed +15%',
            'cost': 500,
            'tier': 1,
            'effects': {'surface_speed': 1.15},
            'xp_required': 100
        },
        {
            'id': 'engine_battery_capacity',
            'name': 'Expanded Battery',
            'category': 'engine',
            'description': 'Battery capacity +25%',
            'cost': 800,
            'tier': 2,
            'effects': {'battery_capacity': 1.25},
            'xp_required': 300
        },
        {
            'id': 'engine_quiet_running',
            'name': 'Silent Drive System',
            'category': 'engine',
            'description': 'Submerged speed +10%, noise -20%',
            'cost': 1300,
            'tier': 3,
            'effects': {'submerged_speed': 1.1, 'noise_signature': 0.8},
            'xp_required': 550
        },
        
        # Systems Upgrades
        {
            'id': 'systems_damage_control',
            'name': 'Advanced Damage Control',
            'category': 'systems',
            'description': 'Repair speed +30%, compartment resilience +15%',
            'cost': 700,
            'tier': 1,
            'effects': {'repair_speed': 1.3, 'compartment_resilience': 1.15},
            'xp_required': 200
        },
        {
            'id': 'systems_radar',
            'name': 'Radar Installation',
            'category': 'systems',
            'description': 'Install radar for surface detection',
            'cost': 1000,
            'tier': 2,
            'effects': {'radar': 1},
            'xp_required': 400
        },
        {
            'id': 'systems_oxygen_generation',
            'name': 'Oxygen Recycler',
            'category': 'systems',
            'description': 'O2 consumption -20%, underwater endurance +25%',
            'cost': 1400,
            'tier': 3,
            'effects': {'oxygen_consumption': 0.8, 'endurance': 1.25},
            'xp_required': 650
        }
    ]
    
    def __init__(self):
        """Initialize upgrade tree."""
        self.upgrades: Dict[str, SubmariueUpgrade] = {}
        self.installed_upgrades: List[str] = []
        self._load_upgrades()
    
    def _load_upgrades(self):
        """Load all available upgrades."""
        for upgrade_data in self.UPGRADES:
            upgrade = SubmariueUpgrade(upgrade_data)
            self.upgrades[upgrade.id] = upgrade
    
    def get_upgrade(self, upgrade_id: str) -> Optional[SubmariueUpgrade]:
        """Get upgrade by ID."""
        return self.upgrades.get(upgrade_id)
    
    def get_upgrades_by_category(self, category: str) -> List[SubmariueUpgrade]:
        """Get all upgrades in category."""
        return [u for u in self.upgrades.values() if u.category == category]
    
    def get_upgrades_by_tier(self, tier: int) -> List[SubmariueUpgrade]:
        """Get all upgrades at tier."""
        return [u for u in self.upgrades.values() if u.tier == tier]
    
    def get_available_upgrades(self, player_xp: int) -> List[SubmariueUpgrade]:
        """Get upgrades available with current XP."""
        return [u for u in self.upgrades.values() 
               if u.xp_required <= player_xp and u.id not in self.installed_upgrades]
    
    def install_upgrade(self, upgrade_id: str) -> bool:
        """Install upgrade on submarine."""
        if upgrade_id in self.installed_upgrades:
            return False
        
        upgrade = self.get_upgrade(upgrade_id)
        if not upgrade:
            return False
        
        upgrade.installed = True
        self.installed_upgrades.append(upgrade_id)
        return True
    
    def get_installed(self) -> List[SubmariueUpgrade]:
        """Get all installed upgrades."""
        return [self.upgrades[uid] for uid in self.installed_upgrades]
    
    def get_upgrade_effects(self) -> Dict:
        """Get combined effects of all installed upgrades."""
        combined_effects = {}
        for upgrade in self.get_installed():
            for effect_type, effect_value in upgrade.effects.items():
                if effect_type not in combined_effects:
                    combined_effects[effect_type] = 1.0 if isinstance(effect_value, float) else 0
                
                if isinstance(effect_value, float):
                    combined_effects[effect_type] *= effect_value
                else:
                    combined_effects[effect_type] += effect_value
        
        return combined_effects
    
    def list_all(self) -> str:
        """Get formatted list of upgrades."""
        result = "Submarine Upgrades:\n\n"
        for tier in [1, 2, 3]:
            upgrades = self.get_upgrades_by_tier(tier)
            result += f"TIER {tier}:\n"
            for upgrade in upgrades:
                status = "✅ INSTALLED" if upgrade.id in self.installed_upgrades else f"⊛ {upgrade.cost} points"
                result += f"  {upgrade.name:40s} {status}\n"
                result += f"    {upgrade.description}\n\n"
        return result
