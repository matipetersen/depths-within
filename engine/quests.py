"""
Quest and mission system for roguelike submarine scenarios.
Supports contract-based missions with objectives, rewards, and consequences.
"""

import random
import json
from typing import Dict, List, Optional, Tuple
from enum import Enum


class MissionType(Enum):
    """Types of missions available."""
    PATROL = "patrol"                  # Standard patrol mission
    SMUGGLE = "smuggle"                # Smuggle cargo
    SABOTAGE = "sabotage"              # Sabotage target vessel/installation
    RESCUE = "rescue"                  # Rescue survivors or agents
    ESCORT = "escort"                  # Escort convoy
    ELDRITCH = "eldritch"              # Encounter eldritch horror
    HUNT = "hunt"                      # Hunt specific high-value target
    SUPPLY_RUN = "supply_run"          # Deliver supplies to location
    RECONNAISSANCE = "reconnaissance"   # Spy mission
    REVENGE = "revenge"                # Personal revenge contract


class MissionStatus(Enum):
    """Status of a mission."""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class Quest:
    """Individual quest/mission definition."""
    
    def __init__(self, quest_id: str, data: Dict):
        """Initialize quest from data."""
        self.id = quest_id
        self.name = data.get('name', 'Unknown Mission')
        self.type = MissionType(data.get('type', 'patrol'))
        self.description = data.get('description', '')
        self.briefing = data.get('briefing', '')
        self.objective = data.get('objective', '')
        self.status = MissionStatus.AVAILABLE
        
        # Rewards and penalties
        self.reward_xp = data.get('reward_xp', 100)
        self.reward_credits = data.get('reward_credits', 1000)
        self.penalty_xp = data.get('penalty_xp', 50)
        self.penalty_credits = data.get('penalty_credits', 500)
        
        # Mission parameters
        self.difficulty = data.get('difficulty', 1)  # 1-5 scale
        self.time_limit = data.get('time_limit', 0)  # Turns, 0 = no limit
        self.target = data.get('target', {})
        self.location = data.get('location', {})
        self.requirements = data.get('requirements', [])
        
        # Tracking
        self.turns_elapsed = 0
        self.progress = 0.0  # 0-1 scale
        self.notes = ""
        self.events_triggered = []
    
    def start(self):
        """Begin this mission."""
        self.status = MissionStatus.ACTIVE
        self.turns_elapsed = 0
        self.progress = 0.0
        self.events_triggered = []
    
    def advance(self, turns: int = 1):
        """Advance mission time."""
        self.turns_elapsed += turns
        
        # Check time limit
        if self.time_limit > 0 and self.turns_elapsed >= self.time_limit:
            self.status = MissionStatus.FAILED
            self.notes = f"Time limit exceeded: {self.turns_elapsed}/{self.time_limit} turns"
    
    def complete(self):
        """Successfully complete mission."""
        self.status = MissionStatus.COMPLETED
        self.progress = 1.0
    
    def fail(self, reason: str = ""):
        """Fail mission."""
        self.status = MissionStatus.FAILED
        self.notes = reason or "Mission failed"
    
    def abandon(self):
        """Abandon mission."""
        self.status = MissionStatus.ABANDONED
        self.notes = "Mission abandoned by player"
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'status': self.status.value,
            'difficulty': self.difficulty,
            'progress': self.progress,
            'turns_elapsed': self.turns_elapsed,
            'time_limit': self.time_limit,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f"<Quest {self.name} ({self.type.value}) - {self.status.value}>"


class QuestGenerator:
    """Generate random quests for roguelike gameplay."""
    
    MISSION_TEMPLATES = {
        MissionType.PATROL: {
            'name': 'Routine Patrol',
            'description': 'Patrol designated waters and report on enemy activity',
            'objective': 'Maintain patrol route for specified duration without being detected',
            'reward_xp': 100,
            'reward_credits': 1000,
            'difficulty': 1,
            'time_limit': 300
        },
        MissionType.SMUGGLE: {
            'name': 'Cargo Smuggle',
            'description': 'Transport contraband cargo to destination without detection',
            'objective': 'Reach destination undetected with cargo intact',
            'reward_xp': 250,
            'reward_credits': 5000,
            'penalty_credits': 2500,
            'difficulty': 3,
            'time_limit': 400
        },
        MissionType.SABOTAGE: {
            'name': 'Sabotage Operation',
            'description': 'Destroy or disable enemy target vessel',
            'objective': 'Sink or cripple target ship; escape without detection',
            'reward_xp': 300,
            'reward_credits': 3000,
            'difficulty': 3,
            'time_limit': 250
        },
        MissionType.RESCUE: {
            'name': 'Rescue Operation',
            'description': 'Extract survivors or intelligence operatives',
            'objective': 'Reach location, retrieve operatives, return safely',
            'reward_xp': 200,
            'reward_credits': 4000,
            'difficulty': 2,
            'time_limit': 350
        },
        MissionType.ESCORT: {
            'name': 'Convoy Escort',
            'description': 'Protect allied merchant convoy from attack',
            'objective': 'Defend convoy; no merchant vessel losses allowed',
            'reward_xp': 150,
            'reward_credits': 2000,
            'difficulty': 2,
            'time_limit': 400
        },
        MissionType.HUNT: {
            'name': 'Hunt Specialty Target',
            'description': 'Locate and sink high-value target (cruiser, warship, transport)',
            'objective': 'Find and destroy specific target ship',
            'reward_xp': 400,
            'reward_credits': 6000,
            'difficulty': 4,
            'time_limit': 500
        },
        MissionType.SUPPLY_RUN: {
            'name': 'Supply Delivery',
            'description': 'Deliver supplies to covert location',
            'objective': 'Reach destination with supplies, leave without trace',
            'reward_xp': 120,
            'reward_credits': 1500,
            'difficulty': 2,
            'time_limit': 300
        },
        MissionType.RECONNAISSANCE: {
            'name': 'Reconnaissance',
            'description': 'Spy on enemy positions and document activity',
            'objective': 'Gather intelligence on specified region',
            'reward_xp': 180,
            'reward_credits': 2500,
            'difficulty': 2,
            'time_limit': 300
        },
    }
    
    ELDRITCH_TEMPLATES = [
        {
            'name': 'The Deep One',
            'description': 'Ancient entity awakens in the abyss',
            'objective': 'Survive encounter with creature of unknown origin; do not engage',
            'reward_xp': 500,
            'reward_credits': 10000,
            'penalty_xp': 200,
            'penalty_credits': 5000,
            'difficulty': 5,
            'time_limit': 150
        },
        {
            'name': 'Whispers in the Dark',
            'description': 'Crew hears strange sounds through hull during deep dive',
            'objective': 'Surface and escape; maintain crew sanity',
            'reward_xp': 300,
            'reward_credits': 5000,
            'penalty_xp': 100,
            'penalty_credits': 2000,
            'difficulty': 4,
            'time_limit': 120
        },
        {
            'name': 'The Sunken City',
            'description': 'Discover vast ruins on ocean floor',
            'objective': 'Document location and return; investigate if brave',
            'reward_xp': 400,
            'reward_credits': 8000,
            'penalty_xp': 150,
            'difficulty': 4,
            'time_limit': 200
        },
        {
            'name': 'Spectral Signals',
            'description': 'Sonar detects impossible contacts - submarines from another time?',
            'objective': 'Investigate signals without engaging; escape if threatened',
            'reward_xp': 350,
            'reward_credits': 6000,
            'difficulty': 4,
            'time_limit': 180
        },
        {
            'name': 'The Sacrifice',
            'description': 'Strange ritual marks appear in sonar readings',
            'objective': 'Leave the area; do not interfere with unknown ceremony',
            'reward_xp': 250,
            'reward_credits': 3000,
            'penalty_xp': 300,
            'difficulty': 3,
            'time_limit': 100
        }
    ]
    
    def __init__(self):
        """Initialize quest generator."""
        self.generated_quests: Dict[str, Quest] = {}
        self.quest_counter = 0
    
    def generate_standard_mission(self, mission_type: Optional[MissionType] = None) -> Quest:
        """Generate a standard military mission."""
        if mission_type is None:
            # Skip ELDRITCH for standard missions
            available = [t for t in MissionType if t != MissionType.ELDRITCH]
            mission_type = random.choice(available)
        
        template = self.MISSION_TEMPLATES.get(mission_type)
        if not template:
            template = self.MISSION_TEMPLATES[MissionType.PATROL]
        
        # Add some randomization
        data = template.copy()
        data['difficulty'] = random.randint(max(1, data.get('difficulty', 1) - 1), 
                                           min(5, data.get('difficulty', 1) + 1))
        data['type'] = mission_type.value
        
        # Generate unique ID
        self.quest_counter += 1
        quest_id = f"mission_{self.quest_counter}"
        
        quest = Quest(quest_id, data)
        self.generated_quests[quest_id] = quest
        return quest
    
    def generate_eldritch_encounter(self) -> Quest:
        """Generate an eldritch horror encounter."""
        template = random.choice(self.ELDRITCH_TEMPLATES)
        data = template.copy()
        data['type'] = MissionType.ELDRITCH.value
        
        self.quest_counter += 1
        quest_id = f"eldritch_{self.quest_counter}"
        
        quest = Quest(quest_id, data)
        self.generated_quests[quest_id] = quest
        return quest
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get quest by ID."""
        return self.generated_quests.get(quest_id)
    
    def get_active_quests(self) -> List[Quest]:
        """Get all active quests."""
        return [q for q in self.generated_quests.values() 
               if q.status == MissionStatus.ACTIVE]
    
    def get_available_quests(self) -> List[Quest]:
        """Get all available quests."""
        return [q for q in self.generated_quests.values() 
               if q.status == MissionStatus.AVAILABLE]
    
    def get_completed_quests(self) -> List[Quest]:
        """Get all completed quests."""
        return [q for q in self.generated_quests.values() 
               if q.status == MissionStatus.COMPLETED]


class QuestManager:
    """Manages active and historical quests."""
    
    def __init__(self):
        """Initialize quest manager."""
        self.generator = QuestGenerator()
        self.active_quest: Optional[Quest] = None
        self.history: List[Quest] = []
        self.total_rewards_xp = 0
        self.total_rewards_credits = 0
        self.total_penalties_xp = 0
        self.total_penalties_credits = 0
    
    def generate_mission(self, mission_type: Optional[MissionType] = None) -> Quest:
        """Generate and add a new standard mission to available list."""
        quest = self.generator.generate_standard_mission(mission_type)
        return quest
    
    def generate_eldritch(self) -> Quest:
        """Generate eldritch encounter."""
        quest = self.generator.generate_eldritch_encounter()
        return quest
    
    def accept_quest(self, quest_id: str) -> bool:
        """Accept a quest and make it active."""
        if self.active_quest is not None:
            return False  # Already have active quest
        
        quest = self.generator.get_quest(quest_id)
        if not quest or quest.status != MissionStatus.AVAILABLE:
            return False
        
        quest.start()
        self.active_quest = quest
        return True
    
    def complete_active_quest(self) -> Dict:
        """Complete active quest and award rewards."""
        if not self.active_quest:
            return {}
        
        quest = self.active_quest
        quest.complete()
        
        rewards = {
            'xp': quest.reward_xp,
            'credits': quest.reward_credits,
            'mission': quest.name
        }
        
        self.total_rewards_xp += quest.reward_xp
        self.total_rewards_credits += quest.reward_credits
        self.history.append(quest)
        self.active_quest = None
        
        return rewards
    
    def fail_active_quest(self, reason: str = "") -> Dict:
        """Fail active quest and apply penalties."""
        if not self.active_quest:
            return {}
        
        quest = self.active_quest
        quest.fail(reason)
        
        penalties = {
            'xp': -quest.penalty_xp,
            'credits': -quest.penalty_credits,
            'mission': quest.name,
            'reason': reason
        }
        
        self.total_penalties_xp += quest.penalty_xp
        self.total_penalties_credits += quest.penalty_credits
        self.history.append(quest)
        self.active_quest = None
        
        return penalties
    
    def abandon_active_quest(self) -> Optional[str]:
        """Abandon current quest."""
        if not self.active_quest:
            return None
        
        quest = self.active_quest
        quest.abandon()
        self.history.append(quest)
        name = quest.name
        self.active_quest = None
        
        return name
    
    def advance_time(self, turns: int = 1):
        """Advance quest time."""
        if self.active_quest:
            self.active_quest.advance(turns)
    
    def get_active_quest_info(self) -> Dict:
        """Get info about active quest."""
        if not self.active_quest:
            return {'status': 'no_active_quest'}
        
        q = self.active_quest
        return {
            'name': q.name,
            'type': q.type.value,
            'objective': q.objective,
            'difficulty': q.difficulty,
            'progress': q.progress,
            'turns_elapsed': q.turns_elapsed,
            'time_limit': q.time_limit,
            'time_remaining': max(0, q.time_limit - q.turns_elapsed) if q.time_limit > 0 else 0,
            'status': q.status.value
        }
    
    def get_career_stats(self) -> Dict:
        """Get career quest statistics."""
        return {
            'quests_completed': len([q for q in self.history if q.status == MissionStatus.COMPLETED]),
            'quests_failed': len([q for q in self.history if q.status == MissionStatus.FAILED]),
            'quests_abandoned': len([q for q in self.history if q.status == MissionStatus.ABANDONED]),
            'total_rewards_xp': self.total_rewards_xp,
            'total_rewards_credits': self.total_rewards_credits,
            'total_penalties_xp': self.total_penalties_xp,
            'total_penalties_credits': self.total_penalties_credits,
            'net_xp': self.total_rewards_xp - self.total_penalties_xp,
            'net_credits': self.total_rewards_credits - self.total_penalties_credits,
        }
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'active_quest': self.active_quest.to_dict() if self.active_quest else None,
            'history': [q.to_dict() for q in self.history],
            'stats': self.get_career_stats()
        }
