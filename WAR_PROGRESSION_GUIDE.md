# War Progression & Dynamic Difficulty System

## Core Concept

The war progresses from September 1939 (Stalemate) through 1945+ (Endgame), with each year and major historical event affecting:

1. **Available Missions** - Mission pool changes based on war status
2. **Enemy Behavior** - Difficulty scaling with war progression
3. **Supply Availability** - Shortages increase as war progresses
4. **Player Advantage/Disadvantage** - Shifts based on war outcomes
5. **Random Events** - Different events become more common

## Historical War Progression Timeline

### 1939: STALEMATE (Phoney War)

**Historical Context:**
- Germany invades Poland (September 1)
- Minor naval engagements
- Both sides building up
- Neither has clear advantage

**Game Status:**
- War Status: STALEMATE
- Axis Advantage: ~50%
- Allied Advantage: ~50%
- Supply Shortage: 10-25%

**Available Missions:**
- Patrol commerce lanes
- Reconnaissance missions
- Escort duties
- Standard naval engagements

**Difficulty:** Easy-Medium
- Fewer enemy escorts
- Standard supply levels
- Frequent resupply opportunities
- Crew relatively fresh

---

### 1940: Axis Momentum

**Historical Context:**
- Germany invades France (May 10)
- Battle of Britain (Summer-Fall)
- Germany dominates continent
- Sub warfare intensifies

**Game Status:**
- War Status: STALEMATE (early) → AXIS_ADVANTAGE (late)
- Axis Advantage: 50% → 65%
- Allied Advantage: 50% → 35%
- Supply Shortage: 15-35%

**Available Missions:**
- Attack convoys heading to Britain
- Commerce raiding in Atlantic
- Mine-laying operations
- Sabotage missions

**Difficulty:** Medium
- Increased escort patrols
- More frequent air patrols
- Supply shortages appear
- Crew morale stable but tensions rise

---

### 1941: Operation Barbarossa (War's Turning Point)

**Historical Context:**
- Germany invades Soviet Union (June 22)
- Japan joins Axis (Dec 11)
- USA enters war (Dec 7)
- Atlantic battle intensifies

**Game Status:**
- War Status: AXIS_ADVANTAGE
- Axis Advantage: 65% → 70%
- Allied Advantage: 35% → 30%
- Supply Shortage: 25-40% (increases mid-year)

**Available Missions:**
- Atlantic convoy hunting
- Mediterranean patrols
- Supply lines protection (if German/Japanese player)
- Intelligence gathering

**Difficulty:** Medium-Hard
- More active defense
- Better-coordinated escorts
- Supply shortages significant
- Crew stress increases
- First real equipment failures possible

**Key Events:**
- Mid-year supply shortage jump (Barbarossa drain)
- Increased Allied production begins
- American ships entering Atlantic

---

### 1942: Continued Axis Pressure, Tide Turning

**Historical Context:**
- Battle of Stalingrad (Aug-Feb 1943)
- Battle of Midway (June) - Pacific turning point
- Germany loses initiative
- First major Allied victory

**Game Status:** (Two phases)

**Early 1942 (Jan-Sept):**
- War Status: AXIS_ADVANTAGE
- Axis Advantage: 70% (peaks ~late summer)
- Supply Shortage: 30-45%

**Late 1942 (Oct-Dec - Stalingrad/Tunisia):**
- War Status: STALEMATE (shifting)
- Axis Advantage: 65% → 55%
- Allied Advantage: 35% → 45%
- Supply Shortage: 40-50%

**Available Missions:**
- High-value target hunting (capital ships)
- Supply line interdiction intensifies
- Rescue missions (increasing)
- Code-breaking intelligence gathering

**Difficulty:** Hard
- Coordinated defense systems
- Sonar technology improving
- Supply critical for sustaining
- Crew morale affected by repeated stress
- Equipment wearing out (torpedo defects more common)

**Key Events:**
- Stalingrad defeat (late year)
- Tunisia campaign begins
- American production ramping up

---

### 1943: Allied Ascendancy Begins

**Historical Context:**
- Sicily invasion (July)
- Italy switches sides (Sept)
- Germany losing ground everywhere
- Convoy systems improving
- Radar becoming widespread

**Game Status:**
- War Status: STALEMATE → ALLIED_ADVANTAGE
- Axis Advantage: 55% → 40%
- Allied Advantage: 45% → 60%
- Supply Shortage: 45-55% (critical for Axis)

**Available Missions:**
- Defense missions (protect shipping if Allied)
- Break supply blockades (if Axis)
- Combined operations (new)
- Search & rescue increasing
- Intelligence missions critical

**Difficulty:** Hard-Very Hard
- Advanced sonar systems widespread
- Better ship formations
- Air support increases
- Supply critically limited for Axis
- Crew exhaustion visible
- Many submarines lost (historical)

**Key Events:**
- Radar detection becomes routine
- Convoy losses reduce access
- Submarine losses accelerate
- New advanced tactics needed

---

### 1944: Axis Collapse Begins

**Historical Context:**
- D-Day (June 6)
- Operation Overlord success
- Germany forced onto defense everywhere
- Japan losing Pacific campaign
- Italy occupied by Allies

**Game Status:**
- War Status: ALLIED_ADVANTAGE
- Axis Advantage: 40% → 20%
- Allied Advantage: 60% → 80%
- Supply Shortage: 60-75% (severe for Axis)

**Available Missions:**
- Liberation operations (if Allied)
- Final defensive stands (if Axis)
- Supply line defense becomes critical
- Strategic bombing support
- Special operations increase

**Difficulty:** Very Hard
- Overwhelming opposition (Axis)
- Victory assured but dangerous (Allied)
- Supply shortage forces tough choices
- Crew mutiny risk rises
- Submarine reliability questionable
- Missions become desperate

**Key Events:**
- Fuel shortages critical
- Crew morale crises possible
- Final U-boats deploy
- Technology unable to match

---

### 1945: War Ending - Endgame

**Historical Context:**
- Germany surrounded
- Japan island-hopping retreat
- Soviet Army entering Germany
- Final desperate offensives
- Unconditional surrender declarations

**Game Status** (Two phases):

**Jan-Aug 1945 (AXIS_DECLINE):**
- War Status: AXIS_DECLINE
- Axis Advantage: 20% → 5%
- Allied Advantage: 80% → 95%
- Supply Shortage: 70-85% (critical)

**Sept+ 1945 (ENDGAME):**
- War Status: ENDGAME
- War officially ended (Sept 2)
- Victory type determined
- Final score calculated

**Available Missions:**
- Final strategic objectives
- Rescue and evacuation (both sides)
- POW retrieval (both sides)
- Last stands and defensive positions
- Mysterious encounters possible

**Difficulty:** Extreme
- Every mission could be last
- Supply literally running out
- Crew mutiny very likely if not handled well
- Final enemy acts desperation-driven
- Victory earned through survival
- Failures are total defeat

**Key Events:**
- Germany surrenders (May 8)
- Japan surrenders (Sept 2)
- War ends
- Final victory type assigned

---

## Supply Shortage System Impact

### Supply Shortage by War Status

```
STALEMATE:              10-25%  (comfortable margins)
  → Can restock regularly
  → Food and fuel abundant
  → Crew morale natural
  → Long patrols possible

AXIS_ADVANTAGE:         20-40%  (beginning scarcity)
  → Resupply takes planning
  → Some rationing considered
  → Crew notices but accepts
  → Patrols still sustainable

ALLIED_ADVANTAGE:       15-30%  (supply lines disrupted)
  → Limited resupply options
  → Rationing becomes normal
  → Crew grumbles increase
  → Missions carefully planned

AXIS_DECLINE:           50-80%  (critical shortage - desperate times)
  → Resupply missions fail
  → Mandatory severe rationing
  → Crew mutiny becomes real threat
  → Patrols shortened, missions risky
  → Equipment cannibalized

ENDGAME:                70-90%  (virtually nothing available)
  → No resupply possible
  → Starvation rationing
  → Crew barely functional
  → One final mission attempt
  → Survival becomes only objective
```

### Gameplay Impact of Supply Shortage

**At 0-20% (Comfortable):**
- No crew morale penalty
- Full rationing levels available
- All equipment operational
- Crew performs at peak

**At 20-40% (Limited):**
- Minor crew morale penalty (-5%)
- Can set REDUCED rations
- Equipment degradation minimal
- Crew accepts situation

**At 40-60% (Critical):**
- Significant morale penalty (-15%)
- Must set STRICT rations
- Equipment failures increase
- Crew discontent growing

**At 60-80% (Severe):**
- Major morale penalty (-25%)
- EMERGENCY rations mandatory
- Equipment breaking down
- Crew mutiny risk rises (30%+)

**At 80-100% (Starvation):**
- Severe morale penalty (-40%)
- CRITICAL rations only (starvation)
- Most equipment offline
- Crew mutiny very likely (60%+)
- Crew illness outbreaks

## Random Event Frequency Scaling

Event probability adjusts based on war status to maintain challenge:

```
STALEMATE:
  - Positive events more common
  - Combat surprises rare
  - Weather events moderate

AXIS_ADVANTAGE:
  - Balanced positive/negative
  - Supplies harder to find
  - Opportunities scarce

ALLIED_ADVANTAGE:
  - Negative events increase
  - Danger encounters frequent
  - Sabotage risks rise

AXIS_DECLINE:
  - Mostly negative events
  - Disasters common
  - Few opportunities
  - Equipment failures frequent

ENDGAME:
  - Mix of last opportunities
  - Extreme dangers
  - Mysterious encounters
  - Final moments
```

## Mission Difficulty Scaling

Mission difficulty (1-5 scale) adjusts based on year:

```
1939: Average difficulty 1-2
1940: Average difficulty 1-3
1941: Average difficulty 2-3
1942: Average difficulty 2-4
1943: Average difficulty 3-4
1944: Average difficulty 3-5
1945: Average difficulty 4-5
```

Higher difficulty means:
- Better enemy escort
- More patrol aircraft
- Longer time limits (risky)
- Higher rewards
- Greater risk

## Player Impact on War Status

Player actions affect the war balance:

```
Player destroys merchant:    -0.5% axis advantage
Player destroys combat ship: -1.0% axis advantage
Player sinks capital ship:   -2.0% axis advantage
Player loses submarine:      +1.0% axis advantage (morale)
Player completes mission:    -0.5% axis advantage (strategic)
Player fails mission:        +1.0% axis advantage
Random convoy battle:        ±2-5% (random outcome)
```

This means:
- Successful player campaigns shift war toward Allies
- Failed operations lengthen war
- Player becomes actual strategic factor
- Victory requires both combat skill AND strategic thinking

## Crew Experience by Era

### Early War (1939-1940)
- Crew mostly inexperienced
- High learning curve
- Morale initially high
- Losses demoralizing

### Mid War (1941-1943)
- Experienced crew surviving
- Veterans have valuable skills
- Losses are irreplaceable
- Crew knows dangers

### Late War (1943-1945)
- Skeleton crews common (replacements rare)
- Exhausted but skilled
- High casualty expectations
- Loyalty tested repeatedly

### Endgame (1945+)
- Final survivors are elite
- Crew bond extremely strong
- One more patrol mentality
- Victory or death only outcomes

## Example Seasonal Scenarios

### Spring 1942
- War Status: AXIS_ADVANTAGE
- Supply: 35% shortage
- Typical Mission: Hunt convoys in Atlantic
- Difficulty: 2-3/5
- Rewards: +100XP, +1500 credits
- Risks: Moderate (frequent escorts)
- Crew Morale: Natural (~70%)
- Special Events: None seasonal

### Winter 1943
- War Status: STALEMATE → ALLIED_ADVANTAGE
- Supply: 50% shortage
- Typical Mission: High-value target hunt
- Difficulty: 3-4/5
- Rewards: +200XP, +3000 credits
- Risks: High (radar equipped escorts)
- Crew Morale: Strained (~55%)
- Special Events: Equipment failures common

### Summer 1944
- War Status: ALLIED_ADVANTAGE
- Supply: 65% shortage (critical)
- Typical Mission: Supply blockade breakthrough
- Difficulty: 4/5
- Rewards: +300XP, +2000 credits
- Risks: Very High (coordinated defense)
- Crew Morale: Crisis (~35%)
- Special Events: Mutiny possible, sabotage detected

### Fall 1945 (Endgame)
- War Status: ENDGAME
- Supply: 85% shortage (starvation)
- Typical Mission: Final strategic objective
- Difficulty: 5/5
- Rewards: +500XP, +5000 credits, war ending bonus
- Risks: Extreme (desperate enemy)
- Crew Morale: Variable (leadership-dependent)
- Special Events: War end, final encounters

## Victory Type Determination

Victory type determined at September 1945:

```
Performance Throughout War          Final Title
────────────────────────────────────────────────
0 ships sunk                    →    CIVILIAN (failure)
1-4 ships sunk                  →    RECRUIT
5-9 ships sunk                  →    SAILOR
10-24 ships sunk                →    VETERAN
25-49 ships sunk                →    SUBMARINE_ACE
50+ ships + 5 capitals sunk     →    CAPITAL_SHIP_KILLER

50+ ships + perfect crew        →    LEGENDARY_COMMANDER
All conditions + war victory    →    LEGENDARY_COMMANDER (max)

No ships sunk                   →    CIVILIAN (special: survivor)
```

## Replayability Through War Progression

Each playthrough has different feel based on:

1. **Starting Year** (if selectable)
   - Start 1939: Full campaign experience
   - Start 1943: Late-war desperate feeling
   - Start 1944: Endgame survival only

2. **Nation Choice**
   - Axis: Face defeat but tactical challenges
   - Allies: Face overwhelming enemies
   - Different technology progression

3. **Random Seed**
   - Determines event order
   - Enemy encounters
   - Supply shortage pattern
   - Weather conditions

4. **Objectives Selected**
   - Commerce raiding: Aggressive gameplay
   - Survival: Defensive gameplay
   - Crew-focused: Social gameplay
   - Intelligence: Strategic gameplay

5. **Difficulty Settings** (if implemented)
   - Easy: More supplies, fewer events
   - Normal: Historical accuracy
   - Hard: Less supplies, more events
   - Impossible: Starvation rations, max enemies

---

**The war progression ensures every playthrough feels different while maintaining historical authenticity.**
