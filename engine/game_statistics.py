"""
Game Statistics System - Tracks all player achievements and events.
Records crew deaths, sabotage attempts, captured spies, ships sunk, missions completed,
and all other measurable game events (except eldritch encounters which remain secretive).
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import json
import os
from datetime import datetime


class StatisticType(Enum):
    """Types of statistics tracked."""
    SHIPS_SUNK = "ships_sunk"
    CREW_DEATHS = "crew_deaths"
    CREW_INJURED = "crew_injured"
    CREW_RECRUITED = "crew_recruited"
    MISSIONS_COMPLETED = "missions_completed"
    MISSIONS_FAILED = "missions_failed"
    ENEMY_CONTACTS = "enemy_contacts"
    TORPEDOES_FIRED = "torpedoes_fired"
    TORPEDOES_HIT = "torpedoes_hit"
    DEPTH_CHARGES_SURVIVED = "depth_charges_survived"
    COMPARTMENTS_FLOODED = "compartments_flooded"
    REPAIRS_COMPLETED = "repairs_completed"
    SPIES_CAUGHT = "spies_caught"
    SABOTAGES_DETECTED = "sabotages_detected"
    SABOTAGES_SUCCESSFUL = "sabotages_successful"
    SUPPLY_SHORTAGES = "supply_shortages"
    DAYS_AT_SEA = "days_at_sea"
    SURFACE_SIGHTINGS = "surface_sightings"
    NAVAL_BATTLES = "naval_battles"
    CONVOY_ENGAGEMENTS = "convoy_engagements"
    SUCCESSFUL_ESCAPES = "successful_escapes"
    CREW_MORALE_CRISES = "crew_morale_crises"
    CREW_STRESS_INCIDENTS = "crew_stress_incidents"
    EQUIPMENT_FAILURES = "equipment_failures"
    SUCCESSFUL_PATROLS = "successful_patrols"
    TOTAL_TONNAGE_SUNK = "total_tonnage_sunk"


@dataclass
class StatisticEvent:
    """Represents a single notable event for statistics."""
    stat_type: StatisticType
    turn: int
    value: int = 1
    details: Optional[str] = None
    crew_involved: Optional[List[str]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class GameStatistics:
    """Central statistics tracker for the game."""
    
    def __init__(self):
        """Initialize statistics system."""
        self.stats: Dict[StatisticType, int] = {stat_type: 0 for stat_type in StatisticType}
        self.events: List[StatisticEvent] = []
        self.start_time: datetime = datetime.now()
        self.game_start_turn: int = 0
        self.session_id: str = self._generate_session_id()
        
        # Detailed tracking
        self.ship_kills: List[Dict] = []  # Ships sunk with details
        self.crew_deaths_log: List[Dict] = []  # Crew deaths with details
        self.spies_caught_log: List[Dict] = []  # Captured spies
        self.sabotages_log: List[Dict] = []  # Sabotage attempts
        self.missions_log: List[Dict] = []  # Mission records
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def record_stat(self, stat_type: StatisticType, turn: int, value: int = 1, 
                   details: Optional[str] = None, crew_involved: Optional[List[str]] = None):
        """Record a statistic event."""
        event = StatisticEvent(
            stat_type=stat_type,
            turn=turn,
            value=value,
            details=details,
            crew_involved=crew_involved or []
        )
        
        self.stats[stat_type] = self.stats.get(stat_type, 0) + value
        self.events.append(event)
    
    def record_ship_sunk(self, turn: int, ship_type: str, tonnage: int, 
                        crew_involved: Optional[List[str]] = None):
        """Record a ship sunk."""
        self.record_stat(StatisticType.SHIPS_SUNK, turn, details=f"{ship_type} ({tonnage}t)", 
                        crew_involved=crew_involved)
        self.record_stat(StatisticType.TOTAL_TONNAGE_SUNK, turn, value=tonnage)
        
        self.ship_kills.append({
            'turn': turn,
            'type': ship_type,
            'tonnage': tonnage,
            'crew_involved': crew_involved or [],
            'timestamp': datetime.now().isoformat()
        })
    
    def record_crew_death(self, turn: int, crew_name: str, rank: str, cause: str, 
                         details: Optional[str] = None):
        """Record crew member death."""
        self.record_stat(StatisticType.CREW_DEATHS, turn, details=f"{crew_name} ({rank}) - {cause}")
        
        self.crew_deaths_log.append({
            'turn': turn,
            'name': crew_name,
            'rank': rank,
            'cause': cause,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_crew_injured(self, turn: int, crew_name: str, injury_type: str):
        """Record crew member injury."""
        self.record_stat(StatisticType.CREW_INJURED, turn, details=f"{crew_name} - {injury_type}")
    
    def record_crew_recruited(self, turn: int, crew_name: str, rank: str, faction: str = None):
        """Record crew member recruitment."""
        self.record_stat(StatisticType.CREW_RECRUITED, turn, details=f"{crew_name} ({rank})")
    
    def record_mission_completed(self, turn: int, mission_type: str, details: Optional[str] = None,
                                rewards: Optional[Dict] = None):
        """Record completed mission."""
        self.record_stat(StatisticType.MISSIONS_COMPLETED, turn, details=mission_type)
        
        self.missions_log.append({
            'turn': turn,
            'type': mission_type,
            'status': 'completed',
            'details': details,
            'rewards': rewards or {},
            'timestamp': datetime.now().isoformat()
        })
    
    def record_mission_failed(self, turn: int, mission_type: str, reason: str):
        """Record failed mission."""
        self.record_stat(StatisticType.MISSIONS_FAILED, turn, details=f"{mission_type} - {reason}")
        
        self.missions_log.append({
            'turn': turn,
            'type': mission_type,
            'status': 'failed',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_enemy_contact(self, turn: int, contact_type: str, distance: int):
        """Record enemy contact."""
        self.record_stat(StatisticType.ENEMY_CONTACTS, turn, details=f"{contact_type} at {distance}m")
    
    def record_torpedo_fired(self, turn: int, target: str):
        """Record torpedo fired."""
        self.record_stat(StatisticType.TORPEDOES_FIRED, turn, details=f"At {target}")
    
    def record_torpedo_hit(self, turn: int, target: str, damage: float):
        """Record torpedo hit."""
        self.record_stat(StatisticType.TORPEDOES_HIT, turn, details=f"{target} - {damage*100:.0f}% damage")
    
    def record_depth_charge_survived(self, turn: int, count: int, damage: float):
        """Record surviving depth charge attack."""
        self.record_stat(StatisticType.DEPTH_CHARGES_SURVIVED, turn, value=count, 
                        details=f"{count} charges - {damage*100:.0f}% damage")
    
    def record_compartment_flooded(self, turn: int, compartment_name: str):
        """Record flooded compartment."""
        self.record_stat(StatisticType.COMPARTMENTS_FLOODED, turn, details=compartment_name)
    
    def record_repair_completed(self, turn: int, compartment_name: str, restore_amount: float):
        """Record completed repair."""
        self.record_stat(StatisticType.REPAIRS_COMPLETED, turn, details=f"{compartment_name} +{restore_amount*100:.0f}%")
    
    def record_spy_caught(self, turn: int, spy_name: str, cover_name: str, details: Optional[str] = None):
        """Record captured spy."""
        self.record_stat(StatisticType.SPIES_CAUGHT, turn, details=f"{spy_name} ({cover_name})")
        
        self.spies_caught_log.append({
            'turn': turn,
            'real_name': spy_name,
            'cover_name': cover_name,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_sabotage_detected(self, turn: int, sabotage_type: str, severity: float):
        """Record detected sabotage."""
        self.record_stat(StatisticType.SABOTAGES_DETECTED, turn, details=f"{sabotage_type} (severity: {severity:.1f})")
        
        self.sabotages_log.append({
            'turn': turn,
            'type': sabotage_type,
            'status': 'detected',
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_sabotage_successful(self, turn: int, sabotage_type: str, damage: float):
        """Record successful sabotage."""
        self.record_stat(StatisticType.SABOTAGES_SUCCESSFUL, turn, details=f"{sabotage_type} - {damage*100:.0f}% damage")
        
        self.sabotages_log.append({
            'turn': turn,
            'type': sabotage_type,
            'status': 'successful',
            'damage': damage,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_supply_shortage(self, turn: int, resource_type: str, remaining: float):
        """Record supply shortage."""
        self.record_stat(StatisticType.SUPPLY_SHORTAGES, turn, details=f"{resource_type} - {remaining:.0f}% remaining")
    
    def record_surface_sighting(self, turn: int, witness_type: str):
        """Record sighting by surface vessel."""
        self.record_stat(StatisticType.SURFACE_SIGHTINGS, turn, details=f"Sighted by {witness_type}")
    
    def record_naval_battle(self, turn: int, opponent_type: str, result: str):
        """Record naval engagement."""
        self.record_stat(StatisticType.NAVAL_BATTLES, turn, details=f"{opponent_type} - {result}")
    
    def record_convoy_engagement(self, turn: int, convoy_size: int, ships_sunk: int):
        """Record convoy engagement."""
        self.record_stat(StatisticType.CONVOY_ENGAGEMENTS, turn, 
                        details=f"Convoy of {convoy_size} - {ships_sunk} sunk")
    
    def record_successful_escape(self, turn: int, from_threat: str, method: str):
        """Record successful escape."""
        self.record_stat(StatisticType.SUCCESSFUL_ESCAPES, turn, details=f"From {from_threat} by {method}")
    
    def record_crew_morale_crisis(self, turn: int, severity: str, trigger: str):
        """Record crew morale crisis."""
        self.record_stat(StatisticType.CREW_MORALE_CRISES, turn, details=f"{severity} - {trigger}")
    
    def record_crew_stress_incident(self, turn: int, crew_name: str, incident_type: str):
        """Record crew stress incident."""
        self.record_stat(StatisticType.CREW_STRESS_INCIDENTS, turn, details=f"{crew_name} - {incident_type}")
    
    def record_equipment_failure(self, turn: int, equipment: str, impact: str):
        """Record equipment failure."""
        self.record_stat(StatisticType.EQUIPMENT_FAILURES, turn, details=f"{equipment} - {impact}")
    
    def record_successful_patrol(self, turn: int, patrol_duration: int, objectives_met: int):
        """Record successful patrol completion."""
        self.record_stat(StatisticType.SUCCESSFUL_PATROLS, turn, 
                        details=f"{patrol_duration} days - {objectives_met} objectives")
    
    def get_stat(self, stat_type: StatisticType) -> int:
        """Get current value of a statistic."""
        return self.stats.get(stat_type, 0)
    
    def get_all_stats(self) -> Dict[StatisticType, int]:
        """Get all statistics."""
        return self.stats.copy()
    
    def get_events_for_stat(self, stat_type: StatisticType) -> List[StatisticEvent]:
        """Get all events for a specific statistic type."""
        return [e for e in self.events if e.stat_type == stat_type]
    
    def get_events_in_range(self, start_turn: int, end_turn: int) -> List[StatisticEvent]:
        """Get events within turn range."""
        return [e for e in self.events if start_turn <= e.turn <= end_turn]
    
    def get_summary_report(self) -> str:
        """Get summary statistics report."""
        from ui.color_system import _color_system
        
        report = ""
        report += _color_system.header("═══ GAME STATISTICS ═══\n")
        
        # Combat stats
        report += _color_system.label("COMBAT RECORD:\n")
        report += f"  Ships Sunk: {_color_system.colorize(str(self.get_stat(StatisticType.SHIPS_SUNK)), 'bright_red')}\n"
        report += f"  Total Tonnage: {_color_system.colorize(f'{self.get_stat(StatisticType.TOTAL_TONNAGE_SUNK)}t', 'bright_yellow')}\n"
        report += f"  Enemy Contacts: {self.get_stat(StatisticType.ENEMY_CONTACTS)}\n"
        report += f"  Torpedoes Fired: {self.get_stat(StatisticType.TORPEDOES_FIRED)}\n"
        report += f"  Torpedoes Hit: {self.get_stat(StatisticType.TORPEDOES_HIT)}\n"
        
        if self.get_stat(StatisticType.TORPEDOES_FIRED) > 0:
            hit_rate = (self.get_stat(StatisticType.TORPEDOES_HIT) / self.get_stat(StatisticType.TORPEDOES_FIRED)) * 100
            report += f"  Hit Rate: {hit_rate:.1f}%\n"
        report += "\n"
        
        # Crew stats
        report += _color_system.label("CREW STATUS:\n")
        report += f"  Recruited: {self.get_stat(StatisticType.CREW_RECRUITED)}\n"
        report += f"  Deaths: {_color_system.colorize(str(self.get_stat(StatisticType.CREW_DEATHS)), 'bright_red')}\n"
        report += f"  Injured: {self.get_stat(StatisticType.CREW_INJURED)}\n"
        report += f"  Morale Crises: {_color_system.colorize(str(self.get_stat(StatisticType.CREW_MORALE_CRISES)), 'bright_yellow')}\n"
        report += f"  Stress Incidents: {self.get_stat(StatisticType.CREW_STRESS_INCIDENTS)}\n"
        report += "\n"
        
        # Mission stats
        report += _color_system.label("MISSION RECORD:\n")
        report += f"  Completed: {_color_system.colorize(str(self.get_stat(StatisticType.MISSIONS_COMPLETED)), 'bright_green')}\n"
        report += f"  Failed: {_color_system.colorize(str(self.get_stat(StatisticType.MISSIONS_FAILED)), 'bright_red')}\n"
        report += f"  Successful Patrols: {self.get_stat(StatisticType.SUCCESSFUL_PATROLS)}\n"
        report += "\n"
        
        # Defense stats
        report += _color_system.label("DEFENSE & SURVIVAL:\n")
        report += f"  Depth Charges Survived: {self.get_stat(StatisticType.DEPTH_CHARGES_SURVIVED)}\n"
        report += f"  Compartments Flooded: {self.get_stat(StatisticType.COMPARTMENTS_FLOODED)}\n"
        report += f"  Repairs Completed: {self.get_stat(StatisticType.REPAIRS_COMPLETED)}\n"
        report += f"  Successful Escapes: {_color_system.colorize(str(self.get_stat(StatisticType.SUCCESSFUL_ESCAPES)), 'bright_green')}\n"
        report += f"  Equipment Failures: {self.get_stat(StatisticType.EQUIPMENT_FAILURES)}\n"
        report += "\n"
        
        # Security stats
        report += _color_system.label("SECURITY:\n")
        report += f"  Spies Caught: {_color_system.colorize(str(self.get_stat(StatisticType.SPIES_CAUGHT)), 'bright_yellow')}\n"
        report += f"  Sabotages Detected: {_color_system.colorize(str(self.get_stat(StatisticType.SABOTAGES_DETECTED)), 'bright_yellow')}\n"
        report += f"  Sabotages Successful: {_color_system.colorize(str(self.get_stat(StatisticType.SABOTAGES_SUCCESSFUL)), 'bright_red')}\n"
        report += f"  Surface Sightings: {self.get_stat(StatisticType.SURFACE_SIGHTINGS)}\n"
        report += "\n"
        
        # Resource stats
        report += _color_system.label("RESOURCES:\n")
        report += f"  Supply Shortages: {self.get_stat(StatisticType.SUPPLY_SHORTAGES)}\n"
        report += "\n"
        
        return report
    
    def get_detailed_report(self) -> str:
        """Get detailed statistics report with event logs."""
        from ui.color_system import _color_system
        
        report = self.get_summary_report()
        
        # Ship kills
        if self.ship_kills:
            report += _color_system.label("SHIPS SUNK:\n")
            for i, kill in enumerate(self.ship_kills[-10:], 1):  # Last 10
                report += f"  {i}. {kill['type']} ({kill['tonnage']}t) - Turn {kill['turn']}\n"
            if len(self.ship_kills) > 10:
                report += f"  ... and {len(self.ship_kills) - 10} more\n"
            report += "\n"
        
        # Crew deaths
        if self.crew_deaths_log:
            report += _color_system.label("CREW LOSSES:\n")
            for i, death in enumerate(self.crew_deaths_log[-10:], 1):  # Last 10
                report += f"  {i}. {death['name']} ({death['rank']}) - {death['cause']} (Turn {death['turn']})\n"
            if len(self.crew_deaths_log) > 10:
                report += f"  ... and {len(self.crew_deaths_log) - 10} more\n"
            report += "\n"
        
        # Spies caught
        if self.spies_caught_log:
            report += _color_system.label("SPIES APPREHENDED:\n")
            for i, spy in enumerate(self.spies_caught_log, 1):
                report += f"  {i}. {spy['real_name']} (Cover: {spy['cover_name']}) - Turn {spy['turn']}\n"
            report += "\n"
        
        # Sabotages
        if self.sabotages_log:
            report += _color_system.label("SABOTAGE INCIDENTS:\n")
            for i, sab in enumerate(self.sabotages_log[-10:], 1):  # Last 10
                status = sab['status'].upper()
                details = f"- {sab['severity']:.1f} severity" if 'severity' in sab else f"- {sab['damage']*100:.0f}% damage"
                report += f"  {i}. {sab['type']} ({status}) {details} - Turn {sab['turn']}\n"
            if len(self.sabotages_log) > 10:
                report += f"  ... and {len(self.sabotages_log) - 10} more\n"
            report += "\n"
        
        # Missions
        if self.missions_log:
            report += _color_system.label("MISSION LOG:\n")
            for i, mission in enumerate(self.missions_log[-10:], 1):  # Last 10
                status = mission['status'].upper()
                report += f"  {i}. {mission['type']} ({status}) - Turn {mission['turn']}\n"
            if len(self.missions_log) > 10:
                report += f"  ... and {len(self.missions_log) - 10} more\n"
            report += "\n"
        
        return report
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'stats': {st.value: val for st, val in self.stats.items()},
            'events': [
                {
                    'type': e.stat_type.value,
                    'turn': e.turn,
                    'value': e.value,
                    'details': e.details,
                    'crew_involved': e.crew_involved,
                    'timestamp': e.timestamp
                }
                for e in self.events
            ],
            'ships_sunk': self.ship_kills,
            'crew_deaths': self.crew_deaths_log,
            'spies_caught': self.spies_caught_log,
            'sabotages': self.sabotages_log,
            'missions': self.missions_log
        }
    
    def save_to_file(self, filepath: str = None) -> str:
        """Save statistics to JSON file."""
        if filepath is None:
            stats_dir = os.path.join(os.path.dirname(__file__), '../data/statistics')
            os.makedirs(stats_dir, exist_ok=True)
            filepath = os.path.join(stats_dir, f"{self.session_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return filepath


# Global statistics instance
_statistics = None


def get_statistics() -> GameStatistics:
    """Get or create global statistics instance."""
    global _statistics
    if _statistics is None:
        _statistics = GameStatistics()
    return _statistics


def reset_statistics():
    """Reset statistics (for new game)."""
    global _statistics
    _statistics = GameStatistics()
