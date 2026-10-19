"""
Enhanced Game Flow Manager - Coordinates all game systems
Manages:
- Game objectives and mission flow
- Random events and special encounters
- War progression and dynamic difficulty
- Supply scarcity tied to war status
- Experience and crew progression
- Captain's log and journal integration
- Endgame conditions and winning scenarios
"""

import random
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime


class WarStatus(Enum):
    """Current status of war - affects available missions, supply levels, enemy behavior"""
    STALEMATE = "stalemate"           # Early war - balanced forces
    AXIS_ADVANTAGE = "axis_advantage" # Axis powers winning - harder missions
    ALLIED_ADVANTAGE = "allied_advantage"  # Allies winning - different mission pool
    AXIS_DECLINE = "axis_decline"     # Axis losing - desperate missions, supply scarce
    ENDGAME = "endgame"               # War ending - final missions available


class GameObjective(Enum):
    """Overall game objectives - player can pursue multiple"""
    DESTROY_ENEMY_SHIPPING = "destroy_shipping"  # Sink enemy merchant/combat vessels
    GATHER_INTELLIGENCE = "gather_intelligence"   # Reconnaissance missions
    PROTECT_SUPPLY_LINES = "protect_supplies"    # Defend own shipping
    SURVIVE_WAR = "survive_war"                    # Make it to war end
    BUILD_LEGENDARY_CREW = "legendary_crew"       # Maximize crew stats and loyalty
    DISCOVER_SECRETS = "discover_secrets"         # Eldritch/mysterious events
    STRATEGIC_VICTORY = "strategic_victory"       # Control regions/achieve objectives


@dataclass
class WarProgressionData:
    """Tracks war progression and influences game difficulty/missions"""
    year: int = 1939
    month: int = 9  # September 1939 - war start
    turn: int = 0
    war_status: WarStatus = WarStatus.STALEMATE
    
    # War outcome influences (0-100%)
    axis_advantage: float = 50.0  # Swings based on player actions and random events
    allied_advantage: float = 50.0
    
    # Tracked metrics
    axis_ships_sunk_by_player: int = 0
    allied_ships_sunk_by_player: int = 0
    player_submarine_damage: int = 0  # Times damaged/sunk and repaired
    crew_losses: int = 0
    successful_missions: int = 0
    failed_missions: int = 0
    
    # Supply situation (affects availability and rationing)
    global_supply_shortage: float = 0.0  # 0-1 scale, 1=critical shortage
    axis_fuel_shortage: float = 0.0
    allied_fuel_shortage: float = 0.0
    
    # Randomization for replayability
    random_seed: int = 0
    
    def advance_month(self):
        """Advance game time by one month"""
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
    
    def calculate_war_status(self):
        """Determine current war status based on progression"""
        if self.year < 1941:
            self.war_status = WarStatus.STALEMATE
        elif self.year < 1942:
            if self.axis_advantage > 55:
                self.war_status = WarStatus.AXIS_ADVANTAGE
            else:
                self.war_status = WarStatus.STALEMATE
        elif self.year < 1943:
            if self.axis_advantage > 60:
                self.war_status = WarStatus.AXIS_ADVANTAGE
            elif self.allied_advantage > 60:
                self.war_status = WarStatus.ALLIED_ADVANTAGE
            else:
                self.war_status = WarStatus.STALEMATE
        elif self.year < 1944:
            if self.allied_advantage > 65:
                self.war_status = WarStatus.ALLIED_ADVANTAGE
            else:
                self.war_status = WarStatus.STALEMATE
        elif self.year < 1945:
            if self.allied_advantage > 75:
                self.war_status = WarStatus.ALLIED_ADVANTAGE
            else:
                self.war_status = WarStatus.STALEMATE
        else:  # 1945+
            if self.year >= 1945 and self.month >= 9:
                self.war_status = WarStatus.ENDGAME
            elif self.allied_advantage > 85:
                self.war_status = WarStatus.AXIS_DECLINE
            else:
                self.war_status = WarStatus.ALLIED_ADVANTAGE
    
    def get_date_string(self) -> str:
        """Return human-readable date"""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return f"{months[self.month-1]} {self.year}"
    
    def update_supply_shortage(self):
        """Calculate global supply shortage based on war status"""
        base_shortage = 0.1  # Always some shortage
        
        if self.war_status == WarStatus.AXIS_ADVANTAGE:
            self.global_supply_shortage = 0.2 + random.random() * 0.2  # 20-40%
            self.axis_fuel_shortage = 0.1
            self.allied_fuel_shortage = 0.4
        elif self.war_status == WarStatus.ALLIED_ADVANTAGE:
            self.global_supply_shortage = 0.15 + random.random() * 0.15  # 15-30%
            self.axis_fuel_shortage = 0.6
            self.allied_fuel_shortage = 0.1
        elif self.war_status == WarStatus.AXIS_DECLINE:
            self.global_supply_shortage = 0.5 + random.random() * 0.3  # 50-80% (critical)
            self.axis_fuel_shortage = 0.8
            self.allied_fuel_shortage = 0.05
        elif self.war_status == WarStatus.ENDGAME:
            self.global_supply_shortage = 0.7 + random.random() * 0.2  # 70-90% (severe)
            self.axis_fuel_shortage = 0.9
            self.allied_fuel_shortage = 0.3
        else:  # STALEMATE
            self.global_supply_shortage = base_shortage + random.random() * 0.15  # 10-25%
            self.axis_fuel_shortage = 0.3
            self.allied_fuel_shortage = 0.3


@dataclass
class RandomEvent:
    """Random events that can occur during game"""
    event_id: str
    name: str
    description: str
    event_type: str  # weather, encounter, opportunity, disaster, intelligence
    probability: float  # 0-1, chance per turn
    impact_on_war: float = 0.0  # -1 to +1, negative helps player's enemy
    xp_reward: int = 0
    supplies_affected: Dict[str, float] = field(default_factory=dict)
    crew_impact: float = 0.0  # Morale change
    turn_triggered: int = -1
    
    def trigger(self) -> str:
        """Generate event message when triggered"""
        return f"EVENT: {self.name} - {self.description}"


class GameFlowManager:
    """Main coordinator for game objectives, events, war progression, and endgame"""
    
    def __init__(self):
        """Initialize game flow manager"""
        self.war_progression = WarProgressionData()
        self.player_objectives: List[GameObjective] = [
            GameObjective.DESTROY_ENEMY_SHIPPING,
            GameObjective.SURVIVE_WAR
        ]
        
        # Mission tracking
        self.active_missions: List[Dict] = []
        self.completed_missions: List[Dict] = []
        self.failed_missions: List[Dict] = []
        self.mission_count = 0
        
        # Random events pool
        self.random_events = self._initialize_random_events()
        self.triggered_events: List[RandomEvent] = []
        self.event_counter = 0
        
        # Captain's log entries
        self.log_entries: List[Dict] = []
        
        # Special encounters (eldritch, legendary enemies, etc)
        self.special_encounters_available: List[str] = []
        self.special_encounters_completed: List[str] = []
        
        # Endgame state
        self.war_ended = False
        self.final_rank = None
        self.final_score = 0
        self.victory_type = None  # "commander", "survivor", "hero", "legendary", "failure"
    
    def _initialize_random_events(self) -> List[RandomEvent]:
        """Initialize pool of random events that can occur"""
        return [
            RandomEvent(
                event_id="storm_weather",
                name="Heavy Storm Encountered",
                description="Severe weather makes navigation difficult. Detection range reduced.",
                event_type="weather",
                probability=0.15,
                crew_impact=-0.05
            ),
            RandomEvent(
                event_id="convoy_sighted",
                name="Enemy Convoy Detected",
                description="Merchant convoy with light escort. Good opportunity for attack.",
                event_type="opportunity",
                probability=0.10,
                impact_on_war=-0.02,
                xp_reward=50
            ),
            RandomEvent(
                event_id="decoy_target",
                name="Decoy Formation",
                description="Allied intelligence reports decoy ships - avoid wasting torpedoes.",
                event_type="intelligence",
                probability=0.08,
                xp_reward=25
            ),
            RandomEvent(
                event_id="engine_trouble",
                name="Engine Malfunction",
                description="Temporary engine trouble. Must surface for repairs.",
                event_type="disaster",
                probability=0.06,
                impact_on_war=0.01,
                supplies_affected={"fuel": -0.1}
            ),
            RandomEvent(
                event_id="crew_celebration",
                name="Crew Celebration",
                description="Crew celebrates successful patrol. Morale boosted.",
                event_type="encounter",
                probability=0.12,
                crew_impact=0.15
            ),
            RandomEvent(
                event_id="spy_detected",
                name="Suspected Spy Onboard",
                description="Intelligence report suggests possible saboteur in crew.",
                event_type="disaster",
                probability=0.05,
                crew_impact=-0.10,
                impact_on_war=0.02
            ),
            RandomEvent(
                event_id="radio_intercept",
                name="Enemy Radio Intercept",
                description="Enemy communication intercepted. Suggests patrol route vulnerability.",
                event_type="intelligence",
                probability=0.09,
                xp_reward=40
            ),
            RandomEvent(
                event_id="supply_cache_found",
                name="Abandoned Supply Cache",
                description="Wreckage of friendly vessel found with salvageable supplies.",
                event_type="opportunity",
                probability=0.07,
                supplies_affected={"ammunition": 0.2, "food": 0.1}
            ),
            RandomEvent(
                event_id="mechanical_failure",
                name="Critical System Failure",
                description="Sonar/Torpedo system temporarily offline. Repairs underway.",
                event_type="disaster",
                probability=0.04,
                impact_on_war=0.03
            ),
            RandomEvent(
                event_id="depth_charge_attack",
                name="Surprise Depth Charge Attack",
                description="Enemy escort dropped depth charges. Emergency evasion!",
                event_type="disaster",
                probability=0.08,
                supplies_affected={"hull": -0.15},
                crew_impact=-0.12
            ),
            RandomEvent(
                event_id="rare_sighting",
                name="Rare Naval Asset Sighted",
                description="Aircraft carrier or battleship spotted. Extremely dangerous target.",
                event_type="opportunity",
                probability=0.03,
                xp_reward=200
            ),
            RandomEvent(
                event_id="crew_illness",
                name="Infectious Disease Outbreak",
                description="Illness spreads through confined crew quarters. Some crew incapacitated.",
                event_type="disaster",
                probability=0.05,
                crew_impact=-0.20,
                supplies_affected={"medicine": -0.3}
            ),
            RandomEvent(
                event_id="rendezvous_success",
                name="Successful Supply Rendezvous",
                description="Resupply mission successful. Critical supplies replenished.",
                event_type="opportunity",
                probability=0.06,
                supplies_affected={"ammunition": 0.4, "fuel": 0.3, "food": 0.2}
            ),
            RandomEvent(
                event_id="lucky_escape",
                name="Narrow Escape",
                description="Enemy detection avoided by mere seconds. Crew alert and ready.",
                event_type="encounter",
                probability=0.10,
                crew_impact=0.08,
                xp_reward=60
            ),
            RandomEvent(
                event_id="old_enemy_returns",
                name="Old Enemy Returns",
                description="Previously-damaged enemy vessel returns. Opportunity for rematch.",
                event_type="opportunity",
                probability=0.04,
                impact_on_war=-0.05,
                xp_reward=150
            ),
        ]
    
    def tick(self, game) -> List[Dict]:
        """Main game flow update - called once per turn"""
        events_triggered = []
        
        self.war_progression.turn += 1
        
        # Every 30 turns = approximately 1 month game time
        if self.war_progression.turn % 30 == 0:
            self.war_progression.advance_month()
            self._monthly_war_update(game)
        
        # Update war status based on progression
        self.war_progression.calculate_war_status()
        
        # Update supply shortage based on war status
        self.war_progression.update_supply_shortage()
        
        # Random event check (every turn, small probability)
        event = self._check_random_events()
        if event:
            events_triggered.append({
                'type': 'random_event',
                'event': event
            })
            self._apply_random_event_effects(game, event)
        
        # Check mission progress and completion
        mission_events = self._update_missions(game)
        events_triggered.extend(mission_events)
        
        # Check endgame conditions
        endgame_event = self._check_endgame_conditions(game)
        if endgame_event:
            events_triggered.append(endgame_event)
        
        return events_triggered
    
    def _monthly_war_update(self, game):
        """Update war status monthly"""
        date_string = self.war_progression.get_date_string()
        
        # Historical war progression
        if self.war_progression.year == 1939:
            # Early war - minor axis advantage
            self.war_progression.axis_advantage += random.uniform(-2, 3)
        elif self.war_progression.year == 1940:
            # Germany wins in France - axis advantage
            self.war_progression.axis_advantage += random.uniform(1, 5)
        elif self.war_progression.year == 1941:
            # Germany invades Russia - balance shifts
            if self.war_progression.month >= 6:  # June 1941 Operation Barbarossa
                self.war_progression.axis_advantage += random.uniform(2, 8)
        elif self.war_progression.year == 1942:
            # Tide beginning to turn
            if self.war_progression.month >= 11:  # Stalingrad turns
                self.war_progression.allied_advantage += random.uniform(2, 6)
            else:
                self.war_progression.axis_advantage += random.uniform(-1, 3)
        elif self.war_progression.year == 1943:
            # Axis losing ground
            self.war_progression.allied_advantage += random.uniform(3, 8)
            self.war_progression.axis_advantage -= random.uniform(1, 4)
        elif self.war_progression.year == 1944:
            # D-Day and beyond - strong allied advantage
            self.war_progression.allied_advantage += random.uniform(4, 10)
            self.war_progression.axis_advantage -= random.uniform(2, 5)
        elif self.war_progression.year >= 1945:
            # War ending
            self.war_progression.allied_advantage += random.uniform(5, 15)
            self.war_progression.axis_advantage -= random.uniform(3, 8)
        
        # Clamp to valid range
        self.war_progression.axis_advantage = max(0, min(100, self.war_progression.axis_advantage))
        self.war_progression.allied_advantage = max(0, min(100, self.war_progression.allied_advantage))
        
        # Log war update
        self._log_entry(f"WAR UPDATE ({date_string}): {self.war_progression.war_status.value}")
    
    def _check_random_events(self) -> Optional[RandomEvent]:
        """Check if a random event triggers this turn"""
        for event in self.random_events:
            if random.random() < event.probability:
                event.turn_triggered = self.war_progression.turn
                self.triggered_events.append(event)
                self.event_counter += 1
                return event
        return None
    
    def _apply_random_event_effects(self, game, event: RandomEvent):
        """Apply effects of random event to game state"""
        # Log event
        self._log_entry(event.trigger())
        
        # Crew morale impact
        if event.crew_impact != 0 and game.crew_roster:
            try:
                current_morale = game.crew_roster.get_average_morale() / 100.0
                new_morale = max(0, min(1.0, current_morale + event.crew_impact))
                for crew_member in game.crew_roster.crew_members.values():
                    crew_member.morale = new_morale * 100
            except:
                pass
        
        # Supply impact
        if event.supplies_affected and game.supply_inventory:
            try:
                for resource_name, amount in event.supplies_affected.items():
                    # Find matching resource and apply effect
                    for resource in game.supply_inventory.resources:
                        if resource_name.lower() in resource.name.lower():
                            resource.consume(int(resource.quantity * abs(amount)))
                            break
            except:
                pass
        
        # War impact
        if event.impact_on_war != 0:
            self.war_progression.axis_advantage += event.impact_on_war * 10
        
        # XP reward
        if event.xp_reward > 0 and game.player_stats:
            try:
                skill = random.choice(list(game.player_stats.skills.keys()))
                game.player_stats.gain_xp(skill, event.xp_reward)
            except:
                pass
    
    def _update_missions(self, game) -> List[Dict]:
        """Update active mission progress"""
        events = []
        
        # Check mission time limits and progress
        for mission in self.active_missions[:]:
            mission['turns_elapsed'] += 1
            
            # Simulate progress (simplified)
            mission['progress'] = min(1.0, mission['progress'] + random.uniform(0.01, 0.05))
            
            # Check completion
            if mission['progress'] >= 1.0:
                self._complete_mission(game, mission)
                events.append({
                    'type': 'mission_completed',
                    'mission': mission
                })
                self.active_missions.remove(mission)
                self.completed_missions.append(mission)
            
            # Check time limit failure
            elif mission.get('time_limit') and mission['turns_elapsed'] >= mission['time_limit']:
                self._fail_mission(game, mission, "Time limit exceeded")
                events.append({
                    'type': 'mission_failed',
                    'mission': mission
                })
                self.active_missions.remove(mission)
                self.failed_missions.append(mission)
        
        return events
    
    def _complete_mission(self, game, mission: Dict):
        """Handle mission completion"""
        reward_xp = mission.get('reward_xp', 100)
        reward_credits = mission.get('reward_credits', 1000)
        
        self._log_entry(f"✓ MISSION COMPLETE: {mission.get('name', 'Unknown')} (+{reward_xp} XP, +{reward_credits} credits)")
        
        # Record in war progression
        self.war_progression.successful_missions += 1
        
        # Update war status based on mission type
        if 'destroy' in mission.get('type', '').lower():
            self.war_progression.axis_advantage -= 1
        elif 'patrol' in mission.get('type', '').lower():
            self.war_progression.axis_advantage -= 0.5
        
        # Award XP to player
        if game.player_stats:
            try:
                game.player_stats.gain_xp('crew_leadership', reward_xp)
            except:
                pass
        
        # Crew morale boost
        if game.crew_roster:
            try:
                current_morale = game.crew_roster.get_average_morale()
                game.crew_roster.crew_count_morale = min(100, current_morale + 5)
            except:
                pass
    
    def _fail_mission(self, game, mission: Dict, reason: str = ""):
        """Handle mission failure"""
        penalty_xp = mission.get('penalty_xp', 25)
        
        self._log_entry(f"✗ MISSION FAILED: {mission.get('name', 'Unknown')} ({reason})")
        
        # Record in war progression
        self.war_progression.failed_missions += 1
        self.war_progression.axis_advantage += 1  # Failure helps enemy
        
        # Penalize XP (less than success)
        if game.player_stats:
            try:
                game.player_stats.total_xp -= penalty_xp
            except:
                pass
    
    def _check_endgame_conditions(self, game) -> Optional[Dict]:
        """Check if game should end and why"""
        
        # Player submarine destroyed
        if game.submarine and hasattr(game.submarine, 'systems'):
            hull = getattr(game.submarine.systems, 'hull', 1.0)
            if hull <= 0:
                self.war_ended = True
                self.victory_type = "failure"
                return {
                    'type': 'game_over',
                    'reason': 'SUBMARINE DESTROYED',
                    'victory': False
                }
        
        # All crew dead
        if game.crew_roster and game.crew_roster.crew_count <= 0:
            self.war_ended = True
            self.victory_type = "failure"
            return {
                'type': 'game_over',
                'reason': 'ALL CREW LOST',
                'victory': False
            }
        
        # War ended (late 1945)
        if self.war_progression.year >= 1945 and self.war_progression.month >= 9:
            self.war_ended = True
            self.victory_type = self._determine_victory_type(game)
            return {
                'type': 'war_ended',
                'reason': 'WAR CONCLUDED',
                'victory_type': self.victory_type,
                'victory': True
            }
        
        # Extended survival (reached 1944)
        if self.war_progression.year >= 1944 and not hasattr(self, '_survival_milestone_1944'):
            self._survival_milestone_1944 = True
            self._log_entry("You've reached 1944! War turning point.")
            if game.player_stats:
                try:
                    game.player_stats.gain_xp('evasion', 200)
                except:
                    pass
        
        return None
    
    def _determine_victory_type(self, game) -> str:
        """Determine victory type based on player stats"""
        total_kills = 0
        crew_alive = 0
        missions_completed = len(self.completed_missions)
        
        if game.player_stats:
            try:
                total_kills = game.player_stats.career_stats.get('ships_sunk', 0)
            except:
                pass
        
        if game.crew_roster:
            crew_alive = game.crew_roster.crew_count
        
        # Determine victory type
        if total_kills >= 50 and missions_completed >= 20 and crew_alive >= 40:
            return "legendary"
        elif total_kills >= 25 and crew_alive >= 30:
            return "commander"
        elif total_kills >= 10:
            return "hero"
        else:
            return "survivor"
    
    def add_mission(self, mission: Dict):
        """Add new mission to active pool"""
        mission['mission_id'] = self.mission_count
        mission['turns_elapsed'] = 0
        mission['progress'] = 0.0
        mission['accepted_turn'] = self.war_progression.turn
        self.active_missions.append(mission)
        self.mission_count += 1
        self._log_entry(f"NEW MISSION: {mission.get('name', 'Unknown')} ({mission.get('type', 'patrol')})")
    
    def _log_entry(self, message: str):
        """Add entry to captain's log"""
        entry = {
            'turn': self.war_progression.turn,
            'date': self.war_progression.get_date_string(),
            'message': message,
            'war_status': self.war_progression.war_status.value,
            'timestamp': datetime.now().isoformat()
        }
        self.log_entries.append(entry)
        
        # Keep last 1000 entries
        if len(self.log_entries) > 1000:
            self.log_entries = self.log_entries[-1000:]
    
    def get_captain_log(self, last_n: int = 20) -> List[Dict]:
        """Get last N entries from captain's log"""
        return self.log_entries[-last_n:]
    
    def get_war_summary(self) -> str:
        """Get current war summary for status display"""
        return f"""
═══ WAR STATUS ═══
Date: {self.war_progression.get_date_string()}
Status: {self.war_progression.war_status.value.upper()}
Axis Advantage: {self.war_progression.axis_advantage:.1f}%
Allied Advantage: {self.war_progression.allied_advantage:.1f}%

Supply Shortage: {self.war_progression.global_supply_shortage*100:.0f}%
Missions Completed: {len(self.completed_missions)}
Missions Failed: {len(self.failed_missions)}
Random Events: {self.event_counter}
"""
    
    def get_objectives_status(self) -> str:
        """Get player's current objective status"""
        lines = ["═══ OBJECTIVES ═══"]
        for objective in self.player_objectives:
            lines.append(f"  • {objective.value.upper()}")
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Serialize for save/load"""
        return {
            'war_progression': {
                'year': self.war_progression.year,
                'month': self.war_progression.month,
                'turn': self.war_progression.turn,
                'war_status': self.war_progression.war_status.value,
                'axis_advantage': self.war_progression.axis_advantage,
                'allied_advantage': self.war_progression.allied_advantage
            },
            'missions': {
                'active': self.active_missions,
                'completed': self.completed_missions,
                'failed': self.failed_missions
            },
            'log_entries': self.log_entries[-100:],  # Keep recent entries
            'endgame': {
                'war_ended': self.war_ended,
                'victory_type': self.victory_type,
                'final_score': self.final_score
            }
        }
