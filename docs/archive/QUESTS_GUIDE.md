# Quest & Mission System Guide

## Overview

The quest system adds dynamic mission-based gameplay to your roguelike submarine adventure. Accept contracts, pursue objectives, and encounter eldritch horrors lurking in the deep.

---

## Mission Types

### Standard Military Missions

**Patrol** ⭐ (Difficulty 1)
- Routine reconnaissance of designated waters
- Objective: Maintain patrol route without detection
- Reward: 100 XP, 1000 credits
- Time limit: 300 turns
- Best for: Getting started, learning the game

**Smuggle** ⭐⭐⭐ (Difficulty 3)
- Transport contraband cargo to destination
- Objective: Reach location undetected with cargo intact
- Reward: 250 XP, 5000 credits
- Penalty: 2500 credits if cargo lost
- Time limit: 400 turns
- Challenge: Stealth navigation and evasion

**Sabotage** ⭐⭐⭐ (Difficulty 3)
- Destroy or cripple an enemy vessel
- Objective: Sink target ship; escape without detection
- Reward: 300 XP, 3000 credits
- Time limit: 250 turns
- Challenge: Combat under pressure, escape routes

**Rescue** ⭐⭐ (Difficulty 2)
- Extract survivors or intelligence operatives
- Objective: Reach location, retrieve operatives, return safely
- Reward: 200 XP, 4000 credits
- Time limit: 350 turns
- Challenge: Timed extraction, safe passage

**Escort** ⭐⭐ (Difficulty 2)
- Protect allied merchant convoy from attack
- Objective: Defend convoy; no merchant losses allowed
- Reward: 150 XP, 2000 credits
- Time limit: 400 turns
- Challenge: Multi-target defense, keeping position

**Hunt** ⭐⭐⭐⭐ (Difficulty 4)
- Locate and sink high-value target (cruiser, warship)
- Objective: Find and destroy specific target ship
- Reward: 400 XP, 6000 credits
- Time limit: 500 turns
- Challenge: Finding a specific target in vast ocean

**Supply Run** ⭐⭐ (Difficulty 2)
- Deliver supplies to covert location
- Objective: Reach destination with supplies, leave without trace
- Reward: 120 XP, 1500 credits
- Time limit: 300 turns
- Challenge: Precise navigation, avoiding patrols

**Reconnaissance** ⭐⭐ (Difficulty 2)
- Spy on enemy positions and document activity
- Objective: Gather intelligence on specified region
- Reward: 180 XP, 2500 credits
- Time limit: 300 turns
- Challenge: Observation without engagement

### Eldritch Horror Encounters

Strange phenomena lurking in the deep ocean, beyond normal military operations.

**The Deep One** ⭐⭐⭐⭐⭐ (Difficulty 5)
- Ancient entity awakens in the abyss
- Objective: Survive encounter; do not engage
- Reward: 500 XP, 10,000 credits (if successful)
- Penalty: 200 XP, 5000 credits (if failed)
- Time limit: 150 turns
- Challenge: Unknown threat, crew sanity at risk

**Whispers in the Dark** ⭐⭐⭐⭐ (Difficulty 4)
- Crew hears strange sounds through hull during deep dive
- Objective: Surface and escape; maintain crew sanity
- Reward: 300 XP, 5000 credits
- Penalty: 100 XP, 2000 credits (if exposed)
- Time limit: 120 turns
- Challenge: Rising dread, time pressure

**The Sunken City** ⭐⭐⭐⭐ (Difficulty 4)
- Discover vast ruins on ocean floor
- Objective: Document location and return; investigate if brave
- Reward: 400 XP, 8000 credits
- Penalty: 150 XP (if encounter goes wrong)
- Time limit: 200 turns
- Challenge: Decision-making: safety vs. glory

**Spectral Signals** ⭐⭐⭐⭐ (Difficulty 4)
- Sonar detects impossible contacts - submarines from another time?
- Objective: Investigate signals without engaging; escape if threatened
- Reward: 350 XP, 6000 credits
- Time limit: 180 turns
- Challenge: Unknown intentions, potential danger

**The Sacrifice** ⭐⭐⭐ (Difficulty 3)
- Strange ritual marks appear in sonar readings
- Objective: Leave the area; do not interfere with unknown ceremony
- Reward: 250 XP, 3000 credits
- Penalty: 300 XP (if interrupted)
- Time limit: 100 turns
- Challenge: Resisting curiosity, strict avoidance

---

## Quest Commands

### Generating Missions

```
mission [type]           # Generate new mission (random type if not specified)
mission patrol           # Generate patrol mission
mission smuggle           # Generate smuggle mission
mission sabotage          # Generate sabotage mission
mission eldritch          # Generate eldritch horror encounter
available                # List all available missions
```

### Managing Missions

```
accept <mission_id>      # Accept a mission and make it active
quest_info               # Show details of active mission
complete                 # Successfully complete active mission
fail [reason]            # Fail current mission with optional reason
abandon                  # Abandon active mission
```

---

## Game Flow

### 1. Generate Mission
```
> mission
=== NEW MISSION AVAILABLE ===
Name: Smuggle Operation
Type: smuggle
Difficulty: ★★★☆☆
Description: Transport contraband cargo to destination without detection
Objective: Reach destination undetected with cargo intact
Rewards: 250 XP, 5000 credits
Penalties on failure: 200 XP, 2500 credits
Time limit: 400 turns
Mission ID: mission_7
Type 'accept mission_7' to begin this mission
```

### 2. Accept Mission
```
> accept mission_7
✓ Accepted mission: Smuggle Operation
```

### 3. Monitor Progress
```
> quest_info
=== ACTIVE MISSION ===
Name: Smuggle Operation
Type: smuggle
Objective: Reach destination undetected with cargo intact
Difficulty: ★★★☆☆
Progress: 0%
Time: 0 / 400 turns
```

### 4. Complete Mission
```
> complete
✓ Mission Complete: Smuggle Operation
Rewards: +250 XP, +5000 credits
```

---

## Mission Success Conditions

### Patrol
- ✓ Complete patrol duration without being sunk
- ✓ Avoid major damage/detection
- ✗ Sunk by enemy contact

### Smuggle
- ✓ Reach destination undetected with cargo
- ✓ Evade enemy forces
- ✗ Cargo destroyed
- ✗ Captured/detected at destination

### Sabotage
- ✓ Sink target vessel
- ✓ Escape without being sunk
- ✗ Target survives with full integrity
- ✗ Your submarine destroyed

### Rescue
- ✓ Reach extraction point
- ✓ Retrieve operatives
- ✓ Return safely
- ✗ Extraction point compromised
- ✗ Operatives lost

### Escort
- ✓ No merchant vessel losses
- ✓ Defend against all attacks
- ✓ Return to port
- ✗ Any merchant ship sunk
- ✗ Escorts destroyed

### Hunt
- ✓ Find specific target
- ✓ Sink target vessel
- ✓ Escape undetected
- ✗ Target escapes or survives

### Supply Run
- ✓ Reach destination
- ✓ Leave supplies and depart
- ✓ No detection
- ✗ Detected by patrol
- ✗ Supplies compromised

### Reconnaissance
- ✓ Document enemy activity
- ✓ Return safely
- ✗ Discovered/captured

### Eldritch Encounters
- ✓ Encounter and survive
- ✓ Maintain crew sanity
- ✓ Escape danger zone
- ✗ Crew panic
- ✗ Supernatural danger escalates

---

## Mission Rewards

### XP Rewards
Completing missions awards player XP:
- **Easy missions (⭐):** 100-150 XP
- **Medium missions (⭐⭐):** 150-200 XP
- **Hard missions (⭐⭐⭐):** 250-300 XP
- **Very hard missions (⭐⭐⭐⭐):** 350-400 XP
- **Extreme missions (⭐⭐⭐⭐⭐):** 500 XP

### Credits
Currency for port upgrades and resupply:
- **Easy missions:** 1000-2000 credits
- **Medium missions:** 2000-4000 credits
- **Hard missions:** 3000-6000 credits
- **Very hard missions:** 5000-8000 credits
- **Extreme missions:** 8000-10000 credits

### Penalties
Mission failures apply both XP and credit penalties:
- **Sabotage failure:** -200 XP, -5000 credits
- **Smuggle failure:** -100 XP, -2500 credits
- **Eldritch horror failure:** -200 XP, -5000 credits

---

## Mission Timing

### Time Limits
Each mission has a turn limit:
- If limit is exceeded, mission automatically fails
- Careful time management is essential
- Example: "Smuggle" = 400 turns to reach destination
- `time_remaining` shows turns left before auto-fail

### Time Pressure Tactics
- Early game: Generous time limits to learn
- Mid game: Moderate pressure (300-400 turns)
- Late game: Severe pressure (100-150 turns)

---

## Strategic Tips

### Mission Selection
- **Starting out:** Choose ⭐ or ⭐⭐ missions to learn
- **Mid-game:** Mix difficulties (some easy, some hard)
- **Late-game:** Hunt high-value targets (⭐⭐⭐⭐)
- **Variety:** Rotate mission types to improve different skills

### Mission Strategy
- **Patrol:** Practice sonar and evasion
- **Smuggle:** Test stealth capabilities
- **Sabotage:** Develop combat tactics
- **Rescue:** Learn precise navigation
- **Hunt:** Build target acquisition skills
- **Eldritch:** Accept challenges only when prepared

### Crew Management
- Assign experienced crew to missions
- Use specialists for mission-specific tasks
- Rest crew between high-difficulty missions
- Track crew stress for morale

### Risk Management
- Check time remaining frequently
- Use `available` to review all options
- Accept missions matching your skill
- `abandon` if situation becomes hopeless
- Penalties for abandonment are better than total loss

---

## Eldritch Horror - Special Rules

### Sanity System (Future)
- Crew gains stress from horror encounters
- High stress increases chance of failure
- Some crew might go mad

### Investigation vs Safety
- Eldritch missions offer choices
- Investigate = more rewards but higher risk
- Play safe = escape but lower rewards
- Your crew will be affected either way

### Unknown Threats
- Eldritch encounters may have unknown effects
- Sonar readings may be misleading
- Creature behavior unpredictable
- Success requires courage AND caution

---

## Career Statistics

Your quest history is tracked:

```
player_stats       # View career progress

Career Stats:
  quests_completed  : 12
  quests_failed     :  2
  quests_abandoned  :  1
  total_rewards_xp  : 2850
  total_penalties_xp:  300
  net_xp            : 2550
  net_credits       : 18500
```

---

## Examples

### Example 1: Easy Start
```
> mission patrol
[Mission generated: Routine Patrol]
> accept mission_1
> quest_info         # Check progress
> complete           # Finished without being detected
✓ Mission Complete: Routine Patrol
Rewards: +100 XP, +1000 credits
```

### Example 2: Challenging Smuggle
```
> mission smuggle
[Mission generated: Cargo Smuggle]
> accept mission_2
> sonar             # Check for enemy contacts
> dive 100          # Go deep to evade
> quest_info        # Check time remaining
> complete          # Successfully avoided detection
✓ Mission Complete: Cargo Smuggle
Rewards: +250 XP, +5000 credits
```

### Example 3: Horror Encounter
```
> mission eldritch
[Mission generated: Spectral Signals]
> accept mission_3
> sonar             # Detect strange contacts
> quest_info        # High difficulty, short time limit
> status            # Check crew stress rising
> fail Crew panic from strange sounds
✗ Mission Failed: Spectral Signals
Reason: Crew panic from strange sounds
Penalties: -350 XP, -6000 credits
```

### Example 4: Abandonment
```
> mission hunt
> accept mission_4
> quest_info        # Difficult target hunt
[After failed attempts...]
> abandon           # Give up on this mission
✗ Mission Abandoned: Hunt Specialty Target
[No rewards, no penalties, but mission noted in history]
```

---

## Advanced Mechanics

### Dynamic Mission Difficulty
- Mission difficulty adjusts based on your level
- Defeating high-difficulty missions unlocks tougher ones
- Career stat multiplier affects available missions

### Cascading Objectives
Future phases will add:
- Multi-stage missions (objective 1 → 2 → 3)
- Mission chains (quest leads to next quest)
- Faction-specific contracts
- Hidden objectives and plot twists

### Procedural Generation
Each mission is procedurally generated:
- Same mission type plays differently
- Different enemy compositions
- Varying weather and conditions
- Unique encounter scenarios

---

## Troubleshooting

**Q: How do I generate a mission?**
A: Use `mission [type]` to generate. Types: patrol, smuggle, sabotage, rescue, escort, hunt, supply_run, reconnaissance, eldritch

**Q: Can I have multiple active missions?**
A: No, only one mission at a time. Complete or abandon your current mission first.

**Q: What if I run out of time?**
A: Mission auto-fails when time limit is exceeded. Accept the penalty and try again.

**Q: Can I redo a failed mission?**
A: Yes, generate a new mission of the same type. Each is procedurally unique.

**Q: How do eldritch missions differ?**
A: They feature unknown threats, horror elements, and often require difficult choices between safety and investigation.

**Q: Do my crew gain XP from missions?**
A: Crew XP comes from specific actions (sonar use, combat, repairs). Missions track player XP.

---

For quick reference, see **QUICK_REFERENCE.md**  
For overall gameplay, see **GAMEPLAY.md**
