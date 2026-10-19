# Crew Management & Player Progression Guide

## Overview

Your submarine is crewed by highly trained personnel. As captain, you can recruit, manage, and develop your crew. Your own career also advances through successful patrols, with opportunities to upgrade your submarine.

---

## Crew System

### Recruiting Crew

When at port (or starting a new game), you can recruit crew members to fill your submarine.

**Command:**
```
recruit [skill]
```

**Examples:**
```
recruit                    # Recruit random crew member
recruit sonar             # Recruit crew with sonar specialty
recruit engineering       # Recruit engineer
```

**Skills Available:**
- `sonar` - Sonar operator
- `torpedo` - Torpedo specialist
- `engineering` - Engineer
- `damage_control` - Damage control specialist
- `navigation` - Navigator

Each recruited crew member has:
- **Name & Rank**: Randomly assigned from historical names/ranks
- **Primary Skill**: Their main expertise area
- **Secondary Skills**: Additional capabilities
- **Level**: Starting at 1, increases with XP
- **Stress**: 0-1 scale; high stress reduces effectiveness
- **Morale**: 0-1 scale; affects crew performance
- **Fatigue**: Increases during active duties; reduces effectiveness
- **Health**: 0-1 scale; damaged crew recover slowly
- **Experience**: Per-skill tracking with career history

### Viewing Crew

**Command:**
```
crew_list
crew
```

Shows all crew with stats:
```
[ID] Name              | Skill        | Compartment     | Level | Stress
[0]  Friedrich Weber   | engineering  | unassigned      | 1     | 0.15
[1]  Klaus Hoffmann    | sonar        | compartment_0   | 2     | 0.42
```

### Detailed Crew Information

**Command:**
```
crew_info <crew_id>
```

Shows detailed stats:
```
--- Friedrich Weber (Petty Officer) ---
ID: 0
Primary Skill: engineering
Level: 1
Stress: 0.15
Morale: 0.82
Fatigue: 0.21
Health: 1.00
Skills: torpedo_operation=45, engineering=230, damage_control=15
```

### Assigning Crew

Before crew can perform duties, they must be assigned to compartments.

**Command:**
```
assign <crew_id> <compartment_id> [role]
```

**Example:**
```
assign 0 1 engineering         # Assign Friedrich (ID 0) to compartment 1 as engineer
assign 1 0 sonar              # Assign Klaus (ID 1) to compartment 0 as sonar operator
```

**Available Roles:**
- `crew` - Standard crew member
- `specialist` - Specialized in their skill
- `officer` - Officer/leader (gets stress bonus)

### Reassigning Crew

Move crew to different compartments or change roles.

**Command:**
```
reassign <crew_id> <compartment_id> [role]
```

### Removing Crew

Transfer or dismiss crew members.

**Command:**
```
fire_crew <crew_id>
```

---

## Crew Performance

### Stress & Morale

- **Stress**: Increases during combat, damage events, and extended patrols
  - High stress (>0.7) reduces skill effectiveness
  - Very high stress (>0.9) can cause crew failures
  - Stress gradually decreases during rest periods
  
- **Morale**: Affects crew reliability
  - Morale drops when stress is high or casualties occur
  - Morale increases during successful patrols
  - Low morale (<0.3) can lead to crew issues

### Fatigue

- Increases during active duties (combat, operations)
- Reduces with rest periods
- High fatigue (>0.8) significantly reduces effectiveness

### Experience & Leveling

- Crew gain experience (XP) in their skills when using them
- Compartment events resolved successfully award XP
- Successful operations (damage control, repairs) grant XP
- Crew level increases every 500 XP in a skill
- Higher level = better effectiveness in that skill

### Effective Skill Calculation

A crew member's effectiveness in a skill is calculated as:
```
effective_skill = base_skill * (1 - stress*0.5) * (1 - fatigue*0.3) * (1 + level*0.1) * morale
```

So a stressed, fatigued crew member with low morale will perform poorly even if experienced.

---

## Compartment Events & Crew Response

When compartment events occur (flooding, fire, equipment failure), the best-trained crew member in that compartment is automatically selected to respond.

**Examples:**
- **Flooding**: Best damage control specialist handles it
- **Fire**: Engineers or specialized firefighters
- **Equipment Failure**: Best engineer responds
- **Crew Injury**: Medical/first aid personnel

Successful event resolution:
- ✓ Awards XP to responder
- ✓ Reduces crew stress
- ✓ Improves morale

Failed event resolution:
- ✗ Increases crew stress
- ✗ Damages responder health
- ✗ May worsen the situation

---

## Player Progression

### Career Stats

As captain, you accumulate career statistics:

**Command:**
```
player_status
```

Shows:
```
--- PLAYER STATUS ---
Level: 3
Total XP: 2100
Next Level At: 2000 XP

Skills:
  sonar_operation      : 450 XP (90%)
  torpedo_accuracy     : 200 XP (40%)
  evasion              :  50 XP (10%)
  resource_management  : 400 XP (80%)
  crew_leadership      : 150 XP (30%)
  navigation           : 400 XP (80%)
  damage_control       : 450 XP (90%)

Career Stats:
  ships_sunk           :    12
  tonnage_sunk         : 85000
  contacts_detected    :   156
  torpedoes_fired      :    89
  successful_hits      :    45
  patrol_days          :   234
  crew_trained         :    28
  narrow_escapes       :    12
  compartments_repaired:   189
```

### Skill Bonuses

Each skill gives bonuses to gameplay:
- **sonar_operation**: Better sonar detection range/accuracy
- **torpedo_accuracy**: Faster torpedo homing, better targeting
- **evasion**: Faster evasion from depth charges
- **resource_management**: Reduced fuel/oxygen consumption
- **crew_leadership**: Crew stress reduction, faster event resolution
- **navigation**: Better dead-reckoning, reduced drift
- **damage_control**: Faster repairs, compartment resilience

### Player Leveling

- Gain XP from successful operations
- Every 500 total XP = +1 player level
- Higher level unlocks better submarine upgrades
- Reaching certain levels unlocks new gameplay features

---

## Submarine Upgrades

### Viewing Available Upgrades

**Command:**
```
upgrades
```

Shows available and installed upgrades:
```
Available Upgrades (5 available):
  [sonar_improved_range] Extended Sonar Range     (Tier 1) - 500 points, 100 XP required
       Increases sonar detection range by 20%
  [hull_reinforcement]   Hull Reinforcement       (Tier 1) - 700 points, 200 XP required
       Increase hull integrity by 15%
  ...

Installed Upgrades:
  ✓ Extended Sonar Range
  ✓ Quick Reload Mechanism
```

### Installing Upgrades

Unlock submarine upgrades by:
1. Gaining enough player XP (each upgrade has requirement)
2. Using accumulated points to purchase
3. Installing the upgrade

**Command:**
```
install_upgrade <upgrade_id>
```

**Example:**
```
install_upgrade sonar_improved_range
```

### Available Upgrades by Tier

**Tier 1 (Entry):**
- Extended Sonar Range
- Quick Reload Mechanism
- Hull Reinforcement
- Tuned Diesel Engines
- Advanced Damage Control

**Tier 2 (Intermediate):**
- Silent Sonar Mode
- Enhanced Homing
- Deep Diving Hull
- Expanded Battery
- Radar Installation

**Tier 3 (Advanced):**
- Target Classification
- Magnetic Detonators
- Advanced Hull Material
- Silent Drive System
- Oxygen Recycler

### Upgrade Effects

Each upgrade provides specific bonuses:
- **Sonar upgrades**: Detection range, signature reduction, target identification
- **Torpedo upgrades**: Reload speed, homing strength, damage
- **Hull upgrades**: Integrity, diving depth, pressure resistance
- **Engine upgrades**: Speed, battery capacity, silent running
- **Systems upgrades**: Repair speed, radar, oxygen efficiency

---

## Campaign Tips

### Crew Management
1. **Hire a balanced crew**: Mix of specialists and versatile crew
2. **Keep stress low**: Rotate crew between hot spots, allow rest periods
3. **Invest in leaders**: Officers provide morale bonuses to nearby crew
4. **Track experience**: Focus damage control crew for dangerous missions

### Career Development
1. **Focus on one skill path**: Specialize in sonar, evasion, or torpedo accuracy
2. **Balanced approach**: Some crews prefer specialization, others generalist
3. **Use career stats**: Track tonnage and ships sunk for prestige
4. **Upgrade strategically**: 
   - Early game: Sonar and hull upgrades for survivability
   - Mid-game: Torpedo and engine upgrades for combat
   - Late game: Advanced systems for specialized missions

### Longterm Strategy
- Keep veteran crew alive (valuable experience)
- Rotate junior crew through different compartments
- Build a core team of elite specialists
- Use upgrades to multiply crew effectiveness
- Plan your career path: Stealth sub? Hunter-killer? Balanced?

---

## Advanced Mechanics

### Stress Cascades

If many crew are stressed simultaneously:
- Errors in compartment event resolution increase
- Morale drops faster
- Fatigue accumulation speeds up
- Performance degrades across all systems

**Prevention:**
- Allow rest periods after intense combat
- Rotate crew assignments
- Use morale-boosting upgrades

### Experience Multipliers

Certain conditions grant bonus XP:
- Successfully resolving difficult events (1.5x XP)
- Sinking larger vessels (tonnage-based)
- Completing patrol objectives
- No crew losses during patrol (bonus)

### Crew Specialization

Over time, crew naturally specialize:
- After 500 XP in a skill, they gain +10% bonus to that skill
- After 1000 XP, they gain +20% bonus
- After 1500 XP, they gain +30% bonus (expert level)

---

## Console Commands Reference

### Crew Commands
```
recruit [skill]                   # Recruit crew member
crew_list / crew                  # List all crew
crew_info <id>                    # Detailed crew info
assign <id> <compartment> [role]  # Assign to compartment
reassign <id> <compartment> [role]# Move to different compartment
fire_crew <id>                    # Remove crew member
```

### Progression Commands
```
player_status                     # Show player stats and skills
upgrades                          # List available upgrades
install_upgrade <id>              # Install submarine upgrade
```

### Related Commands
```
status                            # Current submarine status
compartments                      # Show all compartments and crew
events                            # List pending events
resolve_event <idx> [responder]   # Manually resolve event
```

---

## Career Path Examples

### The Commando Captain
- Focus: Crew Leadership, Damage Control
- Upgrades: Advanced Damage Control, Hull Reinforcement
- Strategy: Push damaged submarines, tank damage with crew skill
- Playstyle: Aggressive, crew-centric

### The Silent Hunter
- Focus: Sonar Operation, Navigation, Evasion
- Upgrades: Extended Sonar Range, Silent Sonar Mode, Silent Drive
- Strategy: Detect targets before they detect you
- Playstyle: Stealth-focused, avoid combat

### The Weapons Expert
- Focus: Torpedo Accuracy, Resource Management
- Upgrades: Enhanced Homing, Magnetic Detonators, Quick Reload
- Strategy: Maximize hit rate, minimize torpedoes needed
- Playstyle: Precision strikes, avoid prolonged combat

### The Legendary Survivor
- Focus: Evasion, Damage Control, Crew Leadership
- Upgrades: Deep Diving Hull, Pressure Resistance, Oxygen Recycler
- Strategy: Out-survive enemy attacks through depth/evasion
- Playstyle: Risk-taking, survival-focused

---

Enjoy your career as submarine captain! The fate of your crew rests in your hands.
