# Crew Loyalty and Endgame War System - Complete Guide

## Overview

Phase 13.5 implements a comprehensive crew loyalty and rebellion system with endgame war ranking. This system adds:

1. **Per-crew loyalty tracking** with stress factors and personality modifiers
2. **Crew-wide rebellion management** with escalating rebellion types
3. **War endgame ranking system** with 6 tiers (Civilian to Legendary Commander)
4. **7 console commands** for monitoring crew morale and war status

## Core Components

### 1. LoyaltyTracker - Individual Crew Member Tracking

**File:** `engine/crew_loyalty.py` (lines 44-233)

**Features:**
- **Loyalty Scale:** 0.0-1.0 representing crew member loyalty
- **Status Levels:** LOYAL (0.7+), CONTENT (0.5-0.7), DISSATISFIED (0.3-0.5), MUTINOUS (0.1-0.3), DESERTER (<0.1)
- **Stress Factors:**
  - `fear_level` (0-1.0): Combat danger, near-death experiences
  - `hunger_level` (0-1.0): Lack of supplies, food shortages
  - `exhaustion_level` (0-1.0): Fatigue from long operations
- **Personality System:** brave, cautious, calm, aggressive, disciplined, curious
  - Each personality affects rebellion risk differently (e.g., disciplined -15% risk, aggressive +15% risk)

**Key Methods:**

```python
# Create tracker for crew member
tracker = LoyaltyTracker(crew_id=1, crew_name="John Pilot", personality="brave")

# Apply and relieve stress
tracker.apply_stress(fear=0.2, hunger=0.1, exhaustion=0.3)
tracker.relieve_stress(amount=0.05)

# Record events
tracker.record_achievement('mission_completed', turn=50)
tracker.record_tragedy('comrade_died', turn=51)

# Check rebellion risk
risk = tracker.get_rebellion_risk()  # Returns 0-1.0 value
status = tracker.get_status()  # Returns CrewLoyaltyStatus enum

# Get crew details
stats = tracker.get_stats()  # Returns dict with all current stats
```

**Tracked Achievements:**
- mission_completed (+0.10)
- enemy_destroyed (+0.15)
- survivors_rescued (+0.20)
- narrowly_escaped (+0.08)
- comrade_saved (+0.12)
- commendation (+0.15)

**Tracked Tragedies:**
- comrade_died (-0.15)
- near_death_experience (-0.10)
- unjust_punishment (-0.10)
- abandoned (-0.20)

### 2. RebellionManager - Crew-Wide Rebellion Management

**File:** `engine/crew_loyalty.py` (lines 236-355)

**Manages:**
- Multiple crew member loyalty trackers
- Crew-wide rebellion detection
- Rebellion responses and crew events
- Overall crew morale calculation

**Rebellion Types (Escalating):**
1. MINOR_COMPLAINT (5% severity) - Grumbling, slowdown
2. WORK_SLOWDOWN (20% severity) - Reduced efficiency
3. REFUSAL_TO_OBEY (45% severity) - Dangerous disobedience
4. MUTINY (70% severity) - Armed rebellion
5. MASS_DESERTION (90% severity) - Crew abandonment

**Key Methods:**

```python
# Create manager
manager = RebellionManager()

# Add crew
manager.add_crew_member(crew_id=1, crew_name="John Pilot", personality="brave")
manager.remove_crew_member(crew_id=1)

# Get morale
morale = manager.get_crew_morale()  # Returns 0-1.0, weighted average

# Check for rebellions each turn
rebellions = manager.check_all_rebellions(turn=100)

# Apply crew-wide events
manager.apply_crew_event('combat_victory')  # Improves morale
manager.apply_crew_event('starvation')      # Reduces morale

# Handle rebellion with captain's response
manager.handle_rebellion(
    crew_id=1,
    rebellion_type=RebellionType.MINOR_COMPLAINT,
    response='sympathetic'  # Options: harsh_punishment, sympathetic, ignore, reward, demote
)

# Track desertions and mutinies
manager.total_desertions    # Count of crew who deserted
manager.mutinies_occurred   # Count of mutinies
```

**Crew Events (Affects All Crew):**
- `combat_victory`: +0.05 loyalty, -0.05 fear
- `combat_defeat`: -0.10 loyalty, +0.10 fear
- `starvation`: -0.15 loyalty, +0.20 hunger
- `successful_rescue`: +0.10 loyalty
- `shore_leave`: +0.10 loyalty, -0.10 stress
- `accident`: -0.05 loyalty, +0.10 fear
- `commendation`: +0.05 loyalty

**Response Options:**
- `harsh_punishment`: +0.20 fear, -0.15 loyalty
- `sympathetic`: +0.10 loyalty, -0.10 fear
- `ignore`: No change
- `reward`: +0.15 loyalty, -0.05 fear
- `demote`: +0.05 fear, -0.05 loyalty

### 3. WarEndgameStats - War Ranking and Endgame Scoring

**File:** `engine/crew_loyalty.py` (lines 357-486)

**Tracks:**
- Combat achievements: ships destroyed, tonnage sunk, capital ships sunk
- Crew status: alive at end, deserted, mutinies, average loyalty
- Heroic actions: survivors rescued, near-death escapes, missions completed
- Mission duration: turns survived

**War Ranks (6 Tiers):**

1. **CIVILIAN** (0 kills)
   - Description: "You did not engage the enemy"
   - Score: Base + crew bonus

2. **RECRUIT** (1-4 kills)
   - Description: "Your first engagements showed promise"
   - Score: 10 pts/kill + crew bonus

3. **SAILOR** (5-9 kills)
   - Description: "You proved yourself in combat"
   - Score: 10 pts/kill + crew bonus

4. **VETERAN** (10-24 kills)
   - Description: "Your experience earned you respect"
   - Score: 10 pts/kill + crew bonus

5. **SUBMARINE_ACE** (25-49 kills)
   - Description: "You became a feared submarine commander"
   - Score: 10 pts/kill + crew bonus

6. **CAPITAL_SHIP_KILLER** (5+ capital ships sunk)
   - Description: "You sank major enemy vessels"
   - Score: 25 pts/capital ship + crew bonus

7. **LEGENDARY_COMMANDER** (50+ kills + perfect loyalty + 15+ rescued)
   - Description: "You are a legend among submariners"
   - Score: 10 pts/kill + 25 pts/capital + full bonuses

**Scoring Calculation:**

```python
score = (
    enemy_ships_destroyed * 10 +
    capital_ships_sunk * 25 +
    survivors_rescued * 50 +
    (crew_average_loyalty > 0.8) * 500 +  # Perfect loyalty bonus
    (war_victory) * 2000 +                 # Victory bonus
    crew_morale_bonus                      # Crew loyalty bonus
)
```

**Key Methods:**

```python
# Create stats tracker
stats = WarEndgameStats()

# Accumulate combat stats
stats.enemy_ships_destroyed = 75
stats.capital_ships_sunk = 3
stats.survivors_rescued = 100
stats.missions_completed = 20

# Set final crew stats (populate before ending war)
stats.crew_alive_at_end = 4
stats.crew_total_recruited = 8
stats.crew_deserted = 2
stats.crew_mutinies = 1
stats.crew_average_loyalty = 0.75
stats.turns_survived = 150

# Calculate results
war_rank = stats.calculate_war_rank()     # Returns WarRank enum
final_score = stats.calculate_final_score()  # Returns int score
report = stats.get_final_report()         # Returns formatted string
```

## Console Commands

### Available Commands

#### 1. `crew_loyalty` / `crew_status`
Shows overall crew loyalty summary:
- Average crew morale percentage
- Total crew count
- Total desertions and mutinies
- Individual crew member loyalty status

Example:
```
Crew Morale: 75.23%
Total Crew: 5
Desertions: 1
Mutinies: 0
  - Crew 1: Loyalty 0.80 [CONTENT]
  - Crew 2: Loyalty 0.65 [CONTENT]
  - Crew 3: Loyalty 0.45 [DISSATISFIED]
  - Crew 4: Loyalty 0.20 [MUTINOUS]
  - Crew 5: Loyalty 0.90 [LOYAL]
```

#### 2. `crew_morale` / `morale`
Shows average crew morale with warnings:
- Displays percentage and crew count
- Warnings if morale < 50% (caution) or < 30% (danger)

#### 3. `rebellion_check` / `rebellion_status`
Displays crew members at high rebellion risk:
- Lists any crew with >50% rebellion risk
- Shows their status and exact risk percentage
- Total desertions and mutinies count

#### 4. `crew_loyalty_detail <crew_id>`
Shows detailed report for specific crew member:
- Loyalty value and status
- All stress levels (fear, hunger, exhaustion)
- Rebellion risk percentage
- Personality type
- Career statistics (missions, near-deaths, rescues, etc.)

Example:
```
Crew 1 Detail Report:
  Loyalty: 0.85
  Status: LOYAL
  Fear Level: 0.20
  Hunger Level: 0.10
  Exhaustion Level: 0.15
  Rebellion Risk: 12.50%
  Personality: brave
  Missions Survived: 8
  Times Nearly Died: 2
  Rescued Survivors: 12
  Combat Victories: 15
  Comrades Lost: 1
```

#### 5. `war_status` / `war_stats`
Displays current war statistics:
- Ships destroyed and tonnage sunk
- Capital ships sunk
- Crew alive/recruited/deserted
- Survivors rescued
- Missions completed and turns survived

#### 6. `end_war` / `complete_war` / `surrender`
Ends current war and generates final report:
- Calculates war rank and final score
- Shows complete war statistics
- Displays rank description and mission outcome

## Integration with Game

### Game Initialization

The Game class automatically initializes both systems:

```python
class Game:
    def __init__(self):
        ...
        self.rebellion_manager = RebellionManager()
        self.war_endgame = WarEndgameStats()
```

### Recommended Game Loop Integration

In your `_tick()` method:

```python
def _tick(self):
    # ... existing turn logic ...
    
    # Check for crew rebellions
    if self.rebellion_manager:
        rebellions = self.rebellion_manager.check_all_rebellions(self.turn)
        for rebellion in rebellions:
            crew_id = rebellion['crew_id']
            rebellion_type = rebellion['type']
            # Log and handle rebellion
            print(f"Crew {crew_id} has initiated {rebellion_type.name}")
    
    # Track combat victories
    # When enemy sunk:
    if self.war_endgame:
        self.war_endgame.enemy_ships_destroyed += 1
        self.war_endgame.enemy_tonnage_sunk += 5000  # Estimate
        if is_capital_ship:
            self.war_endgame.capital_ships_sunk += 1
        # Apply crew event
        self.rebellion_manager.apply_crew_event('combat_victory')
```

## Testing

All systems are thoroughly tested with 158 total tests:

**Phase 13.5 Tests:**
- `test_crew_loyalty.py`: 43 tests for loyalty, rebellion, and war systems
- `test_crew_loyalty_console.py`: 17 integration tests for console commands

**Run tests:**
```bash
pytest tests/test_crew_loyalty.py -v          # Crew loyalty tests
pytest tests/test_crew_loyalty_console.py -v  # Console integration tests
pytest tests/ -q                               # All tests (158 total)
```

## Example Usage Scenarios

### Scenario 1: Monitoring Crew Morale

```
> crew_morale
Average Crew Morale: 65.32% (8 crew members)
CAUTION: Crew morale is low - monitor for signs of unrest

> crew_loyalty
Crew Morale: 65.32%
Total Crew: 8
Desertions: 2
Mutinies: 0
  - Crew 1: Loyalty 0.80 [CONTENT]
  - Crew 2: Loyalty 0.45 [DISSATISFIED]
  - Crew 3: Loyalty 0.25 [MUTINOUS]
  ...

> crew_loyalty_detail 3
Crew 3 Detail Report:
  Status: MUTINOUS (Rebellion Risk: 68.50%)
  Fear Level: 0.85
  Hunger Level: 0.70
  Exhaustion Level: 0.75
  Personality: aggressive
```

### Scenario 2: Ending War and Getting Final Rank

```
> war_status
Current War Statistics:
  Enemy Ships Destroyed: 75
  Enemy Tonnage Sunk: 150000 tons
  Capital Ships Sunk: 3
  Crew Alive: 6/8
  Crew Deserted: 2
  Survivors Rescued: 95
  Near Death Escapes: 12
  Missions Completed: 25
  Turns Survived: 247

> end_war
══════════════════════════════════════════════════════════
WAR END REPORT
══════════════════════════════════════════════════════════

War Rank: SUBMARINE_ACE
"You became a feared submarine commander"

Final Score: 2345

Combat Record:
  Enemy Ships Destroyed: 75
  Capital Ships Sunk: 3
  Enemy Tonnage Sunk: 150000 tons

Crew Record:
  Crew Alive at War End: 6/8
  Desertions: 2
  Mutinies: 0
  Average Loyalty: 72.50%

Heroic Actions:
  Survivors Rescued: 95
  Near Death Escapes: 12
  Missions Completed: 25
  War Turns Survived: 247

War Victory: No
══════════════════════════════════════════════════════════
```

## Design Decisions

1. **Per-Crew Tracking:** Each crew member has independent loyalty, stress, and rebellion risk, allowing granular control
2. **Personality Modifiers:** Personality types affect how crew members respond to stress and orders
3. **Escalating Rebellions:** Rebellion types escalate with risk level, allowing captain to intervene before mass desertion
4. **Event-Driven Loyalty:** Loyalty changes via specific events (achievements, tragedies, crew events) rather than passive decay
5. **Multi-Factor Ranking:** War rank considers combat, crew welfare, and heroism - not just kills
6. **Transparent Scoring:** Score calculation is visible and fair, rewarding both combat success and crew morale

## Future Enhancements

- Crew personality clashes affecting rebellion risk
- Special events based on crew background/nationality
- Crew member quests and personal missions
- Ranking-based unlocks (new ship types, upgraded crew)
- Persistent crew roster across missions
- Court martial system for mutineers
- Shore leave implementation affecting stress relief
