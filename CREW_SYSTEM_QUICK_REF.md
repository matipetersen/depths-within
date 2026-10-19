# Enhanced Crew System - Quick Reference

## 🎯 At a Glance

**Problem:** All crew were generic with no meaningful differences
**Solution:** 6 quality tiers, 20+ specializations, skill-based repairs

---

## 📊 Quick Stats

### Crew Quality Tiers

| Quality | Captain Lvl | Skills | Cost | Best Use |
|---------|------------|--------|------|----------|
| **Recruit** | 1+ | 40-60% | 100 | Early game filler |
| **Trained** | 3+ | 60-75% | 300 | Mid-game standard |
| **Experienced** | 5+ | 75-85% | 800 | Late-game baseline |
| **Veteran** | 8+ | 85-95% | 2,000 | Elite crew |
| **Ace** | 12+ | 95-100% | 5,000 | Best of the best |
| **Legendary** | 15+ | 100-120% | 15,000 | Superhuman legends |

### Top Specializations

| Specialization | Bonus | Best For |
|----------------|-------|----------|
| **Chief Engineer** | +50% repair speed | All repairs |
| **Hull Specialist** | +60% hull repair | Combat damage |
| **Damage Controller** | +70% emergency repairs | Critical situations |
| **Torpedo Specialist** | +30% accuracy, +40% reload | Attacks |
| **Sonar Operator** | +40% range, +50% ID | Detection |
| **Navigator** | +30% efficiency, +20% fuel | Long patrols |

### Repair Speed Comparison (Hull Breach)

| Engineer Type | Time | Speed vs Recruit |
|--------------|------|------------------|
| Recruit | 90 min | 1.0x (baseline) |
| Experienced | 69 min | 1.3x faster |
| Veteran | 61 min | 1.5x faster |
| **Hull Specialist** | **32 min** | **2.8x faster!** |

---

## 🚀 Quick Start

### 1. Create Recruitment Pool
```python
from submarine.crew_recruitment_enhanced import RecruitmentPool

pool = RecruitmentPool("Kiel Naval Base", port_quality=5)
pool.refresh_pool(captain_level=10, reputation=75)
print(pool.get_summary())
```

### 2. Recruit Crew
```python
# Find specialist engineers
engineers = pool.get_available_crew(
    quality_filter=CrewQuality.VETERAN,
    skill_filter='engineering'
)

# Recruit best one
if engineers:
    success, cost = pool.recruit(engineers[0])
    print(f"Recruited {engineers[0].name} for {cost} points")
```

### 3. Setup Repair System
```python
from submarine.engineer_repairs import EngineerRepairSystem, RepairType

repair_system = EngineerRepairSystem()

# Create repair
repair_system.create_repair(
    RepairType.HULL_BREACH,
    severity=0.8,
    compartment_id='forward',
    priority=True
)

# Auto-assign engineers
repair_system.auto_assign_engineers(available_engineers)
```

### 4. Game Loop Integration
```python
def game_tick():
    # Process repairs
    events = repair_system.tick_all_repairs()
    for event in events:
        if event['complete']:
            log_event(event['message'])
    
    # Update crew
    roster.tick()
```

---

## 💡 Strategic Tips

### Early Game (Level 1-4)
- ✅ Recruit diverse skills (one of each)
- ✅ Focus on Trained quality crew
- ❌ Don't waste points on specialists yet
- ❌ Avoid expensive Veterans/Aces

### Mid Game (Level 5-8)
- ✅ Start recruiting Experienced crew
- ✅ Get first specialist (Navigator or Sonar)
- ✅ Build reputation for better pools
- ✅ Replace casualties with quality

### Late Game (Level 9-15)
- ✅ Only recruit Veterans or better
- ✅ Build full specialist roster
- ✅ Chief Engineer is TOP priority
- ✅ Hunt for Legendary crew

### Critical Specialists Priority
1. **Chief Engineer** - Repairs win battles
2. **Sonar Operator** - Detection = survival
3. **Damage Controller** - Saves submarine
4. **Navigator** - Efficiency matters
5. **Torpedo Specialist** - Better kills

---

## 🎯 Decision Guide

### Should I recruit this crew?

**YES if:**
- ✅ Specialist in critical role (engineer, sonar)
- ✅ Quality tier equals or exceeds current average
- ✅ Primary skill matches submarine needs
- ✅ Cost is < 10% of current points
- ✅ Replacing casualty of lower quality

**NO if:**
- ❌ Generic crew below current average
- ❌ Skill not needed (duplicate specialists)
- ❌ Cost > 25% of current points
- ❌ Captain level too low (better crew coming)
- ❌ Can't afford to lose in combat

### Which specialist to recruit first?

**Combat-heavy playstyle:**
1. Damage Controller (survive)
2. Torpedo Specialist (kill)
3. Sonar Operator (detect)

**Stealth playstyle:**
1. Sonar Operator (detect first)
2. Navigator (efficient movement)
3. Hull Specialist (deep diving)

**Campaign mode:**
1. Chief Engineer (long-term value)
2. Navigator (efficiency)
3. Quartermaster (resources)

---

## 📈 Progression Path

### Crew Development Timeline

**Recruit → Trained (Level 3)**
- Base skills improve 40% → 65%
- Recruitment cost: 100 → 300
- Time: ~5-10 missions

**Trained → Experienced (Level 5)**
- Base skills improve 65% → 80%
- Can specialize in basic roles
- Recruitment cost: 300 → 800
- Time: ~10-15 missions

**Experienced → Veteran (Level 8)**
- Base skills improve 80% → 90%
- Can specialize in advanced roles
- Recruitment cost: 800 → 2,000
- Time: ~15-25 missions

**Veteran → Ace (Level 12)**
- Base skills improve 90% → 98%
- Elite performance
- Recruitment cost: 2,000 → 5,000
- Time: ~25-40 missions

**Ace → Legendary (Level 15)**
- Skills exceed 100% (superhuman)
- Rare and expensive
- Recruitment cost: 5,000 → 15,000
- Time: 40+ missions

---

## 🔧 Repair System

### Repair Types by Priority

**EMERGENCY (20 min base):**
- Quick combat patches
- 90% difficulty
- Use Damage Controller

**FLOODING (60 min base):**
- Water infiltration
- 70% difficulty
- Critical to stop spread

**HULL BREACH (120 min base):**
- Structural damage
- 80% difficulty
- Use Hull Specialist

**ELECTRICAL (45 min base):**
- Battery, power systems
- 60% difficulty
- Use Electrical Engineer

**MECHANICAL (90 min base):**
- Engines, propulsion
- 70% difficulty
- Use Mechanical Engineer

### Repair Speed Formula
```
Speed = Base × Skill × Specialization × Difficulty
      × (1 - Stress × 0.3)
      × (1 - Fatigue × 0.2)
```

### Example: Hull Breach (80% severity)
- **Recruit** (50% skill): 90 minutes
- **Veteran** (95% skill): 61 minutes
- **Hull Specialist** (95% + 60% bonus): 32 minutes

**Specialist is 2.8x faster!**

---

## 🎲 Random Events Impact

### High-Quality Crew Benefits

**Legendary crew (100-120% skills):**
- Can succeed at "impossible" tasks
- Morale bonus to nearby crew (+10%)
- Reduced stress from combat (-20%)
- Faster XP gain for trainees (+30%)

**Specialist crew bonuses:**
- Fewer critical failures (-50%)
- Better emergency responses (+40%)
- Improved crew training (+25%)
- Reputation boost in ports (+10)

---

## 📋 Integration Checklist

### Port Phase
- [ ] Refresh recruitment pool with captain level
- [ ] Display available crew by quality
- [ ] Show specialist bonuses
- [ ] Calculate recruitment costs
- [ ] Update roster after recruitment

### Mission Phase
- [ ] Assign crew to stations
- [ ] Monitor stress/fatigue levels
- [ ] Queue repairs as damage occurs
- [ ] Auto-assign engineers to repairs
- [ ] Award XP for actions

### Game Loop
- [ ] Tick repair system every turn
- [ ] Update crew status (stress, fatigue)
- [ ] Check for level ups
- [ ] Check specialization eligibility
- [ ] Process completed repairs

### UI Display
- [ ] Show crew quality in roster
- [ ] Display specialization bonuses
- [ ] Repair progress indicators
- [ ] Skill effectiveness percentages
- [ ] Recruitment pool summary

---

## 🔢 Key Numbers

- **Max crew per submarine:** 50
- **XP for level up:** 500 total XP
- **Specialist cost multiplier:** 1.5x
- **Repair speed range:** 0.5x to 3.0x
- **Skill effectiveness range:** 0% to 200%
- **Stress impact:** Up to -40% effectiveness
- **Fatigue impact:** Up to -30% effectiveness
- **Specialization bonus:** Up to +70%

---

## ⚠️ Common Mistakes

**DON'T:**
- ❌ Recruit low-quality crew late game
- ❌ Ignore specialist bonuses (2-3x value!)
- ❌ Let stress exceed 80% (major penalties)
- ❌ Assign wrong specialist to repairs
- ❌ Forget to rest crew between missions

**DO:**
- ✅ Prioritize engineer specialists
- ✅ Build reputation for better pools
- ✅ Replace casualties with equal/better quality
- ✅ Auto-assign repairs (optimal matching)
- ✅ Monitor stress/fatigue constantly

---

## 🎮 Files Overview

| File | Purpose |
|------|---------|
| `submarine/crew_skills.py` | Core crew system, specializations |
| `submarine/crew_recruitment_enhanced.py` | Recruitment pools, roster management |
| `submarine/engineer_repairs.py` | Repair system, engineer assignments |
| `tests/test_enhanced_crew_system.py` | Comprehensive test suite |
| `ENHANCED_CREW_SYSTEM_GUIDE.md` | Full documentation |

---

**Bottom Line:** Specialists make 2-3x difference in performance. Recruit quality crew, develop specialists, win battles! 🚢⚓
