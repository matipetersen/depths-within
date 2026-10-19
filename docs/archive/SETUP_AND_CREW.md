# Setup Screen & Crew System

## Recent Updates (December 2024)

### ✅ Fixed Issues
1. **Persistent Rendering** - Screen no longer multiplies when turns pass
   - Renders only when turn number changes
   - Clean ANSI-based display updates in place
   - Proper cursor management

2. **Initial Crew** - Submarine now starts with crew members
   - 20 crew members assigned at game start
   - Distributed across all 6 compartments
   - Visible in compartment map display

3. **Setup Screen** - Interactive faction and crew selection
   - Choose from 5 playable factions (Germany, USA, UK, Japan, Italy)
   - Randomly generated crew with skills and traits
   - Re-roll option for different crew roster

## How to Run

### Interactive Setup (Recommended)
```bash
python main.py
```
- Use ↑/↓ arrow keys to select faction
- Press ENTER to confirm
- View generated crew roster
- Press R to re-roll crew or ENTER to start

### Quick Start (Skip Setup)
```bash
python main.py --quick
# or
python main.py --skip-setup
```
- Immediately starts with German submarine
- Auto-generates 20 crew members
- Skips interactive screens

## Crew System

### Starting Roster
- **20 crew members** total
- **Command Staff** (5):
  - Commander (specialization: navigation)
  - Executive Officer (specialization: torpedoes)
  - Chief Engineer (specialization: engineering)
  - Sonar Operator (specialization: sonar)
  - Medical Officer (specialization: medical)
- **Regular Crew** (15):
  - Seamen with various specializations

### Skills
Each crew member has skills in 5 categories (0.0-1.0):
- **Sonar** - Detecting enemy vessels
- **Torpedoes** - Accuracy and reload speed
- **Navigation** - Course plotting and maneuvering
- **Engineering** - Repairs and system maintenance
- **Medical** - Treating injuries and maintaining health

### Traits
Random personality traits affecting behavior:
- **Brave** - Better under pressure, bonus to combat skills
- **Cautious** - Careful decision-making, lower stress
- **Calm** - Stress-resistant
- **Hotheaded** - Quick reactions but higher stress
- **Methodical** - Systematic approach, steady performance
- **Quick** - Fast skill checks, good in emergencies

### Compartment Assignment
Crew automatically distributed across 6 compartments:
- Conning Tower (3 crew)
- Control Room (3 crew)
- Torpedo Room (3 crew)
- Engine Room (3 crew)
- Crew Quarters (3 crew)
- Battery Room (5 crew)

## Viewing Crew

### Compartment Map
```
In-game command: map, cm, comp_map, compartment_map
```
Shows:
- All 6 compartments in visual layout
- Crew count per compartment
- Crew names (abbreviated)
- Integrity and flooding status
- Color-coded warnings

### Tactical View
Compartment status bar always visible at bottom:
```
═ COMPARTMENTS ═  ◉ CON(3) │ ◉ CTR(3) │ ◉ TOR(3) │ ◉ ENG(3) │ ◉ CRE(3) │ ◉ BAT(5)
```
- Status symbols indicate damage/flooding
- Numbers in parentheses = crew count
- Issues line shows critical problems

## Status Indicators

### Damage Levels
- ◉ **Operational** (80-100% integrity) - Green
- ◑ **Minor Damage** (60-80% integrity) - Yellow
- ◐ **Moderate Damage** (40-60% integrity) - Yellow/Red
- ✕ **Heavy Damage** (<40% integrity) - Red

### Flooding Levels
- · **No Flooding** (0-10%) - Green
- ~ **Minor Flooding** (10-30%) - Yellow
- ≈ **Moderate Flooding** (30-50%) - Red
- ⚠ **Critical Flooding** (>50%) - Dark Red

## Faction Options

### Axis Powers
1. **Germany (Kriegsmarine)**
   - Advanced submarine technology
   - Wolf pack tactics
   - Atlantic operations

2. **Japan (Imperial Japanese Navy)**
   - Long-range submarines
   - Pacific theater
   - Reconnaissance focus

3. **Italy (Regia Marina)**
   - Mediterranean operations
   - Moderate submarine force

### Allied Powers
4. **USA (United States Navy)**
   - Industrial powerhouse
   - Advanced torpedoes
   - Pacific campaign

5. **UK (Royal Navy)**
   - Large escort fleet
   - ASW expertise
   - Global operations

## Files Modified

### New Files
- `ui/setup_screen.py` - Interactive setup interface
- `data/crew_names.json` - Faction-specific crew names (expanded)

### Modified Files
- `main.py` - Added setup screen integration
- `engine/game.py` - Added `initialize_from_setup()` method
- `ui/persistent_renderer.py` - Fixed rendering logic to prevent multiplication
- `ui/compartment_map.py` - Crew display integration
- `ui/tactical_display.py` - Compartment status bar with crew counts

## Technical Details

### Persistent Rendering
The renderer tracks the current turn and only updates the screen when the turn changes:
```python
def render(self, game):
    current_turn = getattr(game, 'turn', 0)
    if current_turn != self.last_turn or self.render_count == 0:
        self.screen_manager.render_game_persistent(game)
        self.last_turn = current_turn
        return True
    return False
```

This prevents the screen from printing multiple times per turn, eliminating the scrolling/multiplication issue.

### Crew Distribution
Crew are evenly distributed across compartments during initialization:
```python
crew_per_compartment = len(crew) // len(compartments)
for i, compartment in enumerate(compartments):
    start_idx = i * crew_per_compartment
    end_idx = start_idx + crew_per_compartment
    if i == len(compartments) - 1:  # Last compartment gets remainder
        end_idx = len(crew)
    compartment.crew = crew[start_idx:end_idx]
```

## Future Enhancements

Potential features for crew system:
- [ ] Manual crew reassignment between compartments
- [ ] Crew experience and skill progression
- [ ] Morale and stress management
- [ ] Crew casualties and replacement
- [ ] Special crew abilities and perks
- [ ] Crew interactions and relationships
- [ ] Historical crew members option

## Troubleshooting

### Setup screen not appearing
- Check that `main.py` was updated correctly
- Try running with `--quick` flag to bypass

### Crew not showing in compartments
- Verify `initialize_from_setup()` was called
- Check submarine has `crew` and `compartments` attributes

### Screen still multiplying
- Ensure `persistent_renderer.py` was updated
- Check that game loop only calls `_tick()` once per command
- Verify renderer checks turn number before rendering

## Testing

Run validation tests:
```bash
python -c "
from ui.setup_screen import quick_setup
from engine.game import Game

faction, crew = quick_setup('Germany')
game = Game()
game.initialize_from_setup(faction, crew)
print(f'✅ Faction: {faction[\"name\"]}')
print(f'✅ Crew: {len(crew)} members')
print(f'✅ Compartments: {len(game.submarine.compartments)}')
"
```

---

**Status**: ✅ All systems operational  
**Last Updated**: December 2024  
**Version**: 1.0
