# Quick Statistics Reference

## Using Game Statistics

The statistics system tracks **all meaningful events** in your game except eldritch encounters (which remain secretive by design).

### Quick Start

In-game, type any of these commands:

```
stats summary          # Quick overview
stats full            # Complete report
stats detailed        # Full report + event logs
stats combat          # Combat performance
stats crew            # Crew/personnel record
stats security        # Sabotage & spies
stats missions        # Mission completion
stats help            # Command reference
```

Or use the hotkey:
```
sa                    # Show stats (same as "stats summary")
```

---

## What Gets Tracked

### ✅ TRACKED

- **Combat**: Ships sunk, tonnage, hits, accuracy, engagements
- **Crew**: Deaths, injuries, recruitment, morale crises, stress
- **Missions**: Completed, failed, successful patrols
- **Defense**: Depth charge escapes, repairs, flooding events
- **Security**: Spies caught, sabotages detected/successful
- **Resources**: Supply shortages
- **Survival**: Surface sightings, equipment failures

### ❌ NOT TRACKED (SECRETIVE)

- Eldritch encounters
- Cosmic horror interactions
- Mysterious phenomena
- Unexplained events

*The unknowable shall remain unknown and unrecorded.*

---

## Statistics Categories

### Combat Record
Shows your offensive and defensive performance:
- Ships sunk & tonnage
- Torpedo accuracy
- Naval battles
- Successful escapes
- Notable kills

### Crew Record
Personnel management overview:
- Recruitment & losses
- Morale crises
- Stress incidents
- Recent casualties

### Security Record
Counterintelligence tracking:
- Spies apprehended
- Sabotage attempts
- Success vs. detection rates
- Captured agents list

### Mission Record
Objective completion:
- Success/fail rates
- Patrol completions
- Mission timeline

---

## Example Output

```
═══ GAME STATISTICS ═══

COMBAT RECORD:
  Ships Sunk: 12
  Total Tonnage: 47,500t
  Enemy Contacts: 34
  Torpedoes Fired: 28
  Torpedoes Hit: 14
  Hit Rate: 50.0%

CREW STATUS:
  Recruited: 45
  Deaths: 3
  Injured: 7
  Morale Crises: 1
  Stress Incidents: 5

MISSION RECORD:
  Completed: 5
  Failed: 1
  Success Rate: 83.3%
  Successful Patrols: 3

SECURITY:
  Spies Caught: 1
  Sabotages Detected: 2
  Sabotages Successful: 0
```

---

## Details on Detailed Reports

The `stats detailed` command shows everything plus:

**Ships Sunk** - Last 10 with tonnage and turn numbers
**Crew Losses** - Last 10 deaths with causes
**Apprehended Agents** - All spies caught with real/cover names
**Sabotage Incidents** - Last 10 with status (detected/successful)
**Mission Log** - Last 10 missions with outcomes

---

## Data Persistence

Statistics are automatically saved to:
```
data/statistics/session_YYYYMMDD_HHMMSS.json
```

This includes:
- All numerical statistics
- Complete event history
- Detailed logs
- Session metadata

---

## Strategic Use

Monitor these metrics to improve your game:

1. **Hit Rate** - Optimize torpedo targeting
2. **Casualty Rate** - Improve crew management
3. **Mission Success** - Learn from failures
4. **Sabotage Attempts** - Strengthen security
5. **Supply Shortages** - Better resource management

---

## Commands Quick List

| Command | What It Shows |
|---------|--------------|
| `sa` | Brief summary |
| `stats summary` | Brief summary |
| `stats full` | All statistics |
| `stats detailed` | Stats + event logs |
| `stats combat` | Combat only |
| `stats crew` | Crew only |
| `stats security` | Security only |
| `stats missions` | Missions only |
| `stats help` | This information |

---

## Tips

1. **Check regularly** - After major events, check `stats summary`
2. **Detailed analysis** - After patrol, run `stats detailed`
3. **Post-game review** - Analyze `stats detailed` for improvement areas
4. **Track threats** - Monitor `stats security` for spy/sabotage patterns
5. **Crew health** - Watch `stats crew` to prevent morale collapse

---

*Statistics tracked across all game systems except eldritch encounters.*
*Use data to improve strategy and survive the deep.*
