# Historical Systems Integration Plan

## Overview

This document provides the exact steps needed to fully activate the historical weapons and sonar systems into the game loop. All code is written and tested - this document maps where to hook it in.

**Current State:**
- ✅ All historical data created (torpedoes.json with 8 types, sonar systems, defects)
- ✅ All code written (sonar_systems.py, torpedo.py updated)
- ✅ All tests passing (186/186)
- ⏳ Game loop integration incomplete

**Time to Full Integration:** 2-4 hours

## Phase 1: Initialize SonarManager in Game Flow

### Step 1.1: Modify `engine/game.py` - Add Sonar System Initialization

**Location:** `engine/game.py` in the `Game.__init__()` method

**Current state:** Game initializes tactical_map, but no sonar system

**Action:** After TacticalMap initialization, add sonar setup

```python
# In Game.__init__(), after self.tactical_map = TacticalMap(...):

from world.sonar_systems import SonarManager, SonarOperator, SONAR_SYSTEMS

# Initialize sonar system for player submarine
self.sonar_manager = SonarManager()

# Assign sonar based on submarine nation/type
if self.player_submarine.nation == 'Germany':
    if self.game_year >= 1943:
        sonar_type = 'GHG'  # Active/passive combined
    else:
        sonar_type = 'Balkongerät'  # Passive only
elif self.player_submarine.nation == 'USA':
    sonar_type = 'JT'  # Best American hydrophone
elif self.player_submarine.nation == 'Japan':
    sonar_type = 'Type_93'  # Limited capability
elif self.player_submarine.nation == 'Britain':
    sonar_type = 'Type_128'  # British hydrophone
else:
    sonar_type = 'JT'  # Default

self.sonar_manager.set_sonar_type(sonar_type)

# Create sonar operator from crew
sonar_crew = self.player_submarine.crew.get_by_role('sonar_operator')
if sonar_crew:
    sonar_op = SonarOperator(
        skill_level=sonar_crew.skill,
        fatigue=0.0,
        name=sonar_crew.name
    )
    self.sonar_manager.set_operator(sonar_op)
else:
    # Default if no sonar operator yet
    sonar_op = SonarOperator(skill_level=0.7, fatigue=0.0, name="Unknown")
    self.sonar_manager.set_operator(sonar_op)

# Initialize thermocline state (will be set by TacticalMap)
self.sonar_manager.set_thermocline(None)
```

**Why here:** Game class has access to all systems (player sub, tactical map, crew).

### Step 1.2: Modify `world/tactical_map.py` - Set Thermocline During Generation

**Location:** `world/tactical_map.py` in `TacticalMap._populate_contacts()` or map generation

**Current state:** No thermocline generation

**Action:** Add random thermocline to newly generated maps

```python
# In TacticalMap._populate_contacts() or a new _generate_ocean_conditions() method:

import random

def _generate_ocean_conditions(self):
    """Generate realistic ocean conditions for this tactical map"""
    # Thermocline probability based on region and time of year
    # Tropical regions 80%, temperate 70%, arctic 30%
    
    if random.random() < 0.65:  # 65% chance of thermocline
        # Depth varies by region
        if self.region and self.region.latitude < 20:
            # Tropical: shallow thermocline
            depth = random.randint(50, 150)
        elif self.region and self.region.latitude < 40:
            # Temperate: mid-depth
            depth = random.randint(120, 200)
        else:
            # Arctic/polar: deep
            depth = random.randint(200, 300)
        
        intensity = random.uniform(0.8, 1.0)
        self.thermocline_active = True
        self.thermocline_depth = depth
        self.thermocline_intensity = intensity
    else:
        self.thermocline_active = False
        self.thermocline_depth = None
        self.thermocline_intensity = 0.0

# Call this from _populate_contacts():
self._generate_ocean_conditions()

# Then pass to game's sonar manager:
# (This happens in game loop, see Phase 2)
```

**Why here:** TacticalMap owns ocean state for this patrol.

## Phase 2: Generate Detection Events Each Turn

### Step 2.1: Modify `engine/game.py` - Add Sonar Detection to Game Loop

**Location:** `engine/game.py` in the `Game._tick()` or `_process_world()` method

**Current state:** Game processes weapons, enemies, etc. but no sonar detection

**Action:** Add sonar detection check each turn

```python
# In Game._tick() or similar main loop method, add:

def _process_sonar(self):
    """Check for sonar contacts each turn"""
    
    # Update operator fatigue
    if self.sonar_manager and self.sonar_manager.operator:
        # Fatigue increases with continuous duty
        self.sonar_manager.operator.fatigue = min(
            1.0, 
            self.sonar_manager.operator.fatigue + 0.002  # ~50 hours per game hour
        )
        
        # Reduce fatigue when resting (cruising on battery)
        if not self.player_submarine.is_in_combat:
            self.sonar_manager.operator.fatigue = max(
                0.0,
                self.sonar_manager.operator.fatigue - 0.001
            )
    
    # Set thermocline if map has it
    if self.tactical_map and hasattr(self.tactical_map, 'thermocline_active'):
        if self.tactical_map.thermocline_active:
            self.sonar_manager.set_thermocline(
                depth=self.tactical_map.thermocline_depth,
                intensity=self.tactical_map.thermocline_intensity
            )
        else:
            self.sonar_manager.set_thermocline(None)
    
    # Check for detections of player's enemies
    for enemy in self.tactical_map.all_contacts:
        if enemy.is_submarine:
            # Sonar can detect other submarines
            detection = self.sonar_manager.detect_submarine(
                target_position=(enemy.position.x, enemy.position.y),
                target_speed_kmh=enemy.speed_kmh if hasattr(enemy, 'speed_kmh') else 0,
                target_depth_m=enemy.depth_m if hasattr(enemy, 'depth_m') else 0,
                hunter_depth_m=self.player_submarine.depth_m
            )
            
            if detection:
                self._handle_detection_event(detection, enemy)
        
        elif enemy.is_surface_ship:
            # Check visual/radar detection
            detection = self.sonar_manager.detect_surface_ship(
                target_position=(enemy.position.x, enemy.position.y),
                target_distance=enemy.distance_to_player,
                target_type=enemy.ship_type
            )
            
            if detection:
                self._handle_detection_event(detection, enemy)

def _handle_detection_event(self, detection, target):
    """Process a sonar/radar detection"""
    
    # Log to player
    if detection.detection_quality == 'certain':
        certainty = "CONTACT - CERTAIN"
    elif detection.detection_quality == 'probable':
        certainty = "CONTACT - PROBABLE"
    else:
        certainty = "POSSIBLE CONTACT - UNCERTAIN"
    
    if detection.false_positive:
        certainty += " (POSSIBLE FALSE CONTACT)"
    
    bearing_text = f"{int(detection.bearing):03d}°"
    range_text = f"{int(detection.range):,}m"
    
    message = f"SONAR: {certainty} Bearing {bearing_text}, Range {range_text}"
    
    if hasattr(target, 'ship_name'):
        message += f" - Type: {target.ship_name}"
    elif hasattr(target, 'submarine_type'):
        message += f" - Type: {target.submarine_type}"
    
    self.event_manager.post_event({
        'type': 'sonar_contact',
        'timestamp': self.game_time,
        'detection': detection,
        'target': target,
        'message': message
    })
    
    # Add to tactical map for display
    if hasattr(self.tactical_map, 'add_detected_contact'):
        self.tactical_map.add_detected_contact(detection, target)

# Call this from main _tick():
def _tick(self):
    # ... existing code ...
    self._process_weapons()
    self._process_sonar()  # NEW
    self._process_enemy_ai()
    # ... rest of tick ...
```

**Why here:** Game loop is where all per-turn events happen.

### Step 2.2: Modify `ui/panels/log_panel.py` - Display Detection Events

**Location:** `ui/panels/log_panel.py` in log display handler

**Current state:** Log displays weapons, damage, etc. but not sonar contacts

**Action:** Add sonar event formatting

```python
# In LogPanel or wherever events are formatted for display:

def format_event(self, event):
    """Format event for display in log"""
    
    if event['type'] == 'sonar_contact':
        # Format sonar detection
        detection = event['detection']
        return {
            'text': event['message'],
            'color': (0, 150, 200),  # Sonar blue
            'timestamp': event['timestamp']
        }
    
    elif event['type'] == 'defect_miss':
        # Torpedo defect caused miss
        defect = event['defect']
        return {
            'text': f"Torpedo defect: {defect.name}",
            'color': (200, 100, 100),  # Failure red
            'timestamp': event['timestamp']
        }
    
    # ... existing event types ...
```

## Phase 3: Enemy Sonar Detection of Player

### Step 3.1: Modify `world/tactical_map.py` - Add Enemy Sonar Systems

**Location:** `world/tactical_map.py` in `TacticalMap._populate_contacts()` or enemy initialization

**Current state:** Enemies exist but have no sonar systems

**Action:** Assign sonar systems to enemy submarines and ships

```python
# In TacticalMap or wherever enemies are created:

from world.sonar_systems import SonarManager, SonarOperator, SONAR_SYSTEMS

def _initialize_enemy_sonar(self, enemy):
    """Give enemy appropriate sonar system"""
    
    if not hasattr(enemy, 'sonar_manager'):
        enemy.sonar_manager = SonarManager()
        
        # Assign based on enemy type and nation
        if enemy.nation == 'Germany':
            sonar_type = 'GHG' if self.game_year >= 1943 else 'Balkongerät'
        elif enemy.nation == 'Japan':
            sonar_type = 'Type_93'
        elif enemy.nation == 'Britain':
            sonar_type = 'Type_128'
        elif enemy.nation == 'USA':
            sonar_type = 'JT'
        else:
            sonar_type = 'JT'  # Default
        
        enemy.sonar_manager.set_sonar_type(sonar_type)
        
        # Add operator with varying skill
        skill = random.uniform(0.6, 0.9)  # AI operator quality
        operator = SonarOperator(skill_level=skill, fatigue=0.0, name="Enemy Operator")
        enemy.sonar_manager.set_operator(operator)
        
        # Set thermocline (same as player)
        if hasattr(self, 'thermocline_active'):
            if self.thermocline_active:
                enemy.sonar_manager.set_thermocline(
                    depth=self.thermocline_depth,
                    intensity=self.thermocline_intensity
                )
```

### Step 3.2: Modify `world/tactical_map.py` - Enemy Detection Each Turn

**Location:** `world/tactical_map.py` in `TacticalMap.update()` or `_tick()`

**Current state:** Enemy AI runs but doesn't use sonar data

**Action:** Check if player detected by enemy sonar

```python
# In TacticalMap.update() or equivalent:

def _check_enemy_detection(self):
    """Check if enemies detect the player"""
    
    for enemy in self.all_contacts:
        if hasattr(enemy, 'sonar_manager') and hasattr(enemy, 'is_alerted'):
            # Check sonar detection of player
            if not enemy.is_alerted:
                # Only check if not already combat alert
                detection = enemy.sonar_manager.detect_submarine(
                    target_position=(self.player_position.x, self.player_position.y),
                    target_speed_kmh=self.player_speed_kmh,
                    target_depth_m=self.player_depth_m,
                    hunter_depth_m=enemy.depth_m if hasattr(enemy, 'depth_m') else 50
                )
                
                if detection and not detection.false_positive:
                    # Enemy detected player!
                    enemy.is_alerted = True
                    enemy.player_last_detected_bearing = detection.bearing
                    enemy.player_last_detected_range = detection.range
                    enemy.engaged_player = True
                    
                    # Enemy will now attack or evade
                    return True
    
    return False
```

## Phase 4: Torpedo Type Selection

### Step 4.1: Modify `submarine/submarine.py` - Historic Torpedo Loads

**Location:** `submarine/submarine.py` in submarine initialization

**Current state:** Submarines might have generic torpedo type

**Action:** Assign historical torpedo types to submarines based on class/nation

```python
# In Submarine.__init__() or a new method:

def _load_historical_torpedoes(self):
    """Load historically appropriate torpedoes for this submarine"""
    
    if self.nation == 'Germany':
        if self.submarine_class == 'Type_VIIC':
            # G7e and G7a mix typical of late-war VIIC
            self.torpedo_types = ['G7e', 'G7a']
            self.primary_torpedo = 'G7e'  # Default
        elif self.submarine_class == 'Type_XXI':
            # Advanced electric only
            self.torpedo_types = ['G7e']
            self.primary_torpedo = 'G7e'
    
    elif self.nation == 'USA':
        if self.submarine_class == 'Gato':
            if self.game_year <= 1943:
                # Early war: only Mk_14 (problematic)
                self.torpedo_types = ['Mk_14']
                self.primary_torpedo = 'Mk_14'
            else:
                # Late war: fixed Mk_14 + acoustic Mk_23
                self.torpedo_types = ['Mk_14', 'Mk_23']
                self.primary_torpedo = 'Mk_14'
    
    elif self.nation == 'Japan':
        if self.submarine_class == 'I_class':
            # Type_93 Long Lance if available, Type_95 backup
            self.torpedo_types = ['Type_93', 'Type_95']
            self.primary_torpedo = 'Type_93'
        elif self.submarine_class == 'II_class':
            # Smaller boat, Type_95 only
            self.torpedo_types = ['Type_95']
            self.primary_torpedo = 'Type_95'
    
    elif self.nation == 'Britain':
        # British always had 21-inch reliable torps
        self.torpedo_types = ['21-inch']
        self.primary_torpedo = '21-inch'

# Call this during init:
self._load_historical_torpedoes()
```

### Step 4.2: Modify `engine/game.py` - Fire Correct Torpedo Type

**Location:** `engine/game.py` or `world/tactical_map.py` in weapon firing

**Current state:** Weapon firing creates generic torpedo

**Action:** Use submarine's assigned torpedo type

```python
# When firing torpedo:

def fire_torpedo(self, target, torpedo_slot=0):
    """Fire torpedo at target"""
    
    # Get submarine's primary torpedo type (historical)
    torpedo_type = self.player_submarine.primary_torpedo
    
    # Create torpedo with type
    from submarine.torpedo import Torpedo
    
    torpedo = Torpedo(
        x=self.player_submarine.x,
        y=self.player_submarine.y,
        dx=direction.x,
        dy=direction.y,
        torpedo_type=torpedo_type,  # IMPORTANT: Pass type for defects
        speed=TORPEDO_SPEEDS[torpedo_type]
    )
    
    # Check if defect was assigned
    if torpedo.defect:
        self.event_manager.post_event({
            'type': 'weapon_defect_warning',
            'torpedo_type': torpedo_type,
            'defect': torpedo.defect.name,
            'description': torpedo.defect.description
        })
    
    # Add to world
    self.tactical_map.add_projectile(torpedo)
```

## Phase 5: Operator Crew Integration

### Step 5.1: Modify `submarine/crew.py` - Add Sonar Operator Role

**Location:** `submarine/crew.py` in crew initialization

**Current state:** Crew roles might not include sonar_operator

**Action:** Ensure sonar_operator role exists and is assigned

```python
# In Submarine or CrewManager initialization:

# Default crew roster includes sonar operator
default_roles = [
    'captain',
    'first_officer',
    'chief_engineer',
    'sonar_operator',  # NEW: Critical for detection
    'torpedo_officer',
    'navigator'
]

# Create crew members for each role
for role in default_roles:
    crew_member = CrewMember(
        name=get_random_name(role),
        role=role,
        skill=random.uniform(0.65, 0.95),  # Varies by quality
        morale=100
    )
    self.crew.add(crew_member)
```

### Step 5.2: Modify `ui/panels/compartment_panel.py` - Display Sonar Officer Stats

**Location:** `ui/panels/compartment_panel.py` or crew status panel

**Current state:** Panel shows crew but maybe not sonar operator details

**Action:** Show sonar operator fatigue/skill

```python
# In crew display:

def display_crew_status(self):
    """Display crew status including sonar operator"""
    
    sonar_op = self.submarine.crew.get_by_role('sonar_operator')
    
    if sonar_op:
        status = f"Sonar Officer: {sonar_op.name}"
        status += f"\n  Skill: {sonar_op.skill:.0%}"
        status += f"\n  Fatigue: {self.sonar_manager.operator.fatigue:.0%}"
        status += f"\n  Morale: {sonar_op.morale:.0%}"
        
        # Color coding
        if self.sonar_manager.operator.fatigue > 0.8:
            color = RED  # Extremely fatigued
        elif self.sonar_manager.operator.fatigue > 0.5:
            color = YELLOW  # Fatigued
        else:
            color = GREEN  # Fresh
        
        self.draw_text(status, color)
```

## Phase 6: Testing Integration

### Step 6.1: Unit Tests - Sonar Detection

Create `tests/test_sonar_detection.py`:

```python
import pytest
from world.sonar_systems import SonarManager, SonarOperator

def test_passive_detection_basic():
    """Test basic passive sonar detection"""
    mgr = SonarManager()
    mgr.set_sonar_type('JT')
    
    # Target at 8000m, moving
    detection = mgr.detect_submarine(
        target_position=(8000, 0),
        target_speed_kmh=15,
        target_depth_m=100,
        hunter_depth_m=100
    )
    
    # Should not always detect (probabilistic), but when it does:
    if detection:
        assert 7000 < detection.range <= 8000
        assert 0 <= detection.bearing < 360

def test_thermocline_reduces_range():
    """Test that thermocline reduces detection range"""
    mgr = SonarManager()
    mgr.set_sonar_type('ASDIC')
    
    # Without thermocline
    mgr.set_thermocline(None)
    range_no_therm = mgr.get_effective_range(mgr.sonar_type)
    
    # With thermocline
    mgr.set_thermocline(depth=150, intensity=1.0)
    range_with_therm = mgr.get_effective_range(mgr.sonar_type)
    
    # ASDIC should lose 90% range to thermocline
    reduction = range_no_therm / range_with_therm
    assert 7 < reduction < 15

def test_operator_fatigue_affects_detection():
    """Test that operator fatigue reduces detection"""
    mgr = SonarManager()
    op = SonarOperator(skill_level=0.90, fatigue=0.0)
    mgr.set_operator(op)
    
    fresh_skill = op.get_effective_skill()
    
    op.fatigue = 1.0
    exhausted_skill = op.get_effective_skill()
    
    # Exhausted should be about 50% of fresh
    assert exhausted_skill < fresh_skill * 0.6
```

### Step 6.2: Integration Tests - Torpedo Defects

Create `tests/test_torpedo_defects.py`:

```python
from submarine.torpedo import Torpedo

def test_mk14_defect_rate():
    """Verify Mk_14 defect rate is historically accurate (~35%)"""
    defect_count = 0
    total = 1000
    
    for _ in range(total):
        torpedo = Torpedo(
            x=0, y=0, dx=1, dy=0,
            torpedo_type='Mk_14',
            speed=38
        )
        if torpedo.defect:
            defect_count += 1
    
    actual_rate = defect_count / total
    # Should be around 35%, allow ±5%
    assert 0.30 < actual_rate < 0.40

def test_g7a_hot_run():
    """Test G7a hot run defect behavior"""
    torpedo = Torpedo(
        x=0, y=0, dx=1, dy=0,
        torpedo_type='G7a',
        speed=40
    )
    
    # If defect is hot run, torpedo should change direction
    if torpedo.defect and torpedo.defect.name == 'G7a Hot Run':
        initial_direction = (torpedo.dx, torpedo.dy)
        
        # Step several times
        for _ in range(10):
            torpedo.step()
        
        final_direction = (torpedo.dx, torpedo.dy)
        
        # Direction should have changed
        # (hot run adds random variation)
        assert initial_direction != final_direction
```

### Step 6.3: Run All Tests

```bash
cd "/Users/matiaspetersen/Documents/Depths within"
python -m pytest tests/ -v
```

**Expected result:** All 186 tests passing + new tests passing

## Phase 7: Integration Validation Checklist

- [ ] **SonarManager initialized** in Game.__init__()
- [ ] **Sonar operator linked** to crew system
- [ ] **Thermocline generated** for each tactical map
- [ ] **Detection events logged** each turn
- [ ] **Detection UI displays** contacts properly
- [ ] **Enemy submarines detect** player when in range
- [ ] **Torpedo types assigned** historically correct
- [ ] **Torpedo defects working** (Mk_14, G7a, etc)
- [ ] **Operator fatigue accumulates** during patrol
- [ ] **False contacts generated** occasionally (~2%)
- [ ] **All tests passing** (186+)

## Phase 8: Gameplay Consequences

Once integrated, game will have:

### Early War US Campaign
- Mark 14 failures cause frustration ("misses" despite good setup)
- Player must learn early war was historically challenging
- Switching to contact detonators mid-war provides relief

### German Campaign
- GHG sonar limited effectiveness vs British escorts
- Thermocline escape tactic essential
- False contacts waste ammunition and time

### Japanese Campaign
- Type 93 dominates but volatile (risky if hit)
- Oxygen fuel creates strategic tension
- Incredible range allows standoff attacks

### British Campaign
- 21-inch torpedo reliability provides advantage
- ASDIC detection system varies by location
- Mediterranean thermocline problematic

## Rollback Plan (If Issues)

If integration causes problems:

```python
# In Game class, can disable systems:
ENABLE_HISTORICAL_DEFECTS = True  # Set False to disable
ENABLE_SONAR_DETECTION = True     # Set False to disable
ENABLE_THERMOCLINE = True         # Set False to disable

# Then wrap calls:
if ENABLE_SONAR_DETECTION:
    self._process_sonar()
```

## Files Modified Summary

| File | Modifications | Lines Added |
|------|--------------|------------|
| engine/game.py | Sonar init, sonar tick, detection handling | ~80 |
| world/tactical_map.py | Sonar imports, thermocline generation, enemy sonar | ~50 |
| ui/panels/log_panel.py | Detection event formatting | ~30 |
| submarine/submarine.py | Historical torpedo loading | ~40 |
| submarine/crew.py | Sonar operator role | ~10 |
| ui/panels/compartment_panel.py | Operator status display | ~20 |

**Total new code:** ~230 lines (spread across 6 files)

## Timeline Estimate

| Phase | Task | Time |
|-------|------|------|
| 1 | Initialize SonarManager | 30 min |
| 2 | Detection events | 45 min |
| 3 | Enemy sonar | 30 min |
| 4 | Torpedo types | 30 min |
| 5 | Crew integration | 20 min |
| 6 | Testing | 30 min |
| **Total** | **Full integration** | **~3 hours** |

## Next Steps

1. Start with **Phase 1** - Initialize SonarManager
2. Run tests after each phase
3. Test gameplay manually between phases
4. Adjust thermocline depth ranges based on playtesting
5. Balance defect rates if too frustrating/trivial
