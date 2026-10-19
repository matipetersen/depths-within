# Phase 13.5 Quick Reference: Crew Loyalty System

## 🎯 What Was Added

A complete crew loyalty, rebellion, and war ranking system with 60 new tests and 7 console commands.

**Files Modified/Created:**
- `engine/crew_loyalty.py` (496 lines) - NEW
- `engine/game.py` (+120 lines) - MODIFIED for console commands
- `tests/test_crew_loyalty.py` (305 lines) - NEW
- `tests/test_crew_loyalty_console.py` (228 lines) - NEW
- `docs/CREW_LOYALTY_GUIDE.md` (780 lines) - NEW

## 📊 Test Results
✅ **158/158 tests passing (100%)**
- Phase 13: 98 tests (journal + graphics)
- Phase 13.5: 60 tests (43 crew loyalty + 17 console)
- Others: 0 broken from integration

## 🎮 Console Commands

| Command | Alias | Purpose |
|---------|-------|---------|
| `crew_loyalty` | `crew_status` | Show all crew morale summary |
| `crew_morale` | `morale` | Show average morale with warnings |
| `rebellion_check` | `rebellion_status` | Show high-risk crew members |
| `crew_loyalty_detail <id>` | - | Show detailed stats for crew member |
| `war_status` | `war_stats` | Show current war statistics |
| `end_war` | `complete_war`, `surrender` | End war and get final rank |

## 🔑 Core Classes

### LoyaltyTracker
Per-crew member tracking with stress, personality, and achievements.

```python
tracker = LoyaltyTracker(crew_id=1, crew_name="John", personality="brave")
tracker.loyalty  # 0.0-1.0
tracker.get_status()  # LOYAL, CONTENT, DISSATISFIED, MUTINOUS, DESERTER
tracker.apply_stress(fear=0.2, hunger=0.1, exhaustion=0.3)
tracker.record_achievement('mission_completed', turn=50)
tracker.get_rebellion_risk()  # 0.0-1.0
```

### RebellionManager
Manages all crew, checks for rebellions, applies events.

```python
manager = RebellionManager()
manager.add_crew_member(1, "John", "brave")
manager.get_crew_morale()  # 0.0-1.0 average
manager.check_all_rebellions(turn=100)  # Check for rebellions
manager.apply_crew_event('combat_victory')  # Event to all crew
```

### WarEndgameStats
Track war achievements and calculate final rank/score.

```python
stats = WarEndgameStats()
stats.enemy_ships_destroyed = 75
stats.capital_ships_sunk = 3
stats.survivors_rescued = 100
rank = stats.calculate_war_rank()  # Returns WarRank enum
score = stats.calculate_final_score()  # Returns int
report = stats.get_final_report()  # Returns formatted string
```

## 🎖️ War Ranks

1. **CIVILIAN** - 0 kills
2. **RECRUIT** - 1-4 kills
3. **SAILOR** - 5-9 kills
4. **VETERAN** - 10-24 kills
5. **SUBMARINE_ACE** - 25-49 kills
6. **CAPITAL_SHIP_KILLER** - 5+ capital ships
7. **LEGENDARY_COMMANDER** - 50+ kills + perfect loyalty

## 🔴 Rebellion Types (Escalating)

| Type | Severity | Trigger |
|------|----------|---------|
| MINOR_COMPLAINT | 5% | Risk < 0.3 |
| WORK_SLOWDOWN | 20% | Risk 0.3-0.5 |
| REFUSAL_TO_OBEY | 45% | Risk 0.5-0.7 |
| MUTINY | 70% | Risk 0.7-0.85 |
| MASS_DESERTION | 90% | Risk > 0.85 |

## 💪 Stress Factors

Each crew member has 3 stress levels (0-1.0):
- **Fear:** Combat danger, near-death experiences
- **Hunger:** Lack of supplies, food shortages
- **Exhaustion:** Fatigue from long operations

Stress increases rebellion risk. Higher stress = higher chance of rebellion.

## 🎭 Personality Types

- **Brave:** -10% rebellion risk (loyal)
- **Cautious:** +5% rebellion risk
- **Calm:** -5% rebellion risk
- **Aggressive:** +15% rebellion risk (prone to mutiny)
- **Disciplined:** -15% rebellion risk (most loyal)
- **Curious:** +5% rebellion risk (restless)

## 📈 Scoring Calculation

```python
score = (
    kills * 10 +
    capital_ships * 25 +
    survivors_rescued * 50 +
    (loyalty > 0.8) * 500 +    # Perfect loyalty bonus
    war_victory * 2000 +        # Victory bonus
    crew_morale_bonus
)
```

## 🎯 Game Integration Points

In your `_tick()` or game loop:

```python
# Check for rebellions each turn
rebellions = self.rebellion_manager.check_all_rebellions(self.turn)

# Apply crew events on game events
self.rebellion_manager.apply_crew_event('combat_victory')

# Track combat achievements
self.war_endgame.enemy_ships_destroyed += 1
self.war_endgame.capital_ships_sunk += 1 if is_capital else 0

# End war when needed
if game_over:
    self.war_endgame.crew_alive_at_end = len(active_crew)
    report = self.war_endgame.get_final_report()
```

## 🧪 Testing

All systems tested with 60 comprehensive tests:

```bash
# Run crew loyalty tests
pytest tests/test_crew_loyalty.py -v

# Run console integration tests  
pytest tests/test_crew_loyalty_console.py -v

# Run all tests
pytest tests/ -q
```

Result: **158/158 passing (100%)**

## 📚 Documentation

Complete guide available in: `docs/CREW_LOYALTY_GUIDE.md`

Topics covered:
- API documentation
- Console command reference
- Example usage scenarios
- Integration recommendations
- Design decisions
- Future enhancement ideas

## 🚀 Quick Start

1. System is auto-initialized when game starts
2. Use console commands to monitor crew
3. Check `crew_morale` before dangerous missions
4. Use `crew_loyalty_detail` to find problem crew
5. Run `end_war` when mission complete for ranking

## ⚙️ Configuration Notes

- Personalities are randomly assigned to crew
- Rebellion types escalate automatically based on risk
- Morale affects all crew equally with modifier
- Stress accumulates over time (manual relief needed)
- War rank calculated based on total achievements
- Crew loyalties persist throughout war

## 🔗 Related Systems

Works alongside:
- Journal system (Phase 13) - Logs crew events
- Graphics system (Phase 13) - Can display crew status
- Quest system - Can trigger loyalty events
- Crew recruitment - Manages crew roster
- Submarine systems - Crew interact with compartments

---

**Version:** Phase 13.5
**Status:** Complete ✅
**Tests Passing:** 158/158 (100%)
**Documentation:** Complete
