"""Crew Loyalty, Rebellion, and Endgame Ranking System.

Tracks crew morale, loyalty, stress, and potential for rebellion/desertion.
Implements an endgame war ranking system based on:
- War survival (alive at game end)
- Combat effectiveness (ships sunk, tonnage)
- Crew loyalty (no major desertions/mutinies)
- Rescue operations (survivors saved)
- Player rank achieved
"""

from enum import Enum
from typing import Dict, List, Optional


class CrewLoyaltyStatus(Enum):
    """Crew member loyalty status."""
    LOYAL = "loyal"                  # 0.7+ loyalty, calm
    CONTENT = "content"              # 0.5-0.7 loyalty, normal
    DISSATISFIED = "dissatisfied"    # 0.3-0.5 loyalty, grumbling
    MUTINOUS = "mutinous"            # 0.1-0.3 loyalty, actively rebellious
    DESERTER = "deserter"            # <0.1 loyalty, fled


class RebellionType(Enum):
    """Types of crew rebellion."""
    MINOR_COMPLAINT = "minor_complaint"      # <10% severity
    WORK_SLOWDOWN = "work_slowdown"          # 10-30% severity
    REFUSAL_TO_OBEY = "refusal_to_obey"      # 30-60% severity
    MUTINY = "mutiny"                        # 60-85% severity
    MASS_DESERTION = "mass_desertion"        # 85%+ severity


class WarRank(Enum):
    """War ranking system for endgame."""
    CIVILIAN = "Civilian"                    # Never fought
    RECRUIT = "Recruit"                      # <5 kills
    SAILOR = "Sailor"                        # 5-10 kills
    VETERAN = "Veteran"                      # 10-25 kills
    SUBMARINE_ACE = "Submarine Ace"          # 25-50 kills
    CAPITAL_SHIP_KILLER = "Capital Ship Killer"  # Sunk large vessels
    LEGENDARY_COMMANDER = "Legendary Commander"  # 50+ kills + perfect crew


class LoyaltyTracker:
    """Tracks individual crew member loyalty and rebellion risk."""
    
    def __init__(self, crew_id: int, crew_name: str, personality: str = "calm"):
        """
        Initialize loyalty tracker.
        
        Args:
            crew_id: Crew member ID
            crew_name: Crew member name
            personality: Personality type (brave, cautious, calm, aggressive, disciplined, curious)
        """
        self.crew_id = crew_id
        self.crew_name = crew_name
        self.personality = personality
        
        # Loyalty (0-1.0)
        self.loyalty = 0.75  # Start with moderate loyalty
        
        # Stress factors
        self.fear_level = 0.0  # From combat/danger (0-1.0)
        self.hunger_level = 0.0  # From low supplies (0-1.0)
        self.exhaustion_level = 0.0  # From overwork (0-1.0)
        
        # History tracking
        self.missions_survived = 0
        self.times_nearly_died = 0  # Escapes from sinking/damage
        self.rescued_survivors = 0
        self.combat_victories = 0
        self.comrades_lost = 0
        
        # Rebellion tracking
        self.rebellion_incidents = []  # List of (turn, type, severity)
        self.loyalty_events = []  # List of (turn, event, loyalty_change)
        
        # Morale modifiers
        self.morale_bonus = 0.0  # From achievements, rescues, etc.
        self.morale_penalty = 0.0  # From losses, danger, starvation
    
    def get_loyalty_status(self) -> CrewLoyaltyStatus:
        """Determine current loyalty status."""
        if self.loyalty >= 0.7:
            return CrewLoyaltyStatus.LOYAL
        elif self.loyalty >= 0.5:
            return CrewLoyaltyStatus.CONTENT
        elif self.loyalty >= 0.3:
            return CrewLoyaltyStatus.DISSATISFIED
        elif self.loyalty > 0.1:
            return CrewLoyaltyStatus.MUTINOUS
        else:
            return CrewLoyaltyStatus.DESERTER
    
    def get_rebellion_risk(self) -> float:
        """Calculate current rebellion risk (0-1.0)."""
        base_risk = (1.0 - self.loyalty) * 0.5
        
        # Add stress factors
        stress_contribution = (self.fear_level + self.hunger_level + self.exhaustion_level) / 3 * 0.5
        
        risk = base_risk + stress_contribution
        
        # Personality affects risk
        personality_modifiers = {
            'brave': -0.1,          # Less likely to rebel
            'cautious': 0.05,       # Slightly more cautious
            'calm': -0.05,          # Calmer, less rebellious
            'aggressive': 0.15,     # More prone to rebellion
            'disciplined': -0.15,   # Very resistant to rebellion
            'curious': 0.05,        # Slightly restless
        }
        risk += personality_modifiers.get(self.personality, 0.0)
        
        return max(0.0, min(1.0, risk))
    
    def apply_stress(self, fear: float = 0.0, hunger: float = 0.0, exhaustion: float = 0.0):
        """Apply stress from various sources."""
        self.fear_level = min(1.0, self.fear_level + fear)
        self.hunger_level = min(1.0, self.hunger_level + hunger)
        self.exhaustion_level = min(1.0, self.exhaustion_level + exhaustion)
    
    def relieve_stress(self, amount: float = 0.05):
        """Relieve stress through rest/food/morale activities."""
        self.fear_level = max(0.0, self.fear_level - amount)
        self.hunger_level = max(0.0, self.hunger_level - amount)
        self.exhaustion_level = max(0.0, self.exhaustion_level - amount)
    
    def add_loyalty_event(self, turn: int, event: str, loyalty_change: float):
        """Record a loyalty-affecting event."""
        self.loyalty_events.append((turn, event, loyalty_change))
        self.loyalty = max(0.0, min(1.0, self.loyalty + loyalty_change))
        
        if loyalty_change > 0:
            self.morale_bonus += loyalty_change * 0.1
        else:
            self.morale_penalty += abs(loyalty_change) * 0.1
    
    def check_rebellion(self, turn: int) -> Optional[RebellionType]:
        """Check if crew member initiates rebellion this turn."""
        risk = self.get_rebellion_risk()
        
        # Use personality to bias rebellion type
        rebellion_chance = 0.0
        if self.personality == "aggressive":
            rebellion_chance = risk * 0.8  # More aggressive = higher chance
        else:
            rebellion_chance = risk * 0.4
        
        # Random check
        import random
        if random.random() < rebellion_chance:
            # Determine rebellion type based on risk level
            if risk < 0.3:
                return RebellionType.MINOR_COMPLAINT
            elif risk < 0.5:
                return RebellionType.WORK_SLOWDOWN
            elif risk < 0.7:
                return RebellionType.REFUSAL_TO_OBEY
            elif risk < 0.85:
                return RebellionType.MUTINY
            else:
                return RebellionType.MASS_DESERTION
        
        return None
    
    def record_rebellion(self, turn: int, rebellion_type: RebellionType):
        """Record a rebellion incident."""
        severity = {
            RebellionType.MINOR_COMPLAINT: 0.05,
            RebellionType.WORK_SLOWDOWN: 0.20,
            RebellionType.REFUSAL_TO_OBEY: 0.45,
            RebellionType.MUTINY: 0.70,
            RebellionType.MASS_DESERTION: 0.90,
        }[rebellion_type]
        
        self.rebellion_incidents.append((turn, rebellion_type, severity))
        self.loyalty = max(0.0, min(1.0, self.loyalty - severity))
    
    def record_achievement(self, achievement: str, turn: int, loyalty_change: float = 0.05):
        """Record achievement that improves loyalty."""
        achievements = {
            'mission_completed': 0.10,
            'enemy_destroyed': 0.15,
            'survivors_rescued': 0.20,
            'narrowly_escaped': 0.08,
            'comrade_saved': 0.12,
            'commendation': 0.15,
        }
        
        change = achievements.get(achievement, loyalty_change)
        self.add_loyalty_event(turn, f"Achievement: {achievement}", change)
    
    def record_tragedy(self, tragedy: str, turn: int, loyalty_change: float = -0.05):
        """Record tragedy that reduces loyalty."""
        tragedies = {
            'comrade_died': -0.15,
            'near_death_experience': -0.10,
            'order_backfired': -0.12,
            'unjust_punishment': -0.20,
            'starvation': -0.08,
            'abandoned': -0.25,
        }
        
        change = tragedies.get(tragedy, loyalty_change)
        self.add_loyalty_event(turn, f"Tragedy: {tragedy}", change)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'crew_id': self.crew_id,
            'crew_name': self.crew_name,
            'personality': self.personality,
            'loyalty': self.loyalty,
            'loyalty_status': self.get_loyalty_status().value,
            'fear_level': self.fear_level,
            'hunger_level': self.hunger_level,
            'exhaustion_level': self.exhaustion_level,
            'missions_survived': self.missions_survived,
            'times_nearly_died': self.times_nearly_died,
            'rescued_survivors': self.rescued_survivors,
            'combat_victories': self.combat_victories,
            'comrades_lost': self.comrades_lost,
            'rebellion_incidents': self.rebellion_incidents,
            'loyalty_events': self.loyalty_events,
            'morale_bonus': self.morale_bonus,
            'morale_penalty': self.morale_penalty,
        }
    
    def __repr__(self):
        return f"LoyaltyTracker({self.crew_name}, loyalty={self.loyalty:.2f}, status={self.get_loyalty_status().value})"


class RebellionManager:
    """Manages crew-wide rebellion and mutiny events."""
    
    def __init__(self):
        """Initialize rebellion manager."""
        self.loyalty_trackers: Dict[int, LoyaltyTracker] = {}
        self.active_rebellions: List[Dict] = []  # List of active rebellion events
        self.total_desertions = 0
        self.mutinies_occurred = 0
        self.crew_morale_modifier = 1.0
    
    def add_crew_member(self, crew_id: int, crew_name: str, personality: str = "calm"):
        """Add crew member to tracking."""
        self.loyalty_trackers[crew_id] = LoyaltyTracker(crew_id, crew_name, personality)
    
    def remove_crew_member(self, crew_id: int):
        """Remove crew member from tracking (death/dismissal)."""
        if crew_id in self.loyalty_trackers:
            del self.loyalty_trackers[crew_id]
    
    def get_crew_morale(self) -> float:
        """Get average crew morale (0-1.0)."""
        if not self.loyalty_trackers:
            return 0.5
        
        avg_loyalty = sum(t.loyalty for t in self.loyalty_trackers.values()) / len(self.loyalty_trackers)
        return avg_loyalty * self.crew_morale_modifier
    
    def check_all_rebellions(self, turn: int) -> List[Dict]:
        """Check all crew members for potential rebellions."""
        rebellions = []
        
        for crew_id, tracker in self.loyalty_trackers.items():
            rebellion = tracker.check_rebellion(turn)
            
            if rebellion:
                tracker.record_rebellion(turn, rebellion)
                
                rebellion_event = {
                    'turn': turn,
                    'crew_id': crew_id,
                    'crew_name': tracker.crew_name,
                    'type': rebellion,
                    'severity': self._get_rebellion_severity(rebellion),
                }
                
                rebellions.append(rebellion_event)
                self.active_rebellions.append(rebellion_event)
                
                # Track major events
                if rebellion == RebellionType.MASS_DESERTION:
                    self.total_desertions += 1
                elif rebellion == RebellionType.MUTINY:
                    self.mutinies_occurred += 1
        
        return rebellions
    
    def _get_rebellion_severity(self, rebellion_type: RebellionType) -> float:
        """Get severity of rebellion type."""
        return {
            RebellionType.MINOR_COMPLAINT: 0.05,
            RebellionType.WORK_SLOWDOWN: 0.20,
            RebellionType.REFUSAL_TO_OBEY: 0.45,
            RebellionType.MUTINY: 0.70,
            RebellionType.MASS_DESERTION: 0.90,
        }[rebellion_type]
    
    def handle_rebellion(self, crew_id: int, response: str):
        """Handle rebellion with captain's response."""
        if crew_id not in self.loyalty_trackers:
            return
        
        tracker = self.loyalty_trackers[crew_id]
        
        response_effects = {
            'harsh_punishment': {'loyalty': -0.25, 'fear': 0.15},
            'sympathetic': {'loyalty': 0.10, 'fear': -0.10},
            'ignore': {'loyalty': -0.15, 'fear': 0.05},
            'reward': {'loyalty': 0.20, 'fear': -0.15},
            'demote': {'loyalty': -0.20, 'fear': 0.10},
        }
        
        if response in response_effects:
            effects = response_effects[response]
            tracker.loyalty = max(0.0, min(1.0, tracker.loyalty + effects.get('loyalty', 0)))
            tracker.fear_level = max(0.0, min(1.0, tracker.fear_level + effects.get('fear', 0)))
    
    def apply_crew_event(self, event_type: str, severity: float = 0.1):
        """Apply event affecting all crew (combat, starvation, etc.)."""
        if event_type == "combat_victory":
            for tracker in self.loyalty_trackers.values():
                tracker.record_achievement("enemy_destroyed", 0, severity)
        
        elif event_type == "combat_defeat":
            for tracker in self.loyalty_trackers.values():
                tracker.record_tragedy("near_death_experience", 0, -severity)
        
        elif event_type == "starvation":
            for tracker in self.loyalty_trackers.values():
                tracker.apply_stress(hunger=severity)
        
        elif event_type == "successful_rescue":
            for tracker in self.loyalty_trackers.values():
                tracker.record_achievement("survivors_rescued", 0, severity)
        
        elif event_type == "shore_leave":
            for tracker in self.loyalty_trackers.values():
                tracker.relieve_stress(amount=severity)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'loyalty_trackers': {cid: t.to_dict() for cid, t in self.loyalty_trackers.items()},
            'active_rebellions': self.active_rebellions,
            'total_desertions': self.total_desertions,
            'mutinies_occurred': self.mutinies_occurred,
            'crew_morale': self.get_crew_morale(),
        }


class WarEndgameStats:
    """Tracks statistics for war ranking and endgame scoring."""
    
    def __init__(self):
        """Initialize war endgame statistics."""
        # Combat
        self.enemy_ships_destroyed = 0
        self.enemy_tonnage_sunk = 0
        self.capital_ships_sunk = 0  # Battleships, cruisers
        
        # Crew
        self.crew_alive_at_end = 0
        self.crew_total_recruited = 0
        self.crew_deserted = 0
        self.crew_mutinies = 0
        self.crew_average_loyalty = 0.5
        
        # Heroic actions
        self.survivors_rescued = 0
        self.near_death_escapes = 0
        self.missions_completed = 0
        self.perfect_loyalty_end = False  # No desertions/mutinies
        
        # War duration
        self.turns_survived = 0
        self.war_victory = False
    
    def calculate_war_rank(self) -> WarRank:
        """Calculate final war rank based on statistics."""
        total_kills = self.enemy_ships_destroyed
        
        # Check for legendary status
        if (total_kills >= 50 and self.perfect_loyalty_end and 
            self.crew_average_loyalty > 0.8 and self.survivors_rescued > 10):
            return WarRank.LEGENDARY_COMMANDER
        
        # Capital ship killer
        if self.capital_ships_sunk >= 5:
            return WarRank.CAPITAL_SHIP_KILLER
        
        # Ace rankings
        if total_kills >= 25:
            return WarRank.SUBMARINE_ACE
        elif total_kills >= 10:
            return WarRank.VETERAN
        elif total_kills >= 5:
            return WarRank.SAILOR
        elif total_kills > 0:
            return WarRank.RECRUIT
        else:
            return WarRank.CIVILIAN
    
    def calculate_final_score(self) -> int:
        """Calculate final endgame score."""
        score = 0
        
        # Combat points (10 per kill, 25 per capital ship)
        score += self.enemy_ships_destroyed * 10
        score += self.capital_ships_sunk * 25
        
        # Crew loyalty bonus
        crew_bonus = int(self.crew_average_loyalty * 1000)
        score += crew_bonus
        
        # Heroic actions
        score += self.survivors_rescued * 50
        score += self.near_death_escapes * 20
        score += self.missions_completed * 100
        
        # Perfect crew status bonus
        if self.perfect_loyalty_end:
            score += 500
        
        # War victory bonus
        if self.war_victory:
            score += 2000
        
        # Survival bonus (turns survived)
        score += min(1000, self.turns_survived // 10)
        
        return score
    
    def get_final_report(self) -> str:
        """Generate final war report."""
        rank = self.calculate_war_rank()
        score = self.calculate_final_score()
        
        lines = [
            "═" * 60,
            "WAR END REPORT",
            "═" * 60,
            "",
            f"Final Rank: {rank.value}",
            f"Final Score: {score}",
            "",
            "COMBAT STATISTICS:",
            f"  Enemy Ships Destroyed: {self.enemy_ships_destroyed}",
            f"  Tonnage Sunk: {self.enemy_tonnage_sunk}",
            f"  Capital Ships Sunk: {self.capital_ships_sunk}",
            "",
            "CREW STATISTICS:",
            f"  Crew Alive at War End: {self.crew_alive_at_end}/{self.crew_total_recruited}",
            f"  Desertions: {self.crew_deserted}",
            f"  Mutinies: {self.crew_mutinies}",
            f"  Final Crew Loyalty: {self.crew_average_loyalty:.2%}",
            f"  Perfect Loyalty: {'Yes ✓' if self.perfect_loyalty_end else 'No ✗'}",
            "",
            "HEROIC ACTIONS:",
            f"  Survivors Rescued: {self.survivors_rescued}",
            f"  Near-Death Escapes: {self.near_death_escapes}",
            f"  Missions Completed: {self.missions_completed}",
            f"  War Turns Survived: {self.turns_survived}",
            "",
            f"War Victory: {'Yes ✓✓✓' if self.war_victory else 'No'}",
            "",
            "═" * 60,
        ]
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'enemy_ships_destroyed': self.enemy_ships_destroyed,
            'enemy_tonnage_sunk': self.enemy_tonnage_sunk,
            'capital_ships_sunk': self.capital_ships_sunk,
            'crew_alive_at_end': self.crew_alive_at_end,
            'crew_total_recruited': self.crew_total_recruited,
            'crew_deserted': self.crew_deserted,
            'crew_mutinies': self.crew_mutinies,
            'crew_average_loyalty': self.crew_average_loyalty,
            'perfect_loyalty_end': self.perfect_loyalty_end,
            'survivors_rescued': self.survivors_rescued,
            'near_death_escapes': self.near_death_escapes,
            'missions_completed': self.missions_completed,
            'turns_survived': self.turns_survived,
            'war_victory': self.war_victory,
            'final_rank': self.calculate_war_rank().value,
            'final_score': self.calculate_final_score(),
        }
