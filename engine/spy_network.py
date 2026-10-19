"""
Spy agents and sabotage system for submarines.
Enemy agents embedded in crew can sabotage critical systems.
"""
from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass, field
import random


class SabotageType(Enum):
    """Types of sabotage an agent can perform"""
    OXYGEN_LEAK = "oxygen_leak"           # Gradually reduces oxygen
    POWER_drain = "power_drain"            # Drains electrical power
    FUEL_CONTAMINATION = "fuel_contam"    # Contaminates fuel supply
    TORPEDO_SABOTAGE = "torpedo_sabotage" # Disables/destroys torpedoes
    COMMUNICATION_JAM = "comm_jam"        # Jams radio communications
    ENGINE_DAMAGE = "engine_damage"       # Damages propulsion system
    HULL_WEAKENING = "hull_damage"        # Weakens hull integrity
    COMPARTMENT_FLOODING = "flooding"     # Deliberately floods compartment
    SONAR_INTERFERENCE = "sonar_jam"      # Disables sonar systems
    CREW_SABOTAGE = "crew_sabotage"       # Causes internal conflict/accidents


class SpyStatus(Enum):
    """Status of spy agent"""
    UNKNOWN = "unknown"           # Not yet discovered
    SUSPECTED = "suspected"       # Under suspicion
    EXPOSED = "exposed"           # Discovered, under guard
    ELIMINATED = "eliminated"     # Dead or captured


@dataclass
class SabotageEvent:
    """Record of a sabotage event"""
    turn: int
    sabotage_type: SabotageType
    severity: float                # 0-1.0, how severe
    damage_amount: float           # Amount of damage caused
    detected: bool = False         # Whether crew detected it
    agent_id: Optional[int] = None # Which agent did it (may not be known)
    description: str = ""


@dataclass
class SpyAgent:
    """Enemy spy embedded in crew"""
    agent_id: int
    cover_name: str                # What crew knows them as
    real_identity: str             # Actual name/faction
    infiltration_turn: int         # When they joined
    loyalty_cover: float           # Fake loyalty score (0-1.0)
    actual_loyalty: float          # Always 0.0 for spies
    status: SpyStatus = SpyStatus.UNKNOWN
    preferred_sabotage: List[SabotageType] = field(default_factory=list)
    sabotages_performed: int = 0
    last_sabotage_turn: int = -100 # Turn of last sabotage (prevents too frequent acts)
    discovery_evidence: float = 0.0 # 0-1.0, how much evidence against them
    
    def can_sabotage(self, current_turn: int, cooldown: int = 15) -> bool:
        """Check if agent can perform sabotage"""
        if self.status == SpyStatus.ELIMINATED:
            return False
        if self.status == SpyStatus.EXPOSED:
            return False
        # Need cooldown between sabotages to avoid detection
        return current_turn - self.last_sabotage_turn >= cooldown
    
    def attempt_sabotage(self, current_turn: int) -> Optional[SabotageEvent]:
        """Attempt to perform sabotage. Returns event or None if caught."""
        if not self.can_sabotage(current_turn):
            return None
        
        # Risk of detection
        detection_risk = 0.1 + (self.discovery_evidence * 0.3)
        if random.random() < detection_risk:
            self.discovery_evidence += 0.3  # Evidence accumulates
            return None  # Attempt failed, detected
        
        # Choose sabotage type
        if not self.preferred_sabotage:
            # Choose random if no preference
            sabotage_type = random.choice(list(SabotageType))
        else:
            sabotage_type = random.choice(self.preferred_sabotage)
        
        # Severity depends on agent skill
        severity = random.uniform(0.3, 0.8)
        
        # Create event
        event = SabotageEvent(
            turn=current_turn,
            sabotage_type=sabotage_type,
            severity=severity,
            damage_amount=severity * 100,
            agent_id=self.agent_id,
        )
        
        # Record action
        self.sabotages_performed += 1
        self.last_sabotage_turn = current_turn
        
        return event
    
    def increase_suspicion(self, amount: float = 0.1):
        """Increase evidence/suspicion against agent"""
        self.discovery_evidence = min(1.0, self.discovery_evidence + amount)
        
        # Discovery happens at threshold
        if self.discovery_evidence > 0.7 and self.status == SpyStatus.UNKNOWN:
            self.status = SpyStatus.SUSPECTED
        elif self.discovery_evidence > 0.9 and self.status == SpyStatus.SUSPECTED:
            self.status = SpyStatus.EXPOSED
    
    def get_status_string(self) -> str:
        """Get human-readable status"""
        if self.status == SpyStatus.UNKNOWN:
            return "LOYAL"  # Appears loyal
        elif self.status == SpyStatus.SUSPECTED:
            return "SUSPICIOUS"
        elif self.status == SpyStatus.EXPOSED:
            return "EXPOSED SPY"
        else:
            return "ELIMINATED"


@dataclass
class SpyNetwork:
    """Manages all spies embedded in crew"""
    spies: Dict[int, SpyAgent] = field(default_factory=dict)
    next_agent_id: int = 1000
    sabotage_history: List[SabotageEvent] = field(default_factory=list)
    total_damage_caused: float = 0.0
    espionage_discovered: int = 0  # Counter for discovered acts
    
    def add_spy(self, cover_name: str, real_identity: str, infiltration_turn: int, 
                preferred_sabotage: List[SabotageType] = None) -> SpyAgent:
        """Add a spy to the network"""
        if preferred_sabotage is None:
            preferred_sabotage = random.sample(list(SabotageType), k=2)
        
        agent = SpyAgent(
            agent_id=self.next_agent_id,
            cover_name=cover_name,
            real_identity=real_identity,
            infiltration_turn=infiltration_turn,
            loyalty_cover=random.uniform(0.6, 0.9),  # Appears fairly loyal
            actual_loyalty=0.0,
            preferred_sabotage=preferred_sabotage,
        )
        
        self.spies[self.next_agent_id] = agent
        self.next_agent_id += 1
        return agent
    
    def check_sabotage_attempts(self, current_turn: int) -> List[SabotageEvent]:
        """Check all spies for sabotage attempts. Returns successful events."""
        events = []
        
        for spy_id, spy in self.spies.items():
            if spy.status == SpyStatus.ELIMINATED:
                continue
            
            # Spies attempt sabotage randomly (10% chance each turn if able)
            if random.random() < 0.1 and spy.can_sabotage(current_turn):
                event = spy.attempt_sabotage(current_turn)
                if event:
                    events.append(event)
                    self.sabotage_history.append(event)
                    self.total_damage_caused += event.damage_amount
                else:
                    # Attempt was caught
                    spy.increase_suspicion(0.2)
                    self.espionage_discovered += 1
        
        return events
    
    def discover_spy(self, spy_id: int) -> bool:
        """Discover a spy through investigation. Returns success."""
        if spy_id not in self.spies:
            return False
        
        spy = self.spies[spy_id]
        if spy.status in (SpyStatus.ELIMINATED, SpyStatus.EXPOSED):
            return False
        
        spy.status = SpyStatus.EXPOSED
        return True
    
    def eliminate_spy(self, spy_id: int) -> bool:
        """Eliminate (kill/capture) a spy. Returns success."""
        if spy_id not in self.spies:
            return False
        
        spy = self.spies[spy_id]
        spy.status = SpyStatus.ELIMINATED
        return True
    
    def get_exposed_spies(self) -> List[SpyAgent]:
        """Get list of discovered spies"""
        return [s for s in self.spies.values() if s.status == SpyStatus.EXPOSED]
    
    def get_suspected_spies(self) -> List[SpyAgent]:
        """Get list of suspected spies"""
        return [s for s in self.spies.values() if s.status == SpyStatus.SUSPECTED]
    
    def get_spy_count(self, status: Optional[SpyStatus] = None) -> int:
        """Count spies with optional status filter"""
        if status is None:
            return len(self.spies)
        return sum(1 for s in self.spies.values() if s.status == status)
    
    def get_spy_by_cover_name(self, name: str) -> Optional[SpyAgent]:
        """Find spy by their cover name (crew would know them as this)"""
        for spy in self.spies.values():
            if spy.cover_name.lower() == name.lower():
                return spy
        return None
    
    def get_sabotage_report(self) -> str:
        """Generate sabotage activity report"""
        lines = [
            "═" * 60,
            "ESPIONAGE AND SABOTAGE REPORT",
            "═" * 60,
        ]
        
        if not self.spies:
            lines.append("No known espionage activity detected.")
        else:
            lines.append(f"\nTOTAL SPIES: {len(self.spies)}")
            lines.append(f"  - Unknown: {self.get_spy_count(SpyStatus.UNKNOWN)}")
            lines.append(f"  - Suspected: {self.get_spy_count(SpyStatus.SUSPECTED)}")
            lines.append(f"  - Exposed: {self.get_spy_count(SpyStatus.EXPOSED)}")
            lines.append(f"  - Eliminated: {self.get_spy_count(SpyStatus.ELIMINATED)}")
            
            lines.append(f"\nSABOTAGE HISTORY: {len(self.sabotage_history)} incidents")
            lines.append(f"Total Damage Caused: {self.total_damage_caused:.0f} units")
            lines.append(f"Discovered Acts: {self.espionage_discovered}")
            
            # Recent sabotages
            if self.sabotage_history:
                lines.append("\nRecent Sabotage:")
                for event in self.sabotage_history[-5:]:
                    lines.append(f"  Turn {event.turn}: {event.sabotage_type.value} (severity: {event.severity:.0%})")
        
        lines.append("═" * 60)
        return "\n".join(lines)
    
    def get_crew_morale_impact(self) -> float:
        """Calculate morale impact from known espionage"""
        # Exposed spies lower morale more
        exposed_impact = self.get_spy_count(SpyStatus.EXPOSED) * -0.15
        suspected_impact = self.get_spy_count(SpyStatus.SUSPECTED) * -0.05
        return exposed_impact + suspected_impact
