"""
Enhanced Crew Recruitment System with Captain Level Requirements.
Implements dynamic recruitment pool that improves with player reputation.
"""

import random
from typing import Dict, List, Optional, Tuple
from submarine.crew_skills import (
    SkilledCrewMember, CrewQuality, Specialization,
    get_captain_level_requirement, generate_crew_for_captain_level,
    SPECIALIZATION_DATA
)


class RecruitmentPool:
    """Dynamic recruitment pool based on captain level and port."""
    
    def __init__(self, port_name: str = "Naval Base", port_quality: int = 3):
        """Initialize recruitment pool.
        
        Args:
            port_name: Name of port/base
            port_quality: Port quality 1-5 (affects crew availability)
        """
        self.port_name = port_name
        self.port_quality = port_quality  # 1=small port, 5=major naval base
        self.available_crew: List[SkilledCrewMember] = []
        self.recruitment_cost_modifier = 1.0
    
    def refresh_pool(self, captain_level: int, reputation: int = 0):
        """Refresh available crew based on captain level and reputation.
        
        Args:
            captain_level: Player's captain level
            reputation: Player reputation (-100 to +100)
        """
        self.available_crew.clear()
        
        # Base pool size increases with port quality
        base_pool_size = 10 + (self.port_quality * 5)
        
        # Reputation affects pool size
        reputation_modifier = 1.0 + (reputation / 200.0)  # ±50% based on rep
        pool_size = int(base_pool_size * reputation_modifier)
        
        # Generate crew
        for _ in range(pool_size):
            # Determine skill focus (random or based on needs)
            skill = random.choice(SkilledCrewMember.SKILLS)
            
            # Generate crew appropriate for captain level
            crew = generate_crew_for_captain_level(captain_level, skill)
            
            # Small chance for higher quality crew at major bases
            if self.port_quality >= 4 and random.random() < 0.15:
                # Boost quality by one tier
                higher_qualities = [q for q in CrewQuality if q.value == crew.quality.value + 1]
                if higher_qualities and captain_level >= get_captain_level_requirement(higher_qualities[0]):
                    crew.quality = higher_qualities[0]
                    crew.skills = crew._initialize_skills()  # Re-roll skills
            
            self.available_crew.append(crew)
        
        # High reputation attracts specialists
        if reputation > 50 and captain_level >= 5:
            self._add_specialists(captain_level)
    
    def _add_specialists(self, captain_level: int):
        """Add specialized crew to pool for high-reputation captains."""
        num_specialists = random.randint(1, 3)
        
        for _ in range(num_specialists):
            # Pick random specialization that captain qualifies for
            available_specs = []
            for spec in Specialization:
                spec_data = SPECIALIZATION_DATA[spec]
                if captain_level >= spec_data['level_requirement']:
                    available_specs.append(spec)
            
            if not available_specs:
                continue
            
            spec = random.choice(available_specs)
            spec_data = SPECIALIZATION_DATA[spec]
            
            # Create specialized crew
            quality = spec_data['quality_requirement']
            crew = SkilledCrewMember(
                quality=quality,
                primary_skill=spec_data['primary_skill'],
                specialization=spec
            )
            
            self.available_crew.append(crew)
    
    def get_available_crew(self, quality_filter: CrewQuality = None,
                          skill_filter: str = None,
                          specialization_filter: Specialization = None) -> List[SkilledCrewMember]:
        """Get available crew with optional filters."""
        crew = self.available_crew
        
        if quality_filter:
            crew = [c for c in crew if c.quality == quality_filter]
        
        if skill_filter:
            crew = [c for c in crew if c.primary_skill == skill_filter]
        
        if specialization_filter:
            crew = [c for c in crew if c.specialization == specialization_filter]
        
        return crew
    
    def get_crew_by_quality(self) -> Dict[CrewQuality, List[SkilledCrewMember]]:
        """Get crew organized by quality tier."""
        organized = {q: [] for q in CrewQuality}
        
        for crew in self.available_crew:
            organized[crew.quality].append(crew)
        
        return organized
    
    def get_specialists(self) -> List[SkilledCrewMember]:
        """Get all specialized crew."""
        return [c for c in self.available_crew if c.specialization is not None]
    
    def recruit(self, crew: SkilledCrewMember) -> Tuple[bool, int]:
        """Recruit crew member, return success and cost.
        
        Args:
            crew: Crew to recruit
            
        Returns:
            (success, cost) tuple
        """
        if crew not in self.available_crew:
            return False, 0
        
        # Calculate cost based on quality and specialization
        base_costs = {
            CrewQuality.RECRUIT: 100,
            CrewQuality.TRAINED: 300,
            CrewQuality.EXPERIENCED: 800,
            CrewQuality.VETERAN: 2000,
            CrewQuality.ACE: 5000,
            CrewQuality.LEGENDARY: 15000
        }
        
        cost = base_costs[crew.quality]
        
        # Specialists cost more
        if crew.specialization:
            cost = int(cost * 1.5)
        
        # Apply port modifier
        cost = int(cost * self.recruitment_cost_modifier)
        
        self.available_crew.remove(crew)
        return True, cost
    
    def get_recruitment_info(self, crew: SkilledCrewMember) -> str:
        """Get formatted recruitment information."""
        base_costs = {
            CrewQuality.RECRUIT: 100,
            CrewQuality.TRAINED: 300,
            CrewQuality.EXPERIENCED: 800,
            CrewQuality.VETERAN: 2000,
            CrewQuality.ACE: 5000,
            CrewQuality.LEGENDARY: 15000
        }
        
        cost = base_costs[crew.quality]
        if crew.specialization:
            cost = int(cost * 1.5)
        cost = int(cost * self.recruitment_cost_modifier)
        
        info = f"{crew.name}\n"
        info += f"Quality: {crew.quality.name} (Lvl {crew.level})\n"
        info += f"Primary Skill: {crew.primary_skill.title()}\n"
        
        if crew.specialization:
            spec_data = SPECIALIZATION_DATA[crew.specialization]
            info += f"Specialization: {crew.specialization.value.replace('_', ' ').title()}\n"
            info += f"  {spec_data['description']}\n"
        
        info += f"\nTop Skills:\n"
        sorted_skills = sorted(crew.skills.items(), key=lambda x: x[1], reverse=True)[:3]
        for skill, value in sorted_skills:
            info += f"  {skill.title()}: {value:.0%}\n"
        
        info += f"\nRecruitment Cost: {cost} points\n"
        
        return info
    
    def get_summary(self) -> str:
        """Get pool summary."""
        summary = f"=== {self.port_name} Recruitment Pool ===\n"
        summary += f"Port Quality: {'★' * self.port_quality}\n\n"
        
        by_quality = self.get_crew_by_quality()
        
        for quality in CrewQuality:
            crew_list = by_quality[quality]
            if crew_list:
                summary += f"{quality.name}: {len(crew_list)} available\n"
                
                # Show specialists
                specialists = [c for c in crew_list if c.specialization]
                if specialists:
                    summary += f"  Specialists: {len(specialists)}\n"
        
        summary += f"\nTotal Available: {len(self.available_crew)}\n"
        
        return summary


class CrewRosterManager:
    """Manages submarine crew roster with skill-based system."""
    
    def __init__(self, submarine_id: str, max_crew: int = 50):
        """Initialize crew roster manager."""
        self.submarine_id = submarine_id
        self.max_crew = max_crew
        self.crew: List[SkilledCrewMember] = []
        self.recruitment_pool = RecruitmentPool()
    
    def add_crew(self, crew: SkilledCrewMember) -> bool:
        """Add crew member to roster."""
        if len(self.crew) >= self.max_crew:
            return False
        
        self.crew.append(crew)
        return True
    
    def remove_crew(self, crew: SkilledCrewMember) -> bool:
        """Remove crew member (death, transfer, etc)."""
        if crew in self.crew:
            self.crew.remove(crew)
            return True
        return False
    
    def get_crew_by_skill(self, skill: str, min_effectiveness: float = 0.0) -> List[SkilledCrewMember]:
        """Get crew with skill above threshold."""
        return [c for c in self.crew 
                if c.alive and c.effective_skill(skill) >= min_effectiveness]
    
    def get_best_crew_for_skill(self, skill: str) -> Optional[SkilledCrewMember]:
        """Get best crew member for a skill."""
        candidates = [c for c in self.crew if c.alive]
        if not candidates:
            return None
        
        return max(candidates, key=lambda c: c.effective_skill(skill))
    
    def get_specialists(self, specialization: Specialization = None) -> List[SkilledCrewMember]:
        """Get specialized crew, optionally filtered."""
        crew = [c for c in self.crew if c.alive and c.specialization is not None]
        
        if specialization:
            crew = [c for c in crew if c.specialization == specialization]
        
        return crew
    
    def get_crew_by_compartment(self, compartment_id: str) -> List[SkilledCrewMember]:
        """Get crew assigned to compartment."""
        return [c for c in self.crew if c.alive and c.compartment_id == compartment_id]
    
    def assign_crew_to_compartment(self, crew: SkilledCrewMember, 
                                   compartment_id: str, role: str = 'crew') -> bool:
        """Assign crew to compartment."""
        if crew not in self.crew:
            return False
        
        crew.compartment_id = compartment_id
        crew.role = role
        return True
    
    def get_roster_summary(self) -> str:
        """Get formatted roster summary."""
        summary = f"=== Crew Roster ({len(self.crew)}/{self.max_crew}) ===\n\n"
        
        # Count by quality
        by_quality = {}
        for crew in self.crew:
            if crew.alive:
                quality = crew.quality.name
                by_quality[quality] = by_quality.get(quality, 0) + 1
        
        summary += "Quality Distribution:\n"
        for quality in CrewQuality:
            count = by_quality.get(quality.name, 0)
            if count > 0:
                summary += f"  {quality.name}: {count}\n"
        
        # List specialists
        specialists = self.get_specialists()
        if specialists:
            summary += f"\nSpecialists ({len(specialists)}):\n"
            for crew in specialists:
                spec_name = crew.specialization.value.replace('_', ' ').title()
                summary += f"  {crew.name} - {spec_name} ({crew.rank})\n"
        
        # Status summary
        avg_morale = sum(c.morale for c in self.crew if c.alive) / len(self.crew) if self.crew else 0
        avg_stress = sum(c.stress for c in self.crew if c.alive) / len(self.crew) if self.crew else 0
        
        summary += f"\nCrew Status:\n"
        summary += f"  Average Morale: {avg_morale:.0%}\n"
        summary += f"  Average Stress: {avg_stress:.0%}\n"
        
        return summary
    
    def tick(self):
        """Update crew status each game tick."""
        for crew in self.crew:
            if not crew.alive:
                continue
            
            # Natural recovery when not in combat
            crew.reduce_stress(0.005)
            crew.rest(0.01)
            
            # Morale changes
            if crew.stress > 0.8:
                crew.morale = max(0.2, crew.morale - 0.01)
            elif crew.stress < 0.2:
                crew.morale = min(1.0, crew.morale + 0.005)
