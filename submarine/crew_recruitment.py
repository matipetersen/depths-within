"""
Crew Recruitment and Management System.
Handles hiring, assignment, reassignment, and crew roster management.
"""

import random
import json
import os
from typing import Dict, List, Optional, Tuple


class CrewMember:
    """Represents a single crew member with detailed stats."""
    
    def __init__(self, data: Dict = None):
        """Initialize crew member from data dict or create new."""
        if data:
            self.id = data.get('id', random.randint(1000, 9999))
            self.name = data.get('name', 'Unknown')
            self.rank = data.get('rank', 'Seaman')
            self.primary_skill = data.get('primary_skill', 'general')
            self.secondary_skills = data.get('secondary_skills', [])
        else:
            self.id = random.randint(10000, 99999)
            self.name = self._generate_name()
            self.rank = 'Seaman'
            self.primary_skill = random.choice(['sonar', 'torpedo', 'navigation', 'engineering', 'damage_control'])
            self.secondary_skills = random.sample(['general', 'leadership', 'repair'], 2)
        
        # Experience
        self.xp = data.get('xp', {}) if data else {}
        self.level = data.get('level', 1) if data else 1
        
        # Status
        self.stress = data.get('stress', 0.0) if data else 0.0
        self.morale = data.get('morale', 0.8) if data else 0.8
        self.fatigue = data.get('fatigue', 0.0) if data else 0.0
        self.health = data.get('health', 1.0) if data else 1.0
        
        # Personality (affects behavior)
        self.personality = data.get('personality', self._generate_personality()) if data else self._generate_personality()
        
        # Assignment
        self.compartment_id = data.get('compartment_id', None) if data else None
        self.role = data.get('role', 'unassigned') if data else 'unassigned'
        
        # Combat history
        self.kills = data.get('kills', 0) if data else 0
        self.missions = data.get('missions', 0) if data else 0
        self.damaged_ships_tonnage = data.get('damaged_ships_tonnage', 0) if data else 0
    
    def _generate_name(self) -> str:
        """Generate random German/period-appropriate submarine crew name."""
        first_names = ['Klaus', 'Friedrich', 'Helmut', 'Werner', 'Otto', 'Hans', 'Wolfgang', 
                      'Ernst', 'Rudolf', 'Günther', 'Karl', 'Adolf', 'Wilhelm', 'Georg']
        last_names = ['Schmidt', 'Mueller', 'Schneider', 'Fischer', 'Weber', 'Meyer', 'Wagner',
                     'Becker', 'Schulz', 'Hoffmann', 'Richter', 'Keller', 'Neumann']
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_personality(self) -> str:
        """Generate personality trait affecting stress/morale."""
        return random.choice(['brave', 'cautious', 'calm', 'aggressive', 'disciplined', 'curious'])
    
    def effective_skill(self, skill: str) -> float:
        """Get effective skill level (0-1.0) factoring stress, morale, fatigue."""
        base = 0.5  # Base 50% competency
        
        if skill == self.primary_skill:
            base += 0.3
        elif skill in self.secondary_skills:
            base += 0.15
        
        # Add XP bonus
        base += self.xp.get(skill, 0) * 0.01  # Each XP point = 1% bonus
        
        # Apply modifiers
        stress_penalty = self.stress * 0.3  # Stress reduces by up to 30%
        morale_bonus = (self.morale - 0.5) * 0.2  # Morale effect
        fatigue_penalty = self.fatigue * 0.2  # Fatigue reduces by up to 20%
        
        effective = base + morale_bonus - stress_penalty - fatigue_penalty
        return max(0.1, min(1.0, effective))
    
    def gain_xp(self, skill: str, amount: int = 10):
        """Gain experience in a skill."""
        if skill not in self.xp:
            self.xp[skill] = 0
        self.xp[skill] += amount
        
        # Check for level up
        total_xp = sum(self.xp.values())
        new_level = 1 + (total_xp // 100)
        if new_level > self.level:
            self.level = new_level
            self.morale = min(1.0, self.morale + 0.1)
    
    def apply_stress(self, amount: float):
        """Add stress to crew member (0-1 scale)."""
        self.stress = min(1.0, self.stress + amount)
    
    def relieve_stress(self, amount: float = 0.1):
        """Reduce stress through rest/activity."""
        self.stress = max(0.0, self.stress - amount)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'rank': self.rank,
            'primary_skill': self.primary_skill,
            'secondary_skills': self.secondary_skills,
            'xp': self.xp,
            'level': self.level,
            'stress': self.stress,
            'morale': self.morale,
            'fatigue': self.fatigue,
            'health': self.health,
            'personality': self.personality,
            'compartment_id': self.compartment_id,
            'role': self.role,
            'kills': self.kills,
            'missions': self.missions,
            'damaged_ships_tonnage': self.damaged_ships_tonnage
        }
    
    def __repr__(self):
        return f"<CrewMember {self.name} ({self.rank}, Lvl {self.level})>"


class CrewRecruitmentPool:
    """Manages available crew for recruitment."""
    
    def __init__(self, size: int = 50):
        """Initialize recruitment pool with available crew."""
        self.pool: List[CrewMember] = []
        self.morale_multiplier = 1.0
        self._populate_pool(size)
    
    def _populate_pool(self, size: int):
        """Generate initial pool of recruits."""
        self.pool = [CrewMember() for _ in range(size)]
    
    def recruit(self, crew: CrewMember) -> bool:
        """Recruit a crew member from pool."""
        if crew in self.pool:
            self.pool.remove(crew)
            return True
        return False
    
    def get_available(self, skill: Optional[str] = None) -> List[CrewMember]:
        """Get available crew, optionally filtered by primary skill."""
        if skill:
            return [c for c in self.pool if c.primary_skill == skill]
        return list(self.pool)
    
    def get_random(self, skill: Optional[str] = None) -> Optional[CrewMember]:
        """Get random available crew member."""
        available = self.get_available(skill)
        return random.choice(available) if available else None
    
    def add_recruits(self, count: int = 5):
        """Add new recruits to the pool (port activity)."""
        for _ in range(count):
            self.pool.append(CrewMember())
    
    def remove_available(self, count: int):
        """Remove crew from available pool (attrition/reassignment)."""
        for _ in range(min(count, len(self.pool))):
            self.pool.pop()


class CrewRoster:
    """Manages submarine crew roster and assignments."""
    
    def __init__(self, submarine_id: str, max_crew: int = 50):
        """Initialize crew roster."""
        self.submarine_id = submarine_id
        self.crew: List[CrewMember] = []
        self.max_crew = max_crew
        self.recruitment_pool = CrewRecruitmentPool()
        self.unassigned_crew: List[CrewMember] = []
    
    def recruit_crew(self, crew: CrewMember) -> bool:
        """Recruit a crew member from the pool."""
        if len(self.crew) >= self.max_crew:
            return False
        
        if self.recruitment_pool.recruit(crew):
            self.crew.append(crew)
            self.unassigned_crew.append(crew)
            return True
        
        return False
    
    def recruit_random(self, skill: Optional[str] = None) -> Optional[CrewMember]:
        """Recruit random crew member with optional skill filter."""
        crew = self.recruitment_pool.get_random(skill)
        if crew and self.recruit_crew(crew):
            return crew
        return None
    
    def assign_crew(self, crew: CrewMember, compartment_id: str, role: str = 'crew') -> bool:
        """Assign crew to compartment."""
        if crew not in self.crew:
            return False
        
        crew.compartment_id = compartment_id
        crew.role = role
        
        if crew in self.unassigned_crew:
            self.unassigned_crew.remove(crew)
        
        return True
    
    def reassign_crew(self, crew: CrewMember, new_compartment: str, new_role: str = 'crew') -> bool:
        """Reassign crew to different compartment."""
        if crew not in self.crew:
            return False
        
        crew.compartment_id = new_compartment
        crew.role = new_role
        return True
    
    def remove_crew(self, crew: CrewMember) -> bool:
        """Remove crew (KIA/transfer/etc)."""
        if crew in self.crew:
            self.crew.remove(crew)
            if crew in self.unassigned_crew:
                self.unassigned_crew.remove(crew)
            return True
        return False
    
    def get_crew_by_compartment(self, compartment_id: str) -> List[CrewMember]:
        """Get all crew assigned to compartment."""
        return [c for c in self.crew if c.compartment_id == compartment_id]
    
    def get_crew_by_skill(self, skill: str) -> List[CrewMember]:
        """Get all crew with skill."""
        return [c for c in self.crew 
               if c.primary_skill == skill or skill in c.secondary_skills]
    
    def get_best_crew_for_skill(self, skill: str) -> Optional[CrewMember]:
        """Get best crew member for a skill (highest effective skill)."""
        candidates = self.get_crew_by_skill(skill)
        if not candidates:
            return None
        return max(candidates, key=lambda c: c.effective_skill(skill))
    
    def get_all_crew(self) -> List[CrewMember]:
        """Get all crew members."""
        return list(self.crew)
    
    def get_crew_by_id(self, crew_id: int) -> Optional[CrewMember]:
        """Get crew member by ID."""
        for crew in self.crew:
            if crew.id == crew_id:
                return crew
        return None
    
    def get_unassigned(self) -> List[CrewMember]:
        """Get unassigned crew."""
        return list(self.unassigned_crew)
    
    def get_status_summary(self) -> Dict:
        """Get crew roster status."""
        return {
            'total': len(self.crew),
            'capacity': self.max_crew,
            'unassigned': len(self.unassigned_crew),
            'avg_level': sum(c.level for c in self.crew) / len(self.crew) if self.crew else 0,
            'avg_morale': sum(c.morale for c in self.crew) / len(self.crew) if self.crew else 0,
            'avg_stress': sum(c.stress for c in self.crew) / len(self.crew) if self.crew else 0,
            'pool_available': len(self.recruitment_pool.pool)
        }
    
    def tick(self):
        """Crew status changes per game tick."""
        for crew in self.crew:
            # Natural stress reduction while resting
            if crew.compartment_id:
                crew.relieve_stress(0.01)
            
            # Fatigue accumulation
            crew.fatigue = min(1.0, crew.fatigue + 0.01)
            
            # Morale changes based on stress
            if crew.stress > 0.7:
                crew.morale = max(0.2, crew.morale - 0.02)
            elif crew.stress < 0.3:
                crew.morale = min(1.0, crew.morale + 0.01)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'submarine_id': self.submarine_id,
            'crew': [c.to_dict() for c in self.crew],
            'unassigned_crew': [c.to_dict() for c in self.unassigned_crew],
            'max_crew': self.max_crew
        }
