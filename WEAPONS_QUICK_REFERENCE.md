# Weapons Quick Reference Card

## Map Symbols

### Tactical View (Top-Down)
| Symbol | Meaning | Color | Threat |
|--------|---------|-------|--------|
| S | Your submarine | Green | - |
| M | Merchant ship | White | Low |
| D | Destroyer/Escort | White | High |
| E | Enemy submarine | Red | Very High |
| A | Allied submarine | Green | - |
| → | Torpedo | Yellow | High |
| ↗ | Homing torpedo | Yellow | Very High |
| o | Depth charge | Red | High |
| W | Whale | White | Low |
| w | Dolphin | Blue | Low |
| * | Shark | Red | Medium |
| ✈ | Aircraft | Cyan | Medium |

### Depth Profile (Side View)
| Symbol | Location | Meaning |
|--------|----------|---------|
| M/D | Row 0 | Ships at surface |
| ~ | Rows 1+ | Water layers |
| = | Mid depth | Shelf |
| : | Deep | Deep trench |
| # | Bottom | Seabed |
| E/A/U | At depth | Submarines |
| → / ↗ | At depth | Torpedoes |
| o | At depth | Depth charges |
| ✈ | Rows 0-4 | Aircraft (altitude) |

## Threat Assessment

### Depth Charges
```
Threat Level: ⚠️⚠️⚠️ (HIGH)

Characteristics:
- Deployed by destroyers/escorts/aircraft
- Set to detonate at estimated depth (50-200m)
- Damage: 5-30% depending on depth accuracy
- Blast radius: 4 map units

Counter-Tactics:
1. Change depth rapidly (dive/surface commands)
2. Move away from deployment point
3. Use high speed (arrow keys)
4. Maintain distance from enemies
```

### Aircraft Attacks
```
Threat Level: ⚠️⚠️ (MEDIUM)

Characteristics:
- Attack types: bomb (25%), depth_charge (20%), torpedo (35%)
- Attack duration: ~8 turns
- Hit range: ±2 map units from aircraft
- Cannot attack submerged submarines

Counter-Tactics:
1. SUBMERGE immediately when aircraft detected
2. Use depth changes to evade
3. Keep speed high (arrows to move)
4. Aircraft move slower than submarines
```

### Destroyer Attacks
```
Threat Level: ⚠️⚠️⚠️⚠️ (VERY HIGH)

Characteristics:
- Detection range: 10 map units
- Attack range: 3 map units
- Attacks: Depth charges + direct damage
- Attack cooldown: 8 turns

Counter-Tactics:
1. Avoid detection (sonar operator skill)
2. Torpedo attack before they close
3. Use evasion maneuvers
4. Maintain 5+ units distance if possible
```

## Combat Damage Chart

| Damage Source | Type | Damage Range | Notes |
|---------------|------|--------------|-------|
| Depth Charge | Subsurface | 5-30% | Distance-based from detonation depth |
| Destroyer Attack | Direct | 10% | Random compartment |
| Aircraft Bomb | Surface | 25% | Only at surface (0m) |
| Aircraft Depth Charge | Subsurface | 20% | During attack run |
| Aircraft Torpedo | Subsurface | 35% | Rare, highly destructive |
| Shell (Gun Fire) | Surface | 8% | Ships vs submarines only |
| Collision | Impact | 5% (ship) / 10% (sub) | See collision guide |

## Weapon Damage Depth Chart (Depth Charges)

```
Optimal Damage: Charge detonates at your exact depth (30% damage)
Safe Depth: 50m+ away from detonation depth (5% damage or less)

Depth Differential | Damage | Survival Strategy
0m (exact)        | 30%   | NOT SAFE - severe damage
±1m               | 25%   | High risk - avoid
±2m               | 20%   | Medium risk - risky
±3m               | 15%   | Lower risk - manageable
±4m               | 10%   | Low risk - doable
±5m               | 5%    | Very low risk - safe
>5m               | 0%    | SAFE - miss
```

## Defensive Maneuvers

### Immediate Response to Depth Charge Alert
```
1. Note charge location on map (red 'o')
2. Identify detonation depth (depth row on right)
3. Dive or surface AWAY from that depth
   Example: If charge set to 150m, dive to 50m or surface to 0m
4. Move horizontally (left/right arrows) away from charge location
5. Maintain evasion for 15+ turns until charge expires
```

### Against Pursuing Destroyer
```
Turn 1-3: Detect enemy (D symbol within 10 units)
  - Start evasive maneuvers
  - Prepare torpedo
  - Activate sonar

Turn 4: If within 3 units
  - Fire torpedo immediately (F key)
  - Dive to separate depth
  - Full speed evasion

Turn 5+: If attacked
  - Continue evasion
  - Monitor hull integrity
  - Repair critical damage
```

### Against Aircraft
```
1. Sonar detects ✈ symbol
2. IMMEDIATELY submerge (D key)
3. Change depth 100m+ from current
4. Wait for aircraft to disengage
5. Can surface after 20+ turns

Note: Aircraft cannot hit submerged targets
      Only dangerous when you surface
```

## Status Indicators

### Compartment Damage Levels
| Level | Status | Action |
|-------|--------|--------|
| 0% | Intact | - |
| 1-25% | Damaged | Monitor |
| 26-50% | Critical | Repair soon |
| 51-75% | Severe | REPAIR NOW |
| 76-100% | Destroyed | Catastrophic failure likely |

### Flooding Severity
| Level | Status | Risk |
|-------|--------|------|
| 0-20% | Minimal | Low |
| 21-40% | Moderate | Medium |
| 41-60% | Serious | High |
| 61-80% | Critical | Very High |
| 81-100% | Disaster | Ship loss imminent |

## Command Quick Keys

| Key | Action | Use Against |
|-----|--------|-------------|
| ↑↓← → | Move | All threats (range) |
| D [depth] | Dive | Depth charges, aircraft |
| S | Surface | (Be careful!) |
| F | Fire torpedo | Destroyers, ships |
| P | Ping sonar | Early warning detection |
| C | Compartments | Monitor damage |
| SA | Statistics | Track survivor progress |
| Q | Quit | Emergency exit |

## Threat Priority Matrix

```
Threat Type          | Proximity | Action
─────────────────────┼───────────┼─────────────────────
Destroyer (D)        | <3 units  | IMMEDIATE: Fire torpedo
Destroyer (D)        | 3-5 units | Evasive maneuvers
Destroyer (D)        | 5+ units  | Continue current course
Aircraft (✈)         | Any       | SUBMERGE NOW
Depth Charge (o)     | Nearby    | Change depth ±5m+
Torpedo (→)          | <2 units  | Emergency dive/surface
Merchant (M)         | Any       | Optional target
Whale/Dolphin (W/w)  | Any       | Avoid (false sonar)
```

## Survival Tips

1. **Early Detection**: Use sonar frequently (P key)
2. **Depth Changes**: Assign hot-key for favorite depths
3. **Speed Management**: Balance stealth vs evasion
4. **Compartment Repair**: Don't let damage stack
5. **Weapon Preparedness**: Keep torpedoes loaded
6. **Maneuver Planning**: Know your depth zones
7. **Crew Morale**: Keep morale high for combat effectiveness
8. **Course Evasion**: Use diagonal movements (arrows)

## Emergency Checklist

```
☐ Detected enemy within 10 units?
  → Check sonar (P)
  → Prepare evasion path

☐ Depth charge spawned?
  → Note detonation depth
  → Move away ±5m+ from that depth

☐ Aircraft detected?
  → Submerge immediately (D key)
  → Change to deep depth (D 200+)

☐ Hull integrity below 50%?
  → Get to safe depth (100-150m)
  → Repair critical compartments
  → Avoid new combat

☐ Multiple threats?
  → Separate them with distance
  → Attack smallest threat first
  → Prepare escape route
```

## Notes
- All depth measurements in meters
- All distances in map units
- All damage values as percentages (multiply by compartment integrity)
- Turn time approximately 30-60 seconds game-time
- Weapons process automatically each turn
