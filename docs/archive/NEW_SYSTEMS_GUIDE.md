# New Systems Implementation Guide
**Divers | Day/Night Cycle | Fog of War**

## Overview

Three interconnected tactical systems have been implemented to add depth and realism to submarine operations:

1. **Diver Operations System** - Combat divers for reconnaissance, sabotage, and special operations
2. **Day/Night Cycle** - 24-hour time system with dynamic visibility and detection risk
3. **Fog of War** - Sensor-based visibility system using periscope, sonar, and radar

---

## 1. Diver Operations System

### Features

**6 Diver Specializations:**
- **Reconnaissance** - Scout enemy positions, gather intelligence
- **Sabotage** - Plant limpet mines, cut nets
- **Rescue** - Recover downed pilots, stranded crew
- **Infiltration** - Harbor penetration, facility entry
- **Demolition** - Underwater demolition, obstacle clearing
- **Combat** - Underwater combat specialist

**10 Mission Types:**
- Harbor Reconnaissance
- Ship Sabotage
- Net Cutting
- Beach Reconnaissance
- Pilot Rescue
- Mine Placement
- Facility Infiltration
- Wreck Salvage
- Cable Cutting
- Obstacle Clearing

### Core Classes

#### `Diver`
Represents a combat diver with skills, equipment, and status.

```python
from submarine.divers import Diver, DiverSpecialty

# Create diver
diver = Diver(
    name="Hans Schmidt",
    specialty=DiverSpecialty.RECONNAISSANCE
)

# Skills (0.0-1.0)
print(diver.skills['stealth'])      # 0.85 (boosted by specialty)
print(diver.skills['swimming'])     # 0.78
print(diver.skills['demolition'])   # 0.65
print(diver.skills['combat'])       # 0.70
print(diver.skills['navigation'])   # 0.75
print(diver.skills['endurance'])    # 0.82

# Status
print(diver.health)    # 1.0 (0-1 scale)
print(diver.fatigue)   # 0.0 (increases during missions)
print(diver.stress)    # 0.0
print(diver.alive)     # True
print(diver.available) # True

# Equipment
print(diver.equipment['diving_suit'])    # True
print(diver.equipment['rebreather'])     # True
print(diver.equipment['limpet_mines'])   # 2 available

# Calculate effectiveness for mission type
effectiveness = diver.get_effectiveness(DiverMissionType.HARBOR_RECON)
print(effectiveness)  # 0.92 (92% effective)
```

#### `DiverMission`
Represents a diver mission with difficulty, risk, and progress tracking.

```python
from submarine.divers import DiverMission, DiverMissionType

# Create mission
mission = DiverMission(
    mission_type=DiverMissionType.SHIP_SABOTAGE,
    target_location="Brest Harbor",
    difficulty=0.7  # 70% difficulty
)

# Mission parameters
print(mission.duration)      # 60 ticks (~60 minutes)
print(mission.risk_level)    # 0.87 (87% risk)
print(mission.status)        # PREPARING

# Assign diver
mission.assign_diver(diver)

# Mission info
print(mission.get_mission_info())
"""
Mission: Ship Sabotage
Location: Brest Harbor
Difficulty: 70%
Risk Level: 87%
Duration: ~60 minutes
Status: preparing

Assigned Divers:
  - Hans Schmidt (Effectiveness: 92%)
"""
```

#### `DiverOperationsManager`
Manages all diver operations and missions.

```python
from submarine.divers import DiverOperationsManager

manager = DiverOperationsManager()

# Recruit divers
recon_diver = manager.recruit_diver(specialty=DiverSpecialty.RECONNAISSANCE)
sabotage_diver = manager.recruit_diver(specialty=DiverSpecialty.SABOTAGE)

# Get available divers
available = manager.get_available_divers()
print(f"{len(available)} divers available")

# Create and launch mission
mission = manager.create_mission(
    DiverMissionType.HARBOR_RECON,
    target="Enemy Harbor",
    difficulty=0.6
)
mission.assign_diver(recon_diver)
manager.launch_mission(mission)

# Process mission ticks
for tick in range(50):
    events = manager.tick_missions()
    
    for event in events:
        if event['success']:
            print(f"✅ Mission Success!")
            print(f"Intelligence: {event['intelligence']}")
        else:
            print(f"❌ Mission Failed")
        
        if event['casualties'] > 0:
            print(f"⚠️ Casualties: {event['casualties']}")

# Get operations summary
print(manager.get_operations_summary())
"""
=== Diver Operations ===

Available Divers: 1/2

Active Missions: 0

Completed Missions: 1 (1 successful)
"""
```

### Intelligence Gathering

Successful missions provide tactical intelligence:

**Harbor Reconnaissance:**
```python
{
    'type': 'harbor_layout',
    'ship_count': 8,
    'defenses': 'moderate',
    'patrol_frequency': 'high',
    'net_defenses': True
}
```

**Ship Sabotage:**
```python
{
    'type': 'sabotage_result',
    'ships_damaged': 2,
    'estimated_tonnage': 15000,
    'detection_risk': 'delayed'
}
```

**Beach Reconnaissance:**
```python
{
    'type': 'coastal_recon',
    'beach_suitability': 'good',
    'obstacles': 'light',
    'defenders': 'moderate'
}
```

---

## 2. Day/Night Cycle System

### Features

**Time Periods:**
- Night (00:00 - 05:59) - 5-20% visibility
- Dawn (06:00 - 07:59) - 50% visibility
- Morning (08:00 - 11:59) - 100% visibility
- Noon (12:00 - 13:59) - 100% visibility
- Afternoon (14:00 - 17:59) - 100% visibility
- Dusk (18:00 - 19:59) - 50% visibility
- Evening (20:00 - 23:59) - 15-30% visibility

**Moon Phases:**
- New Moon (0% illumination)
- Waxing Crescent (25%)
- First Quarter (50%)
- Waxing Gibbous (75%)
- Full Moon (100%)
- Waning Gibbous (75%)
- Last Quarter (50%)
- Waning Crescent (25%)

### Core Classes

#### `TimeSystem`
Manages game time and calculates time-based modifiers.

```python
from engine.time_system import TimeSystem, TimeOfDay

# Initialize
time_system = TimeSystem(
    start_hour=6,           # 06:00
    start_minute=0,
    start_day=1,
    season=Season.SUMMER
)

# Advance time
time_system.tick()  # +5 minutes (default)
print(time_system.get_time_string())  # "06:05"

# Set specific time
time_system.set_time(22, 30)  # 22:30

# Get time of day
tod = time_system.get_time_of_day()
print(tod)  # TimeOfDay.EVENING

# Check conditions
print(time_system.is_daylight())  # False
print(time_system.is_night())     # True
```

### Visibility Modifiers

Time and weather affect visibility:

```python
# Base visibility (time of day)
visibility = time_system.get_visibility_modifier()
print(visibility)  # 0.15 (15% at 22:30)

# Visibility with moon
visibility_with_moon = time_system.get_visibility_modifier(include_moon=True)
print(visibility_with_moon)  # 0.30 (30% with full moon)

# Periscope range (affected by time and weather)
range_clear = time_system.get_periscope_range('clear')
range_fog = time_system.get_periscope_range('fog')
print(range_clear)  # 3.0 km at night
print(range_fog)    # 0.9 km in fog at night
```

### Detection Risk

Surface detection risk varies dramatically by time:

```python
# Day surface detection
time_system.set_time(12, 0)
day_risk = time_system.get_detection_risk_modifier(on_surface=True)
print(day_risk)  # 1.0 (100% - very dangerous!)

# Night surface detection
time_system.set_time(2, 0)
night_risk = time_system.get_detection_risk_modifier(on_surface=True)
print(night_risk)  # 0.35 (35% - much safer)

# Submerged (always low risk)
submerged_risk = time_system.get_detection_risk_modifier(on_surface=False)
print(submerged_risk)  # 0.10 (10% - safest)

# Tactical decision
is_good, reason = time_system.is_good_time_for_surface()
if is_good:
    print(f"✓ Safe to surface: {reason}")
else:
    print(f"✗ Stay submerged: {reason}")
```

### UI Display

```python
# Get formatted display
display = time_system.get_ui_display()
print(display)
"""
🌙 22:30 - Day 3
   EVENING
   Moon: Full Moon (100%)
   Visibility: 45%
"""

# Get comprehensive info
info = time_system.get_time_info()
print(info)
"""
{
    'time': '22:30',
    'date': 'Day 3',
    'time_of_day': 'evening',
    'is_daylight': False,
    'is_night': True,
    'sun_position': 0.08,
    'moon_phase': 'full_moon',
    'moon_illumination': 1.0,
    'visibility': 0.45,
    'detection_risk': 0.45
}
"""
```

---

## 3. Fog of War System

### Features

**4 Sensor Types:**
- **Periscope** - Visual detection, surface only, time/weather dependent
- **Sonar** - Acoustic detection, omnidirectional, limited detail
- **Radar** - Surface contacts, long range, weather independent
- **Hydrophone** - Passive acoustic, very long range

**Sensor Ranges (tiles):**
- Periscope: 15 tiles (0-15 depending on conditions)
- Sonar: 30 tiles
- Radar: 50 tiles (surface only)
- Hydrophone: 60 tiles (passive)

**Visibility States:**
- Unexplored (never seen)
- Explored (seen before)
- Visible (currently visible)
- Sonar Contact (detected acoustically)

### Core Classes

#### `FogOfWar`
Manages tile visibility and sensor detection.

```python
from engine.fog_of_war import FogOfWar, SensorType, TileVisibility

# Initialize
fog = FogOfWar(width=100, height=100)

# Update visibility with active sensors
submarine_pos = (50, 50)
active_sensors = {SensorType.PERISCOPE, SensorType.SONAR}

fog.update_visibility(
    submarine_pos=submarine_pos,
    active_sensors=active_sensors,
    time_visibility=0.3,      # 30% (night)
    weather_visibility=1.0,   # 100% (clear)
    depth=10                  # 10m (periscope depth)
)

# Check tile visibility
tile_vis = fog.get_visibility((55, 55))
print(tile_vis)  # TileVisibility.VISIBLE

is_visible = fog.is_visible((60, 60))
print(is_visible)  # True

is_explored = fog.is_explored((80, 80))
print(is_explored)  # False (too far)
```

### Contact Tracking

```python
from engine.fog_of_war import ContactType

# Add contact
contact = fog.add_contact(
    position=(62, 67),
    sensor=SensorType.SONAR,
    contact_type=ContactType.WARSHIP
)

print(contact.confidence)  # 0.5 (initial)
print(contact.threat_level)  # 0.0

# Update contact (improves confidence)
fog.update_contact(
    contact_id=contact.id,
    position=(63, 68),
    sensor=SensorType.PERISCOPE
)

print(contact.confidence)  # 0.6 (improved)

# Classify contact (visual > radar > sonar)
success = fog.classify_contact(contact.id)
if success:
    print(f"Classified as: {contact.contact_type.value}")
    print(f"Detail level: {contact.detail_level}/5")

# Get contacts in range
nearby = fog.get_contacts_in_range(submarine_pos, range_km=20)
print(f"{len(nearby)} contacts within 20km")

# Get nearest threat
nearest = fog.get_nearest_contact(submarine_pos, ContactType.WARSHIP)
if nearest:
    print(f"Nearest warship at {nearest.position}")

# Remove stale contacts
fog.remove_stale_contacts(max_age=100)
```

### Sensor Combinations

Different scenarios require different sensor setups:

**Periscope Depth (Day):**
```python
fog.update_visibility(
    submarine_pos,
    {SensorType.PERISCOPE, SensorType.SONAR},
    time_visibility=1.0,    # 100% (day)
    weather_visibility=1.0,  # 100% (clear)
    depth=10
)
# Result: ~2821 tiles detected (709 visible, 2112 sonar)
```

**Periscope Depth (Fog):**
```python
fog.update_visibility(
    submarine_pos,
    {SensorType.PERISCOPE, SensorType.SONAR},
    time_visibility=1.0,    # 100% (day)
    weather_visibility=0.3,  # 30% (heavy fog)
    depth=10
)
# Result: ~1757 tiles detected (69 visible, 1688 sonar)
```

**Deep Dive (Sonar Only):**
```python
fog.update_visibility(
    submarine_pos,
    {SensorType.SONAR, SensorType.HYDROPHONE},
    time_visibility=1.0,
    weather_visibility=1.0,
    depth=100  # Too deep for periscope
)
# Result: ~9507 tiles detected (all sonar/hydrophone)
```

**Surface (All Sensors):**
```python
fog.update_visibility(
    submarine_pos,
    {SensorType.PERISCOPE, SensorType.SONAR, SensorType.RADAR},
    time_visibility=1.0,
    weather_visibility=1.0,
    depth=0  # Surface
)
# Result: ~7843 tiles detected (maximum coverage)
```

---

## Integration Examples

### Example 1: Night Harbor Infiltration

```python
from submarine.divers import DiverOperationsManager, DiverSpecialty, DiverMissionType
from engine.time_system import TimeSystem
from engine.fog_of_war import FogOfWar, SensorType

# Setup
time_system = TimeSystem(start_hour=2)  # 02:00 (deep night)
fog = FogOfWar(width=100, height=100)
diver_ops = DiverOperationsManager()

submarine_pos = (45, 55)
harbor_pos = (60, 65)

# Check conditions
visibility = time_system.get_visibility_modifier()
detection_risk = time_system.get_detection_risk_modifier(on_surface=True)

print(f"Visibility: {visibility:.0%}")      # 20%
print(f"Detection Risk: {detection_risk:.0%}")  # 35%

# Approach harbor with minimal sensors
fog.update_visibility(
    submarine_pos,
    {SensorType.SONAR},  # Passive only
    time_visibility=visibility,
    weather_visibility=1.0,
    depth=50  # Deep approach
)

# Deploy reconnaissance diver
diver = diver_ops.recruit_diver(specialty=DiverSpecialty.RECONNAISSANCE)
mission = diver_ops.create_mission(
    DiverMissionType.HARBOR_RECON,
    target="Enemy Harbor",
    difficulty=0.7
)
mission.assign_diver(diver)

# Night provides stealth bonus
effectiveness = diver.get_effectiveness(mission.mission_type)
night_bonus = (1.0 - detection_risk) * 0.3
total_effectiveness = min(1.0, effectiveness + night_bonus)

print(f"Diver effectiveness: {effectiveness:.0%}")
print(f"Night bonus: +{night_bonus:.0%}")
print(f"Total: {total_effectiveness:.0%}")  # Often 100%!

# Launch and execute
diver_ops.launch_mission(mission)

for tick in range(50):
    events = diver_ops.tick_missions()
    
    for event in events:
        if event['success']:
            intel = event['intelligence']
            print(f"Harbor has {intel['ship_count']} ships")
            print(f"Defenses: {intel['defenses']}")
            print(f"Net defenses: {intel['net_defenses']}")
```

### Example 2: Dawn Patrol

```python
# Start at dawn
time_system = TimeSystem(start_hour=6)  # 06:00

# Monitor conditions throughout day
for hour in range(24):
    time_system.advance_to_time(hour)
    
    visibility = time_system.get_visibility_modifier()
    detection_risk = time_system.get_detection_risk_modifier(on_surface=True)
    periscope_range = time_system.get_periscope_range('clear')
    
    print(f"{hour:02d}:00 - Vis:{visibility:.0%} Risk:{detection_risk:.0%} "
          f"Periscope:{periscope_range:.1f}km")
    
    # Tactical decision
    if detection_risk < 0.3:
        print("  → SAFE: Can surface for battery charge")
    elif detection_risk > 0.7:
        print("  → DANGER: Remain deep, high detection risk")
```

### Example 3: Multi-Sensor Search

```python
# Surface search in good conditions
time_system.set_time(14, 0)  # 14:00 (afternoon)

# Use all sensors
fog.update_visibility(
    submarine_pos=(50, 50),
    active_sensors={SensorType.PERISCOPE, SensorType.SONAR, SensorType.RADAR},
    time_visibility=1.0,
    weather_visibility=1.0,
    depth=0  # Surface
)

# Add contacts
contacts = [
    ((65, 70), ContactType.MERCHANT),
    ((55, 80), ContactType.WARSHIP),
    ((72, 65), ContactType.WARSHIP),
]

for pos, ctype in contacts:
    fog.add_contact(pos, SensorType.RADAR, ctype)

# Get sensor display info
info = fog.get_sensor_display_info(submarine_pos=(50, 50))

print(f"Active sensors: {info['active_sensors']}")
print(f"Contacts: {info['contacts_count']}")
print(f"Visible tiles: {info['visible_tiles']}")

for contact_info in info['contacts']:
    print(f"  {contact_info['type']} @ {contact_info['bearing']}° "
          f"({contact_info['distance']:.1f}km)")
```

---

## Gameplay Impact

### Tactical Considerations

**Night Operations:**
- ✅ Low detection risk (20-35%)
- ✅ Good for surfacing/charging
- ✅ Ideal for diver operations
- ⚠️ Limited visual range
- ⚠️ Harder to identify targets

**Day Operations:**
- ✅ Maximum visual range
- ✅ Easy target identification
- ✅ Best for periscope attacks
- ⚠️ High detection risk (90-100%)
- ⚠️ Dangerous to surface

**Dusk/Dawn:**
- Balanced visibility and risk
- Good for transitioning depth
- Moderate conditions for all operations

**Moon Phase:**
- Full moon: +30% night visibility, +30% detection risk
- New moon: Darkest conditions, safest for surface operations

### Strategic Planning

**Mission Timing:**
```python
# Plan sabotage for new moon, deep night
if time_system.get_moon_illumination() < 0.3 and time_system.hour < 4:
    # Deploy divers - maximum stealth
    launch_sabotage_mission()

# Plan convoy attack for dawn/dusk
if time_system.get_time_of_day() in [TimeOfDay.DAWN, TimeOfDay.DUSK]:
    # Good visibility, moderate risk
    initiate_attack()

# Evade during day
if time_system.is_daylight():
    # Stay deep, use passive sonar only
    dive_to_depth(100)
    activate_sensors({SensorType.HYDROPHONE})
```

---

## File Structure

```
submarine/
  divers.py                 # Diver operations system (580 lines)

engine/
  time_system.py            # Day/night cycle (360 lines)
  fog_of_war.py             # Fog of war system (380 lines)

examples/
  systems_integration_demo.py  # Complete demo (390 lines)

tests/
  test_new_systems.py       # Comprehensive tests (500 lines)
```

**Total:** ~2,210 lines of new code

---

## Testing

All systems have been comprehensively tested:

```bash
python3 tests/test_new_systems.py
```

**Test Results:**
```
✅ ALL TESTS PASSED!

Systems validated:
  ✓ Diver operations (6 specialties, 10 mission types)
  ✓ Time system (24-hour cycle, moon phases)
  ✓ Visibility modifiers (time, weather, moon)
  ✓ Detection risk calculations
  ✓ Fog of war (4 sensor types)
  ✓ Multi-sensor visibility
  ✓ Contact tracking
  ✓ Integrated operations
```

**Integration Demo:**
```bash
python3 examples/systems_integration_demo.py
```

Shows 4 complete scenarios demonstrating all features.

---

## Performance Notes

- Fog of war optimized with bounding box calculations
- Contact tracking uses spatial queries
- Time system has minimal overhead (simple arithmetic)
- Diver missions process only active operations

**Typical Performance:**
- FogOfWar.update_visibility(): ~1-2ms for 100x100 grid
- TimeSystem.tick(): <0.1ms
- DiverOperationsManager.tick_missions(): <0.5ms per active mission

---

## Future Enhancements

Potential additions:
- **Diver equipment upgrades** (better rebreathers, more limpet mines)
- **Diver training system** (improve skills over time)
- **Weather effects on diver operations** (storms prevent deployment)
- **Seasonal day length variation** (summer longer days, winter longer nights)
- **Cloud cover** (affects visibility independent of time)
- **Sensor degradation** (damaged sensors have reduced range)
- **Contact classification mini-game** (player identifies ship types)
- **Diver narrative events** (stories from missions)

---

## Quick Reference

**Recruit & Deploy Diver:**
```python
manager = DiverOperationsManager()
diver = manager.recruit_diver(DiverSpecialty.SABOTAGE)
mission = manager.create_mission(DiverMissionType.SHIP_SABOTAGE, "Harbor", 0.7)
mission.assign_diver(diver)
manager.launch_mission(mission)
```

**Check Time Conditions:**
```python
time_system = TimeSystem(start_hour=2)
visibility = time_system.get_visibility_modifier()
is_safe, reason = time_system.is_good_time_for_surface()
```

**Update Fog of War:**
```python
fog = FogOfWar(100, 100)
fog.update_visibility(sub_pos, {SensorType.PERISCOPE, SensorType.SONAR},
                     time_visibility=0.3, weather_visibility=1.0, depth=10)
```

**Track Contacts:**
```python
contact = fog.add_contact((60, 60), SensorType.SONAR, ContactType.WARSHIP)
fog.classify_contact(contact.id)
nearest = fog.get_nearest_contact(sub_pos, ContactType.WARSHIP)
```
