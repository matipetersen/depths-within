# Enhanced Crew Management System Guide

## Overview
The game now features an **enhanced crew management system** with comprehensive UI commands for managing your submarine crew. This includes displaying crew information, handling assignments, and managing crew morale and stress.

## Crew Management UI Components

### CrewManagementUI Class
Provides methods for displaying crew information in various formats.

#### Key Methods

##### `format_crew_member(crew_member, show_detailed=False)`
Formats a single crew member for display with color coding.

**Basic Display:**
```
  Commander Anderson | Captain | Skill: Command | Health: 98.5%
```

**Detailed Display:**
```
  Commander Anderson | Captain | Skill: Command | Health: 98.5%
    Stress: 45.0% | Morale: 85.0% | Fatigue: 12.3%
    Personality: Steady | Level: 5 | Missions: 23
```

**Color Coding:**
- Health: Green (>60%), Yellow (30-60%), Red (<30%)
- Stress: Green (<40%), Yellow (40-70%), Red (>70%)
- Morale: Green (>70%), Yellow (40-70%), Red (<40%)

---

##### `show_crew_roster(crew_roster, game, show_detailed=False)`
Displays the full crew roster with all crew members listed.

**Output:**
```
═══ CREW ROSTER ═══
Personnel: 47/50

 1.  Commander Anderson | Captain | Skill: Command | Health: 98.5%
 2.  Chief Peterson | Chief | Skill: Engineering | Health: 95.2%
 3.  Sonarman Jones | Specialist | Skill: Sonar | Health: 100.0%
 4.  Gunner Martinez | Warrant Officer | Skill: Weapons | Health: 87.3%
 5.  ...
```

**Command:**
```
crew list        # Show crew roster
crew detailed    # Show roster with detailed stats
```

---

##### `show_crew_by_assignment(crew_roster)`
Displays crew organized by compartment assignment.

**Output:**
```
═══ CREW BY ASSIGNMENT ═══

Engine Room:
  Chief Peterson | Chief | Skill: Engineering | Health: 95.2%
  Engineer Thompson | Specialist | Skill: Engineering | Health: 89.1%

Combat Center:
  Gunner Martinez | Warrant Officer | Skill: Weapons | Health: 87.3%
  Torpedo Specialist Wilson | Specialist | Skill: Weapons | Health: 92.5%

UNASSIGNED:
  Sailor Connor | Seaman | Skill: General | Health: 100.0%
```

**Command:**
```
crew by-assignment    # Show crew by compartment
```

---

##### `show_crew_morale_summary(crew_roster)`
Displays comprehensive morale and stress statistics.

**Output:**
```
═══ CREW MORALE REPORT ═══

Average Morale: 78.3%
Average Stress:  34.5%
Average Fatigue: 12.8%

Healthy:  45
Injured:  2
Stressed: 8

Crew morale is excellent!
```

**Color Indicators:**
- Morale: Green (>70%), Yellow (40-70%), Red (<40%)
- Overall Status: "Excellent" (>70%), "Stable" (50-70%), "Declining" (30-50%), "Critical" (<30%)

**Command:**
```
crew morale    # Show morale report
```

---

##### `show_stress_management_tips(game)`
Displays tips for managing crew stress and maintaining morale.

**Output:**
```
═══ CREW STRESS MANAGEMENT ═══

Ways to reduce crew stress:
  1. Rest crew at safe depths (50-100m)
  2. Avoid combat when possible
  3. Surface periodically to refresh air
  4. Maintain supplies (food, water)
  5. Complete missions successfully
  6. Allow crew to socialize (random conversations)

High stress effects:
  • Reduced skill effectiveness
  • Increased mistakes in critical systems
  • Lower morale (creates stress spiral)
  • Potential crew injuries
```

**Command:**
```
crew stress-tips    # Show stress management advice
```

---

## Crew Management Commands

All crew management commands use the format:
```
crew <subcommand> [arguments]
```

### Command Reference

#### `crew help` or `crew ?`
Shows all available crew management commands with descriptions.

**Output:**
```
═══ CREW MANAGEMENT COMMANDS ═══

Viewing:
  crew list          - Show all crew members
  crew detailed      - Show detailed crew stats
  crew by-assignment - Show crew by compartment
  crew morale        - Show morale report
  crew stress-tips   - Show stress management tips

Management:
  crew assign <name> <compartment> - Assign crew member
  crew rest          - Order crew to rest (reduce stress)
  crew inspire       - Captain's speech (boost morale)
```

**Usage:**
```
crew help
crew ?
```

---

#### `crew list`
Shows all crew members in the roster.

**Output:**
```
Personnel: 47/50

 1.  Commander Anderson | Captain | Skill: Command | Health: 98.5%
 2.  Chief Peterson | Chief | Skill: Engineering | Health: 95.2%
 3.  Sonarman Jones | Specialist | Skill: Sonar | Health: 100.0%
 ...
```

**Usage:**
```
crew list
```

---

#### `crew detailed`
Shows all crew members with detailed statistics including stress, morale, fatigue, personality, level, and mission history.

**Output:**
```
 1.  Commander Anderson | Captain | Skill: Command | Health: 98.5%
     Stress: 45.0% | Morale: 85.0% | Fatigue: 12.3%
     Personality: Steady | Level: 5 | Missions: 23

 2.  Chief Peterson | Chief | Skill: Engineering | Health: 95.2%
     Stress: 34.0% | Morale: 78.0% | Fatigue: 28.5%
     Personality: Reliable | Level: 4 | Missions: 18
 ...
```

**Usage:**
```
crew detailed
```

---

#### `crew by-assignment`
Shows crew organized by their compartment assignment. Includes "UNASSIGNED" section for crew not yet placed.

**Output:**
```
═══ CREW BY ASSIGNMENT ═══

Engine Room:
  Chief Peterson | Chief | Skill: Engineering | Health: 95.2%
  Engineer Thompson | Specialist | Skill: Engineering | Health: 89.1%

Combat Center:
  Gunner Martinez | Warrant Officer | Skill: Weapons | Health: 87.3%

UNASSIGNED:
  Sailor Connor | Seaman | Skill: General | Health: 100.0%
```

**Usage:**
```
crew by-assignment
```

---

#### `crew morale`
Shows detailed morale and stress report with statistics and trend analysis.

**Output:**
```
═══ CREW MORALE REPORT ═══

Average Morale: 78.3%
Average Stress:  34.5%
Average Fatigue: 12.8%

Healthy:  45
Injured:  2
Stressed: 8

Crew morale is excellent!
```

**Usage:**
```
crew morale
```

---

#### `crew stress-tips`
Shows practical advice for managing crew stress and maintaining morale during the mission.

**Output:**
```
═══ CREW STRESS MANAGEMENT ═══

Ways to reduce crew stress:
  1. Rest crew at safe depths (50-100m)
  2. Avoid combat when possible
  3. Surface periodically to refresh air
  4. Maintain supplies (food, water)
  5. Complete missions successfully
  6. Allow crew to socialize (random conversations)

High stress effects:
  • Reduced skill effectiveness
  • Increased mistakes in critical systems
  • Lower morale (creates stress spiral)
  • Potential crew injuries
```

**Usage:**
```
crew stress-tips
```

---

#### `crew assign <name> <compartment>`
Assigns a crew member to a specific compartment.

**Parameters:**
- `<name>`: First or last name of crew member
- `<compartment>`: Compartment ID to assign to

**Example Usage:**
```
crew assign anderson engine
crew assign peterson combat
crew assign jones sonar
```

**Output:**
```
✓ Assigned Commander Anderson to engine
✓ Assigned Chief Peterson to combat
✓ Assigned Sonarman Jones to sonar
```

**Error Handling:**
```
✗ Crew member 'smith' not found
✗ Assignment failed: Invalid compartment
```

---

#### `crew rest`
Orders all crew members to rest. Reduces stress levels across the submarine.

**Effect:**
- Each crew member's stress reduced by 20%
- Best used after combat or extended high-stress operations
- Cannot reduce stress below 0%

**Example Usage:**
```
crew rest
```

**Output:**
```
✓ Crew ordered to rest. Stress levels reduced.
```

**Timing:**
- Best used at safe depths (50-100m)
- Safe patrol areas away from combat
- Before major tactical operations

---

#### `crew inspire`
The captain gives an inspiring speech to boost crew morale.

**Effect:**
- Each crew member's morale increased by 15%
- Cannot increase morale above 100%
- Logged as a significant event
- Visible in game journal

**Example Usage:**
```
crew inspire
```

**Output:**
```
✓ Captain's inspiring speech boosts crew morale!
[Journal] Captain's inspiring speech boosts crew morale!
```

**Strategic Use:**
- After defeats or high losses
- Before major offensive operations
- When morale is critically low
- After extended combat tours

---

## Crew Statistics Explained

### Health (0-100%)
- Represents physical condition
- Reduced by: combat, injuries, fatigue
- Increased by: rest, medical attention
- Critical below 30%

### Stress (0-100%)
- Represents psychological pressure
- Increased by: combat, damage, danger
- Decreased by: rest, success, morale
- Affects skill effectiveness

### Morale (0-100%)
- Represents crew satisfaction/motivation
- Increased by: success, inspiration, good conditions
- Decreased by: losses, danger, stress
- Affects performance and loyalty

### Fatigue (0-100%)
- Represents physical exhaustion
- Increased by: work, combat, travel
- Decreased by: rest, relaxation
- Affects accuracy and response time

### Level (1-10)
- Represents experience and training
- Increases with completed missions
- Affects skill effectiveness
- Never decreases

### Missions (0+)
- Count of completed missions
- Determines experience level
- Contributes to overall submarine crew strength

---

## Crew Management Strategy

### Optimal Crew Composition
- **Captain/Officers**: 3-5 for command structure
- **Engineering**: 8-10 for engine maintenance
- **Combat**: 5-8 for weapons/torpedoes
- **Sonar/Navigation**: 4-6 for tactical systems
- **Medical**: 2-3 for health management
- **General Support**: 20+ for various duties

### Stress Management
1. **Prevention**: Avoid unnecessary combat
2. **Mitigation**: Use `crew rest` at safe depths
3. **Recovery**: Use `crew inspire` after crises
4. **Monitoring**: Check `crew morale` regularly

### Assignment Strategy
1. Match crew skills to compartment specialties
2. Keep backup crew for critical positions
3. Rotate assignments to prevent burnout
4. Consider personality types for team balance

### Morale Maintenance
- Monitor morale report regularly
- Use inspire command strategically
- Complete missions successfully
- Maintain adequate supplies
- Allow random conversations (automatic)

---

## Color Reference in Crew Displays

| Element | Color | Meaning |
|---------|-------|---------|
| **Rank** | Cyan | Crew position/title |
| **Skill** | Bright Cyan | Specialization |
| **Health** | Green/Yellow/Red | Physical condition |
| **Stress** | Green/Yellow/Red | Psychological state |
| **Morale** | Green/Yellow/Red | Motivation level |
| **Fatigue** | Bright Yellow | Tiredness level |
| **Personality** | Bright Magenta | Character traits |
| **Compartments** | White (bold) | Section headers |
| **Success** | Bright Green | Positive actions |
| **Warning** | Bright Yellow | Caution messages |
| **Alert** | Bright Red | Critical issues |

---

## Integration with Other Systems

### Supply Management
- Crew stress/morale affected by supply availability
- Low food/water increases stress
- Use `supplies` command to check resources

### Combat System
- Crew stress increases during combat
- Stress affects weapon accuracy/effectiveness
- High stress may cause crew errors

### Crew Communications
- Random thoughts and conversations reflect crew state
- Stressed crew have different thoughts
- Happy crew morale boosts conversations

### Journal/Logging
- Major crew events logged automatically
- Inspire/rest commands recorded
- Crew deaths/injuries documented
- Mission completions tracked

---

## Example Game Session

```
Turn 100: [Status Check]
> crew morale
Average Morale: 82.3%, Average Stress: 28.5%
Crew morale is excellent!

Turn 150: [During Combat]
> crew morale
Average Morale: 45.2%, Average Stress: 78.3%
Crew morale is declining.

Turn 151: [Recovery]
> crew rest
✓ Crew ordered to rest. Stress levels reduced.

Turn 152: [Morale Boost]
> crew inspire
✓ Captain's inspiring speech boosts crew morale!

Turn 153: [Follow-up Check]
> crew morale
Average Morale: 68.5%, Average Stress: 48.2%
Crew morale is stable.

Turn 200: [Regular Monitoring]
> crew detailed
[Shows 50 crew members with full statistics]

Turn 250: [Assignment Check]
> crew by-assignment
[Shows crew distributed across compartments]
```

---

## Crew Management Best Practices

1. **Regular Monitoring**: Check `crew morale` every 10-20 turns
2. **Proactive Rest**: Use `crew rest` before stress reaches critical levels
3. **Celebration**: Use `crew inspire` after major victories
4. **Assignment Optimization**: Keep specialized crew in their best-fit compartments
5. **Emergency Protocol**: Maintain unassigned crew for emergency replacements
6. **Documentation**: Review crew performance in detailed view
7. **Compartment Watch**: Use `crew by-assignment` to verify station assignments
8. **Morale Trend Analysis**: Compare morale reports over time to track crew health

---

## Troubleshooting

**Issue**: Crew morale keeps declining
- **Solution**: Use `crew rest` and `crew inspire` more frequently, avoid unnecessary combat

**Issue**: Can't find crew member to assign
- **Solution**: Use `crew list` to find exact name, check spelling

**Issue**: Crew assignment not working
- **Solution**: Verify compartment ID is correct, check crew roster not at max capacity

**Issue**: Too many unassigned crew
- **Solution**: Use `crew assign` to place crew members in compartments

**Issue**: Stress levels too high
- **Solution**: Surface to safe depth, use `crew rest`, review stress management tips

---

## Related Commands

See also:
- `supplies` - Check resource inventory
- `journal` / `log` - View crew/mission events
- `lore` - Read crew stories and background
- `dashboard` - Full game status overview
- `compartments` - View compartment damage/integrity

