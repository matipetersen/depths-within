# Phase 14: Quick Start Guide

## Starting the Game with New Systems

```bash
cd "/Users/matiaspetersen/Documents/Depths within"
python main.py
```

The game will now include supply management, spy networks, and eldritch encounters.

---

## Monitoring Resources

### Check Current Supplies
```
> supplies
Resource Summary:
  OXYGEN      : [████████░░░░░░░░░░] 80.0% (GOOD)
  POWER       : [███████████░░░░░░░░] 70.0% (GOOD)
  FOOD        : [██████████████░░░░░░] 90.0% (EXCELLENT)
  WATER       : [███████████░░░░░░░░] 65.0% (GOOD)
  AMMUNITION  : [██████████░░░░░░░░░░] 50.0% (LOW)
  FUEL        : [███████████████░░░░░░] 85.0% (EXCELLENT)
  MEDICAL     : [█████████░░░░░░░░░░░] 45.0% (LOW)
  REPAIR_MAT  : [██████░░░░░░░░░░░░░░] 30.0% (CRITICAL)
```

### Quick Resource Summary
```
> resource_summary
Resource Summary:
  OXYGEN              : [████████░░░░░░░░░░] 80.0%
  POWER               : [███████████░░░░░░░░] 70.0%
  FOOD                : [██████████████░░░░░░] 90.0%
  WATER               : [███████████░░░░░░░░] 65.0%
  AMMUNITION          : [██████████░░░░░░░░░░] 50.0%
  FUEL                : [███████████████░░░░░░] 85.0%
  MEDICAL             : [█████████░░░░░░░░░░░] 45.0%
  REPAIR_MATERIALS    : [██████░░░░░░░░░░░░░░] 30.0%
```

### Adjust Rationing
```
> ration_level NORMAL
Ration level set to NORMAL (consumption multiplier: 1.0)

> ration_level REDUCED
Ration level set to REDUCED (consumption multiplier: 0.75)

> ration_level STRICT
Ration level set to STRICT (consumption multiplier: 0.5)

> ration_level EMERGENCY
Ration level set to EMERGENCY (consumption multiplier: 0.25)

> ration_level CRITICAL
Ration level set to CRITICAL (consumption multiplier: 0.1)
```

**Ration Level Effects:**
- **NORMAL**: Full consumption - crew morale normal
- **REDUCED**: 25% less consumption - minor morale penalty
- **STRICT**: 50% less consumption - moderate morale penalty
- **EMERGENCY**: 75% less consumption - high morale penalty, crew unrest
- **CRITICAL**: 90% less consumption - severe morale penalty, crew may mutiny

---

## Detecting & Eliminating Spies

### Check for Spies
```
> spy_status

Sabotage Activity Report:
  Total Sabotage Events: 2
  Successful Sabotage: 1
  Sabotage History:
    - Turn 15: OXYGEN_LEAK (Severity: 0.8) - DETECTED
    - Turn 28: POWER_DRAIN (Severity: 0.6) - SUCCESS

Known Spies:
  No known or suspected spies
```

If you notice sabotage in the logs, spies are present but still hidden.

### After Detecting Spies
```
> spy_status

Sabotage Activity Report:
  Total Sabotage Events: 5
  Successful Sabotage: 3
  Crew Morale Impact: -0.15

Known Spies:
  SUSPECTED: "Engineer_Klaus" - Suspicion: 0.75
  EXPOSED: "Officer_Ivan" - Suspicion: 0.92
```

### Eliminate a Spy
```
> eliminate_spy Officer_Ivan
Eliminated suspected spy: Officer_Ivan
```

**Spy Mechanics:**
- Spies try to sabotage every 15+ turns
- Failed sabotage attempts increase suspicion
- SUSPECTED (70% evidence) - player learns their identity
- EXPOSED (90% evidence) - crew becomes aware
- Once exposed, player can eliminate them

---

## Managing Eldritch Encounters

### Check Current Encounters
```
> encounter_status

════════════════════════════════════════════════════════
ACTIVE ENCOUNTERS SUMMARY
════════════════════════════════════════════════════════

No active encounters detected.
```

### When an Encounter Starts
```
> encounter_status

════════════════════════════════════════════════════════
ACTIVE ENCOUNTERS SUMMARY
════════════════════════════════════════════════════════

Encounter 1: SHADOW_MASS
  Phase: PSYCHOLOGICAL (Turn 1/3)
  Severity: 0.50
  Crew Response: FEARFUL
  Description: A massive shadow moves in the water,
               watching with intent...
  
  Effects: 
    - Crew sanity loss: 5 per turn
    - Crew fear increase: 0.02 per turn
  
  Resolution Methods (Attempt Chances):
    • retreat (60%)  - Flee the area
    • evasion (50%)  - Perform evasive maneuvers
    • weapons (40%)  - Attack the entity
    • prayer (35%)   - Spiritual resistance
    • full_depth (45%) - Dive to maximum depth
    • surface (30%)  - Emergency surface
    • ignore (10%)   - Hope it goes away
```

### Resolve an Encounter
```
> resolve_encounter weapons
Resolution attempt using weapons: 40% success chance

[After resolution, check status again with 'encounter_status']
```

**Encounter Phases:**
1. **PSYCHOLOGICAL** (Turns 1-3)
   - Crew experiences fear, sanity loss
   - No physical threat yet
   - Can still resolve easily

2. **MANIFESTATION** (Turns 4-7)
   - Equipment glitches
   - Navigation errors
   - Sensor interference

3. **PHYSICAL** (Turns 8-17)
   - Hull damage
   - Creature visible for combat
   - Weapon effectiveness reduced

4. **CRITICAL** (Turn 18+)
   - Extreme hull damage risk
   - Must resolve immediately
   - Possible crew death

**Resolution Methods & Success Rates:**
- **retreat** (60%) - Flee the area - usually works
- **evasion** (50%) - Perform evasive maneuvers - moderately effective
- **weapons** (40%) - Attack the entity - risky, ineffective
- **prayer** (35%) - Spiritual resistance - rarely works
- **full_depth** (45%) - Dive to maximum depth - can escape some encounters
- **surface** (30%) - Emergency surface - panicked escape
- **ignore** (10%) - Hope it goes away - almost never works

**Strategy Tips:**
- Act during PSYCHOLOGICAL phase (higher resolution success)
- Avoid combat - weapons are least effective
- Retreat/evasion most likely to succeed
- Each attempt costs resources (fuel, morale, etc.)

---

## Resource Depletion Triggers

### From Submarines Systems
- **Oxygen** - Consumed by crew, increases with depth
- **Power** - Consumed by engines/systems, 2x in combat
- **Food** - Consumed by crew, rationing affects morale
- **Water** - Fresh water for crew hydration
- **Ammunition** - Used when firing torpedoes
- **Fuel** - Used by diesel/nuclear engines
- **Medical** - Used for crew healing in compartments
- **Repair Materials** - Used to repair hull damage

### From Spy Sabotage
- **OXYGEN_LEAK** - Direct oxygen loss
- **POWER_DRAIN** - Direct power loss
- **FUEL_CONTAMINATION** - Fuel unusable (emergency only)
- **TORPEDO_SABOTAGE** - Ammunition lost
- **COMMUNICATION_JAM** - Temporary sonar loss
- **ENGINE_DAMAGE** - Fuel consumption increases
- **HULL_WEAKENING** - Repair materials used
- **COMPARTMENT_FLOODING** - Water/food lost, crew injured
- **SONAR_INTERFERENCE** - Equipment malfunction
- **CREW_SABOTAGE** - General morale loss

### From Eldritch Encounters
- **PSYCHOLOGICAL Phase** - Crew sanity loss, fear increase
- **MANIFESTATION Phase** - Equipment damage/malfunction
- **PHYSICAL Phase** - Hull damage accumulation
- **CRITICAL Phase** - Severe damage, crew casualties

---

## Game Loop Integration

The systems automatically tick each turn:

1. **Supply Consumption** - Resources used based on depth, combat status, crew count
2. **Spy Sabotage** - Spies attempt sabotage every 15+ turns
3. **Encounter Progression** - Encounters escalate through phases
4. **Crisis Cascade** - Systems interact (low supplies → morale loss → crew problems)

### Example Turn Sequence
```
Turn 1:
  - Supply inventory ticks (oxygen: 100→98, power: 100→97)
  - No spy sabotage (all on cooldown)
  - No encounters active

Turn 15:
  - Supplies consumed (oxygen: 75→73, depth = 150m)
  - Spy attempts sabotage - POWER_DRAIN detected!
  - Power drops 97→88

Turn 28:
  - Supplies normal consumption
  - Spy attempts again - SUCCESS (hidden)
  - Oxygen drops unexpectedly (leak)

Turn 50:
  - ENCOUNTER STARTED: SHADOW_MASS
  - Crew sanity: 100→95 (psychological effect)
  - Crew fear increases
```

---

## Monitoring System Health

### Use 'status' Command
```
> status
```
This will show overview of all systems including crew morale, which can be affected by spies and encounters.

### Use 'crew_loyalty' Command
```
> crew_loyalty
```
Shows crew morale and rebellion risk, impacted by:
- Spy activity (known spies reduce morale)
- Low supplies (rationing penalties)
- Encounters (crew fear from encounters)

### Use 'log' Command
```
> journal
```
Check recent events logged automatically:
- Sabotage activity
- Encounter phase changes
- Resource warnings
- Crew problems

---

## Optimal Strategies

### Early Game (Turns 1-50)
- Monitor supplies - rationing not usually needed yet
- Watch for sabotage signs in logs
- If encounters appear, resolve during PSYCHOLOGICAL phase
- Keep crew morale high

### Mid Game (Turns 50-150)
- Start rationing if supplies dropping
- Eliminate exposed spies to prevent morale loss
- Use evasion/retreat for encounters
- Manage crew loyalty actively

### Late Game (Turns 150+)
- Carefully manage critical resources
- Multiple spies likely - expose and eliminate quickly
- Encounters come more frequently
- Coordinate all systems for survival

---

## Troubleshooting

### "CRITICAL: OXYGEN running dangerously low!"
- Reduce depth if possible (decreases oxygen consumption)
- Set ration level to REDUCED or STRICT
- End combat if possible (2x power drain reduces power usage)

### "Multiple spies sabotaging!"
- Check spy_status for exposed spies
- Eliminate exposed spies: `eliminate_spy <name>`
- Investigate suspicious crew members

### "Encounter won't resolve!"
- Try different resolution methods
- Some methods have better odds than others
- Retreat/evasion usually best options
- Act quickly before reaching CRITICAL phase

### Game runs slowly?
- This is normal - systems tick every turn
- No optimization issues
- Performance is good even with many systems active

---

## Advanced: Chaining Sabotage & Encounters

The systems interact in dangerous ways:

**Scenario:** Low supplies + Spies + Encounter
1. Supply rationing causes morale loss (crew_loyalty affected)
2. Spies detect instability, sabotage increases
3. Sabotage depletes more supplies (spiral begins)
4. Encounter appears (crew already stressed)
5. Stressed crew more susceptible to possession/panic
6. Encounter damage compounds supply crisis

**Counter-strategy:**
- Maintain supply buffer (don't let resources drop too low)
- Eliminate spies immediately when exposed
- Resolve encounters quickly (before they advance)
- Keep crew morale above 50% whenever possible

---

## Console Command Reference

**Supply Commands:**
- `supplies` - Full supply report
- `supply_status` - Same as supplies
- `ration_level <LEVEL>` - Change ration (NORMAL/REDUCED/STRICT/EMERGENCY/CRITICAL)
- `resource_summary` - Quick percentage bars

**Spy Commands:**
- `spy_status` - Show spies and sabotage
- `spies` - Same as spy_status
- `eliminate_spy <name>` - Remove exposed spy

**Encounter Commands:**
- `encounter_status` - Show active encounters
- `encounter` - Same as encounter_status
- `resolve_encounter <method>` - Attempt resolution

**Game Commands:**
- `help` - Show all commands
- `tick` - Advance one turn manually
- `status` - General game status
- `crew_loyalty` - Crew morale (affected by systems)
- `journal` - Event log (shows system events)

