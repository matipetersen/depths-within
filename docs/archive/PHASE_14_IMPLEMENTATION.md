# Phase 14: Advanced Crew Conflict & Supply Systems

## Overview

Phase 14 implements three major new systems that add depth to crew management and submarine operations:

1. **Supply Management System** - Resource rationing and depletion mechanics
2. **Spy Network System** - Crew sabotage and espionage mechanics
3. **Eldritch Encounter System** - Multi-phase psychological encounters

**Status:** ✅ **COMPLETE - 186/186 Tests Passing (100%)**

---

## System Summaries

### 1. Supply Management System (`engine/supply_management.py`)

**Purpose:** Simulate realistic submarine resource constraints and crew provisioning.

#### Key Components

**ResourceType (Enum)**
- `OXYGEN` - Breathing air
- `POWER` - Reactor/battery power
- `FOOD` - Crew rations
- `WATER` - Fresh water
- `AMMUNITION` - Torpedo and gun rounds
- `FUEL` - Diesel/nuclear fuel
- `MEDICAL` - First aid and medicines
- `REPAIR_MATERIALS` - Hull and equipment repairs

**RationLevel (Enum)**
- `NORMAL` (1.0) - Full consumption
- `REDUCED` (0.75) - 25% less consumption
- `STRICT` (0.5) - Half consumption
- `EMERGENCY` (0.25) - 75% less consumption
- `CRITICAL` (0.1) - Severe rationing, crew suffering increases

**Resource Class**
```python
Resource:
  - current: float (current amount)
  - maximum: float (tank capacity)
  - consumption_rate: float (per tick base rate)
  
  Methods:
  - consume(amount, efficiency=1.0) -> float
  - replenish(amount) -> float
  - get_percentage() -> float (0-100)
  - get_status() -> str ("EXCELLENT", "GOOD", "LOW", "CRITICAL", "DEPLETED")
```

**SupplyInventory Class**

Main interface for all supply management:

```python
SupplyInventory:
  - resources: Dict[ResourceType, Resource]
  - current_ration_level: RationLevel
  
  Methods:
  - tick(crew_count, depth, in_combat) -> Dict
    * Processes resource consumption
    * Depth-based oxygen consumption (deeper = more oxygen use)
    * Combat multiplier (2x power drain when in combat)
    * Returns warnings for critical resources
  
  - set_ration_level(RationLevel) -> None
    * Changes consumption multiplier for all resources
  
  - use_ammunition(count) -> bool
    * Depletes ammunition resource
    * Returns success if enough ammo available
  
  - repair_damage(amount) -> bool
    * Uses repair materials for hull repairs
    * Returns success if enough materials available
  
  - use_medical(amount) -> bool
    * Uses medical supplies for crew healing
    * Returns success if enough medical supplies available
  
  - get_critical_resources() -> List[ResourceType]
    * Returns resources below critical threshold (20%)
  
  - get_status_report() -> str
    * Formatted report of all resources
    * Shows percentage bars and status indicators
  
  - get_summary() -> Dict[ResourceType, float]
    * Simple percentage dictionary for UI display
```

#### Integration Points

**Game.__init__():**
```python
self.supply_inventory = SupplyInventory()
```

**Game._tick():**
- Called each turn to process resource consumption
- Crew count from `crew_roster.crew_count`
- Depth from `submarine.current_depth`
- Combat status from `tactical_map.any_contacts()`
- Critical warnings logged automatically

**Console Commands:**
- `supplies` / `supply_status` - Show full report
- `ration_level <LEVEL>` - Change ration level
- `resource_summary` / `res_summary` - Show quick summary

#### Gameplay Mechanics

- **Oxygen:** Consumed based on crew count and depth. Deeper = 2x consumption
- **Power:** Consumed by submarine systems. Combat = 2x consumption
- **Food:** Consumed by crew. Rationing affects crew morale
- **Water:** Fresh water for crew. Low water increases thirst stress
- **Ammunition:** Depleted by firing. Critical ammo limits tactical options
- **Fuel:** Consumed by engines. Low fuel forces surface/towing
- **Medical:** Used for crew healing. Low medical increases casualty risk
- **Repair Materials:** Used for hull repairs. Low supplies force damage acceptance

---

### 2. Spy Network System (`engine/spy_network.py`)

**Purpose:** Introduce internal crew conflict through sabotage and espionage.

#### Key Components

**SabotageType (Enum) - 10 Types**
1. `OXYGEN_LEAK` - Compromises oxygen tanks
2. `POWER_DRAIN` - Drains reactor/battery power
3. `FUEL_CONTAMINATION` - Contaminates fuel supply
4. `TORPEDO_SABOTAGE` - Disables torpedoes
5. `COMMUNICATION_JAM` - Blocks radio/sonar signals
6. `ENGINE_DAMAGE` - Damages propulsion systems
7. `HULL_WEAKENING` - Weakens hull integrity
8. `COMPARTMENT_FLOODING` - Causes compartment leaks
9. `SONAR_INTERFERENCE` - Disrupts sonar systems
10. `CREW_SABOTAGE` - Saboteur influences other crew members

**SpyStatus (Enum)**
- `UNKNOWN` - No evidence
- `SUSPECTED` - Suspicion > 0.7
- `EXPOSED` - Suspicion > 0.9, crew knows about spy
- `ELIMINATED` - Spy has been removed

**SabotageEvent (Dataclass)**
```python
SabotageEvent:
  - turn: int (when sabotage occurred)
  - sabotage_type: SabotageType
  - severity: float (0-1.0, damage magnitude)
  - was_detected: bool (success or caught?)
```

**SpyAgent Class**

Individual spy/saboteur:

```python
SpyAgent:
  - cover_name: str (fake identity)
  - real_identity: str (true identity, if known)
  - status: SpyStatus
  - infiltration_turn: int (when they joined)
  - preferred_sabotage: List[SabotageType]
  - suspicion_level: float (0-1.0, evidence accumulation)
  - last_sabotage_turn: int (cooldown tracking)
  - sabotage_cooldown: int (minimum turns between acts)
  
  Methods:
  - can_sabotage(current_turn, cooldown) -> bool
    * Checks cooldown (default 15 turns)
    * Returns True if enough time has passed
  
  - attempt_sabotage(current_turn) -> SabotageEvent | None
    * Performs sabotage if not on cooldown
    * 30-40% detection chance (scales with suspicion)
    * Returns sabotage event or None if detected
  
  - increase_suspicion(amount) -> None
    * Accumulates evidence against spy
    * Updates status when thresholds crossed
    * 0.7 = SUSPECTED, 0.9 = EXPOSED
  
  - get_status_string() -> str
    * Returns human-readable status summary
```

**SpyNetwork Class**

Manages all spies and sabotage:

```python
SpyNetwork:
  - spies: List[SpyAgent]
  - sabotage_history: List[SabotageEvent]
  - total_damage_caused: float
  - spies_exposed: int
  
  Methods:
  - add_spy(cover_name, real_identity, infiltration_turn, 
            preferred_sabotage) -> None
    * Creates new spy and adds to network
    * Initializes with UNKNOWN status
  
  - check_sabotage_attempts(current_turn) -> List[SabotageEvent]
    * Returns list of successful (undetected) sabotage events
    * Each spy may attempt one sabotage per check
    * Failed sabotage attempts increase suspicion
  
  - discover_spy(spy_id) -> None
    * Sets spy status to EXPOSED
    * Increments spies_exposed counter
  
  - eliminate_spy(spy_id) -> None
    * Removes spy from active roster
    * Logs elimination event
  
  - get_exposed_spies() -> List[SpyAgent]
    * Returns all EXPOSED spies
  
  - get_suspected_spies() -> List[SpyAgent]
    * Returns all SUSPECTED spies
  
  - get_spy_count(status=None) -> int
    * Count spies by optional status filter
  
  - get_sabotage_report() -> str
    * Formatted report of sabotage activity
    * Shows damage, exposed spies, recent incidents
  
  - get_crew_morale_impact() -> float
    * Returns morale penalty (0-1.0)
    * Increases with exposed/suspected spies
```

#### Integration Points

**Game.__init__():**
```python
self.spy_network = SpyNetwork()
```

**Game._tick():**
- Spies attempt sabotage each turn
- Successful sabotage affects resources (see Supply Management integration)
- Detection events logged

**Console Commands:**
- `spy_status` / `spies` - Show known/suspected spies
- `eliminate_spy <name>` - Execute suspected spy
- Sabotage is auto-detected and reported in logs

#### Gameplay Mechanics

- **Discovery:** Spies accumulate suspicion through failed sabotage attempts
- **Cooldown:** Each spy needs 15 turns between sabotage acts to avoid detection
- **Damage:** Each sabotage reduces specific resources based on type
- **Morale:** Crew aware of spies suffer morale penalty
- **Resolution:** Players can eliminate exposed or suspected spies
- **Escalation:** Suspicion without elimination leads to EXPOSED status

---

### 3. Eldritch Encounter System (`engine/eldritch_encounters.py`)

**Purpose:** Create psychological horror that escalates from mental to physical threat.

#### Key Components

**EncounterPhase (Enum) - 4-Phase Progression**
1. `PSYCHOLOGICAL` - Crew fears/sanity damage, no physical threat
2. `MANIFESTATION` - Equipment glitches, sensor errors, navigation issues
3. `PHYSICAL` - Actual hull damage, creature visibility, weapons ready
4. `CRITICAL` - Imminent danger, extreme damage if not resolved

**EncounterType (Enum) - 8 Encounter Types**
1. `WHISPERS` - Voices in the dark
2. `SHADOW_MASS` - Unidentified moving shadow
3. `RADIATION_ANOMALY` - Gamma spike detection
4. `TIME_DISTORTION` - Temporal anomalies
5. `DIMENSIONAL_RIFT` - Spatial distortion
6. `POSSESSED_CREW` - Crew member possessed/influenced
7. `CREATURE_CONTACT` - Unknown creature contact
8. `REALITY_FRACTURE` - Reality itself breaks down

**CrewResponse (Enum) - Crew Reactions**
- `CALM` - Crew maintains discipline
- `FEARFUL` - Increased vigilance, decreased morale
- `PANICKED` - Poor decisions, friendly fire risk
- `HOSTILE` - Crew turns on each other/captain
- `CATATONIC` - Crew frozen, non-responsive
- `POSSESSED` - Crew under unknown influence

**PsychologicalPhase (Dataclass)**
```python
PsychologicalPhase:
  - description: str
  - sanity_damage: float (crew sanity loss per tick)
  - crew_fear_increase: float
  - escalation_chance: float (0-1.0, chance to move to MANIFESTATION)
  - turns_duration: int (turns before auto-escalation)
  - signs: List[str] (psychological indicators)
```

**ManifestationPhase (Dataclass)**
```python
ManifestationPhase:
  - description: str
  - equipment_malfunctions: Dict[str, float]
    * e.g., {"sonar": 0.5, "radar": 0.3}
  - navigation_error: float (degree offset)
  - sensor_interference: bool
  - strange_readings: List[str]
```

**PhysicalPhase (Dataclass)**
```python
PhysicalPhase:
  - description: str
  - hull_damage_rate: float (damage per tick)
  - creature_visible: bool (can be targeted)
  - weapon_effectiveness: float (accuracy multiplier)
  - escape_difficulty: float (1.0 = normal, 2.0 = very hard)
  - turns_until_critical: int (auto-escalation timer)
```

**EldrischEncounter Class**

Active encounter tracking:

```python
EldrischEncounter:
  - encounter_type: EncounterType
  - current_phase: EncounterPhase
  - started_turn: int
  - turns_in_phase: int
  - severity: float (0-1.0, escalation multiplier)
  - crew_responses: Dict[CrewMember, CrewResponse]
  
  Methods:
  - progress_phase() -> EncounterPhase
    * Checks if phase should escalate
    * Returns new phase or current if staying
  
  - apply_psychological_effects() -> Dict
    * Returns sanity_loss, fear_increase
    * Only in PSYCHOLOGICAL phase
  
  - apply_manifestation_effects() -> Dict
    * Returns equipment_glitches, navigation_error
    * Only in MANIFESTATION phase
  
  - apply_physical_effects(crew_count) -> float
    * Returns hull damage amount
    * Crew count affects damage scale
  
  - attempt_resolution(method) -> float
    * Returns success percentage (0-1.0)
    * Methods: retreat, evasion, weapons, prayer, full_depth, surface, ignore
```

**EncounterManager Class**

Manages all active encounters:

```python
EncounterManager:
  - active_encounters: Dict[str, EldrischEncounter]
  - encounter_history: List[Dict]
  
  Methods:
  - start_encounter(encounter_type, turn) -> str
    * Creates new encounter
    * Returns encounter ID
  
  - tick_encounters(crew_count) -> List[str]
    * Processes all active encounters
    * Applies phase-specific effects
    * Auto-escalates if conditions met
    * Returns list of effect descriptions
  
  - resolve_encounter(encounter_id, method) -> float
    * Attempts resolution using specified method
    * Returns success rate (0-1.0)
    * May eliminate encounter or reduce severity
  
  - get_active_encounter_description() -> str
    * Returns current encounter description
  
  - get_encounter_summary() -> str
    * Formatted report of all encounters
```

#### Integration Points

**Game.__init__():**
```python
self.encounter_manager = EncounterManager()
```

**Game._tick():**
- Called each turn to process active encounters
- Encounters progress through phases automatically
- Effects applied to crew and submarine

**Console Commands:**
- `encounter_status` / `encounter` - Show current encounter(s)
- `resolve_encounter <method>` - Attempt resolution

#### Gameplay Mechanics

**Phase Progression:**
- PSYCHOLOGICAL → MANIFESTATION: 40% chance per turn
- MANIFESTATION → PHYSICAL: 30% chance per turn
- PHYSICAL → CRITICAL: Automatic after 10 turns

**Resolution Methods & Success Rates:**
- `retreat` (60%) - Flee the area
- `evasion` (50%) - Perform evasive maneuvers
- `weapons` (40%) - Attack the entity
- `prayer` (35%) - Spiritual resistance
- `full_depth` (45%) - Dive to maximum depth
- `surface` (30%) - Emergency surface
- `ignore` (10%) - Hope it goes away

**Crew Impact:**
- Encounters trigger crew responses based on type
- Responses affect morale and combat effectiveness
- Possessed crew members pose internal threat

---

## Console Commands

### Supply Management
```bash
supplies / supply_status
  → Show full supply report with percentages and status

ration_level <NORMAL|REDUCED|STRICT|EMERGENCY|CRITICAL>
  → Change consumption multiplier for all resources

resource_summary / res_summary
  → Show quick resource percentage bars
```

### Spy Network
```bash
spy_status / spies
  → List all known, suspected, and exposed spies
  → Show sabotage activity report

eliminate_spy <name>
  → Remove a suspected or exposed spy from crew
```

### Eldritch Encounters
```bash
encounter_status / encounter
  → Show current active encounters
  → Display current phase and effects

resolve_encounter <retreat|evasion|weapons|prayer|full_depth|surface|ignore>
  → Attempt to resolve current encounter using specified method
```

---

## Test Coverage

**Total Tests:** 28 new tests, all passing

**Test Classes:**

1. **TestSupplyManagement** (9 tests)
   - Resource creation and management
   - Consumption and replenishment
   - Ration level effects
   - Ammunition and medical usage
   - Critical resource detection
   - Status report generation

2. **TestSpyNetwork** (6 tests)
   - Spy creation and sabotage
   - Detection and suspicion mechanics
   - Spy discovery and elimination
   - Sabotage report generation
   - Crew morale impact calculation

3. **TestEldrischEncounters** (9 tests)
   - Encounter creation and type variety
   - Phase progression mechanics
   - Psychological and physical effects
   - Resolution attempt success rates
   - Encounter manager ticking
   - Summary report generation

4. **TestSystemIntegration** (3 tests)
   - Cross-system sabotage effects on supplies
   - Encounter impacts on crew fear
   - Combined crisis scenarios

**Run Tests:**
```bash
pytest tests/test_advanced_systems.py -v
pytest tests/ -q  # Full suite
```

---

## Integration Example

```python
from engine.game import Game

game = Game()

# Each turn, systems tick automatically:
game._tick()

# Check supplies:
print(game.supply_inventory.get_status_report())

# Check for spies:
print(game.spy_network.get_sabotage_report())

# Check encounters:
print(game.encounter_manager.get_encounter_summary())

# Attempt to resolve encounter:
success_rate = game.encounter_manager.resolve_encounter(
    encounter_id="enc_1", 
    method="weapons"
)
```

---

## Game Loop Impact

All three systems are integrated into `Game._tick()`:

1. **Supplies tick** - Resource consumption, warnings logged
2. **Spy network tick** - Sabotage attempts, damage applied to supplies
3. **Encounter tick** - Phase progression, effects applied to crew

The systems interact naturally:
- Spy sabotage depletes supplies
- Low supplies stress crew (loyalty impact)
- Stressed crew more susceptible to possession
- Encounters damage resources and crew

---

## File Structure

```
engine/
  ├── supply_management.py (330 lines)
  ├── spy_network.py (340 lines)
  ├── eldritch_encounters.py (410 lines)
  └── game.py (modified, +90 lines for integration)

tests/
  └── test_advanced_systems.py (327 lines, 28 tests)
```

---

## Future Enhancements

1. **Supply Events** - Random events (contamination, discovery of resources, etc.)
2. **Spy Recruitment** - Ability to recruit spies from enemy vessels
3. **Encounter Lore** - Detailed lore entries for each encounter type
4. **Crew Responses** - Full crew loyalty integration with encounter responses
5. **Dynamic Difficulty** - Encounter severity scales with player performance
6. **Supply Trading** - Trade resources at ports
7. **Advanced Sabotage** - Chain sabotage events with escalating effects

---

## Status Summary

✅ **COMPLETE**
- All systems implemented
- All tests passing (28/28 new + 158/158 existing = 186/186 total)
- Game integration complete
- Console commands added
- Game loop integration verified
- Ready for gameplay testing

