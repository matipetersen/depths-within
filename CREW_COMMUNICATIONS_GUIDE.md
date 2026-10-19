# Crew Communications System Guide

## Overview
The game now features a **crew communications system** (`engine/crew_communications.py`) that adds personality and immersion through:
- **Random crew thoughts** reflecting emotional states
- **Contextual conversations** between crew members
- **Cooldown management** to prevent dialogue spam

## System Components

### 1. CrewThought Class
Manages random thoughts crew members have based on their emotional state.

#### Thought Categories (8 types)
Each category contains themed thoughts:

| Category | Context | Examples |
|----------|---------|----------|
| **ANXIOUS** | Danger/uncertainty | "What if we don't make it?", "I hope the captain knows what he's doing..." |
| **CALM** | Normal operations | "Just another day on patrol", "The engines are running smoothly" |
| **STRESSED** | High pressure | "This is too much!", "I can't take this anymore!" |
| **HAPPY** | Victory/success | "We did it!", "That was incredible!" |
| **COMBAT** | Battle situations | "Enemy contact!", "All hands to battle stations!" |
| **DAMAGE** | Critical situations | "The hull won't take much more!", "We're going down!" |
| **SUPPLIES** | Resource concerns | "Are we going to run out of food?", "Fuel is getting low..." |
| **BOREDOM** | Routine patrol | "When will something interesting happen?", "Same old, same old..." |

### 2. CrewDialogue Class
Manages realistic conversations between crew members.

#### Dialogue Types (8 types)
Each type represents realistic naval conversations:

| Type | Topics | Examples |
|------|--------|----------|
| **SUB** | About the submarine | "How's the engine room?", "The periscope is acting up" |
| **WAR** | About WWII/mission | "Think we'll see action today?", "The Germans won't know what hit them" |
| **FOOD** | About eating | "What's for chow?", "I could murder a steak" |
| **MORALE** | About crew morale | "Morale seems high today", "The crew's spirits are up" |
| **FEAR** | About dangers | "Depth charges scare me", "What if we get trapped?" |
| **HOME** | About family/home | "I miss my wife", "Can't wait to get back to port" |
| **VICTORY** | About successes | "That was our best patrol yet!", "We sank three ships!" |
| **TENSION** | About battle/danger | "This is it, we're under attack!", "Hold on, incoming!" |

## Usage

### Triggering Random Thoughts
```python
from engine.crew_communications import get_communication_manager

comm_manager = get_communication_manager()

# Get a random thought for a crew member
thought = comm_manager.trigger_random_thought(
    crew_member=crew_obj,
    stress=0.8,  # Stress level (0.0-1.0)
    morale=0.5,  # Morale level (0.0-1.0)
    context='combat'  # One of: anxious, calm, stressed, happy, combat, damage, supplies, boredom
)

if thought:
    print(f"Crew thought: {thought}")
    # Output: "Crew thought: We need to destroy that enemy destroyer!"
```

### Triggering Conversations
```python
# Get a random dialogue between crew members
dialogue = comm_manager.trigger_conversation(
    context='sub'  # One of: sub, war, food, morale, fear, home, victory, danger
)

if dialogue:
    print(f"Crew: {dialogue}")
    # Output: "Crew: Chief Peterson, how are the engines holding up?"
```

### Convenience Functions
```python
from engine.crew_communications import trigger_crew_thought, trigger_crew_dialogue

# Quick access functions
trigger_crew_thought(crew_member, stress=0.5, morale=0.7, context='calm')
trigger_crew_dialogue(context='war')
```

### Getting Recent Communications
```python
# Get last 20 communications
recent = comm_manager.get_recent_communications(limit=20)
for comm in recent:
    print(comm)
```

## Integration with Game Loop

The crew communications system is integrated into `engine/game.py` and triggers during each game tick:

### In _tick() Method
```python
# ~10% chance per tick for random thoughts
# ~3% chance per tick for conversations
# Contextual: thoughts/dialogue change based on game state
```

#### Game State Contexts
- **calm**: During safe, patrol conditions
- **combat**: When tactical_map has enemy contacts
- **stressed**: When crew stress is high (>0.7)
- **happy**: When crew morale is high (>0.7)
- **damage**: During critical situations
- **supplies**: When supply inventory is low

### Thought Selection Algorithm
The system chooses thought categories based on crew state:

```
if crew_stress > 0.7:
    Use STRESSED or DAMAGE thoughts
elif crew_morale > 0.7:
    Use HAPPY or CALM thoughts
elif game_state == "combat":
    Use COMBAT thoughts
elif supplies_low:
    Use SUPPLIES thoughts
else:
    Use contextual thoughts (ANXIOUS, CALM, etc.)
```

## Color Integration

All crew communications are displayed with appropriate colors:

```python
from ui.color_system import _color_system

# Thoughts are colored based on emotional state
thought = _color_system.crew_thought("I wonder what's out there...")
stressed_thought = _color_system.crew_stressed("This is too much!")
happy_thought = _color_system.crew_happy("We did it!")
```

## Cooldown System

The system prevents dialogue spam with intelligent cooldowns:

- **Thoughts**: 3-8 turn cooldown between thoughts
- **Conversations**: 10-20 turn cooldown between conversations
- **Per-crew**: Individual cooldowns for each crew member

This ensures:
- Dialogue feels organic, not repetitive
- Game log isn't flooded with messages
- Each thought/dialogue is impactful

## Examples in Gameplay

### During Normal Patrol
```
Turn 145: Crew thought: "Just another day on patrol"
Turn 156: Crew: "Think we'll see action today?"
Turn 223: Crew: "The engines are running smoothly"
Turn 245: Crew thought: "When will something interesting happen?"
```

### During Combat
```
Turn 450: Crew thought: "Enemy contact!"
Turn 451: Crew: "All hands to battle stations!"
Turn 452: Crew thought: "We need to destroy that destroyer!"
Turn 453: Crew: [Sonar operator's perspective on the situation]
```

### During Crisis
```
Turn 890: Crew thought: "The hull won't take much more!"
Turn 891: Crew: "We're going down!"
Turn 892: Crew thought: "Hull integrity critical!"
Turn 893: Crew: "Emergency repairs to all compartments!"
```

### During Victory
```
Turn 1200: Crew thought: "We did it!"
Turn 1210: Crew: "That was our best patrol yet!"
Turn 1220: Crew thought: "I can't believe we pulled that off!"
```

## Customization

### Adding New Thoughts
Edit `engine/crew_communications.py`:

```python
ANXIOUS_THOUGHTS = [
    "What if we don't make it?",
    "I hope the captain knows what he's doing...",
    # Add new thoughts here
    "Are we safe down here?"
]
```

### Adding New Dialogue Types
```python
class CrewDialogue:
    CUSTOM_CONVERSATIONS = [
        ("Officer", "Sailor", "What's your assessment?"),
        ("Sailor", "Officer", "Everything looks good, sir!"),
        # Add new conversation pairs
    ]
```

### Adjusting Trigger Probabilities
In `engine/game.py`, modify the _tick() method:

```python
# Increase thought frequency (default 0.1 = 10%)
if random.random() < 0.15:  # 15% chance per tick
    trigger_random_thought(...)

# Increase conversation frequency (default 0.03 = 3%)
if random.random() < 0.05:  # 5% chance per tick
    trigger_conversation(...)
```

## Performance Notes

- **Lightweight**: Minimal CPU overhead
- **Memory efficient**: Reuses global manager instance
- **No file I/O**: All data in memory
- **Smart cooldowns**: Prevents excessive computation

## Log Display

All communications are logged through `engine/logger.py`:

```
[Turn 145] Crew thought: "I wonder what's out there..."
[Turn 156] Crew: "How's the engine room?"
[Turn 223] Crew: "Chief Peterson, all clear on sonar"
```

Colors applied automatically via ColorSystem integration.

## Testing

Crew communications can be tested independently:

```python
from engine.crew_communications import CrewThought, CrewDialogue

# Test thought generation
thought = CrewThought.get_thought_for_state(
    stress=0.8, morale=0.3, context='combat'
)
assert thought is not None

# Test dialogue generation
dialogue = CrewDialogue.get_dialogue_for_context('war')
assert dialogue is not None
```

## Interaction with Crew Management

The system works with the crew management system:

```python
from engine.crew_management import CrewManagementUI

# Crew stress levels affect thought selection
# Crew morale levels affect dialogue tone
# System respects crew assignment and compartment data
```

## Future Enhancements

Possible additions:
- Crew personality-based thought variations
- Specific dialogue based on crew roles/specialties
- Branching conversations with choices
- Crew bonding through shared experiences
- Morale-boosting dialogue chains
- Crisis-specific emergency procedures
- Multiple language support
- Historical radio intercepts/reports
- Psychological state progression
- Crew relationships and conflicts

## Debugging

Check if communications are triggering:

```python
from engine.crew_communications import get_communication_manager

comm_manager = get_communication_manager()

# Get recent communications
recents = comm_manager.get_recent_communications(limit=10)
if not recents:
    print("No recent communications")
else:
    print("Recent communications:")
    for comm in recents:
        print(f"  - {comm}")
```

Check cooldowns:

```python
# Verify cooldown system is working
print(f"Recent thoughts: {len(comm_manager.recent_thoughts)}")
print(f"Recent conversations: {len(comm_manager.recent_conversations)}")
```
