"""
Engineer-based Repair System.
Implements skill-based repairs with engineer specializations affecting outcomes.
"""

import random
from typing import Dict, List, Optional, Tuple
from enum import Enum
from submarine.crew_skills import SkilledCrewMember, Specialization


class RepairType(Enum):
    """Types of repairs engineers can perform."""
    HULL_BREACH = 'hull_breach'              # Hull integrity damage
    FLOODING = 'flooding'                     # Water infiltration
    ELECTRICAL = 'electrical'                 # Battery, power systems
    MECHANICAL = 'mechanical'                 # Engines, propulsion
    TORPEDO_TUBE = 'torpedo_tube'            # Torpedo systems
    SONAR = 'sonar'                          # Sonar equipment
    PERISCOPE = 'periscope'                  # Periscope damage
    COMPARTMENT = 'compartment'              # General compartment damage
    EMERGENCY = 'emergency'                  # Critical emergency repairs


class RepairTask:
    """Represents a repair task."""
    
    def __init__(self, repair_type: RepairType, severity: float, 
                 compartment_id: str = None, location: str = None):
        """Initialize repair task.
        
        Args:
            repair_type: Type of repair needed
            severity: Damage severity (0.0-1.0)
            compartment_id: Compartment needing repair
            location: Description of damage location
        """
        self.repair_type = repair_type
        self.severity = severity
        self.compartment_id = compartment_id
        self.location = location or "Unknown"
        
        # Repair progress
        self.progress = 0.0  # 0.0-1.0, complete at 1.0
        self.time_remaining = self._calculate_base_time()
        self.assigned_engineer = None
        self.difficulty = self._calculate_difficulty()
    
    def _calculate_base_time(self) -> float:
        """Calculate base repair time in game ticks."""
        # Base times by repair type (in ticks, ~1 tick = 1 minute game time)
        base_times = {
            RepairType.HULL_BREACH: 120,      # 2 hours
            RepairType.FLOODING: 60,          # 1 hour
            RepairType.ELECTRICAL: 45,        # 45 minutes
            RepairType.MECHANICAL: 90,        # 1.5 hours
            RepairType.TORPEDO_TUBE: 75,      # 1.25 hours
            RepairType.SONAR: 30,             # 30 minutes
            RepairType.PERISCOPE: 40,         # 40 minutes
            RepairType.COMPARTMENT: 50,       # 50 minutes
            RepairType.EMERGENCY: 20          # 20 minutes (quick patch)
        }
        
        base = base_times.get(self.repair_type, 60)
        # Scale by severity
        return base * (0.5 + self.severity * 0.5)
    
    def _calculate_difficulty(self) -> float:
        """Calculate repair difficulty (0.0-1.0)."""
        # Base difficulty by type
        difficulties = {
            RepairType.HULL_BREACH: 0.8,
            RepairType.FLOODING: 0.7,
            RepairType.ELECTRICAL: 0.6,
            RepairType.MECHANICAL: 0.7,
            RepairType.TORPEDO_TUBE: 0.65,
            RepairType.SONAR: 0.5,
            RepairType.PERISCOPE: 0.55,
            RepairType.COMPARTMENT: 0.6,
            RepairType.EMERGENCY: 0.9  # High stress, quick work
        }
        
        base = difficulties.get(self.repair_type, 0.6)
        # Severity increases difficulty
        return min(1.0, base + (self.severity * 0.2))
    
    def assign_engineer(self, engineer: SkilledCrewMember):
        """Assign engineer to repair task."""
        self.assigned_engineer = engineer
    
    def is_complete(self) -> bool:
        """Check if repair is complete."""
        return self.progress >= 1.0
    
    def get_description(self) -> str:
        """Get repair task description."""
        desc = f"{self.repair_type.value.replace('_', ' ').title()}"
        desc += f" (Severity: {self.severity:.0%})"
        if self.compartment_id:
            desc += f" in {self.compartment_id}"
        if self.assigned_engineer:
            desc += f"\nAssigned: {self.assigned_engineer.name}"
        desc += f"\nProgress: {self.progress:.0%}"
        return desc


class EngineerRepairSystem:
    """Manages engineer-based repair system."""
    
    def __init__(self):
        """Initialize repair system."""
        self.active_repairs: List[RepairTask] = []
        self.completed_repairs: List[RepairTask] = []
        self.repair_queue: List[RepairTask] = []
    
    def add_repair_task(self, task: RepairTask, priority: bool = False):
        """Add repair task to queue.
        
        Args:
            task: Repair task to add
            priority: If True, add to front of queue
        """
        if priority:
            self.repair_queue.insert(0, task)
        else:
            self.repair_queue.append(task)
    
    def create_repair(self, repair_type: RepairType, severity: float,
                     compartment_id: str = None, priority: bool = False) -> RepairTask:
        """Create and queue a repair task."""
        task = RepairTask(repair_type, severity, compartment_id)
        self.add_repair_task(task, priority)
        return task
    
    def assign_engineer_to_task(self, engineer: SkilledCrewMember, 
                               task: RepairTask = None) -> bool:
        """Assign engineer to repair task.
        
        Args:
            engineer: Engineer to assign
            task: Specific task, or None to auto-assign from queue
            
        Returns:
            Success status
        """
        # If no task specified, take from queue
        if task is None:
            if not self.repair_queue:
                return False
            task = self.repair_queue.pop(0)
        
        # Assign engineer
        task.assign_engineer(engineer)
        self.active_repairs.append(task)
        return True
    
    def perform_repair_tick(self, task: RepairTask) -> Dict:
        """Perform one tick of repair work.
        
        Returns:
            Dict with repair results and events
        """
        if not task.assigned_engineer or task.is_complete():
            return {'progress': 0.0, 'complete': task.is_complete()}
        
        engineer = task.assigned_engineer
        
        # Calculate relevant skill
        skill_type = self._get_skill_for_repair(task.repair_type)
        skill_level = engineer.effective_skill(skill_type)
        
        # Get specialization bonuses
        bonuses = self._get_specialization_bonuses(engineer, task.repair_type)
        
        # Calculate repair speed
        base_speed = 1.0 / task.time_remaining  # Base progress per tick
        
        # Skill modifier (0.5x to 2.0x speed based on skill)
        skill_modifier = 0.5 + (skill_level * 1.5)
        
        # Specialization modifier
        spec_modifier = 1.0
        for bonus_type, bonus_value in bonuses.items():
            if 'repair' in bonus_type or bonus_type == 'all_engineering':
                spec_modifier += bonus_value
        
        # Difficulty modifier
        difficulty_modifier = 2.0 - task.difficulty  # Easier = faster
        
        # Environmental modifiers
        stress_penalty = 1.0 - (engineer.stress * 0.3)  # Up to 30% slower
        fatigue_penalty = 1.0 - (engineer.fatigue * 0.2)  # Up to 20% slower
        
        # Calculate final progress
        progress_this_tick = (base_speed * skill_modifier * spec_modifier * 
                            difficulty_modifier * stress_penalty * fatigue_penalty)
        
        task.progress += progress_this_tick
        
        # Engineer gains XP
        xp_gain = int(10 * task.severity)
        engineer.gain_xp(skill_type, xp_gain)
        engineer.repairs_performed += 1
        
        # Apply fatigue and stress
        engineer.apply_fatigue(0.01 * task.severity)
        if task.repair_type == RepairType.EMERGENCY:
            engineer.apply_stress(0.05)
        
        # Check for completion
        if task.progress >= 1.0:
            task.progress = 1.0
            self.active_repairs.remove(task)
            self.completed_repairs.append(task)
            
            return {
                'progress': progress_this_tick,
                'complete': True,
                'engineer': engineer.name,
                'repair_type': task.repair_type.value,
                'message': f"{engineer.name} completed {task.repair_type.value} repair"
            }
        
        return {
            'progress': progress_this_tick,
            'complete': False,
            'total_progress': task.progress
        }
    
    def _get_skill_for_repair(self, repair_type: RepairType) -> str:
        """Get relevant skill for repair type."""
        skill_map = {
            RepairType.HULL_BREACH: 'engineering',
            RepairType.FLOODING: 'damage_control',
            RepairType.ELECTRICAL: 'engineering',
            RepairType.MECHANICAL: 'engineering',
            RepairType.TORPEDO_TUBE: 'torpedoes',
            RepairType.SONAR: 'sonar',
            RepairType.PERISCOPE: 'navigation',
            RepairType.COMPARTMENT: 'engineering',
            RepairType.EMERGENCY: 'damage_control'
        }
        return skill_map.get(repair_type, 'engineering')
    
    def _get_specialization_bonuses(self, engineer: SkilledCrewMember, 
                                    repair_type: RepairType) -> Dict[str, float]:
        """Get specialization bonuses for repair type."""
        if not engineer.specialization:
            return {}
        
        bonuses = engineer.get_specialization_bonuses()
        
        # Filter relevant bonuses for repair type
        relevant_bonuses = {}
        
        if repair_type == RepairType.HULL_BREACH:
            if 'hull_repair' in bonuses:
                relevant_bonuses['hull_repair'] = bonuses['hull_repair']
        elif repair_type == RepairType.FLOODING:
            if 'flooding_control' in bonuses:
                relevant_bonuses['flooding_control'] = bonuses['flooding_control']
        elif repair_type == RepairType.ELECTRICAL:
            if 'systems_repair' in bonuses or 'battery_efficiency' in bonuses:
                relevant_bonuses.update({k: v for k, v in bonuses.items() 
                                       if 'battery' in k or 'systems' in k})
        elif repair_type == RepairType.MECHANICAL:
            if 'engine_repair' in bonuses:
                relevant_bonuses['engine_repair'] = bonuses['engine_repair']
        elif repair_type == RepairType.EMERGENCY:
            if 'emergency_repair' in bonuses:
                relevant_bonuses['emergency_repair'] = bonuses['emergency_repair']
        
        # All engineers benefit from general engineering bonus
        if 'all_engineering' in bonuses:
            relevant_bonuses['all_engineering'] = bonuses['all_engineering']
        
        if 'repair_speed' in bonuses:
            relevant_bonuses['repair_speed'] = bonuses['repair_speed']
        
        return relevant_bonuses
    
    def get_best_engineer_for_task(self, task: RepairTask, 
                                   available_engineers: List[SkilledCrewMember]) -> Optional[SkilledCrewMember]:
        """Get best engineer for a repair task."""
        if not available_engineers:
            return None
        
        skill_type = self._get_skill_for_repair(task.repair_type)
        
        # Score each engineer
        scores = []
        for engineer in available_engineers:
            if not engineer.alive:
                continue
            
            # Base score from skill
            score = engineer.effective_skill(skill_type) * 100
            
            # Bonus for relevant specialization
            if engineer.specialization:
                bonuses = self._get_specialization_bonuses(engineer, task.repair_type)
                bonus_score = sum(bonuses.values()) * 50
                score += bonus_score
            
            # Penalty for high stress/fatigue
            score *= (1.0 - engineer.stress * 0.3)
            score *= (1.0 - engineer.fatigue * 0.2)
            
            scores.append((engineer, score))
        
        if not scores:
            return None
        
        # Return engineer with highest score
        return max(scores, key=lambda x: x[1])[0]
    
    def tick_all_repairs(self) -> List[Dict]:
        """Perform one tick on all active repairs.
        
        Returns:
            List of repair events
        """
        events = []
        
        for task in list(self.active_repairs):  # Copy list to avoid modification during iteration
            result = self.perform_repair_tick(task)
            if result['complete']:
                events.append(result)
        
        return events
    
    def get_repair_summary(self) -> str:
        """Get formatted repair status."""
        summary = "=== Repair Status ===\n\n"
        
        if self.active_repairs:
            summary += f"Active Repairs ({len(self.active_repairs)}):\n"
            for task in self.active_repairs:
                summary += f"  {task.get_description()}\n\n"
        else:
            summary += "No active repairs\n\n"
        
        if self.repair_queue:
            summary += f"Queued Repairs ({len(self.repair_queue)}):\n"
            for task in self.repair_queue[:3]:  # Show first 3
                summary += f"  {task.repair_type.value.replace('_', ' ').title()} "
                summary += f"(Severity: {task.severity:.0%})\n"
            if len(self.repair_queue) > 3:
                summary += f"  ... and {len(self.repair_queue) - 3} more\n"
        
        if self.completed_repairs:
            summary += f"\nCompleted: {len(self.completed_repairs)} repairs\n"
        
        return summary
    
    def get_engineer_workload(self, engineer: SkilledCrewMember) -> int:
        """Get number of tasks assigned to engineer."""
        return sum(1 for task in self.active_repairs 
                  if task.assigned_engineer == engineer)
    
    def auto_assign_engineers(self, available_engineers: List[SkilledCrewMember]) -> int:
        """Auto-assign available engineers to queued tasks.
        
        Returns:
            Number of assignments made
        """
        assignments = 0
        
        # Get engineers not currently assigned
        assigned_engineers = {task.assigned_engineer for task in self.active_repairs 
                            if task.assigned_engineer}
        free_engineers = [e for e in available_engineers if e not in assigned_engineers]
        
        while self.repair_queue and free_engineers:
            task = self.repair_queue[0]
            engineer = self.get_best_engineer_for_task(task, free_engineers)
            
            if engineer:
                self.assign_engineer_to_task(engineer, task)
                free_engineers.remove(engineer)
                assignments += 1
            else:
                break
        
        return assignments
