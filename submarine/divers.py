"""
Diver Operations System.
Implements combat divers for reconnaissance, sabotage, and special operations.
"""

import random
from enum import Enum
from typing import Dict, List, Optional, Tuple


class DiverSpecialty(Enum):
    """Diver specialization types."""
    RECONNAISSANCE = 'reconnaissance'    # Scout enemy positions, gather intel
    SABOTAGE = 'sabotage'               # Place limpet mines, cut nets
    RESCUE = 'rescue'                   # Recover downed pilots, crew
    INFILTRATION = 'infiltration'       # Harbor penetration, facility entry
    DEMOLITION = 'demolition'           # Underwater demolition, obstacles
    COMBAT = 'combat'                   # Underwater combat specialist


class DiverMissionType(Enum):
    """Types of diver missions."""
    HARBOR_RECON = 'harbor_recon'              # Scout harbor defenses
    SHIP_SABOTAGE = 'ship_sabotage'            # Plant limpet mines on ships
    NET_CUTTING = 'net_cutting'                # Cut anti-submarine nets
    BEACH_RECON = 'beach_recon'                # Coastal reconnaissance
    PILOT_RESCUE = 'pilot_rescue'              # Recover downed aircrew
    MINE_PLACEMENT = 'mine_placement'          # Place mines in shipping lanes
    FACILITY_INFILTRATION = 'facility_infiltration'  # Shore facility entry
    WRECK_SALVAGE = 'wreck_salvage'            # Salvage from sunken ships
    CABLE_CUTTING = 'cable_cutting'            # Cut underwater cables
    OBSTACLE_CLEARING = 'obstacle_clearing'    # Clear underwater obstacles


class DiverMissionStatus(Enum):
    """Mission status."""
    PREPARING = 'preparing'
    DEPLOYED = 'deployed'
    IN_PROGRESS = 'in_progress'
    RETURNING = 'returning'
    COMPLETED = 'completed'
    FAILED = 'failed'
    ABORTED = 'aborted'


class Diver:
    """Combat diver with skills and equipment."""
    
    def __init__(self, name: str = None, specialty: DiverSpecialty = None):
        """Initialize diver."""
        # Identity
        self.id = random.randint(100000, 999999)
        self.name = name or self._generate_name()
        self.specialty = specialty or random.choice(list(DiverSpecialty))
        
        # Skills (0.0-1.0)
        self.skills = {
            'swimming': random.uniform(0.7, 0.95),
            'stealth': random.uniform(0.6, 0.9),
            'demolition': random.uniform(0.5, 0.9),
            'combat': random.uniform(0.5, 0.85),
            'navigation': random.uniform(0.6, 0.9),
            'endurance': random.uniform(0.7, 0.95),
        }
        
        # Boost specialty skill
        specialty_skill_map = {
            DiverSpecialty.RECONNAISSANCE: 'stealth',
            DiverSpecialty.SABOTAGE: 'demolition',
            DiverSpecialty.RESCUE: 'swimming',
            DiverSpecialty.INFILTRATION: 'stealth',
            DiverSpecialty.DEMOLITION: 'demolition',
            DiverSpecialty.COMBAT: 'combat',
        }
        if self.specialty in specialty_skill_map:
            boost_skill = specialty_skill_map[self.specialty]
            self.skills[boost_skill] = min(1.0, self.skills[boost_skill] + 0.15)
        
        # Status
        self.health = 1.0
        self.fatigue = 0.0
        self.stress = 0.0
        self.alive = True
        self.available = True
        
        # Experience
        self.missions_completed = 0
        self.successful_sabotages = 0
        self.intelligence_gathered = 0
        
        # Equipment
        self.equipment = {
            'diving_suit': True,
            'rebreather': True,
            'limpet_mines': 2,
            'knife': True,
            'compass': True,
            'torch': True,
        }
    
    def _generate_name(self) -> str:
        """Generate diver name."""
        first_names = ['Hans', 'Friedrich', 'Klaus', 'Werner', 'Otto', 
                      'Helmut', 'Karl', 'Wilhelm', 'Ernst', 'Rudolf']
        last_names = ['Schmidt', 'Mueller', 'Weber', 'Fischer', 'Becker',
                     'Schneider', 'Wagner', 'Hoffmann', 'Schulz', 'Koch']
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def get_effectiveness(self, mission_type: DiverMissionType) -> float:
        """Calculate effectiveness for mission type."""
        # Base effectiveness from relevant skills
        base = 0.5
        
        if mission_type in [DiverMissionType.HARBOR_RECON, DiverMissionType.BEACH_RECON]:
            base = (self.skills['stealth'] + self.skills['navigation']) / 2
        elif mission_type in [DiverMissionType.SHIP_SABOTAGE, DiverMissionType.MINE_PLACEMENT]:
            base = (self.skills['demolition'] + self.skills['stealth']) / 2
        elif mission_type == DiverMissionType.NET_CUTTING:
            base = (self.skills['swimming'] + self.skills['endurance']) / 2
        elif mission_type in [DiverMissionType.PILOT_RESCUE, DiverMissionType.WRECK_SALVAGE]:
            base = (self.skills['swimming'] + self.skills['endurance']) / 2
        elif mission_type == DiverMissionType.FACILITY_INFILTRATION:
            base = (self.skills['stealth'] + self.skills['combat']) / 2
        
        # Specialty bonus
        specialty_bonus = 0.0
        if self.specialty == DiverSpecialty.RECONNAISSANCE and 'RECON' in mission_type.value.upper():
            specialty_bonus = 0.2
        elif self.specialty == DiverSpecialty.SABOTAGE and 'SABOTAGE' in mission_type.value.upper():
            specialty_bonus = 0.2
        elif self.specialty == DiverSpecialty.RESCUE and 'RESCUE' in mission_type.value.upper():
            specialty_bonus = 0.2
        elif self.specialty == DiverSpecialty.INFILTRATION and 'INFILTRATION' in mission_type.value.upper():
            specialty_bonus = 0.2
        elif self.specialty == DiverSpecialty.DEMOLITION and 'MINE' in mission_type.value.upper():
            specialty_bonus = 0.2
        
        # Status modifiers
        health_modifier = self.health
        fatigue_penalty = self.fatigue * 0.3
        stress_penalty = self.stress * 0.2
        
        effectiveness = (base + specialty_bonus) * health_modifier - fatigue_penalty - stress_penalty
        
        return max(0.1, min(1.0, effectiveness))
    
    def apply_fatigue(self, amount: float):
        """Apply fatigue to diver."""
        self.fatigue = min(1.0, self.fatigue + amount)
    
    def rest(self, amount: float = 0.2):
        """Rest to reduce fatigue."""
        self.fatigue = max(0.0, self.fatigue - amount)
        self.stress = max(0.0, self.stress - amount * 0.5)
    
    def __repr__(self):
        return f"<Diver {self.name} ({self.specialty.value})>"


class DiverMission:
    """Represents a diver mission."""
    
    def __init__(self, mission_type: DiverMissionType, target_location: str,
                 difficulty: float = 0.5):
        """Initialize mission."""
        self.id = random.randint(100000, 999999)
        self.mission_type = mission_type
        self.target_location = target_location
        self.difficulty = difficulty  # 0.0-1.0
        
        # Mission params
        self.duration = self._calculate_duration()
        self.risk_level = self._calculate_risk()
        
        # Status
        self.status = DiverMissionStatus.PREPARING
        self.progress = 0.0
        self.time_elapsed = 0
        
        # Assigned divers
        self.assigned_divers: List[Diver] = []
        
        # Results
        self.success = False
        self.intelligence = {}
        self.casualties = 0
        self.equipment_lost = []
    
    def _calculate_duration(self) -> int:
        """Calculate mission duration in game ticks."""
        base_durations = {
            DiverMissionType.HARBOR_RECON: 45,
            DiverMissionType.SHIP_SABOTAGE: 60,
            DiverMissionType.NET_CUTTING: 30,
            DiverMissionType.BEACH_RECON: 40,
            DiverMissionType.PILOT_RESCUE: 35,
            DiverMissionType.MINE_PLACEMENT: 50,
            DiverMissionType.FACILITY_INFILTRATION: 70,
            DiverMissionType.WRECK_SALVAGE: 55,
            DiverMissionType.CABLE_CUTTING: 45,
            DiverMissionType.OBSTACLE_CLEARING: 40,
        }
        return base_durations.get(self.mission_type, 45)
    
    def _calculate_risk(self) -> float:
        """Calculate mission risk level."""
        base_risks = {
            DiverMissionType.HARBOR_RECON: 0.6,
            DiverMissionType.SHIP_SABOTAGE: 0.8,
            DiverMissionType.NET_CUTTING: 0.5,
            DiverMissionType.BEACH_RECON: 0.4,
            DiverMissionType.PILOT_RESCUE: 0.7,
            DiverMissionType.MINE_PLACEMENT: 0.7,
            DiverMissionType.FACILITY_INFILTRATION: 0.9,
            DiverMissionType.WRECK_SALVAGE: 0.5,
            DiverMissionType.CABLE_CUTTING: 0.6,
            DiverMissionType.OBSTACLE_CLEARING: 0.5,
        }
        base = base_risks.get(self.mission_type, 0.5)
        return min(1.0, base + (self.difficulty * 0.3))
    
    def assign_diver(self, diver: Diver) -> bool:
        """Assign diver to mission."""
        if not diver.available or not diver.alive:
            return False
        
        self.assigned_divers.append(diver)
        diver.available = False
        return True
    
    def get_mission_info(self) -> str:
        """Get formatted mission information."""
        info = f"Mission: {self.mission_type.value.replace('_', ' ').title()}\n"
        info += f"Location: {self.target_location}\n"
        info += f"Difficulty: {self.difficulty:.0%}\n"
        info += f"Risk Level: {self.risk_level:.0%}\n"
        info += f"Duration: ~{self.duration} minutes\n"
        info += f"Status: {self.status.value}\n"
        
        if self.assigned_divers:
            info += f"\nAssigned Divers:\n"
            for diver in self.assigned_divers:
                effectiveness = diver.get_effectiveness(self.mission_type)
                info += f"  - {diver.name} (Effectiveness: {effectiveness:.0%})\n"
        
        if self.status == DiverMissionStatus.IN_PROGRESS:
            info += f"\nProgress: {self.progress:.0%}\n"
        
        return info


class DiverOperationsManager:
    """Manages diver operations and missions."""
    
    def __init__(self):
        """Initialize diver operations."""
        self.divers: List[Diver] = []
        self.active_missions: List[DiverMission] = []
        self.completed_missions: List[DiverMission] = []
        self.available_mission_types = list(DiverMissionType)
    
    def recruit_diver(self, specialty: DiverSpecialty = None) -> Diver:
        """Recruit new diver."""
        diver = Diver(specialty=specialty)
        self.divers.append(diver)
        return diver
    
    def get_available_divers(self) -> List[Diver]:
        """Get divers available for missions."""
        return [d for d in self.divers if d.available and d.alive and d.fatigue < 0.7]
    
    def create_mission(self, mission_type: DiverMissionType, target: str,
                      difficulty: float = 0.5) -> DiverMission:
        """Create new diver mission."""
        mission = DiverMission(mission_type, target, difficulty)
        return mission
    
    def launch_mission(self, mission: DiverMission) -> bool:
        """Launch prepared mission."""
        if not mission.assigned_divers:
            return False
        
        mission.status = DiverMissionStatus.DEPLOYED
        self.active_missions.append(mission)
        return True
    
    def tick_missions(self) -> List[Dict]:
        """Process one tick for all active missions."""
        events = []
        
        for mission in list(self.active_missions):
            if mission.status == DiverMissionStatus.DEPLOYED:
                mission.status = DiverMissionStatus.IN_PROGRESS
            
            elif mission.status == DiverMissionStatus.IN_PROGRESS:
                # Calculate progress
                avg_effectiveness = sum(d.get_effectiveness(mission.mission_type) 
                                       for d in mission.assigned_divers) / len(mission.assigned_divers)
                
                progress_rate = avg_effectiveness / mission.duration
                mission.progress += progress_rate
                mission.time_elapsed += 1
                
                # Apply fatigue
                for diver in mission.assigned_divers:
                    diver.apply_fatigue(0.02)
                
                # Check for completion
                if mission.progress >= 1.0:
                    mission.status = DiverMissionStatus.RETURNING
                    result = self._resolve_mission(mission)
                    events.append(result)
            
            elif mission.status == DiverMissionStatus.RETURNING:
                # Divers return to sub
                mission.status = DiverMissionStatus.COMPLETED
                self.active_missions.remove(mission)
                self.completed_missions.append(mission)
                
                # Make divers available again
                for diver in mission.assigned_divers:
                    if diver.alive:
                        diver.available = True
        
        return events
    
    def _resolve_mission(self, mission: DiverMission) -> Dict:
        """Resolve mission outcome."""
        # Calculate success chance
        avg_effectiveness = sum(d.get_effectiveness(mission.mission_type) 
                               for d in mission.assigned_divers) / len(mission.assigned_divers)
        
        success_chance = avg_effectiveness * (1.0 - mission.difficulty * 0.3)
        
        # Roll for success
        mission.success = random.random() < success_chance
        
        # Roll for casualties based on risk
        for diver in mission.assigned_divers:
            if random.random() < mission.risk_level * 0.3:
                # Diver injured
                injury = random.uniform(0.2, 0.5)
                diver.health = max(0.0, diver.health - injury)
                
                if diver.health <= 0:
                    diver.alive = False
                    diver.available = False
                    mission.casualties += 1
        
        # Generate intelligence/rewards if successful
        if mission.success:
            mission.intelligence = self._generate_intelligence(mission)
            
            # Award XP
            for diver in mission.assigned_divers:
                if diver.alive:
                    diver.missions_completed += 1
                    if mission.mission_type in [DiverMissionType.SHIP_SABOTAGE, 
                                               DiverMissionType.MINE_PLACEMENT]:
                        diver.successful_sabotages += 1
                    elif 'RECON' in mission.mission_type.value.upper():
                        diver.intelligence_gathered += 1
        
        # Create event
        event = {
            'mission_id': mission.id,
            'mission_type': mission.mission_type.value,
            'success': mission.success,
            'casualties': mission.casualties,
            'intelligence': mission.intelligence,
            'message': self._create_mission_report(mission)
        }
        
        return event
    
    def _generate_intelligence(self, mission: DiverMission) -> Dict:
        """Generate intelligence from successful mission."""
        intel = {}
        
        if mission.mission_type == DiverMissionType.HARBOR_RECON:
            intel = {
                'type': 'harbor_layout',
                'ship_count': random.randint(3, 12),
                'defenses': random.choice(['light', 'moderate', 'heavy']),
                'patrol_frequency': random.choice(['low', 'medium', 'high']),
                'net_defenses': random.choice([True, False])
            }
        
        elif mission.mission_type == DiverMissionType.SHIP_SABOTAGE:
            intel = {
                'type': 'sabotage_result',
                'ships_damaged': random.randint(1, 3),
                'estimated_tonnage': random.randint(5000, 20000),
                'detection_risk': random.choice(['none', 'delayed', 'immediate'])
            }
        
        elif mission.mission_type == DiverMissionType.BEACH_RECON:
            intel = {
                'type': 'coastal_recon',
                'beach_suitability': random.choice(['excellent', 'good', 'poor']),
                'obstacles': random.choice(['none', 'light', 'heavy']),
                'defenders': random.choice(['none', 'light', 'moderate', 'heavy'])
            }
        
        elif mission.mission_type == DiverMissionType.WRECK_SALVAGE:
            intel = {
                'type': 'salvage',
                'items_recovered': random.choice(['documents', 'equipment', 'supplies']),
                'value': random.choice(['low', 'moderate', 'high'])
            }
        
        return intel
    
    def _create_mission_report(self, mission: DiverMission) -> str:
        """Create mission report message."""
        if mission.success:
            report = f"✅ Mission Success: {mission.mission_type.value.replace('_', ' ').title()}"
            report += f"\n   Location: {mission.target_location}"
            
            if mission.intelligence:
                if mission.mission_type == DiverMissionType.HARBOR_RECON:
                    intel = mission.intelligence
                    report += f"\n   Intelligence: {intel['ship_count']} ships, "
                    report += f"{intel['defenses']} defenses"
                elif mission.mission_type == DiverMissionType.SHIP_SABOTAGE:
                    intel = mission.intelligence
                    report += f"\n   Result: {intel['ships_damaged']} ships damaged, "
                    report += f"~{intel['estimated_tonnage']} tons"
            
            if mission.casualties > 0:
                report += f"\n   ⚠️  Casualties: {mission.casualties} diver(s)"
        else:
            report = f"❌ Mission Failed: {mission.mission_type.value.replace('_', ' ').title()}"
            report += f"\n   Location: {mission.target_location}"
            if mission.casualties > 0:
                report += f"\n   Casualties: {mission.casualties} diver(s)"
        
        return report
    
    def get_operations_summary(self) -> str:
        """Get summary of diver operations."""
        summary = "=== Diver Operations ===\n\n"
        
        available = self.get_available_divers()
        summary += f"Available Divers: {len(available)}/{len(self.divers)}\n"
        
        if self.active_missions:
            summary += f"\nActive Missions: {len(self.active_missions)}\n"
            for mission in self.active_missions:
                summary += f"  - {mission.mission_type.value}: {mission.progress:.0%} complete\n"
        
        if self.completed_missions:
            successful = sum(1 for m in self.completed_missions if m.success)
            summary += f"\nCompleted Missions: {len(self.completed_missions)} "
            summary += f"({successful} successful)\n"
        
        return summary
