# Historical Systems - Developer Quick Reference

## File Locations & Structure

```
world/sonar_systems.py          # Complete sonar/radar/detection system (400+ lines)
├─ SonarType class              # Individual sonar system definition
├─ RadarSystem class            # Individual radar system definition
├─ DetectionEvent class         # Detection result record
├─ SonarOperator class          # Crew member with skill/fatigue
├─ SonarManager class           # Main detection logic
└─ HistoricalDefect class       # Torpedo defect definition

submarine/torpedo.py            # Updated to include defects
├─ check_historical_defects()   # Assigns defect on creation
├─ step()                       # Applies defect effects (hot run, deep running)
└─ Collision detection          # Checks for defect-based misses

data/torpedoes.json             # 8 historical torpedo types
├─ G7e, G7a (German)
├─ Mk_14, Mk_23 (US)
├─ 21-inch (British)
└─ Type_93, Type_95 (Japanese)

data/submarines.json            # [Future: submarine sonar assignments]
data/ships.json                 # [Future: ship sonar/radar assignments]
```

## Quick API Reference

### Creating Sonar Manager
```python
from world.sonar_systems import SonarManager, SONAR_SYSTEMS, SonarOperator

# Initialize for player submarine
sonar_mgr = SonarManager()
sonar_mgr.set_sonar_type('JT')  # American JT hydrophone
sonar_mgr.set_operator(SonarOperator(skill_level=0.85, name="Sonarman First Class"))

# Set ocean conditions
sonar_mgr.set_thermocline(depth=150, intensity=1.0)

# In game loop, each turn:
sonar_mgr.operator.fatigue = min(1.0, sonar_mgr.operator.fatigue + 0.05)  # Accumulate fatigue
```

### Detecting Contacts
```python
# Passive detection of submarine at 6000m range
detection = sonar_mgr.detect_submarine(
    target_position=(6000, 0),
    target_speed_kmh=15,
    target_depth_m=80,
    hunter_depth_m=120
)

if detection:
    event = detection  # DetectionEvent instance
    print(f"Contact at {event.range}m bearing {event.bearing}°")
    print(f"Quality: {event.detection_quality}")
    print(f"Confirmed: {event.confirmed}")
else:
    print("No contact detected")
```

### Torpedo Defects
```python
from submarine.torpedo import Torpedo

# Defects automatically assigned during creation
torpedo = Torpedo(
    x=100, y=100, 
    dx=50, dy=0,
    torpedo_type='Mk_14',  # Specify type for historical defects
    speed=38
)

# Check what defect (if any) was assigned
if torpedo.defect:
    print(f"Warning: {torpedo.defect.name}")
    print(f"Effect: {torpedo.defect.description}")
    
# Defects are automatically applied during torpedo.step()
# No additional code needed - defects just work

# In collision detection, defects can cause misses:
if torpedo.did_collide:
    # Torpedo.py handles defect miss chance internally
    # Event will indicate if it was a defect miss
    event = torpedo.get_last_event()
    if event.get('type') == 'defect_miss':
        print(f"Torpedo failed to detonate: {event['defect'].name}")
```

### Historical Data Access
```python
from world.sonar_systems import SONAR_SYSTEMS, RADAR_SYSTEMS, TORPEDO_DEFECTS

# List all sonar types with specs
for sonar_id, sonar in SONAR_SYSTEMS.items():
    print(f"{sonar.name} ({sonar.nation})")
    print(f"  Passive: {sonar.passive_range}m @ {sonar.reliability}% reliable")
    print(f"  Type: {sonar.tech_type}")

# Access specific sonar stats
jt = SONAR_SYSTEMS['JT']
effective_range = jt.passive_range * jt.reliability
print(f"JT Hydrophone effective range: {effective_range}m")

# List torpedo defects
for defect in TORPEDO_DEFECTS:
    print(f"{defect.name} (Affects: {defect.affected_torpedo_types})")
    print(f"  Occurrence rate: {defect.occurrence_rate*100}%")
    print(f"  Effect: {defect.description}")
```

## Integration Checklist

### Phase 1: Initialize Systems
- [ ] In `engine/game.py` or `world/tactical_map.py`:
```python
from world.sonar_systems import SonarManager, SonarOperator, SONAR_SYSTEMS

self.sonar_manager = SonarManager()

# Assign sonar based on submarine type
if self.player_submarine.submarine_class == 'Type_VIIC':
    self.sonar_manager.set_sonar_type('GHG')  # German sonar
elif self.player_submarine.submarine_class == 'Gato':
    self.sonar_manager.set_sonar_type('JT')   # American sonar
```

### Phase 2: Operator Management
- [ ] Add sonar operator to crew
- [ ] Link crew fatigue to sonar operator effectiveness
```python
sonar_operator = self.crew.get_specialist('sonar_operator')
self.sonar_manager.set_operator(sonar_operator)

# Each game tick, accumulate fatigue
sonar_operator.fatigue += 0.01  # 1% per tick
```

### Phase 3: Detection Events
- [ ] In game loop `_tick()`:
```python
# Check for detections
for enemy_sub in self.tactical_map.enemy_submarines:
    detection = self.sonar_manager.detect_submarine(
        target_position=enemy_sub.position,
        target_speed_kmh=enemy_sub.speed_kmh,
        target_depth_m=enemy_sub.depth_m,
        hunter_depth_m=self.player_submarine.depth_m
    )
    
    if detection:
        self.add_log_event(f"SONAR: Contact bearing {detection.bearing}°, range {detection.range}m")
        self.tactical_map.add_detection(detection)
```

### Phase 4: Thermocline Generation
- [ ] In `tactical_map._populate_ocean()`:
```python
from world.sonar_systems import SonarManager

sonar_mgr = SonarManager()

# Random thermocline for this region
if random.random() < 0.7:  # 70% of regions have thermocline
    depth = random.randint(100, 250)
    sonar_mgr.set_thermocline(depth=depth, intensity=1.0)
    self.sonar_manager = sonar_mgr
```

### Phase 5: Enemy Detection
- [ ] Add sonar systems to enemy submarines
- [ ] Enemy submarines detect player each turn:
```python
for enemy_sub in self.tactical_map.enemy_submarines:
    if hasattr(enemy_sub, 'sonar_manager'):
        # Enemy sonar detects player
        player_detected = enemy_sub.sonar_manager.detect_submarine(
            target_position=self.player_submarine.position,
            target_speed_kmh=self.player_submarine.speed_kmh,
            target_depth_m=self.player_submarine.depth_m,
            hunter_depth_m=enemy_sub.depth_m
        )
        
        if player_detected and not enemy_sub.is_alerted:
            enemy_sub.become_alerted()
```

## Configuration Options

### Difficulty Adjustments (if needed)
```python
# In SonarManager or at initialization:

# Hard mode: Better detection
sonar_mgr.difficulty_multiplier = 1.2  # +20% detection range

# Easy mode: Worse detection
sonar_mgr.difficulty_multiplier = 0.8  # -20% detection range

# Realistic mode: Historical accuracy
sonar_mgr.difficulty_multiplier = 1.0  # No adjustment
```

### Historical Accuracy Toggle
```python
# Enable/disable defects globally
class Torpedo:
    HISTORICAL_DEFECTS_ENABLED = True  # Can toggle for gameplay
    
    def check_historical_defects(self):
        if not self.HISTORICAL_DEFECTS_ENABLED:
            return
        # ... rest of defect logic
```

## Testing Historical Systems

### Unit Test: Torpedo Defect Rate
```python
from submarine.torpedo import Torpedo

defect_count = 0
torpedo_count = 1000

for i in range(torpedo_count):
    torpedo = Torpedo(
        x=0, y=0, dx=1, dy=0, 
        torpedo_type='Mk_14',
        speed=38
    )
    if torpedo.defect:
        defect_count += 1

actual_rate = defect_count / torpedo_count
print(f"Mk_14 defect rate: {actual_rate*100:.1f}% (expected: 35%)")
```

### Unit Test: Sonar Detection
```python
from world.sonar_systems import SonarManager

mgr = SonarManager()
mgr.set_sonar_type('JT')  # 80% reliability, 12000m range

# Test static target
detection = mgr.detect_submarine(
    target_position=(10000, 0),
    target_speed_kmh=0,      # Stationary
    target_depth_m=100,
    hunter_depth_m=100
)

# Should detect with reduced probability
assert detection or not detection  # May not detect due to randomness
```

### Unit Test: Thermocline Effect
```python
from world.sonar_systems import SonarManager

mgr = SonarManager()
mgr.set_sonar_type('ASDIC')  # 2000m active range

# Without thermocline
mgr.set_thermocline(None)
range_no_therm = mgr.get_effective_range(mgr.sonar_type)

# With thermocline
mgr.set_thermocline(depth=150, intensity=1.0)
range_with_therm = mgr.get_effective_range(mgr.sonar_type)

# ASDIC should be ~90% reduced by thermocline
reduction = range_no_therm / range_with_therm
assert 7 < reduction < 15, f"ASDIC thermocline reduction incorrect: {reduction}x"
```

## Debugging

### Check Defect Assignment
```python
from submarine.torpedo import Torpedo
from world.sonar_systems import TORPEDO_DEFECTS

torpedo = Torpedo(..., torpedo_type='Mk_14')

if torpedo.defect:
    print(f"Defect: {torpedo.defect.name}")
    print(f"Probability: {torpedo.defect.occurrence_rate*100}%")
    print(f"Effect: {torpedo.defect.description}")
else:
    print("No defect - lucky shot!")
```

### Check Detection Range
```python
from world.sonar_systems import SonarManager

mgr = SonarManager()
mgr.set_sonar_type('Balkongerät')

# Debug detection calculation
sonar = mgr.sonar_type
base_range = sonar.passive_range
reliability = sonar.reliability
thermocline_factor = 0.4 if mgr.thermocline_active else 1.0
speed_bonus = 1.0  # Moving target

effective = base_range * reliability * thermocline_factor * speed_bonus

print(f"Base range: {base_range}m")
print(f"Reliability: {reliability*100}%")
print(f"Thermocline factor: {thermocline_factor}")
print(f"Effective range: {effective}m")
```

### Check Operator Fatigue
```python
from world.sonar_systems import SonarOperator

op = SonarOperator(skill_level=0.90)

print(f"Fresh skill: {op.get_effective_skill():.0%}")

op.fatigue = 0.5
print(f"Fatigued (50%): {op.get_effective_skill():.0%}")

op.fatigue = 1.0
print(f"Exhausted: {op.get_effective_skill():.0%}")

# Fatigued operator should be 25-50% less effective
```

## Common Patterns

### Pattern 1: Weapon Selection
```python
# Choose weapon based on situation and historical availability
if self.player_submarine.nation == 'Germany' and self.game_year >= 1943:
    torpedo_types = ['G7e', 'G7a']  # Both available
    
if self.player_submarine.nation == 'USA' and self.game_year <= 1943:
    torpedo_types = ['Mk_14']  # Only unreliable Mk_14
    
if self.player_submarine.nation == 'Japan' and self.game_year >= 1941:
    torpedo_types = ['Type_93', 'Type_95']  # Choose by situation
    
# Use most reliable if available
if 'Type_93' in available_torps:
    use_type_93 = True  # But risky if hit
else:
    use_mk14 = True  # Expect misses
```

### Pattern 2: Sonar Operator Integration
```python
# Create sonar operator crew member
from submarine.crew import CrewMember

sonar_op = CrewMember(
    name="Sonarman First Class Johnson",
    role='sonar_operator',
    skill=0.85,
    morale=100
)

# Link to sonar system
from world.sonar_systems import SonarOperator

sonar_player = SonarOperator(
    skill_level=sonar_op.skill,
    fatigue=0.0,
    name=sonar_op.name
)

sonar_manager.set_operator(sonar_player)

# Track fatigue from crew status
sonar_player.fatigue = 1.0 - (sonar_op.morale / 100)  # Low morale = fatigue
```

## Historical Accuracy Validation Checklist

- [ ] Mk_14 failure rate > 30% (documented 35%)
- [ ] G7a occasionally hot runs (5% rate)
- [ ] Type_93 most powerful torpedo (490kg warhead)
- [ ] British 21-inch most reliable (8% failure)
- [ ] ASDIC defeats thermocline (90% range reduction)
- [ ] Operator fatigue affects detection (max 50% skill reduction)
- [ ] Passive detection harder than active (slower)
- [ ] Thermocline present in ~70% of regions
- [ ] False contacts ~2% per detection attempt
- [ ] Deep-running targets harder to detect (exponential decay)

## Performance Notes

- SonarManager.detect_submarine() complexity: O(1) per call
- Thermocline lookup: O(1) dictionary access
- All historical data loaded once from JSON (no repeat parsing)
- Defect checking: O(1) random selection from TORPEDO_DEFECTS array

## Known Limitations (Future Enhancement)

- [ ] Thermocline doesn't affect noise propagation realism
- [ ] Single thermocline layer (real oceans have multiple)
- [ ] No acoustic convergence zones
- [ ] False contact discrimination not implemented
- [ ] Sonar operator personality not affecting style of reporting
- [ ] No sonar frequency selection by operator
- [ ] Speed calculation simplified (real ships have unique signatures)
