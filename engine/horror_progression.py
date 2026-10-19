"""
Horror Progression System - The Descent into Madness

The war is a facade. As the submarine descends deeper and stays underwater longer,
the crew begins to realize they are not alone in the depths. Reality itself begins
to unravel as eldritch horrors become more apparent with each passing day.

Progression Stages:
1. DENIAL (Days 1-3): Everything seems normal. War operations. Minor oddities.
2. UNEASE (Days 4-7): Strange sounds, unsettling dreams, equipment glitches.
3. DREAD (Days 8-14): Crew sees things, reality bends, encounters intensify.
4. TERROR (Days 15-21): Undeniable manifestations, crew sanity breaking.
5. MADNESS (Days 22+): The submarine is in another realm entirely.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import random


class HorrorStage(Enum):
    """Stages of horror progression."""
    DENIAL = 1      # "It's just the war..."
    UNEASE = 2      # "Something feels wrong..."
    DREAD = 3       # "We shouldn't be here..."
    TERROR = 4      # "They're real... oh God, they're real..."
    MADNESS = 5     # "There is no surface anymore..."


class SanityLevel(Enum):
    """Crew sanity states."""
    STABLE = "stable"           # 100-80%: Functioning normally
    SHAKEN = "shaken"           # 79-60%: Minor issues, jumpiness
    DISTURBED = "disturbed"     # 59-40%: Paranoia, hallucinations
    UNHINGED = "unhinged"       # 39-20%: Dangerous, unpredictable
    BROKEN = "broken"           # 19-0%: Catatonic or violent


class RealityStability(Enum):
    """How stable reality is aboard the submarine."""
    NORMAL = "normal"           # Physics work as expected
    WARPED = "warped"           # Minor impossibilities
    FRACTURED = "fractured"     # Major reality breaks
    SHATTERED = "shattered"     # Nothing makes sense anymore


@dataclass
class HorrorMetrics:
    """Tracks the submarine's descent into horror."""
    # Time tracking
    days_submerged: int = 0
    total_days: int = 0
    deepest_dive: float = 0.0
    time_at_crush_depth: int = 0  # Turns spent near max depth
    
    # Sanity tracking
    average_crew_sanity: float = 100.0
    crew_lost_to_madness: int = 0
    unexplained_deaths: int = 0
    
    # Horror exposure
    encounters_witnessed: int = 0
    reality_breaches: int = 0
    forbidden_knowledge_gained: int = 0
    
    # Environmental
    consecutive_turns_in_darkness: int = 0
    turns_without_surfacing: int = 0
    distance_from_known_territory: float = 0.0
    
    def calculate_horror_stage(self) -> HorrorStage:
        """LEGACY: time-driven stage. Used only when no DreadBridge is attached.

        With a bridge attached the stage is derived from crew/ship state
        (DESIGN.md 3.4); elapsed days are no longer a cause of horror.
        """
        # Primary factor: days since start
        if self.total_days <= 3:
            return HorrorStage.DENIAL
        elif self.total_days <= 7:
            # Can skip to DREAD if severe exposure
            if self.encounters_witnessed >= 3 or self.average_crew_sanity < 70:
                return HorrorStage.DREAD
            return HorrorStage.UNEASE
        elif self.total_days <= 14:
            # Can skip to TERROR if extreme exposure
            if self.encounters_witnessed >= 5 or self.average_crew_sanity < 50:
                return HorrorStage.TERROR
            return HorrorStage.DREAD
        elif self.total_days <= 21:
            # Can skip to MADNESS if crew is broken
            if self.crew_lost_to_madness >= 3 or self.average_crew_sanity < 30:
                return HorrorStage.MADNESS
            return HorrorStage.TERROR
        else:
            return HorrorStage.MADNESS
    
    def calculate_reality_stability(self) -> RealityStability:
        """Determine how stable reality is."""
        if self.reality_breaches == 0:
            return RealityStability.NORMAL
        elif self.reality_breaches <= 2:
            return RealityStability.WARPED
        elif self.reality_breaches <= 5:
            return RealityStability.FRACTURED
        else:
            return RealityStability.SHATTERED


@dataclass
class CrewMember:
    """Extended crew member with sanity tracking."""
    name: str
    sanity: float = 100.0  # 0-100
    fear_level: float = 0.0  # 0-100
    witnessed_horrors: int = 0
    has_insight: bool = False  # Understands the truth
    days_until_breakdown: Optional[int] = None
    
    def get_sanity_level(self) -> SanityLevel:
        """Get current sanity state."""
        if self.sanity >= 80:
            return SanityLevel.STABLE
        elif self.sanity >= 60:
            return SanityLevel.SHAKEN
        elif self.sanity >= 40:
            return SanityLevel.DISTURBED
        elif self.sanity >= 20:
            return SanityLevel.UNHINGED
        else:
            return SanityLevel.BROKEN
    
    def lose_sanity(self, amount: float, reason: str = "") -> str:
        """Lose sanity. Returns a message about the effect."""
        self.sanity = max(0, self.sanity - amount)
        level = self.get_sanity_level()
        
        if level == SanityLevel.BROKEN and self.sanity < 10:
            return f"{self.name} stares blankly, muttering about 'the things below'..."
        elif level == SanityLevel.UNHINGED:
            return f"{self.name} is gripping their head, whispering frantically."
        elif level == SanityLevel.DISTURBED:
            return f"{self.name} looks haunted, jumping at shadows."
        elif level == SanityLevel.SHAKEN:
            return f"{self.name} seems nervous, avoiding certain areas of the sub."
        
        return ""


class HorrorManager:
    """Manages the progressive horror experience."""
    
    def __init__(self):
        self.metrics = HorrorMetrics()
        self.dread = None            # DreadBridge; see attach_dread()
        self.current_stage = HorrorStage.DENIAL
        self.reality_state = RealityStability.NORMAL
        
        # Encounter spawning
        self.turns_since_last_encounter = 0
        self.encounter_frequency_modifier = 1.0
        
        # Stage-specific messages
        self.ambient_messages: Dict[HorrorStage, List[str]] = {
            HorrorStage.DENIAL: [
                "The sonar pings rhythmically. All seems normal.",
                "Another routine patrol in hostile waters.",
                "The crew jokes to keep spirits up.",
                "Standard wartime operations continue.",
            ],
            HorrorStage.UNEASE: [
                "The sonar picked up something... but it's gone now.",
                "One of the crew swears they heard humming in the pipes.",
                "The compass needle twitched for a moment.",
                "Did the lights flicker? Nobody's sure.",
                "There's a faint smell nobody can place.",
                "The temperature dropped suddenly, then normalized.",
            ],
            HorrorStage.DREAD: [
                "The sonar shows impossible readings.",
                "Multiple crew report the same nightmare.",
                "Something is scratching at the hull.",
                "The emergency lights are flickering more than usual.",
                "A crew member claims they saw movement in the bilge.",
                "The radio picks up whispers in no known language.",
                "Time seems... wrong. How long were we submerged?",
            ],
            HorrorStage.TERROR: [
                "SOMETHING IS OUTSIDE THE HULL.",
                "The walls are breathing. The crew all see it.",
                "A crew member vanished from a locked compartment.",
                "The periscope shows a sky that isn't ours.",
                "Blood seeps from the bulkheads. It's not rust.",
                "They're in the hydrophones. They're calling to us.",
                "The captain's log contains entries he never wrote.",
            ],
            HorrorStage.MADNESS: [
                "The submarine is not in water anymore.",
                "There are more crew members than there should be.",
                "The depth gauge reads negative numbers.",
                "Everyone remembers dying. Multiple times.",
                "The 'surface' is a concept we no longer understand.",
                "We are being digested. Slowly. Eternally.",
                "HOME IS A LIE. DEPTH IS TRUTH.",
            ],
        }
    
    def attach_dread(self, bridge):
        """Switch to the state-driven model (dread/bridge.py)."""
        self.dread = bridge
        self.current_stage = self._derive_stage()

    def _derive_stage(self) -> HorrorStage:
        if self.dread is not None:
            return HorrorStage[self.dread.stage()]
        return self.metrics.calculate_horror_stage()

    def _advance_dread(self, time_passed_hours: float, current_depth: float, submarine=None) -> Dict[str, any]:
        results = {'messages': [], 'sanity_effects': [], 'spawn_encounter': False,
                   'encounter_type': None, 'reality_breach': False}
        self.metrics.total_days = int(self.metrics.total_days + time_passed_hours / 24)
        if current_depth > 50:
            self.metrics.turns_without_surfacing += 1
            self.metrics.days_submerged += time_passed_hours / 24
        else:
            self.metrics.turns_without_surfacing = 0
        self.metrics.deepest_dive = max(self.metrics.deepest_dive, current_depth)
        results['messages'].extend(self.dread.tick(current_depth, submarine))
        self.metrics.average_crew_sanity = self.dread.mean_sanity()
        old, self.current_stage = self.current_stage, self._derive_stage()
        if self.current_stage != old:
            results['messages'].append(self._get_stage_transition_message(self.current_stage))
        return results

    def advance_turn(self, time_passed_hours: float, current_depth: float, submarine=None) -> Dict[str, any]:
        """
        Advance horror progression. Returns events/messages.
        
        Args:
            time_passed_hours: How many hours passed this turn
            current_depth: Current submarine depth in meters
        """
        results = {
            'messages': [],
            'sanity_effects': [],
            'spawn_encounter': False,
            'encounter_type': None,
            'reality_breach': False,
        }
        
        if self.dread is not None:
            return self._advance_dread(time_passed_hours, current_depth, submarine)

        # Update metrics
        self.metrics.total_days = int(self.metrics.total_days + time_passed_hours / 24)
        
        if current_depth > 50:  # Submerged
            self.metrics.turns_without_surfacing += 1
            self.metrics.days_submerged += time_passed_hours / 24
        else:
            self.metrics.turns_without_surfacing = 0
        
        if current_depth > self.metrics.deepest_dive:
            self.metrics.deepest_dive = current_depth
        
        # Update stage
        old_stage = self.current_stage
        self.current_stage = self.metrics.calculate_horror_stage()
        
        # Stage transition message
        if self.current_stage != old_stage:
            results['messages'].append(self._get_stage_transition_message(self.current_stage))
        
        # Ambient horror message (occasional)
        if random.random() < 0.3:  # 30% chance per turn
            results['messages'].append(self._get_ambient_message())
        
        # Encounter spawning (increases with progression)
        self.turns_since_last_encounter += 1
        spawn_chance = self._calculate_encounter_chance()
        
        if random.random() < spawn_chance:
            results['spawn_encounter'] = True
            results['encounter_type'] = self._choose_encounter_type()
            self.turns_since_last_encounter = 0
            self.metrics.encounters_witnessed += 1
        
        # Reality breaches (rare but escalating)
        if self.current_stage.value >= HorrorStage.DREAD.value:
            breach_chance = (self.current_stage.value - 2) * 0.02  # 2%, 4%, 6%
            if random.random() < breach_chance:
                results['reality_breach'] = True
                self.metrics.reality_breaches += 1
                results['messages'].append(self._get_reality_breach_message())
        
        return results
    
    def _calculate_encounter_chance(self) -> float:
        """Calculate chance of eldritch encounter this turn."""
        base_chance = 0.05  # 5% base
        
        # Increase with stage
        stage_multiplier = self.current_stage.value * 1.5
        
        # Increase with time without surfacing
        desperation = min(2.0, self.metrics.turns_without_surfacing / 20)
        
        # Increase with depth
        depth_factor = min(1.5, self.metrics.deepest_dive / 300)
        
        return min(0.6, base_chance * stage_multiplier * (1 + desperation) * (1 + depth_factor))
    
    def _choose_encounter_type(self) -> str:
        """Choose appropriate encounter type for current stage."""
        from engine.eldritch_encounters import EncounterType
        
        stage_encounters = {
            HorrorStage.DENIAL: [EncounterType.WHISPERS],
            HorrorStage.UNEASE: [EncounterType.WHISPERS, EncounterType.RADIATION_ANOMALY],
            HorrorStage.DREAD: [EncounterType.SHADOW_MASS, EncounterType.TIME_DISTORTION],
            HorrorStage.TERROR: [EncounterType.CREATURE_CONTACT, EncounterType.DIMENSIONAL_RIFT, EncounterType.POSSESSED_CREW],
            HorrorStage.MADNESS: [EncounterType.REALITY_FRACTURE, EncounterType.CREATURE_CONTACT],
        }
        
        available = stage_encounters.get(self.current_stage, [EncounterType.WHISPERS])
        return random.choice(available).value
    
    def _get_ambient_message(self) -> str:
        """Get a random ambient horror message for current stage."""
        messages = self.ambient_messages.get(self.current_stage, ["The voyage continues."])
        return random.choice(messages)
    
    def _get_stage_transition_message(self, stage: HorrorStage) -> str:
        """Get message when transitioning to a new horror stage."""
        messages = {
            HorrorStage.DENIAL: "Mission begins. The crew is confident.",
            HorrorStage.UNEASE: "Something feels... off. The crew whispers nervously.",
            HorrorStage.DREAD: "The pretense of normalcy is crumbling. They know something is wrong.",
            HorrorStage.TERROR: "THE TRUTH IS UNDENIABLE. SOMETHING IS DOWN HERE WITH US.",
            HorrorStage.MADNESS: "We have passed beyond. There is no return. Only depth.",
        }
        return f"\n{'='*70}\n{messages[stage]}\n{'='*70}\n"
    
    def _get_reality_breach_message(self) -> str:
        """Get a message describing a reality breach."""
        breaches = [
            "The walls phase momentarily. You see... other places.",
            "For a moment, the submarine exists in two places at once.",
            "Time loops. You experience this moment again. And again.",
            "A door opens to a compartment that doesn't exist.",
            "The ocean outside becomes something else entirely.",
            "You glimpse the truth: you never left port. You've always been HERE.",
        ]
        return random.choice(breaches)
    
    def reach_port(self, at_friendly_port: bool = True) -> Dict[str, any]:
        """
        Handle reaching port - restores sanity and reduces horror.
        
        Args:
            at_friendly_port: True if at friendly port, False if neutral/hostile
        
        Returns:
            Dict with restoration messages and effects
        """
        results = {
            'messages': [],
            'sanity_restored': 0.0,
            'horror_reduced': False,
        }
        
        if at_friendly_port:
            # Full restoration at friendly port
            old_sanity = self.metrics.average_crew_sanity
            self.metrics.average_crew_sanity = min(100.0, self.metrics.average_crew_sanity + 30.0)
            sanity_gain = self.metrics.average_crew_sanity - old_sanity
            results['sanity_restored'] = sanity_gain
            
            # Reset some horror metrics
            self.metrics.days_submerged = 0
            self.metrics.turns_without_surfacing = 0
            self.metrics.consecutive_turns_in_darkness = 0
            
            # Reduce encounters witnessed (crew gets therapy/leave)
            if self.metrics.encounters_witnessed > 0:
                self.metrics.encounters_witnessed = max(0, self.metrics.encounters_witnessed - 2)
            
            # Port safety messages
            if self.current_stage == HorrorStage.MADNESS:
                results['messages'].append("═══ PORT ARRIVAL ═══")
                results['messages'].append("The crew stumbles ashore, changed. Some never speak again.")
                results['messages'].append("Shore leave and medical treatment begin...")
                results['horror_reduced'] = True
            elif self.current_stage == HorrorStage.TERROR:
                results['messages'].append("═══ PORT ARRIVAL ═══")
                results['messages'].append("Safe harbor at last. The crew breathes easier on solid ground.")
                results['messages'].append("Debriefings scheduled. Some stories won't be believed.")
                results['horror_reduced'] = True
            elif self.current_stage == HorrorStage.DREAD:
                results['messages'].append("═══ PORT ARRIVAL ═══")
                results['messages'].append("The familiar sight of port brings relief to the crew.")
                results['messages'].append("Shore leave granted. Hot food. Real beds.")
                results['horror_reduced'] = True
            else:
                results['messages'].append("═══ PORT ARRIVAL ═══")
                results['messages'].append("Routine docking procedures complete.")
                results['messages'].append(f"Crew sanity restored: +{sanity_gain:.1f}%")
        else:
            # Partial restoration at neutral port
            old_sanity = self.metrics.average_crew_sanity
            self.metrics.average_crew_sanity = min(100.0, self.metrics.average_crew_sanity + 15.0)
            sanity_gain = self.metrics.average_crew_sanity - old_sanity
            results['sanity_restored'] = sanity_gain
            
            self.metrics.turns_without_surfacing = 0
            
            results['messages'].append("═══ NEUTRAL PORT ═══")
            results['messages'].append("Brief respite in neutral waters.")
            results['messages'].append(f"Limited shore leave. Sanity restored: +{sanity_gain:.1f}%")
        
        # Recalculate stage after port visit
        if self.dread is not None:
            self.dread.reach_port(at_friendly_port)
            self.metrics.average_crew_sanity = self.dread.mean_sanity()
        old_stage = self.current_stage
        self.current_stage = self._derive_stage()
        
        if old_stage != self.current_stage:
            results['messages'].append(f"Horror subsides: {old_stage.name} → {self.current_stage.name}")
            results['horror_reduced'] = True
        
        return results
    
    def surface_near_land(self) -> Dict[str, any]:
        """
        Handle surfacing near land/shallow water - minor horror reduction.
        
        Returns:
            Dict with minor restoration messages
        """
        results = {
            'messages': [],
            'sanity_restored': 0.0,
        }
        
        # Small sanity boost from seeing land/shallow water
        old_sanity = self.metrics.average_crew_sanity
        self.metrics.average_crew_sanity = min(100.0, self.metrics.average_crew_sanity + 5.0)
        sanity_gain = self.metrics.average_crew_sanity - old_sanity
        results['sanity_restored'] = sanity_gain
        
        # Reset surface timer
        self.metrics.turns_without_surfacing = 0
        
        if self.current_stage in [HorrorStage.TERROR, HorrorStage.MADNESS]:
            results['messages'].append("Land visible on the horizon. The crew remembers what 'normal' feels like.")
        elif self.current_stage == HorrorStage.DREAD:
            results['messages'].append("The sight of land brings comfort to the crew.")
        elif sanity_gain > 0:
            results['messages'].append(f"Fresh air and open sky. Crew morale improves (+{sanity_gain:.1f}%).")
        
        return results
    
    def get_stage_info(self) -> str:
        """Get formatted info about current horror state."""
        return f"""
Horror Stage: {self.current_stage.name}
Reality Stability: {self.reality_state.name}
Days at Sea: {self.metrics.total_days}
Encounters Witnessed: {self.metrics.encounters_witnessed}
Crew Sanity Average: {self.metrics.average_crew_sanity:.1f}%
Turns Without Surfacing: {self.metrics.turns_without_surfacing}
        """.strip()
