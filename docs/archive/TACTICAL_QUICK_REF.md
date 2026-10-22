# Tactical Systems Quick Reference Card

## Commands At-A-Glance

### Display Information
```
time               Show time & environmental conditions
divers             Show diver operations status
sensors            Show sensor & contact status
tactical_status    Show all three panels side-by-side
tactical_hud       Show compact status bar
```

### Take Actions
```
sensor <type>                  Toggle sensor on/off
  Types: periscope, sonar, radar, hydrophone

recruit_diver [specialty]      Recruit new diver
  Specialties: reconnaissance, sabotage, rescue,
               infiltration, demolition, combat

diver_mission <type> <target> [difficulty]
  Types: harbor_recon, ship_sabotage, net_cutting,
         beach_recon, pilot_rescue, mine_placement,
         facility_infiltration, wreck_salvage,
         cable_cutting, obstacle_clearing
```

### Get Help
```
help tactical      Tactical systems overview
time_help          Detailed time system guide
diver_help         Detailed diver operations guide
sensor_help        Detailed sensor systems guide
```

---

## Time System Quick Facts

**Time Periods:**
- 🌙 Night (00:00-05:59) - 5-20% vis, 20-35% risk → SAFE
- 🌅 Dawn (06:00-07:59) - 50% vis, 50% risk → CAUTION
- ☀️ Morning (08:00-11:59) - 100% vis, 90-100% risk → DANGER
- ☀️ Noon (12:00-13:59) - 100% vis, 100% risk → DANGER
- ☀️ Afternoon (14:00-17:59) - 100% vis, 90-100% risk → DANGER
- 🌇 Dusk (18:00-19:59) - 50% vis, 50% risk → CAUTION
- 🌙 Evening (20:00-23:59) - 15-30% vis, 25-40% risk → SAFE

**Moon Phases (8):**
New Moon → Waxing Crescent → First Quarter → Waxing Gibbous →
Full Moon → Waning Gibbous → Last Quarter → Waning Crescent

**Key Fact:** Each turn = 5 minutes game time

---

## Diver Operations Quick Facts

**6 Specializations:**
1. Reconnaissance - Intel gathering, scouting
2. Sabotage - Ship damage, limpet mines
3. Rescue - Pilot recovery, crew rescue
4. Infiltration - Harbor penetration, facility entry
5. Demolition - Obstacle clearing, demolition
6. Combat - Underwater combat specialist

**Mission Success Factors:**
- ✓ Specialist matches mission type = +effectiveness
- ✓ Low fatigue = better performance
- ✓ Night operation = lower detection risk
- ✓ New moon = maximum stealth

**Key Fact:** Divers gain fatigue during missions, reduce effectiveness when tired

---

## Sensor Systems Quick Facts

**4 Sensor Types:**

| Sensor | Range | Requirements | Best For |
|--------|-------|--------------|----------|
| **Periscope** | 15 tiles | Depth ≤ 15m | Visual ID, daylight |
| **Sonar** | 30 tiles | Any depth | Underwater, all-round |
| **Radar** | 50 tiles | Surface only | Long-range surface |
| **Hydrophone** | 60 tiles | Any depth | Passive, silent |

**Contact Types:**
- Unknown (?)
- Merchant (cargo, tanker)
- Warship (destroyer, cruiser, battleship)
- Submarine (ally or enemy)
- Aircraft (patrol, recon)
- Coastal (battery, lighthouse)

**Confidence Levels:**
- Uncertain < 50% - Initial detection
- Probable 50-80% - Likely classification
- Certain > 80% - Confirmed identification

**Key Fact:** Multiple sensors = better intel

---

## Tactical Situation Examples

### Example 1: Night Surface Run
```
> time
🌙 22:00 - EVENING - Vis: 20% - Risk: 25% - ✓ SAFE

> surface
Safe to surface. Charging batteries...
```

### Example 2: Diver Sabotage Mission
```
> time
🌙 02:00 - NIGHT - Moon: New - ✓ SAFE

> recruit_diver sabotage
✓ Klaus Schmidt recruited

> diver_mission ship_sabotage "Brest Harbor" 0.7
Mission launched! ETA: 20 turns
```

### Example 3: Contact Detection
```
> sensor periscope
Periscope activated

> sensor sonar
Sonar activated

> sensors
Contacts: 2
  merchant    045°  3.2km  85%
  warship     315°  5.8km  95%
```

### Example 4: Dawn Periscope Attack
```
> time
🌅 06:30 - DAWN - Vis: 50% - Risk: 50% - ⚠ CAUTION

> sensor periscope
Periscope range: 5.0 km
Good time for visual targeting
```

---

## Decision Matrix

### When to Surface?
- ✓ Night (22:00-05:59)
- ✓ New moon preferred
- ✗ Day (06:00-19:59)
- ⚠ Dawn/Dusk (brief windows)

### When to Launch Divers?
- ✓ Night operations
- ✓ New moon (darkest)
- ✓ Low fatigue divers
- ✗ Day (too risky)
- ⚠ Check specialist match

### When to Use Sensors?
- **Periscope:** Dawn/day for visual ID, shallow water only
- **Sonar:** Always (passive mode), underwater detection
- **Radar:** Surface only, long-range surface contacts
- **Hydrophone:** Silent detection, supplement sonar

### Mission Planning?
1. Check time → Is it night?
2. Check divers → Any available?
3. Match specialist → Recon for recon, sabotage for sabotage
4. Launch mission → Monitor progress
5. Collect intel → Use for tactical advantage

---

## Status Indicators

### Time Panel Symbols
- ✓ = Safe to surface
- ⚠ = Caution advised
- ✗ = Danger, stay submerged
- 🌙 = Night/Evening
- 🌅 = Dawn
- ☀️ = Day
- 🌇 = Dusk

### Diver Panel Symbols
- READY = Available for mission
- BUSY = Currently on mission
- Fatigue % = 0% fresh, 100% exhausted

### Sensor Panel Symbols
- ● = Sensor active (ON)
- ○ = Sensor inactive (OFF)
- % = Contact confidence level

---

## Pro Tips

**Survival:**
- Stay deep during day (depth > 30m)
- Surface only at night for battery charging
- Monitor detection risk constantly

**Intelligence:**
- Launch recon missions before attacks
- Harbor intel reveals ship counts, defenses
- Multiple sensors = better contact classification

**Operations:**
- Sabotage missions most effective at new moon
- Rest fatigued divers between missions
- Match specialist to mission type for best results

**Sensors:**
- Use periscope for visual confirmation
- Keep sonar on for omnidirectional awareness
- Activate radar when surfaced for long-range detection
- Use hydrophone passively to avoid detection

---

## Troubleshooting

**Q: Time not advancing?**
A: Time advances per turn. Use `tick` or perform actions.

**Q: Can't see contacts?**
A: Check sensors are active: `sensor sonar`

**Q: Diver mission not starting?**
A: Check diver availability: `divers`

**Q: Periscope not working?**
A: Check depth ≤ 15m and sensor is active

**Q: Mission progress stuck?**
A: Missions progress per turn. Keep playing.

---

## Full Documentation

- **User Guide:** TACTICAL_UI_GUIDE.md (450 lines)
- **Technical:** NEW_SYSTEMS_GUIDE.md (800 lines)
- **Overview:** PROJECT_STATUS.md
- **Tests:** test_ui_quick.py, test_new_systems.py

---

**Print this card and keep it handy during gameplay!**

Last Updated: Current session
Version: 1.0 - Tactical Systems Complete
