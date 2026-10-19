"""
Eldritch encounter system with psychological and physical phases.
Encounters start as psychological events, potentially escalate to physical.
"""
from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass, field
import random


class EncounterPhase(Enum):
    """Phases of an eldritch encounter"""
    PSYCHOLOGICAL = "psychological"  # Crew sanity effects only
    MANIFESTATION = "manifestation"  # Reality distortion starts
    PHYSICAL = "physical"            # Actual threats to sub
    CRITICAL = "critical"            # Imminent danger to vessel


class EncounterType(Enum):
    """Types of eldritch encounters"""
    WHISPERS = "whispers"           # Voices in sonar, crew hears things
    SHADOW_MASS = "shadow_mass"     # Dark shape in water
    RADIATION_ANOMALY = "radiation" # Impossible radiation readings
    TIME_DISTORTION = "time"        # Time seems to move strangely
    DIMENSIONAL_RIFT = "rift"       # Hole in reality
    POSSESSED_CREW = "possession"   # Crew member seems possessed
    CREATURE_CONTACT = "creature"   # Something large is near
    REALITY_FRACTURE = "reality"    # Laws of physics breaking down


class CrewResponse(Enum):
    """Crew reactions to encounters"""
    CALM = "calm"                   # Rational, follows orders
    FEARFUL = "fearful"             # Scared, but functional
    PANICKED = "panicked"           # Irrationally afraid
    HOSTILE = "hostile"             # Aggressive, may mutiny
    CATATONIC = "catatonic"         # Shocked into inaction
    POSSESSED = "possessed"         # Acting strangely


@dataclass
class PsychologicalPhase:
    """Initial psychological effect phase"""
    description: str                # What crew experiences
    sanity_damage: float            # Sanity points lost (per crew)
    crew_fear_increase: float       # Fear stat increase (0-1.0)
    escalation_chance: float        # Chance to escalate per turn (0-1.0)
    turns_duration: int             # How long this phase lasts (turns)
    signs: List[str] = field(default_factory=list)  # Observable signs


@dataclass
class ManifestationPhase:
    """Reality distortion phase"""
    description: str
    equipment_malfunctions: List[str]  # Systems that start glitching
    navigation_error: float            # How wrong navigation becomes
    sensor_interference: float         # Sonar/radar interference %
    strange_readings: List[str]        # Weird sensor readings
    escalation_chance: float           # Chance to escalate to physical


@dataclass
class PhysicalPhase:
    """Actual threat phase"""
    description: str
    hull_damage_rate: float            # Damage per turn if not handled
    creature_visible: bool             # Is there something actual?
    weapon_effectiveness: float        # How well weapons work (0-1.0)
    escape_difficulty: float           # How hard to escape (0-1.0)
    turns_until_critical: int          # How many turns until critical


@dataclass
class EldrischEncounter:
    """Active eldritch encounter"""
    encounter_id: int
    encounter_type: EncounterType
    start_turn: int
    current_phase: EncounterPhase = EncounterPhase.PSYCHOLOGICAL
    turns_in_phase: int = 0
    
    # Psychological info
    psychological: Optional[PsychologicalPhase] = None
    manifestation: Optional[ManifestationPhase] = None
    physical: Optional[PhysicalPhase] = None
    
    # Status
    total_crew_sanity_lost: int = 0
    total_damage_caused: float = 0.0
    crew_responses: Dict[int, CrewResponse] = field(default_factory=dict)  # crew_id -> response
    active: bool = True
    resolved: bool = False
    
    # Resolution
    resolution_method: Optional[str] = None  # How it ended
    
    def progress_phase(self) -> Optional[EncounterPhase]:
        """Progress to next phase if conditions met. Returns new phase or None."""
        if not self.active or self.resolved:
            return None
        
        self.turns_in_phase += 1
        
        if self.current_phase == EncounterPhase.PSYCHOLOGICAL:
            if self.psychological:
                # Check escalation
                if self.turns_in_phase >= self.psychological.turns_duration:
                    if random.random() < self.psychological.escalation_chance:
                        self.current_phase = EncounterPhase.MANIFESTATION
                        self.turns_in_phase = 0
                        return self.current_phase
        
        elif self.current_phase == EncounterPhase.MANIFESTATION:
            if self.manifestation:
                if random.random() < self.manifestation.escalation_chance:
                    self.current_phase = EncounterPhase.PHYSICAL
                    self.turns_in_phase = 0
                    return self.current_phase
        
        elif self.current_phase == EncounterPhase.PHYSICAL:
            if self.physical:
                if self.turns_in_phase >= self.physical.turns_until_critical:
                    self.current_phase = EncounterPhase.CRITICAL
                    return self.current_phase
        
        return None
    
    def apply_psychological_effects(self) -> Dict[str, any]:
        """Apply sanity/fear effects. Returns impacts."""
        if not self.psychological:
            return {}
        
        impacts = {
            'sanity_loss': self.psychological.sanity_damage,
            'fear_increase': self.psychological.crew_fear_increase,
            'affected_crew_count': 0,
        }
        
        return impacts
    
    def apply_manifestation_effects(self) -> Dict[str, any]:
        """Apply equipment/navigation glitches."""
        if not self.manifestation:
            return {}
        
        impacts = {
            'malfunctions': self.manifestation.equipment_malfunctions.copy(),
            'nav_error': self.manifestation.navigation_error,
            'sensor_interference': self.manifestation.sensor_interference,
        }
        
        return impacts
    
    def apply_physical_effects(self, crew_count: int = 1) -> float:
        """Apply physical damage. Returns damage amount."""
        if not self.physical:
            return 0.0
        
        damage = self.physical.hull_damage_rate * crew_count
        self.total_damage_caused += damage
        return damage
    
    def attempt_resolution(self, method: str) -> float:
        """Attempt to resolve encounter. Returns success percentage (0-1.0)."""
        if not self.active or self.resolved:
            return 0.0
        
        success_rates = {
            'retreat': 0.4,          # Fleeing has moderate success
            'evasion': 0.5,          # Evasive maneuvers
            'weapons': 0.3 if not self.physical else self.physical.weapon_effectiveness,
            'prayer': 0.1,           # Unlikely but possible
            'full_depth': 0.7,       # Going deep often works
            'surface': 0.6,          # Surfacing can help
            'ignore': 0.05,          # Unlikely to work
        }
        
        return success_rates.get(method.lower(), 0.1)


@dataclass
class EncounterManager:
    """Manages active and historical encounters"""
    encounters: Dict[int, EldrischEncounter] = field(default_factory=dict)
    next_encounter_id: int = 1
    encounter_history: List[EldrischEncounter] = field(default_factory=list)
    active_encounter: Optional[EldrischEncounter] = None
    
    crew_total_sanity_loss: int = 0
    
    def start_encounter(self, encounter_type: EncounterType, turn: int) -> EldrischEncounter:
        """Start a new encounter"""
        encounter = self._create_encounter(encounter_type, turn)
        self.encounters[encounter.encounter_id] = encounter
        self.active_encounter = encounter
        return encounter
    
    def _create_encounter(self, encounter_type: EncounterType, turn: int) -> EldrischEncounter:
        """Create a new encounter with appropriate details"""
        encounter = EldrischEncounter(
            encounter_id=self.next_encounter_id,
            encounter_type=encounter_type,
            start_turn=turn,
        )
        self.next_encounter_id += 1
        
        # Create psychological phase based on type
        psych_details = {
            EncounterType.WHISPERS: PsychologicalPhase(
                description="The sonar begins picking up strange voices. They seem to know your name.",
                sanity_damage=15,
                crew_fear_increase=0.2,
                escalation_chance=0.15,
                turns_duration=random.randint(3, 6),
                signs=["Sonar distortions", "Crew reports hearing voices", "Equipment malfunctions temporarily"],
            ),
            EncounterType.SHADOW_MASS: PsychologicalPhase(
                description="A massive shadow passes beneath the submarine. It moves with purpose.",
                sanity_damage=20,
                crew_fear_increase=0.25,
                escalation_chance=0.2,
                turns_duration=random.randint(4, 8),
                signs=["Sonar contact lost", "Crew reports seeing shapes", "Pressure hull creaks"],
            ),
            EncounterType.RADIATION_ANOMALY: PsychologicalPhase(
                description="Radiation readings spike impossibly. No known source.",
                sanity_damage=10,
                crew_fear_increase=0.15,
                escalation_chance=0.1,
                turns_duration=random.randint(2, 5),
                signs=["Geiger counters going wild", "Instruments showing contradictions"],
            ),
            EncounterType.TIME_DISTORTION: PsychologicalPhase(
                description="Time seems to move incorrectly. Clocks don't agree.",
                sanity_damage=25,
                crew_fear_increase=0.3,
                escalation_chance=0.25,
                turns_duration=random.randint(3, 7),
                signs=["Clock disagreement", "Crew reports memory gaps", "Instruments lag"],
            ),
            EncounterType.POSSESSED_CREW: PsychologicalPhase(
                description="One of the crew begins acting strangely. Their eyes seem wrong.",
                sanity_damage=30,
                crew_fear_increase=0.35,
                escalation_chance=0.3,
                turns_duration=random.randint(5, 10),
                signs=["Crew member acting erratically", "Speaking in unknown languages", "Superhuman strength observed"],
            ),
        }
        
        encounter.psychological = psych_details.get(
            encounter_type,
            PsychologicalPhase(
                description="Something is wrong. You can feel it.",
                sanity_damage=15,
                crew_fear_increase=0.2,
                escalation_chance=0.15,
                turns_duration=5,
                signs=["Unease among crew", "Systems behaving oddly"],
            ),
        )
        
        return encounter
    
    def tick_encounters(self, crew_count: int) -> List[Dict]:
        """Process all active encounters. Returns list of effects/warnings."""
        effects = []
        
        for encounter_id, encounter in list(self.encounters.items()):
            if not encounter.active:
                continue
            
            # Progress phase
            new_phase = encounter.progress_phase()
            if new_phase:
                effects.append({
                    'type': 'phase_change',
                    'encounter_id': encounter_id,
                    'new_phase': new_phase.value,
                    'encounter_type': encounter.encounter_type.value,
                })
            
            # Apply effects based on phase
            if encounter.current_phase == EncounterPhase.PSYCHOLOGICAL:
                psych_effects = encounter.apply_psychological_effects()
                effects.append({
                    'type': 'psychological',
                    'encounter_id': encounter_id,
                    'sanity_loss': psych_effects.get('sanity_loss', 0),
                })
            
            elif encounter.current_phase == EncounterPhase.PHYSICAL:
                damage = encounter.apply_physical_effects(crew_count)
                effects.append({
                    'type': 'physical',
                    'encounter_id': encounter_id,
                    'damage': damage,
                })
        
        return effects
    
    def resolve_encounter(self, encounter_id: int, method: str) -> bool:
        """Attempt to resolve an encounter"""
        if encounter_id not in self.encounters:
            return False
        
        encounter = self.encounters[encounter_id]
        success_chance = encounter.attempt_resolution(method)
        
        if random.random() < success_chance:
            encounter.resolved = True
            encounter.active = False
            encounter.resolution_method = method
            self.encounter_history.append(encounter)
            self.active_encounter = None
            return True
        
        return False
    
    def get_active_encounter_description(self) -> Optional[str]:
        """Get description of current encounter"""
        if not self.active_encounter or not self.active_encounter.active:
            return None
        
        encounter = self.active_encounter
        
        if encounter.current_phase == EncounterPhase.PSYCHOLOGICAL and encounter.psychological:
            return encounter.psychological.description
        elif encounter.current_phase == EncounterPhase.MANIFESTATION and encounter.manifestation:
            return encounter.manifestation.description
        elif encounter.current_phase == EncounterPhase.PHYSICAL and encounter.physical:
            return encounter.physical.description
        
        return "Something is very wrong..."
    
    def get_encounter_summary(self) -> str:
        """Generate summary of all encounters"""
        lines = [
            "═" * 60,
            "ENCOUNTER SUMMARY",
            "═" * 60,
        ]
        
        if self.active_encounter and self.active_encounter.active:
            enc = self.active_encounter
            lines.append(f"\nACTIVE ENCOUNTER: {enc.encounter_type.value}")
            lines.append(f"  Phase: {enc.current_phase.value}")
            lines.append(f"  Duration: {enc.turns_in_phase} turns")
            lines.append(f"  Damage Caused: {enc.total_damage_caused:.0f}")
        
        lines.append(f"\nTotal Encounters: {len(self.encounter_history)}")
        lines.append(f"Total Crew Sanity Lost: {self.crew_total_sanity_loss}")
        
        if self.encounter_history:
            lines.append("\nPrevious Encounters:")
            for enc in self.encounter_history[-5:]:
                lines.append(f"  - {enc.encounter_type.value} (turns {enc.start_turn}-{enc.start_turn + enc.turns_in_phase})")
        
        lines.append("═" * 60)
        return "\n".join(lines)
