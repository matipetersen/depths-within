# QUICK COMMAND REFERENCE - GRAPHICAL DISPLAYS

## 🎮 Display Commands

```
t                    Tactical Map (120x35)      - Full tactical awareness
sonar                Sonar Display (40x25)      - Pure sonar view
dash                 Dashboard                  - Full system status
compartment_detail   Compartment Report         - Damage details
crew_detail          Crew Roster                - Personnel details
sonar_detail         Sonar Details              - Contact breakdown
view                 List Modes                 - Show all displays
legend               Map Legend                 - Reference guide
```

## 📊 Display Contents

### TACTICAL MAP (`t`)
```
─ Submarine position (@) at center
─ Contact positions (C,W,E,A,S,T)
─ Bearing and range calculations
─ Depth zones with colors
─ Heading indicator (>)
─ Real-time HUD (right side)
  ├ Heading, Speed, Depth
  ├ Compartment status
  ├ Weapon status
  ├ Crew count
  └ Sonar status
```

### SONAR DISPLAY (`sonar`)
```
─ Circular sonar representation
─ Concentric range rings
─ Cardinal directions (N,S,E,W)
─ Your submarine (@) at center
─ Contact markers (C)
─ Realistic sonar appearance
```

### DASHBOARD (`dash`)
```
SUBMARINE COLUMN          COMPARTMENT COLUMN        CREW COLUMN
─────────────────         ──────────────────        ───────────
Name & Nation             Total compartments        Total crew
Heading                   Damaged count             Alive count
Speed                     Flooded count             Injured count
Depth                     Top 5 compartments        Morale bar
Hull integrity            Damage percentages        Loyalty bar
Engine status             Status indicators         XP/Level
Battery level             ✓/⚠/✗ symbols            

WEAPONS COLUMN            SONAR CONTACTS COLUMN
──────────────            ─────────────────────
Total torpedoes           Total contacts detected
Loaded count              Per-contact info:
Ready to fire             ├ Bearing (degrees)
Torpedo types             ├ Range (meters)
By type breakdown         ├ Type (Merchant/Warship/etc)
In water count            └ Quality % (detection confidence)
```

### COMPARTMENTS (`compartment_detail`)
```
Per compartment:
─ Status indicator (✓/⚠/✗)
─ Name
─ Integrity percentage [████░░]
─ Flooding level [█░░░░░░]
─ Crew count
─ Special systems
```

### CREW (`crew_detail`)
```
Per crew member (first 20):
─ Status (✓/⚠/✗)
─ Name
─ Role
─ Health percentage
```

### SONAR (`sonar_detail`)
```
─ Active sonar system name
─ Current operator name
─ Operator fatigue level
─ Each contact:
  ├ Bearing (degrees)
  ├ Range (meters)
  ├ Type (Merchant/Warship/etc)
  └ Quality (detection confidence %)
```

## 🎨 Legend

### Contact Types
```
C  Merchant vessel (yellow)      W  Warship (red)
E  Escort (red)                  A  Aircraft (red)
S  Submarine (green)             T  Torpedo (yellow)
?  Unknown (gray)
```

### Your Submarine
```
@  Submarine position (green)    >  Heading indicator (green)
```

### Depth Zones
```
~  Shallow (50-100m)            ≈  Moderate (100-150m)
=  Deep (150-250m)              ≡  Very deep (250-400m)
≋  Abyssal (400m+)              *  Thermocline
```

### Status Indicators
```
✓  Normal / Healthy (green)
⚠  Warning / Damaged (yellow)
✗  Critical / Flooded (red)
-  Offline (gray)
```

### Status Bars
```
[██████████] 100% - All good
[████░░░░░░] 40%  - Getting low
[██░░░░░░░░] 20%  - Critical
```

## ⌨️ Keyboard Controls

**While Viewing Displays:**
- Press **Enter** to return to command prompt
- Type new command to switch displays

**Quick Navigation:**
```
t          → Tactical map
sonar      → Sonar view
dash       → Dashboard
help       → Command help
q          → Quit game
```

## 🎯 Common Workflows

### Tactical Situation Assessment
```
1. Type: t              (see tactical map)
2. Type: sonar          (confirm sonar contacts)
3. Type: dash           (check weapon status)
4. Type: compartment_detail (verify damage)
```

### Before Combat
```
1. Type: dash           (full system check)
2. Type: compartment_detail (verify integrity)
3. Type: sonar_detail   (confirm targets)
4. Type: t              (final position check)
```

### Emergency Assessment
```
1. Type: compartment_detail (damage report)
2. Type: crew_detail    (personnel status)
3. Type: dash           (overall status)
4. Type: t              (tactical escape analysis)
```

### Sonar Operator Training
```
1. Type: sonar          (pure sonar view)
2. Type: sonar_detail   (detailed contacts)
3. Type: t              (correlation with tactical)
```

## 📈 Real-Time Indicators

### Status Bars Show:
- Hull integrity (0-100%)
- Engine power (0-100%)
- Battery charge (0-100%)
- Crew morale (0-100%)
- Crew loyalty (0-100%)
- Compartment integrity (per compartment)
- Sonar contact quality (per contact)

### Color Indicators:
```
Green   = Healthy (≥75%)
Yellow  = Caution (50-75%)
Red     = Critical (<50%)
Gray    = Offline/Inactive
```

## 📊 Information Priority

**TACTICAL MAP** - Best for:
- Navigation planning
- Contact positioning
- Visual tactical assessment
- Real-time combat
- Target selection

**SONAR VIEW** - Best for:
- Pure sonar data
- Range ring reference
- Detection quality assessment
- Stealth analysis
- Bearing confirmation

**DASHBOARD** - Best for:
- System health monitoring
- Resource management
- Mission planning
- Crew status
- Detailed contact list

**DETAILED PANELS** - Best for:
- Damage assessment
- Crew personnel review
- System detail inspection
- Sonar contact analysis

## ⚡ Performance Tips

**Fastest Displays (for low-lag gaming):**
1. Status bar (5-10ms)
2. Sonar view (20-40ms)
3. Tactical map (50-100ms)
4. Dashboard (80-150ms)

Use **status bar** during combat for minimal lag.
Use **dashboard** during planning phases.

## 🔄 Terminal Requirements

**Recommended:**
- 256-color terminal support
- 120+ character width
- 35+ line height
- UTF-8 encoding

**Will Work On:**
- 8-color terminals (degraded colors)
- 80-char width (narrow tactical map)
- Standard terminals
- SSH sessions
- Terminal emulators

## 🎬 Example Gaming Session

```
$ python main.py                           # Launch game
> t                                        # Show tactical map
  ≈≈≈≈≈@>≈≈≈≈≈ ═ SYSTEMS ═ ...          # See surroundings
  
> sonar                                    # Switch to sonar
  ·    ·          N         ·              # Study contacts
  ·W   ·    @    ·       E ·               
  
> dash                                     # Check systems
  Torpedoes: 6/12 loaded                  # Ready for combat
  Crew morale: 85%
  
> sonar_detail                             # Final targeting info
  Bearing 180° | Range 2500m | Warship    # Select target
  
> f                                        # Fire
  (Assuming 'f' fires torpedoes)
  
> t                                        # Watch it happen
  ≈≈≈≈≈@>≈≈≈≈≈                            # Torpedo tracks
  ≈T≈≈W≈≈≈≈≈≈≈                            # Heading to target
```

## 🆘 Troubleshooting

**Colors Not Showing?**
- Terminal may not support 256 colors
- Try setting: `export TERM=xterm-256color`
- Colors will degrade gracefully

**Display Too Wide?**
- Resize terminal to ≥120 characters
- Tactical map will be clipped (but functional)

**Display Too Tall?**
- Resize terminal to ≥35 lines
- Dashboard may scroll (but readable)

**Characters Wrong?**
- Check UTF-8 encoding: `locale`
- Should show UTF-8 compatible locale

---

**Print this card and keep it by your desk for quick reference!**

Last updated: December 1, 2025
