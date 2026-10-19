"""
Advanced Crew Skills and Specialization System.
Implements skill-based crew with experience, specializations, and quality tiers.
"""

import random
from enum import Enum
from typing import Dict, List, Optional, Tuple


class CrewQuality(Enum):
    """Crew quality tier - determines base stats and captain level requirement."""
    RECRUIT = 1      # Level 1+, basic skills (40-60%)
    TRAINED = 2      # Level 3+, trained skills (60-75%)
    EXPERIENCED = 3  # Level 5+, experienced skills (75-85%)
    VETERAN = 4      # Level 8+, veteran skills (85-95%)
    ACE = 5          # Level 12+, elite skills (95-100%)
    LEGENDARY = 6    # Level 15+, legendary (100%+)


class Specialization(Enum):
    """Crew specializations with unique bonuses."""
    # Engineering specializations
    CHIEF_ENGINEER = 'chief_engineer'         # Master of all repairs
    ELECTRICAL_ENGINEER = 'electrical_engineer'  # Battery, systems
    MECHANICAL_ENGINEER = 'mechanical_engineer'  # Engines, propulsion
    HULL_SPECIALIST = 'hull_specialist'       # Hull integrity, diving
    DAMAGE_CONTROLLER = 'damage_controller'   # Emergency repairs, flooding
    
    # Weapons specializations
    TORPEDO_SPECIALIST = 'torpedo_specialist'  # Torpedo accuracy, maintenance
    WEAPONS_OFFICER = 'weapons_officer'        # All weapons coordination
    FIRE_CONTROL = 'fire_control'              # Targeting solutions
    MINE_EXPERT = 'mine_expert'                # Mine detection, deployment
    
    # Sensors specializations
    SONAR_OPERATOR = 'sonar_operator'          # Sonar detection, analysis
    RADAR_OPERATOR = 'radar_operator'          # Radar operation
    PERISCOPE_OFFICER = 'periscope_officer'    # Visual identification
    SIGNALS_INTELLIGENCE = 'signals_intelligence'  # Radio intercept
    
    # Navigation specializations
    NAVIGATOR = 'navigator'                    # Route planning, positioning
    HELMSMAN = 'helmsman'                      # Ship handling, evasion
    QUARTERMASTER = 'quartermaster'            # Resource management
    
    # Command specializations
    EXECUTIVE_OFFICER = 'executive_officer'    # Second in command
    MORALE_OFFICER = 'morale_officer'          # Crew morale, stress
    MEDICAL_OFFICER = 'medical_officer'        # Crew health, injuries
    COMMUNICATIONS = 'communications'          # Radio, signals


# Specialization bonuses and requirements
SPECIALIZATION_DATA = {
    # Engineering specializations
    Specialization.CHIEF_ENGINEER: {
        'primary_skill': 'engineering',
        'bonuses': {'repair_speed': 0.5, 'all_engineering': 0.3},
        'level_requirement': 8,
        'quality_requirement': CrewQuality.VETERAN,
        'description': 'Master engineer, 50% faster repairs, 30% bonus to all engineering tasks'
    },
    Specialization.ELECTRICAL_ENGINEER: {
        'primary_skill': 'engineering',
        'bonuses': {'battery_efficiency': 0.4, 'systems_repair': 0.4},
        'level_requirement': 5,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Electrical systems expert, 40% better battery efficiency and systems repair'
    },
    Specialization.MECHANICAL_ENGINEER: {
        'primary_skill': 'engineering',
        'bonuses': {'engine_repair': 0.5, 'propulsion_efficiency': 0.3},
        'level_requirement': 5,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Mechanical expert, 50% faster engine repairs, 30% propulsion efficiency'
    },
    Specialization.HULL_SPECIALIST: {
        'primary_skill': 'engineering',
        'bonuses': {'hull_repair': 0.6, 'depth_tolerance': 0.2},
        'level_requirement': 6,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Hull expert, 60% faster hull repairs, 20% deeper diving'
    },
    Specialization.DAMAGE_CONTROLLER: {
        'primary_skill': 'engineering',
        'bonuses': {'emergency_repair': 0.7, 'flooding_control': 0.5},
        'level_requirement': 7,
        'quality_requirement': CrewQuality.VETERAN,
        'description': 'Emergency specialist, 70% faster emergency repairs, 50% better flooding control'
    },
    
    # Weapons specializations
    Specialization.TORPEDO_SPECIALIST: {
        'primary_skill': 'torpedoes',
        'bonuses': {'torpedo_accuracy': 0.3, 'reload_speed': 0.4},
        'level_requirement': 6,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Torpedo expert, 30% better accuracy, 40% faster reload'
    },
    Specialization.WEAPONS_OFFICER: {
        'primary_skill': 'torpedoes',
        'bonuses': {'all_weapons': 0.3, 'critical_hit': 0.15},
        'level_requirement': 8,
        'quality_requirement': CrewQuality.VETERAN,
        'description': 'Weapons master, 30% bonus to all weapons, 15% critical hit chance'
    },
    Specialization.FIRE_CONTROL: {
        'primary_skill': 'torpedoes',
        'bonuses': {'targeting_speed': 0.5, 'solution_quality': 0.3},
        'level_requirement': 5,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Targeting expert, 50% faster solutions, 30% better accuracy'
    },
    Specialization.MINE_EXPERT: {
        'primary_skill': 'torpedoes',
        'bonuses': {'mine_detection': 0.5, 'mine_avoidance': 0.4},
        'level_requirement': 4,
        'quality_requirement': CrewQuality.TRAINED,
        'description': 'Mine specialist, 50% better detection, 40% avoidance'
    },
    
    # Sensors specializations
    Specialization.SONAR_OPERATOR: {
        'primary_skill': 'sonar',
        'bonuses': {'sonar_range': 0.4, 'contact_identification': 0.5},
        'level_requirement': 6,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Sonar expert, 40% better range, 50% faster identification'
    },
    Specialization.RADAR_OPERATOR: {
        'primary_skill': 'sonar',
        'bonuses': {'radar_range': 0.3, 'aircraft_detection': 0.5},
        'level_requirement': 4,
        'quality_requirement': CrewQuality.TRAINED,
        'description': 'Radar expert, 30% better range, 50% aircraft detection'
    },
    Specialization.PERISCOPE_OFFICER: {
        'primary_skill': 'navigation',
        'bonuses': {'visual_range': 0.3, 'ship_identification': 0.4},
        'level_requirement': 5,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Periscope expert, 30% visual range, 40% ship ID accuracy'
    },
    Specialization.SIGNALS_INTELLIGENCE: {
        'primary_skill': 'sonar',
        'bonuses': {'radio_intercept': 0.6, 'enemy_prediction': 0.3},
        'level_requirement': 7,
        'quality_requirement': CrewQuality.VETERAN,
        'description': 'Signals expert, 60% radio intercept, 30% enemy prediction'
    },
    
    # Navigation specializations
    Specialization.NAVIGATOR: {
        'primary_skill': 'navigation',
        'bonuses': {'route_efficiency': 0.3, 'fuel_economy': 0.2},
        'level_requirement': 5,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Navigation expert, 30% route efficiency, 20% fuel economy'
    },
    Specialization.HELMSMAN: {
        'primary_skill': 'navigation',
        'bonuses': {'evasion': 0.4, 'maneuverability': 0.3},
        'level_requirement': 6,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Expert helmsman, 40% evasion, 30% maneuverability'
    },
    Specialization.QUARTERMASTER: {
        'primary_skill': 'navigation',
        'bonuses': {'supply_efficiency': 0.4, 'oxygen_management': 0.3},
        'level_requirement': 4,
        'quality_requirement': CrewQuality.TRAINED,
        'description': 'Supply expert, 40% supply efficiency, 30% oxygen management'
    },
    
    # Command specializations
    Specialization.EXECUTIVE_OFFICER: {
        'primary_skill': 'leadership',
        'bonuses': {'crew_efficiency': 0.3, 'command_effectiveness': 0.4},
        'level_requirement': 10,
        'quality_requirement': CrewQuality.VETERAN,
        'description': 'Second in command, 30% crew efficiency, 40% command effectiveness'
    },
    Specialization.MORALE_OFFICER: {
        'primary_skill': 'leadership',
        'bonuses': {'morale_boost': 0.5, 'stress_reduction': 0.4},
        'level_requirement': 5,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Morale expert, 50% morale boost, 40% stress reduction'
    },
    Specialization.MEDICAL_OFFICER: {
        'primary_skill': 'medical',
        'bonuses': {'healing_speed': 0.6, 'injury_prevention': 0.3},
        'level_requirement': 6,
        'quality_requirement': CrewQuality.EXPERIENCED,
        'description': 'Medical expert, 60% faster healing, 30% injury prevention'
    },
    Specialization.COMMUNICATIONS: {
        'primary_skill': 'navigation',
        'bonuses': {'signal_clarity': 0.4, 'code_breaking': 0.3},
        'level_requirement': 4,
        'quality_requirement': CrewQuality.TRAINED,
        'description': 'Communications expert, 40% signal clarity, 30% code breaking'
    }
}


class SkilledCrewMember:
    """Enhanced crew member with specialization and quality tier."""
    
    # Skill categories
    SKILLS = [
        'engineering',      # Repairs, maintenance
        'torpedoes',        # Weapons operation
        'sonar',            # Detection, sensors
        'navigation',       # Ship handling, positioning
        'leadership',       # Command, morale
        'medical',          # Health, injuries
        'damage_control',   # Emergency repairs
        'general'           # Basic duties
    ]
    
    # Names by nationality (expand as needed)
    GERMAN_FIRST_NAMES = ['Klaus', 'Friedrich', 'Helmut', 'Werner', 'Otto', 'Hans', 
                          'Wolfgang', 'Ernst', 'Rudolf', 'Günther', 'Karl', 'Wilhelm']
    GERMAN_LAST_NAMES = ['Schmidt', 'Mueller', 'Schneider', 'Fischer', 'Weber', 'Meyer',
                         'Wagner', 'Becker', 'Schulz', 'Hoffmann', 'Richter', 'Keller']
    
    # Rank progression
    RANKS = ['Recruit', 'Seaman', 'Petty Officer', 'Chief', 'Lieutenant', 'Commander', 'Captain']
    
    def __init__(self, name: str = None, quality: CrewQuality = CrewQuality.RECRUIT,
                 primary_skill: str = None, specialization: Specialization = None):
        """Initialize skilled crew member."""
        # Identity
        self.id = random.randint(100000, 999999)
        self.name = name or self._generate_name()
        self.quality = quality
        
        # Skills
        self.primary_skill = primary_skill or random.choice(self.SKILLS)
        self.specialization = specialization
        self.skills = self._initialize_skills()
        
        # Experience
        self.level = 1
        self.xp = {skill: 0 for skill in self.SKILLS}
        self.total_xp = 0
        
        # Status
        self.stress = 0.0
        self.morale = 0.8
        self.fatigue = 0.0
        self.health = 1.0
        self.alive = True
        
        # Assignment
        self.compartment_id = None
        self.role = 'unassigned'
        
        # Career
        self.missions_completed = 0
        self.repairs_performed = 0
        self.ships_hit = 0
        self.contacts_detected = 0
        
        # Personality
        self.personality = random.choice(['brave', 'cautious', 'calm', 'methodical', 
                                         'quick', 'aggressive', 'disciplined'])
        
        # Rank based on level
        self.rank = self._get_rank_for_level()
    
    def _generate_name(self) -> str:
        """Generate crew name."""
        first = random.choice(self.GERMAN_FIRST_NAMES)
        last = random.choice(self.GERMAN_LAST_NAMES)
        return f"{first} {last}"
    
    def _initialize_skills(self) -> Dict[str, float]:
        """Initialize skills based on quality tier."""
        skills = {}
        
        # Base skill levels by quality
        quality_bases = {
            CrewQuality.RECRUIT: (0.40, 0.60),      # 40-60%
            CrewQuality.TRAINED: (0.60, 0.75),      # 60-75%
            CrewQuality.EXPERIENCED: (0.75, 0.85),  # 75-85%
            CrewQuality.VETERAN: (0.85, 0.95),      # 85-95%
            CrewQuality.ACE: (0.95, 1.00),          # 95-100%
            CrewQuality.LEGENDARY: (1.00, 1.20)     # 100-120% (superhuman)
        }
        
        min_skill, max_skill = quality_bases[self.quality]
        
        for skill in self.SKILLS:
            if skill == self.primary_skill:
                # Primary skill is higher
                skills[skill] = random.uniform(max_skill - 0.05, max_skill)
            elif self.specialization and skill == SPECIALIZATION_DATA[self.specialization]['primary_skill']:
                # Specialization skill bonus
                skills[skill] = random.uniform(max_skill - 0.10, max_skill - 0.05)
            else:
                # Other skills
                skills[skill] = random.uniform(min_skill, (min_skill + max_skill) / 2)
        
        return skills
    
    def _get_rank_for_level(self) -> str:
        """Get rank based on level."""
        if self.level >= 15:
            return self.RANKS[6]  # Captain
        elif self.level >= 12:
            return self.RANKS[5]  # Commander
        elif self.level >= 8:
            return self.RANKS[4]  # Lieutenant
        elif self.level >= 5:
            return self.RANKS[3]  # Chief
        elif self.level >= 3:
            return self.RANKS[2]  # Petty Officer
        elif self.level >= 2:
            return self.RANKS[1]  # Seaman
        else:
            return self.RANKS[0]  # Recruit
    
    def effective_skill(self, skill: str) -> float:
        """Calculate effective skill with all modifiers."""
        if skill not in self.skills:
            return 0.0
        
        base = self.skills[skill]
        
        # Experience bonus (XP in this skill)
        xp_bonus = min(0.2, self.xp[skill] * 0.0001)  # Up to 20% from XP
        
        # Specialization bonus
        spec_bonus = 0.0
        if self.specialization:
            spec_data = SPECIALIZATION_DATA[self.specialization]
            if skill == spec_data['primary_skill']:
                # Check specific bonuses
                for bonus_type, bonus_value in spec_data['bonuses'].items():
                    if bonus_type == f'{skill}_bonus' or bonus_type == 'all_engineering':
                        spec_bonus += bonus_value * 0.3  # Convert to skill modifier
        
        # Status modifiers
        stress_penalty = self.stress * 0.4  # Up to 40% penalty
        morale_modifier = (self.morale - 0.5) * 0.2  # ±10%
        fatigue_penalty = self.fatigue * 0.3  # Up to 30% penalty
        health_modifier = self.health * 0.1  # Up to 10%
        
        # Personality bonuses
        personality_bonus = 0.0
        if self.personality == 'methodical' and skill in ['engineering', 'damage_control']:
            personality_bonus = 0.05
        elif self.personality == 'brave' and skill == 'torpedoes':
            personality_bonus = 0.05
        elif self.personality == 'quick' and skill == 'navigation':
            personality_bonus = 0.05
        
        effective = (base + xp_bonus + spec_bonus + personality_bonus + 
                    morale_modifier + health_modifier - stress_penalty - fatigue_penalty)
        
        return max(0.0, min(2.0, effective))  # Cap at 200%
    
    def gain_xp(self, skill: str, amount: int = 10):
        """Gain experience in a skill."""
        if skill not in self.xp:
            self.xp[skill] = 0
        
        self.xp[skill] += amount
        self.total_xp += amount
        
        # Improve base skill slowly with XP
        if skill in self.skills:
            improvement = amount * 0.0001  # 1000 XP = 0.1 skill increase
            self.skills[skill] = min(1.5, self.skills[skill] + improvement)
        
        # Check for level up
        new_level = 1 + (self.total_xp // 500)  # Level up every 500 XP
        if new_level > self.level:
            self.level = new_level
            self.rank = self._get_rank_for_level()
            self.morale = min(1.0, self.morale + 0.1)  # Morale boost on level up
    
    def can_specialize(self, spec: Specialization) -> bool:
        """Check if crew can gain specialization."""
        if self.specialization is not None:
            return False  # Already specialized
        
        spec_data = SPECIALIZATION_DATA[spec]
        
        # Check level requirement
        if self.level < spec_data['level_requirement']:
            return False
        
        # Check quality requirement
        if self.quality.value < spec_data['quality_requirement'].value:
            return False
        
        # Check primary skill
        primary_skill = spec_data['primary_skill']
        if self.skills.get(primary_skill, 0) < 0.7:
            return False
        
        return True
    
    def specialize(self, spec: Specialization) -> bool:
        """Gain specialization."""
        if not self.can_specialize(spec):
            return False
        
        self.specialization = spec
        
        # Boost primary skill
        spec_data = SPECIALIZATION_DATA[spec]
        primary_skill = spec_data['primary_skill']
        if primary_skill in self.skills:
            self.skills[primary_skill] = min(1.5, self.skills[primary_skill] + 0.2)
        
        return True
    
    def get_specialization_bonuses(self) -> Dict[str, float]:
        """Get all specialization bonuses."""
        if not self.specialization:
            return {}
        
        return SPECIALIZATION_DATA[self.specialization]['bonuses'].copy()
    
    def apply_stress(self, amount: float):
        """Apply stress to crew member."""
        self.stress = min(1.0, self.stress + amount)
        
        # High stress damages morale
        if self.stress > 0.8:
            self.morale = max(0.2, self.morale - 0.02)
    
    def reduce_stress(self, amount: float):
        """Reduce stress through rest."""
        self.stress = max(0.0, self.stress - amount)
        
        # Low stress improves morale
        if self.stress < 0.3:
            self.morale = min(1.0, self.morale + 0.01)
    
    def apply_fatigue(self, amount: float):
        """Apply fatigue."""
        self.fatigue = min(1.0, self.fatigue + amount)
    
    def rest(self, amount: float = 0.2):
        """Rest to reduce fatigue and stress."""
        self.fatigue = max(0.0, self.fatigue - amount)
        self.reduce_stress(amount * 0.5)
    
    def take_damage(self, amount: float):
        """Take health damage."""
        self.health = max(0.0, self.health - amount)
        if self.health <= 0.0:
            self.alive = False
    
    def heal(self, amount: float):
        """Heal health damage."""
        self.health = min(1.0, self.health + amount)
    
    def get_description(self) -> str:
        """Get detailed crew description."""
        desc = f"{self.name} ({self.rank})\n"
        desc += f"Quality: {self.quality.name}\n"
        desc += f"Level {self.level} - {self.total_xp} XP\n"
        desc += f"Primary: {self.primary_skill.title()}\n"
        
        if self.specialization:
            spec_data = SPECIALIZATION_DATA[self.specialization]
            desc += f"Specialization: {self.specialization.value.replace('_', ' ').title()}\n"
            desc += f"  {spec_data['description']}\n"
        
        desc += f"\nStatus:\n"
        desc += f"  Health: {self.health:.0%}  Morale: {self.morale:.0%}\n"
        desc += f"  Stress: {self.stress:.0%}  Fatigue: {self.fatigue:.0%}\n"
        
        desc += f"\nTop Skills:\n"
        sorted_skills = sorted(self.skills.items(), key=lambda x: x[1], reverse=True)[:3]
        for skill, value in sorted_skills:
            effective = self.effective_skill(skill)
            desc += f"  {skill.title()}: {value:.0%} (Effective: {effective:.0%})\n"
        
        return desc
    
    def __repr__(self):
        spec_str = f", {self.specialization.value}" if self.specialization else ""
        return f"<{self.quality.name} {self.rank} {self.name} Lvl{self.level}{spec_str}>"


def get_captain_level_requirement(quality: CrewQuality) -> int:
    """Get minimum captain level to recruit this quality crew."""
    requirements = {
        CrewQuality.RECRUIT: 1,
        CrewQuality.TRAINED: 3,
        CrewQuality.EXPERIENCED: 5,
        CrewQuality.VETERAN: 8,
        CrewQuality.ACE: 12,
        CrewQuality.LEGENDARY: 15
    }
    return requirements[quality]


def generate_crew_for_captain_level(captain_level: int, primary_skill: str = None) -> SkilledCrewMember:
    """Generate crew appropriate for captain's level/reputation."""
    # Determine available quality tiers
    available_qualities = []
    for quality in CrewQuality:
        if captain_level >= get_captain_level_requirement(quality):
            available_qualities.append(quality)
    
    # Weight towards higher quality as captain level increases
    weights = []
    for quality in available_qualities:
        # Higher quality more likely with higher captain level
        weight = 1.0 + (quality.value * 0.3 * (captain_level / 15.0))
        weights.append(weight)
    
    # Select quality
    quality = random.choices(available_qualities, weights=weights)[0]
    
    # Generate crew
    return SkilledCrewMember(quality=quality, primary_skill=primary_skill)
