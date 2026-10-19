"""Event journal system for tracking major gameplay events.

The Journal tracks all significant events during gameplay:
- Mission events (accepted, completed, failed, abandoned)
- Crew events (recruited, assigned, promoted, injured, deceased)
- Combat events (torpedo fired, target hit/missed, ship sunk, damaged)
- World events (weather changes, encounters, discoveries)
- Progression events (level up, upgrade installed, new abilities)
- System events (damage, repairs, malfunctions)

Each event is timestamped with in-game time and tagged for filtering/search.
"""

from enum import Enum
from datetime import datetime


class EventCategory(Enum):
    """Categories for journal events."""
    MISSION = "mission"
    CREW = "crew"
    COMBAT = "combat"
    WORLD = "world"
    PROGRESSION = "progression"
    SYSTEM = "system"
    LORE = "lore"
    OTHER = "other"


class EventSeverity(Enum):
    """Severity levels for events."""
    TRIVIAL = 0  # Low-importance events (crew morale change, minor repairs)
    MINOR = 1  # Minor events (small damage, crew transfers)
    STANDARD = 2  # Normal events (missions, standard combat)
    MAJOR = 3  # Significant events (mission completion, crew death)
    CRITICAL = 4  # Game-changing events (near-sinking, huge rewards)


class JournalEntry:
    """A single journal entry with all metadata."""
    
    def __init__(self, category, title, description, severity=EventSeverity.STANDARD, 
                 turn=0, tags=None, data=None):
        """
        Create a journal entry.
        
        Args:
            category: EventCategory enum value
            title: Short title for the event (20-50 chars)
            description: Full description (1-200 chars)
            severity: EventSeverity enum value
            turn: In-game turn when event occurred
            tags: List of string tags for filtering (e.g., ['mission_10', 'sabotage'])
            data: Dict with additional metadata (mission_id, crew_name, reward, etc)
        """
        self.category = category
        self.title = title
        self.description = description
        self.severity = severity
        self.turn = turn
        self.tags = tags or []
        self.data = data or {}
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return (f"JournalEntry(turn={self.turn}, category={self.category.value}, "
                f"severity={self.severity.name}, title={self.title})")
    
    def to_dict(self):
        """Serialize to dictionary."""
        return {
            'category': self.category.value,
            'title': self.title,
            'description': self.description,
            'severity': self.severity.value,
            'turn': self.turn,
            'tags': self.tags,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }
    
    def format_line(self):
        """Format as single line: [Turn XXX] TITLE - description"""
        return f"[Turn {self.turn:04d}] {self.title} - {self.description}"
    
    def format_detailed(self):
        """Format as multi-line detailed view."""
        lines = [
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Turn {self.turn} | {self.category.value.upper()} | {self.severity.name}",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"{self.title}",
            f"",
            f"{self.description}",
        ]
        if self.tags:
            lines.append(f"\nTags: {', '.join(self.tags)}")
        if self.data:
            lines.append(f"\nDetails:")
            for key, value in self.data.items():
                lines.append(f"  • {key}: {value}")
        return "\n".join(lines)


class Journal:
    """Main journal manager for tracking all gameplay events."""
    
    def __init__(self, max_entries=500):
        """
        Initialize journal.
        
        Args:
            max_entries: Maximum entries to keep (older entries removed when exceeded)
        """
        self.entries = []
        self.max_entries = max_entries
        self.statistics = {
            'total_events': 0,
            'events_by_category': {},
            'events_by_severity': {},
            'first_entry_turn': None,
            'last_entry_turn': None,
        }
    
    def log_event(self, category, title, description, severity=EventSeverity.STANDARD,
                  turn=0, tags=None, data=None):
        """
        Log a new journal entry.
        
        Args:
            category: EventCategory enum value
            title: Short title
            description: Full description
            severity: EventSeverity enum value
            turn: In-game turn
            tags: List of tags
            data: Additional metadata dict
        
        Returns:
            The created JournalEntry
        """
        entry = JournalEntry(category, title, description, severity, turn, tags, data)
        self.entries.append(entry)
        
        # Update statistics
        self.statistics['total_events'] += 1
        cat_key = category.value
        sev_key = severity.name
        self.statistics['events_by_category'][cat_key] = \
            self.statistics['events_by_category'].get(cat_key, 0) + 1
        self.statistics['events_by_severity'][sev_key] = \
            self.statistics['events_by_severity'].get(sev_key, 0) + 1
        
        if self.statistics['first_entry_turn'] is None:
            self.statistics['first_entry_turn'] = turn
        self.statistics['last_entry_turn'] = turn
        
        # Trim if over limit
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)
        
        return entry
    
    def get_entries(self, category=None, severity=None, tag=None, limit=None):
        """
        Retrieve entries with optional filtering.
        
        Args:
            category: Filter by EventCategory (or None for all)
            severity: Filter by EventSeverity (or None for all)
            tag: Filter by tag string (or None for all)
            limit: Maximum entries to return (or None for all)
        
        Returns:
            List of JournalEntry objects matching criteria
        """
        results = self.entries[:]
        
        if category:
            results = [e for e in results if e.category == category]
        
        if severity:
            results = [e for e in results if e.severity == severity]
        
        if tag:
            results = [e for e in results if tag in e.tags]
        
        if limit:
            results = results[-limit:]  # Get last N entries
        
        return results
    
    def get_entries_by_turn_range(self, start_turn, end_turn):
        """Get entries within turn range (inclusive)."""
        return [e for e in self.entries if start_turn <= e.turn <= end_turn]
    
    def search(self, query):
        """
        Search journal entries by title or description.
        
        Args:
            query: Search string (case-insensitive)
        
        Returns:
            List of matching JournalEntry objects
        """
        query_lower = query.lower()
        return [e for e in self.entries 
                if query_lower in e.title.lower() or query_lower in e.description.lower()]
    
    def get_mission_events(self, mission_id):
        """Get all events related to a specific mission."""
        return self.get_entries(tag=f'mission_{mission_id}')
    
    def get_crew_events(self, crew_name):
        """Get all events related to a specific crew member."""
        return self.get_entries(tag=f'crew_{crew_name}')
    
    def get_last_entries(self, count=10):
        """Get the last N entries."""
        return self.entries[-count:] if self.entries else []
    
    def get_recent_summary(self, count=5):
        """Get formatted summary of last N entries."""
        recent = self.get_last_entries(count)
        if not recent:
            return "No events recorded yet."
        
        lines = [f"Recent Events (Last {count}):"]
        lines.append("─" * 50)
        for entry in recent:
            lines.append(entry.format_line())
        return "\n".join(lines)
    
    def get_statistics(self):
        """Get journal statistics."""
        return self.statistics.copy()
    
    def clear(self):
        """Clear all entries (dangerous!)."""
        self.entries.clear()
        self.statistics = {
            'total_events': 0,
            'events_by_category': {},
            'events_by_severity': {},
            'first_entry_turn': None,
            'last_entry_turn': None,
        }
    
    def to_dict(self):
        """Serialize journal to dictionary."""
        return {
            'entries': [e.to_dict() for e in self.entries],
            'statistics': self.statistics,
            'max_entries': self.max_entries,
        }
    
    def __len__(self):
        return len(self.entries)
    
    def __repr__(self):
        return f"Journal({len(self.entries)} entries)"


# Quick helper methods for common event types

def create_mission_event(journal, mission_name, event_type, turn, mission_id=None, 
                         reward_xp=0, reward_credits=0):
    """Create a mission-related journal event."""
    severity_map = {
        'accepted': EventSeverity.STANDARD,
        'completed': EventSeverity.MAJOR,
        'failed': EventSeverity.MAJOR,
        'abandoned': EventSeverity.MINOR,
    }
    
    title_map = {
        'accepted': f"Mission: {mission_name}",
        'completed': f"✓ {mission_name} Complete",
        'failed': f"✗ {mission_name} Failed",
        'abandoned': f"~ {mission_name} Abandoned",
    }
    
    description_map = {
        'accepted': f"Started mission: {mission_name}",
        'completed': f"Successfully completed {mission_name}. Earned {reward_xp} XP and {reward_credits} credits.",
        'failed': f"Failed mission: {mission_name}",
        'abandoned': f"Abandoned mission: {mission_name}",
    }
    
    tags = ['mission']
    if mission_id:
        tags.append(f'mission_{mission_id}')
    
    return journal.log_event(
        category=EventCategory.MISSION,
        title=title_map.get(event_type, f"Mission: {mission_name}"),
        description=description_map.get(event_type, f"Mission event: {mission_name}"),
        severity=severity_map.get(event_type, EventSeverity.STANDARD),
        turn=turn,
        tags=tags,
        data={'mission_name': mission_name, 'event_type': event_type, 
              'reward_xp': reward_xp, 'reward_credits': reward_credits}
    )


def create_crew_event(journal, crew_name, event_type, turn, details=None):
    """Create a crew-related journal event."""
    severity_map = {
        'recruited': EventSeverity.MINOR,
        'assigned': EventSeverity.MINOR,
        'promoted': EventSeverity.MAJOR,
        'injured': EventSeverity.MAJOR,
        'deceased': EventSeverity.CRITICAL,
        'reassigned': EventSeverity.MINOR,
    }
    
    title_map = {
        'recruited': f"New Crew: {crew_name}",
        'assigned': f"{crew_name} Assigned",
        'promoted': f"{crew_name} Promoted",
        'injured': f"{crew_name} Injured",
        'deceased': f"{crew_name} Deceased",
        'reassigned': f"{crew_name} Reassigned",
    }
    
    description_map = {
        'recruited': f"Recruited new crew member: {crew_name}",
        'assigned': f"{crew_name} assigned to compartment",
        'promoted': f"{crew_name} received promotion",
        'injured': f"{crew_name} suffered injuries",
        'deceased': f"{crew_name} has been lost",
        'reassigned': f"{crew_name} reassigned to new duties",
    }
    
    return journal.log_event(
        category=EventCategory.CREW,
        title=title_map.get(event_type, f"Crew: {crew_name}"),
        description=description_map.get(event_type, f"Crew event for {crew_name}"),
        severity=severity_map.get(event_type, EventSeverity.STANDARD),
        turn=turn,
        tags=['crew', f'crew_{crew_name}'],
        data={'crew_name': crew_name, 'event_type': event_type, 'details': details or {}}
    )


def create_combat_event(journal, event_type, turn, target=None, damage=0, xp_reward=0):
    """Create a combat-related journal event."""
    severity_map = {
        'torpedo_fired': EventSeverity.MINOR,
        'hit': EventSeverity.MAJOR,
        'miss': EventSeverity.MINOR,
        'damaged': EventSeverity.CRITICAL,
        'sinking': EventSeverity.CRITICAL,
        'destroyed': EventSeverity.CRITICAL,
    }
    
    title_map = {
        'torpedo_fired': "Torpedo Fired",
        'hit': f"Direct Hit: {target}",
        'miss': "Torpedo Miss",
        'damaged': f"Took Damage",
        'sinking': f"Enemy Sinking",
        'destroyed': f"Enemy Destroyed",
    }
    
    return journal.log_event(
        category=EventCategory.COMBAT,
        title=title_map.get(event_type, "Combat Event"),
        description=f"{event_type.replace('_', ' ').title()}: {target}" if target else event_type,
        severity=severity_map.get(event_type, EventSeverity.STANDARD),
        turn=turn,
        tags=['combat', f'combat_{event_type}'],
        data={'event_type': event_type, 'target': target, 'damage': damage, 'xp_reward': xp_reward}
    )


def create_progression_event(journal, event_type, turn, details=None):
    """Create a progression-related journal event."""
    severity_map = {
        'level_up': EventSeverity.MAJOR,
        'upgrade_installed': EventSeverity.MAJOR,
        'new_ability': EventSeverity.MAJOR,
        'milestone': EventSeverity.MAJOR,
    }
    
    title_map = {
        'level_up': "Level Up!",
        'upgrade_installed': "Upgrade Installed",
        'new_ability': "New Ability Unlocked",
        'milestone': "Milestone Achieved",
    }
    
    return journal.log_event(
        category=EventCategory.PROGRESSION,
        title=title_map.get(event_type, "Progression Event"),
        description=details or event_type.replace('_', ' ').title(),
        severity=severity_map.get(event_type, EventSeverity.STANDARD),
        turn=turn,
        tags=['progression', f'progression_{event_type}'],
        data={'event_type': event_type, 'details': details}
    )
