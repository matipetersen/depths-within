# Enemy Weapons System - Complete Guide

## Overview
The game now features a complete weapons system for enemy units including:
- **Depth Charges** - Deployed by escort ships and aircraft at estimated submarine depths
- **Shell Trajectories** - Gun fire from surface ships with arc trajectories
- **Aircraft Attacks** - Bomber and torpedo bomber runs with various payloads
- **Visual Rendering** - All weapons displayed on both tactical and depth profile maps

## Weapon Types

### 1. Depth Charges (`o` symbol - RED)
**Deployed by:** Destroyers, Escorts, ASW Aircraft
**Mechanics:**
- Set to detonate at estimated submarine depth
- Damage ranges 0-30% depending on depth differential
- Maximum blast radius: 4 map units horizontally
- More damaging when detonating near submarine (0m differential = 30% damage)
- Damage decreases with distance from detonation depth

**Depth Damage Table:**
```
Depth differential | Damage
0m (exact)        | 30%
±1m               | 25%
±2m               | 20%
±3m               | 15%
±4m               | 10%
±5m               | 5%
>5m               | 0% (miss)
```

**Visual Indicators:**
- Tactical map: Red `o` at deployment location
- Depth map: Red `o` at detonation depth
- Age timer: Charges fade after 20 turns (time for detonation)

### 2. Shell Trajectories (`-` symbol - YELLOW)
**Deployed by:** Merchant ships, Destroyers, Armed escorts
**Mechanics:**
- Surface-only weapon (can't hit submerged submarines)
- Arc trajectory from firing ship to target
- Travel distance: 0.5 units per turn
- Maximum range: 15 map units
- Damage on hit: 8% hull damage to surface vessels

**Firing Logic:**
- Destroyers attempt to shoot at detected submarines
- Shells can only damage surfaces (player at 0m depth)
- Each shell shows on map as it travels to target
- Deactivates when reaching max range

**Tactical Use:**
- Surface to attack escorts before they close
- Use evasion to dodge incoming fire
- Counter-attack with your own torpedoes

### 3. Aircraft Attacks (`✈` symbol - CYAN)
**Deployed by:** Patrol aircraft, Bomber aircraft, Torpedo bombers
**Attack Types:**
- `bomb`: 25% damage (generic bombing run)
- `depth_charge`: 20% damage (anti-submarine bomb)
- `torpedo`: 35% damage (rare aircraft-dropped torpedo)
- `gun`: 10% damage (machine gun strafing)

**Attack Progress:**
- Duration: 8 turns per attack run
- Hit occurs at 80% progress (near end of run)
- Hit range: ±2 map units from aircraft position
- Multiple aircraft can attack simultaneously

**Threat Assessment:**
- Aircraft show at their patrol altitude on depth profile
- Altitude ranges 50-200m (shown on depth map)
- Aircraft speed varies by type (2-8 units per turn)
- Can re-engage multiple times unless damaged/destroyed

## Ship Combat Abilities

### Destroyer Combat AI
**Detection Range:** 10 map units
**Attack Sequence:**
1. Detect player submarine within 10 units
2. Pursue toward player position
3. When within 3 units: Deploy depth charges
4. Depth charges aimed at estimated submarine depth
5. Attack cooldown: 8 turns between attacks

**Evasion Behavior:**
- Evades when torpedo detected within 4 units
- Evasion duration: 3-6 turns
- Evasion direction: Away from threat
- Can chain multiple evasions if threatened

### Merchant Ship Behavior
**Primary Goal:** Follow route across map
**Combat Response:** Limited defensive capability
**If Attacked:**
- No offensive weapons
- May be sunk by player torpedoes
- Provides supply/tonnage rewards when sunk

### Escort Behavior
**Mixed Combat Role:**
- Follow convoys or patrol routes
- Can engage submarines
- Similar depth charge attacks to destroyers
- May coordinate with other escorts

## Weapon System Architecture

### WeaponManager Class
Located in `world/weapons.py`

**Methods:**
```python
# Spawn weapons
spawn_depth_charge(x, y, depth, owner_id, owner_type='ship')
spawn_shell(sx, sy, tx, ty, owner_id, owner_type='merchant')
spawn_aircraft_attack(aircraft_id, name, nation, x, y, depth, attack_type='bomb')

# Process and check hits
tick(submarine, tmap)  # Returns list of (weapon_type, damage, location) hits

# Get active weapons
get_active_charges()
get_active_shells()
get_active_aircraft_attacks()
```

**Integration Points:**
- TacticalMap initializes `weapon_manager` in `__init__`
- Ship AI calls `weapon_manager.spawn_depth_charge()` during engagement
- Game._process_weapons() ticks manager and applies damage each turn

## Map Display

### Dual-View Map Legend
```
Tactical View (Left - Top-Down):
  S = Your submarine
  M = Merchant ship
  D = Destroyer/Escort
  E = Enemy submarine
  A = Allied submarine
  → = Torpedo (yellow)
  ↗ = Homing torpedo (yellow)
  o = Depth charge (red)
  W = Whale
  w = Dolphin
  * = Shark

Depth Profile (Right - Side View):
  [Surface row]
  ~ = Water column
  = = Shelf/Medium depth
  : = Deep water
  # = Trench/Bottom
  
  Overlays (by depth):
  E = Enemy submarine
  A = Allied submarine
  → = Torpedo (yellow)
  ↗ = Homing torpedo (yellow)
  o = Depth charge (red)
  ✈ = Aircraft (cyan)
```

### Collision Detection
- Depth charges check hit every turn
- Aircraft attacks check hit at 80% progress
- Shells don't affect submarines (surface only)
- All hits logged with damage amount and location

## Combat Tactics

### Defending Against Depth Charges
1. **Evasion:** Use high speed to move away from deployment area
2. **Depth:** Maintain depth away from estimated detonation depth
3. **Maneuvers:** Make unpredictable course changes
4. **Decoys:** Future system - deploy countermeasures (planned)

### Defending Against Aircraft
1. **Submerge:** Aircraft can only attack at surface
2. **High Evasion:** Depth jumping (surface then dive immediately)
3. **Speed:** Aircraft have slower speed than submarines
4. **Detection:** Use sonar to detect aircraft approach

### Counter-Attacking
1. **Fire Torpedoes:** At detected enemies (ships, subs, aircraft on water)
2. **Surface Gun Fire:** Future system - arm deck guns (planned)
3. **Ramming:** Risky but possible (collision system)
4. **Evasion:** Lead attackers into mines/other hazards (planned)

## Statistics Integration
All weapon damage recorded:
- `DEPTH_CHARGES_SURVIVED` - Count of depth charge impacts
- `DAMAGE_TAKEN` - Total damage from all sources
- `AIRCRAFT_ATTACKS_SURVIVED` - Aircraft attack count (future)
- `HULL_INTEGRITY` - Overall submarine integrity percentage

## Future Enhancements

### Planned Weapon Systems
1. **Mines** - Stationary sea mines, detectable by sonar
2. **Ramming** - Intentional collision damage (high risk/reward)
3. **Depth Charge Patterns** - Multiple charges deployed in grids
4. **Decoys** - Countermeasures to mislead weapons
5. **Sonobuoys** - Aircraft deploying listening devices
6. **Homing Weapons** - Enemy acoustic-homing torpedoes
7. **Underwater Warfare** - Enemy submarines with their own weapons

### Balance Considerations
- Depth charges: Most dangerous when submarine at estimated depth
- Aircraft: Primary threat at surface, must submerge
- Ships: Limited offensive range, slow compared to subs
- Multiple threats: Encounters with aircraft + ships are critical danger

## Testing Commands
```
# Fire torpedo (for testing ship response)
> f

# Dive to avoid depth charges
> d 150

# Surface quickly for escape
> s

# Check torpedo count
> (view with SA hotkey)

# Watch weapon animations on map
> (press arrows to move and observe enemy weapons)
```

## Configuration Parameters
Located in `world/weapons.py`:
- `DepthCharge.blast_radius = 4` - Horizontal blast range
- `DepthCharge.damage_at_depth` - Dict of depth differentials
- `ShellTrajectory.max_range = 15` - Shell travel distance
- `ShellTrajectory.damage = 0.08` - Shell damage percentage
- `AircraftAttack.duration = 8` - Turns per attack run
- Ship AI `attack_range = 3.0` - Detection range
- Ship AI `threat_range = 4.0` - Torpedo evasion trigger
