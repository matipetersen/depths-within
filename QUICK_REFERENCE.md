# Quick Reference: Crew Management & Upgrades

## Most-Used Commands

### Crew Management
```
recruit [skill]           # Hire crew (random or with skill filter)
crew_list                 # Show all crew
crew_info <id>            # Detailed crew stats
assign <id> <comp> [role] # Assign crew to compartment
reassign <id> <comp>      # Move to different compartment
fire_crew <id>            # Remove crew member
```

### Player Progression
```
player_status             # Show career stats and XP
upgrades                  # List all upgrades
install_upgrade <id>      # Install submarine upgrade
```

---

## Crew Skills

| Skill | Focus | Used In |
|-------|-------|---------|
| sonar | Detection | Sonar system |
| torpedo | Targeting | Torpedo firing |
| engineering | Repairs | Damage control |
| damage_control | Crisis response | Event resolution |
| navigation | Positioning | Movement |

---

## Upgrade Examples

| ID | Name | Cost | Effect |
|----|------|------|--------|
| sonar_improved_range | Extended Sonar | 500 | +20% range |
| hull_reinforcement | Hull Reinforcement | 700 | +15% integrity |
| torpedo_faster_reloading | Quick Reload | 600 | -25% reload time |
| engine_battery_capacity | Expanded Battery | 800 | +25% capacity |
| hull_deeper_diving | Deep Diving Hull | 1100 | +50m depth |

---

## Crew Status Scales

- **Stress**: 0 (calm) → 1 (panicked) — reduces effectiveness when >0.7
- **Morale**: 0 (broken) → 1 (excellent) — affects reliability
- **Fatigue**: 0 (fresh) → 1 (exhausted) — slows down crew
- **Health**: 0 (dying) → 1 (healthy) — affects ability to work

---

## Career Stats Tracked

- **ships_sunk** - Total enemy vessels destroyed
- **tonnage_sunk** - Total tonnage of ships destroyed
- **contacts_detected** - Total sonar contacts identified
- **torpedoes_fired** - Total torpedoes launched
- **successful_hits** - Total torpedo hits
- **patrol_days** - Total mission duration
- **crew_trained** - Total crew recruited
- **narrow_escapes** - Times you avoided destruction
- **compartments_repaired** - Total damage control operations

---

## Crew Assignment Roles

- `crew` - Standard crew member
- `specialist` - Specialized in their primary skill
- `officer` - Leader (better stress management)

---

## Effective Skill Formula

```
effectiveness = base_skill × (1 - stress×0.5) × (1 - fatigue×0.3) × (1 + level×0.1) × morale
```

**Factors:**
- High stress: -50% effectiveness
- High fatigue: -30% effectiveness  
- Each level: +10% effectiveness
- Low morale: Reduces multiplier

**Example:**
- Base skill 100, stress 0.5, fatigue 0.4, level 3, morale 0.8:
- 100 × 0.75 × 0.88 × 1.3 × 0.8 = **68.6 effectiveness**

---

## Leveling Thresholds

| Level | XP Required | Typical Milestone |
|-------|-------------|------------------|
| 1 | 0 | Starting captain |
| 2 | 500 | Early campaign |
| 3 | 1000 | First upgrades |
| 4 | 1500 | Mid-game |
| 5+ | +500 per level | Veteran captain |

---

## Crew Lifecycle

```
Recruit → Assign → Experience → Level Up → Specialize → Veteran/Casualty
```

1. **Recruit**: Find crew at port or random recruitment
2. **Assign**: Place in compartment with role
3. **Experience**: Gain XP through gameplay
4. **Level Up**: Every 500 skill XP increases level
5. **Specialize**: Higher levels in one skill = expert
6. **Veteran/Casualty**: Long-term crew or lost in action

---

## Strategic Tips

### Crew Recruitment
- Balance specialists and generalists
- Recruit higher-ranked crew when possible
- Keep pool fresh by recruiting during patrols

### Crew Management
- Rotate crew between compartments to prevent stress cascades
- Assign officers to critical compartments
- Keep trauma specialists (damage control) fresh

### Progression
- Focus on 2-3 skills rather than spreading thin
- Upgrade synergistically (e.g., sonar + navigation)
- Track career stats for achievements

---

## Console Command Cheat Sheet

```
# Crew Viewing
crew_list                    # Show roster
crew_info 0                  # Info on crew ID 0

# Crew Management
recruit                      # Hire random
recruit sonar               # Hire sonar specialist
assign 1 0 sonar            # Crew 1 → Compartment 0 as sonar
reassign 1 1 engineering    # Move to compartment 1

# Status
player_status               # Career progress
compartments                # Compartment status

# Upgrades
upgrades                    # List all
install_upgrade sonar_improved_range  # Install upgrade
```

---

## Examples

### Example: Build a Sonar Team
```
recruit sonar               # Hire first sonar op
recruit sonar               # Hire second sonar op
crew_list                   # Check IDs
assign 0 0 specialist       # Crew 0 to compartment 0
assign 1 1 specialist       # Crew 1 to compartment 1
player_status               # Check your sonar XP
install_upgrade sonar_improved_range  # Boost sonar
```

### Example: Emergency Damage Control
```
recruit damage_control      # Hire damage specialist
assign 0 2 specialist       # Place in engine compartment
# When flooding occurs, they'll respond automatically
crew_info 0                 # Check their stress level
# They gain XP from successful resolution
```

### Example: Career Progression
```
# Early game
recruit                     # Hire generalist crew
patrol a few turns
player_status               # ~100 XP accumulated

# Mid game (500+ XP)
upgrades                    # New tier-1 options available
install_upgrade hull_reinforcement  # Upgrade hull
recruit engineering         # Add specialist

# Late game (1500+ XP)
install_upgrade silent_drive_system  # Tier-3 upgrade
crew_list                   # Review veteran crew
```

---

## Troubleshooting

**Q: Why is my crew's effectiveness so low?**  
A: Check their stress/fatigue. Use `crew_info <id>` to see status. Allow rest periods.

**Q: Can I respec crew skills?**  
A: No, crew specializes as they gain XP. Plan carefully or recruit new crew.

**Q: Will my upgrades persist between patrols?**  
A: Yes! Upgrades are installed permanently on your submarine.

**Q: How do I get more XP for upgrades?**  
A: Engage in combat, sink ships, complete patrols. Career stats accumulate.

**Q: Can crew die?**  
A: Currently crew can be removed/transferred. Full casualty system coming later.

---

For detailed mechanics, see **CREW_PROGRESSION_GUIDE.md**  
For technical details, see **PHASE_11_SUMMARY.md**
