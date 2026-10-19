# Phase 13 Quick Reference

## What's New

### Journal System ✅
- Log all gameplay events (missions, crew, combat, etc.)
- 5 console commands for journal access
- Full-text search and filtering
- Career statistics tracking

### Graphics System ✅
- Multi-backend rendering (tilesheet, tcod, ASCII)
- 64-tile submarine tileset
- Sonar display with ASCII rendering
- Auto-detection of available graphics

---

## Console Commands

| Command | Usage | Example |
|---------|-------|---------|
| `journal` | Show recent 10 events | `> journal` |
| `log_search` | Search journal | `> log_search cargo` |
| `log_category` | Filter by category | `> log_category mission` |
| `log_stats` | Show statistics | `> log_stats` |
| `log_detail` | Show last event in detail | `> log_detail` |

---

## Journal Categories

- **mission** - Quest events (accept, complete, fail, abandon)
- **crew** - Crew management (recruit, assign, promote, injured, death)
- **combat** - Battle events (torpedo fired, hit, miss, sinking)
- **world** - Environmental events
- **progression** - Skill/upgrade gains
- **system** - Submarine status changes
- **lore** - Story/narrative events
- **other** - Miscellaneous

---

## Code Usage

### Log a Mission Event
```python
from engine.journal import create_mission_event

create_mission_event(
    journal=game.journal,
    mission_name="Cargo Smuggle",
    event_type="completed",  # accepted, completed, failed, abandoned
    turn=game.turn,
    mission_id=1,
    reward_xp=250,
    reward_credits=5000
)
```

### Query Journal
```python
# Get recent events
recent = game.journal.get_last_entries(10)

# Filter by category
missions = game.journal.get_entries(category=EventCategory.MISSION)

# Search
results = game.journal.search("torpedo")

# Statistics
stats = game.journal.get_statistics()
```

### Check Graphics
```python
from ui.graphics import GraphicsRenderer

renderer = GraphicsRenderer()
backend = renderer.get_render_backend()  # tilesheet, tcod_fallback, ascii_console

if renderer.has_tilesheet():
    print("Pixel graphics available!")
```

---

## Files Changed

### New Files
- `engine/journal.py` - Event journal system (520 lines)
- `ui/graphics.py` - Graphics rendering (280 lines)
- `tests/test_journal.py` - Journal tests (450 lines)
- `tests/test_graphics.py` - Graphics tests (130 lines)

### Modified Files
- `engine/game.py` - Added journal + commands
- `assets/tilesets/atlas.json` - Expanded to 64 tiles

### Documentation
- `PHASE_13_SUMMARY.md` - Technical details
- `PHASE_13_COMPLETE.md` - Full summary
- `JOURNAL_GUIDE.md` - User & dev guide

---

## Test Status

✅ **98/98 tests passing** (100% pass rate)
- Journal tests: 34/34 ✓
- Graphics tests: 15/15 ✓
- Other tests: 49/49 ✓

---

## Key Features

### Journal
- Event timestamps with in-game turns
- 8 event categories
- 5 severity levels
- Full-text search
- Career statistics
- Per-mission tracking
- Per-crew tracking

### Graphics
- Multi-backend support
- 64-tile tileset
- Automatic fallback
- Sonar display rendering
- Extensible architecture

---

## Next Steps

1. **Try the console:** `> help` to see all commands
2. **Log events:** Use mission/crew system to generate events
3. **Query journal:** `> journal` to see logged events
4. **Check graphics:** Rendering happens automatically
5. **Explore:** `> log_search`, `> log_category`, `> log_stats`

---

## Tips & Tricks

### Performance
- Journal handles 500+ events easily
- Graphics auto-detects best backend
- Search is O(n) - use categories for large journals

### Development
- Add logging to any new game system
- Use helper functions (create_mission_event, etc.)
- Tags enable easy filtering

### Graphics
- Tileset is at `assets/tilesets/modern_tileset.png`
- Atlas mapping in `assets/tilesets/atlas.json`
- 64 tiles available for future features

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Journal not working? | Check `game.journal` exists and is not None |
| Search finds nothing? | Try `log_stats` to verify events exist |
| Graphics wrong? | Run in ASCII mode to verify rendering |
| Commands not listed? | Type `help` to see all available commands |

---

## Documentation Files

- **PHASE_13_SUMMARY.md** - Technical deep dive
- **PHASE_13_COMPLETE.md** - Full implementation summary
- **JOURNAL_GUIDE.md** - Complete user & developer guide
- **QUICK_REFERENCE.md** - This file

---

**Phase 13 Status: ✅ COMPLETE**
- 1,460+ lines of code
- 98/98 tests passing
- Ready for Phase 14!
