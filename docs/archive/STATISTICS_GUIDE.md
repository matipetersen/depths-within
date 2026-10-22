# Game Statistics & Tracking Guide

## Overview

The game now includes a comprehensive **statistics system** that tracks all player achievements and events throughout the game. Every significant action—from ships sunk to crew deaths to sabotage attempts—is recorded and available for review.

**Important Note:** Eldritch encounters remain completely secretive and are **NOT** tracked in statistics. Their nature is too mysterious to record.

---

## Tracked Statistics

### Combat Record
- **Ships Sunk**: Total number of enemy vessels destroyed
- **Total Tonnage**: Combined tonnage of all sunk ships
- **Enemy Contacts**: Number of times enemy vessels were detected
- **Torpedoes Fired**: Total torpedoes launched
- **Torpedoes Hit**: Successful torpedo impacts
- **Hit Rate**: Accuracy percentage (calculated)
- **Naval Battles**: Major engagements with warships
- **Convoy Engagements**: Attacks on merchant convoys
- **Successful Escapes**: Times enemy pursuit was evaded

### Crew & Personnel
- **Crew Recruited**: Total crew members hired
- **Crew Deaths**: Casualties during gameplay
- **Crew Injured**: Non-fatal casualties
- **Morale Crises**: Major morale events
- **Stress Incidents**: Individual crew stress reactions

### Defensive Operations
- **Depth Charges Survived**: Successful evasions from depth charge attacks
- **Compartments Flooded**: Hull breaches sustained
- **Repairs Completed**: Damage repairs performed
- **Equipment Failures**: Mechanical breakdowns
- **Supply Shortages**: Critical resource scarcities

### Espionage & Security
- **Spies Caught**: Enemy agents apprehended
- **Sabotages Detected**: Internal sabotage attempts discovered
- **Sabotages Successful**: Sabotage that actually occurred
- **Surface Sightings**: Times detected by surface vessels

### Missions & Objectives
- **Missions Completed**: Successful mission completions
- **Missions Failed**: Failed objectives
- **Successful Patrols**: Completed patrol missions

---

## Statistics Commands

### Quick Summary
```
stats summary
```
Shows a brief overview of your key statistics in one screen.

### Full Report
```
stats full
```
Displays comprehensive statistics across all categories.

### Detailed Report
```
stats detailed
```
Shows full statistics plus event logs including:
- Ships sunk (last 10)
- Crew losses (last 10)
- Apprehended spies (all)
- Sabotage incidents (last 10)
- Mission log (last 10)

### Combat Record
```
stats combat
```
Focuses on combat-related statistics:
- Offensive performance (ships, tonnage, accuracy)
- Defensive performance (escapes, depth charge survival)
- Notable kills (last 3 documented)

### Crew Record
```
stats crew
```
Personnel-focused statistics:
- Recruited crew count
- Deaths and injuries
- Morale crises
- Stress incidents
- Recent losses (last 5)

### Security Record
```
stats security
```
Counterintelligence and sabotage tracking:
- Spies caught
- Sabotages detected vs. successful
- List of apprehended agents
- Sabotage incident timeline

### Mission Record
```
stats missions
```
Mission performance metrics:
- Completed vs. failed missions
- Success rate percentage
- Successful patrols count
- Recent mission log (last 10)

### Help
```
stats help
```
Shows all statistics commands and their descriptions.

---

## Detailed Event Logs

The system maintains detailed logs for critical events:

### Ship Kills Log
Each ship sunk is recorded with:
- Turn number
- Ship type
- Tonnage
- Crew members involved
- Timestamp

### Crew Deaths Log
Each crew death includes:
- Turn number
- Crew member name
- Rank
- Cause of death
- Additional details
- Timestamp

### Spies Apprehended Log
Each captured spy is recorded with:
- Turn number
- Real name
- Cover name/identity
- Apprehension details
- Timestamp

### Sabotage Incidents Log
Each sabotage attempt records:
- Turn number
- Sabotage type
- Status (detected or successful)
- Severity/damage percentage
- Timestamp

### Mission Log
Each mission stores:
- Turn number
- Mission type
- Completion status
- Details or failure reason
- Rewards earned
- Timestamp

---

## Color Coding in Statistics

Statistics use color coding for quick visual assessment:

- **Bright Red**: Critical achievements (ships sunk, crew deaths, successful sabotage)
- **Bright Yellow**: Notable events (spies caught, sabotages detected, tonnage)
- **Bright Green**: Positive outcomes (missions completed, successful escapes, hit rate)
- **Standard Colors**: Neutral information

---

## Session Tracking

Each game session is assigned a unique **Session ID** with format:
```
session_YYYYMMDD_HHMMSS
```

This allows for:
- Session-specific statistics review
- Post-game analysis
- Comparison between playthroughs
- Game session export and archival

---

## Integration with Game Systems

### Crew Deaths
When a crew member dies:
```
stats record_crew_death(turn, name, rank, cause, details)
```

### Ships Sunk
When an enemy vessel is destroyed:
```
stats record_ship_sunk(turn, ship_type, tonnage, crew_involved)
```

### Spies Caught
When a spy is apprehended:
```
stats record_spy_caught(turn, real_name, cover_name, details)
```

### Sabotages Detected
When sabotage is discovered:
```
stats record_sabotage_detected(turn, sabotage_type, severity)
```

### Missions Completed
When a mission objective is achieved:
```
stats record_mission_completed(turn, mission_type, details, rewards)
```

---

## Game Statistics Export

Statistics are automatically saved to:
```
data/statistics/session_YYYYMMDD_HHMMSS.json
```

This JSON file contains:
- Session metadata
- All tracked statistics
- Complete event history
- Detailed logs for all categories

---

## Example Statistics Session

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
  Successful Patrols: 3

SECURITY:
  Spies Caught: 1
  Sabotages Detected: 2
  Sabotages Successful: 0
  Surface Sightings: 4
```

---

## Privacy & Eldritch Secrecy

**Important:** The statistics system intentionally does NOT track:
- Eldritch encounter events
- Mysterious phenomena
- Cosmic horror interactions
- Unexplained occurrences

These remain completely separate from the statistics system. What happens in the deep remains unknowable and unrecorded.

---

## Tips for Statistics Tracking

1. **Regular Checks**: Review your stats regularly to understand game performance
2. **Combat Performance**: Use `stats combat` to optimize your strategy
3. **Crew Management**: Monitor `stats crew` to ensure personnel health
4. **Security**: Watch `stats security` for internal threats
5. **Mission Progress**: Track `stats missions` for objective completion
6. **Detailed Analysis**: Use `stats detailed` for comprehensive post-patrol review

---

## Game Commands Reference

| Command | Effect |
|---------|--------|
| `stats summary` | Brief statistics overview |
| `stats full` | Complete statistics report |
| `stats detailed` | Full report with event logs |
| `stats combat` | Combat-specific statistics |
| `stats crew` | Personnel and morale statistics |
| `stats security` | Espionage and sabotage tracking |
| `stats missions` | Mission completion record |
| `stats help` | Statistics command help |

---

*Statistics system v1.0 - All trackers active except eldritch encounters*
