"""Tests for event journal system."""

import pytest
from engine.journal import (
    Journal, JournalEntry, EventCategory, EventSeverity,
    create_mission_event, create_crew_event, create_combat_event, create_progression_event
)


class TestEventSeverity:
    """Test severity enum."""
    
    def test_severity_values(self):
        assert EventSeverity.TRIVIAL.value == 0
        assert EventSeverity.MINOR.value == 1
        assert EventSeverity.STANDARD.value == 2
        assert EventSeverity.MAJOR.value == 3
        assert EventSeverity.CRITICAL.value == 4
    
    def test_severity_ordering(self):
        severities = [
            EventSeverity.TRIVIAL,
            EventSeverity.MINOR,
            EventSeverity.STANDARD,
            EventSeverity.MAJOR,
            EventSeverity.CRITICAL,
        ]
        values = [s.value for s in severities]
        assert values == sorted(values)


class TestEventCategory:
    """Test category enum."""
    
    def test_all_categories_exist(self):
        categories = [
            EventCategory.MISSION,
            EventCategory.CREW,
            EventCategory.COMBAT,
            EventCategory.WORLD,
            EventCategory.PROGRESSION,
            EventCategory.SYSTEM,
            EventCategory.LORE,
            EventCategory.OTHER,
        ]
        assert len(categories) == 8


class TestJournalEntry:
    """Test individual journal entries."""
    
    def test_entry_creation(self):
        entry = JournalEntry(
            category=EventCategory.MISSION,
            title="Test Mission",
            description="This is a test mission event",
            severity=EventSeverity.STANDARD,
            turn=10,
            tags=['test', 'mission_1'],
            data={'mission_id': 1}
        )
        
        assert entry.category == EventCategory.MISSION
        assert entry.title == "Test Mission"
        assert entry.description == "This is a test mission event"
        assert entry.severity == EventSeverity.STANDARD
        assert entry.turn == 10
        assert entry.tags == ['test', 'mission_1']
        assert entry.data['mission_id'] == 1
    
    def test_entry_format_line(self):
        entry = JournalEntry(
            category=EventCategory.MISSION,
            title="Test Mission",
            description="Test description",
            turn=15
        )
        
        line = entry.format_line()
        assert "[Turn 0015]" in line
        assert "Test Mission" in line
        assert "Test description" in line
    
    def test_entry_format_detailed(self):
        entry = JournalEntry(
            category=EventCategory.CREW,
            title="Crew Promoted",
            description="John was promoted",
            severity=EventSeverity.MAJOR,
            turn=25,
            tags=['crew', 'crew_john'],
            data={'crew_name': 'John', 'new_rank': 'Chief'}
        )
        
        detailed = entry.format_detailed()
        assert "Turn 25" in detailed
        assert "CREW" in detailed
        assert "MAJOR" in detailed
        assert "Crew Promoted" in detailed
        assert "John was promoted" in detailed
        assert "crew, crew_john" in detailed or "crew" in detailed
    
    def test_entry_to_dict(self):
        entry = JournalEntry(
            category=EventCategory.COMBAT,
            title="Hit",
            description="Direct hit",
            severity=EventSeverity.MAJOR,
            turn=30,
            tags=['combat'],
            data={'damage': 50}
        )
        
        data = entry.to_dict()
        assert data['category'] == 'combat'
        assert data['title'] == 'Hit'
        assert data['severity'] == 3
        assert data['turn'] == 30
        assert data['data']['damage'] == 50


class TestJournal:
    """Test main Journal class."""
    
    def test_journal_creation(self):
        journal = Journal()
        assert len(journal) == 0
        assert journal.max_entries == 500
        assert journal.statistics['total_events'] == 0
    
    def test_log_event(self):
        journal = Journal()
        
        entry = journal.log_event(
            category=EventCategory.MISSION,
            title="Test",
            description="Test event",
            turn=5
        )
        
        assert len(journal) == 1
        assert journal.statistics['total_events'] == 1
        assert entry.title == "Test"
    
    def test_multiple_events(self):
        journal = Journal()
        
        journal.log_event(EventCategory.MISSION, "M1", "Mission 1", turn=10)
        journal.log_event(EventCategory.CREW, "C1", "Crew 1", turn=15)
        journal.log_event(EventCategory.COMBAT, "X1", "Combat 1", turn=20)
        
        assert len(journal) == 3
        assert journal.statistics['total_events'] == 3
        assert journal.statistics['events_by_category']['mission'] == 1
        assert journal.statistics['events_by_category']['crew'] == 1
        assert journal.statistics['events_by_category']['combat'] == 1
    
    def test_max_entries_enforcement(self):
        journal = Journal(max_entries=10)
        
        for i in range(20):
            journal.log_event(
                EventCategory.OTHER,
                f"Event {i}",
                f"Event {i}",
                turn=i
            )
        
        assert len(journal) == 10
        # Oldest entries removed
        assert journal.entries[0].title == "Event 10"
    
    def test_get_entries_by_category(self):
        journal = Journal()
        
        journal.log_event(EventCategory.MISSION, "M1", "Mission", turn=10)
        journal.log_event(EventCategory.MISSION, "M2", "Mission", turn=15)
        journal.log_event(EventCategory.CREW, "C1", "Crew", turn=20)
        
        missions = journal.get_entries(category=EventCategory.MISSION)
        assert len(missions) == 2
        
        crew = journal.get_entries(category=EventCategory.CREW)
        assert len(crew) == 1
    
    def test_get_entries_by_severity(self):
        journal = Journal()
        
        journal.log_event(
            EventCategory.OTHER, "E1", "Event 1", 
            severity=EventSeverity.MINOR, turn=10
        )
        journal.log_event(
            EventCategory.OTHER, "E2", "Event 2",
            severity=EventSeverity.MAJOR, turn=15
        )
        journal.log_event(
            EventCategory.OTHER, "E3", "Event 3",
            severity=EventSeverity.MAJOR, turn=20
        )
        
        major = journal.get_entries(severity=EventSeverity.MAJOR)
        assert len(major) == 2
    
    def test_get_entries_by_tag(self):
        journal = Journal()
        
        journal.log_event(
            EventCategory.MISSION, "M1", "Mission 1",
            tags=['mission_1', 'smuggle'], turn=10
        )
        journal.log_event(
            EventCategory.MISSION, "M2", "Mission 2",
            tags=['mission_2', 'patrol'], turn=15
        )
        
        smuggle_missions = journal.get_entries(tag='smuggle')
        assert len(smuggle_missions) == 1
        assert smuggle_missions[0].title == "M1"
    
    def test_get_entries_with_limit(self):
        journal = Journal()
        
        for i in range(10):
            journal.log_event(EventCategory.OTHER, f"E{i}", f"Event {i}", turn=i)
        
        recent = journal.get_entries(limit=3)
        assert len(recent) == 3
        assert recent[-1].title == "E9"
    
    def test_get_entries_by_turn_range(self):
        journal = Journal()
        
        for i in range(0, 100, 10):
            journal.log_event(EventCategory.OTHER, f"E{i}", f"Event", turn=i)
        
        range_entries = journal.get_entries_by_turn_range(20, 60)
        assert len(range_entries) == 5
    
    def test_search(self):
        journal = Journal()
        
        journal.log_event(
            EventCategory.MISSION, "Cargo Delivery",
            "Smuggle cargo", turn=10
        )
        journal.log_event(
            EventCategory.CREW, "Crew Assigned",
            "John assigned", turn=15
        )
        
        results = journal.search("cargo")
        assert len(results) == 1
        assert results[0].title == "Cargo Delivery"
        
        results = journal.search("assigned")
        assert len(results) == 1
        assert results[0].title == "Crew Assigned"
    
    def test_get_mission_events(self):
        journal = Journal()
        
        journal.log_event(
            EventCategory.MISSION, "M1", "Mission 1",
            tags=['mission_5'], turn=10
        )
        journal.log_event(
            EventCategory.MISSION, "M2", "Mission 2",
            tags=['mission_5'], turn=15
        )
        journal.log_event(
            EventCategory.MISSION, "M3", "Mission 3",
            tags=['mission_6'], turn=20
        )
        
        m5_events = journal.get_mission_events(5)
        assert len(m5_events) == 2
    
    def test_get_crew_events(self):
        journal = Journal()
        
        journal.log_event(
            EventCategory.CREW, "Recruited",
            "John recruited", tags=['crew_john'], turn=10
        )
        journal.log_event(
            EventCategory.CREW, "Promoted",
            "John promoted", tags=['crew_john'], turn=20
        )
        
        john_events = journal.get_crew_events('john')
        assert len(john_events) == 2
    
    def test_get_last_entries(self):
        journal = Journal()
        
        for i in range(15):
            journal.log_event(EventCategory.OTHER, f"E{i}", f"Event {i}", turn=i)
        
        last_5 = journal.get_last_entries(5)
        assert len(last_5) == 5
        assert last_5[-1].title == "E14"
    
    def test_get_recent_summary(self):
        journal = Journal()
        
        for i in range(5):
            journal.log_event(EventCategory.OTHER, f"E{i}", f"Event {i}", turn=i)
        
        summary = journal.get_recent_summary(3)
        assert "Recent Events" in summary
        assert "E2" in summary
        assert "E3" in summary
        assert "E4" in summary
    
    def test_get_statistics(self):
        journal = Journal()
        
        journal.log_event(
            EventCategory.MISSION, "M1", "Mission",
            severity=EventSeverity.MAJOR, turn=10
        )
        journal.log_event(
            EventCategory.CREW, "C1", "Crew",
            severity=EventSeverity.MINOR, turn=15
        )
        
        stats = journal.get_statistics()
        assert stats['total_events'] == 2
        assert stats['events_by_category']['mission'] == 1
        assert stats['events_by_category']['crew'] == 1
        assert stats['events_by_severity']['MAJOR'] == 1
        assert stats['events_by_severity']['MINOR'] == 1
    
    def test_clear(self):
        journal = Journal()
        
        journal.log_event(EventCategory.OTHER, "E1", "Event", turn=10)
        journal.log_event(EventCategory.OTHER, "E2", "Event", turn=15)
        
        assert len(journal) == 2
        journal.clear()
        assert len(journal) == 0
        assert journal.statistics['total_events'] == 0
    
    def test_to_dict(self):
        journal = Journal()
        
        journal.log_event(EventCategory.MISSION, "M1", "Mission", turn=10)
        journal.log_event(EventCategory.CREW, "C1", "Crew", turn=15)
        
        data = journal.to_dict()
        assert 'entries' in data
        assert 'statistics' in data
        assert len(data['entries']) == 2
        assert data['statistics']['total_events'] == 2


class TestMissionEventHelper:
    """Test mission event helper."""
    
    def test_mission_accepted(self):
        journal = Journal()
        
        entry = create_mission_event(
            journal, "Cargo Smuggle", "accepted", turn=10, mission_id=1
        )
        
        assert entry.category == EventCategory.MISSION
        assert entry.severity == EventSeverity.STANDARD
        assert 'mission_1' in entry.tags
        assert entry.data['mission_name'] == "Cargo Smuggle"
    
    def test_mission_completed(self):
        journal = Journal()
        
        entry = create_mission_event(
            journal, "Cargo Smuggle", "completed", turn=50,
            mission_id=1, reward_xp=250, reward_credits=5000
        )
        
        assert entry.severity == EventSeverity.MAJOR
        assert "Successfully completed" in entry.description
        assert entry.data['reward_xp'] == 250
    
    def test_mission_failed(self):
        journal = Journal()
        
        entry = create_mission_event(
            journal, "Cargo Smuggle", "failed", turn=55, mission_id=1
        )
        
        assert entry.severity == EventSeverity.MAJOR
        assert "✗" in entry.title


class TestCrewEventHelper:
    """Test crew event helper."""
    
    def test_crew_recruited(self):
        journal = Journal()
        
        entry = create_crew_event(
            journal, "John", "recruited", turn=5
        )
        
        assert entry.category == EventCategory.CREW
        assert entry.severity == EventSeverity.MINOR
        # Check for either crew_john or crew_John (case variations)
        assert 'crew' in entry.tags
        assert any('john' in tag.lower() for tag in entry.tags)
    
    def test_crew_promoted(self):
        journal = Journal()
        
        entry = create_crew_event(
            journal, "John", "promoted", turn=50,
            details={'new_rank': 'Chief'}
        )
        
        assert entry.severity == EventSeverity.MAJOR
        assert "Promoted" in entry.title
    
    def test_crew_deceased(self):
        journal = Journal()
        
        entry = create_crew_event(
            journal, "John", "deceased", turn=100
        )
        
        assert entry.severity == EventSeverity.CRITICAL


class TestCombatEventHelper:
    """Test combat event helper."""
    
    def test_combat_hit(self):
        journal = Journal()
        
        entry = create_combat_event(
            journal, "hit", turn=20, target="Convoy", damage=50
        )
        
        assert entry.category == EventCategory.COMBAT
        assert entry.severity == EventSeverity.MAJOR
        assert "Direct Hit" in entry.title
    
    def test_combat_miss(self):
        journal = Journal()
        
        entry = create_combat_event(
            journal, "miss", turn=22
        )
        
        assert entry.severity == EventSeverity.MINOR


class TestProgressionEventHelper:
    """Test progression event helper."""
    
    def test_level_up(self):
        journal = Journal()
        
        entry = create_progression_event(
            journal, "level_up", turn=100,
            details="Reached Level 5"
        )
        
        assert entry.category == EventCategory.PROGRESSION
        assert entry.severity == EventSeverity.MAJOR
        assert "Level Up" in entry.title


class TestJournalIntegration:
    """Test journal with realistic gameplay scenarios."""
    
    def test_mission_lifecycle(self):
        journal = Journal()
        
        # Player starts mission
        create_mission_event(
            journal, "Sabotage Facility", "accepted", turn=10, mission_id=1
        )
        
        # Mid-mission: combat
        create_combat_event(journal, "hit", turn=25, target="Destroyer", damage=75)
        
        # Crew takes damage
        create_crew_event(journal, "Hans", "injured", turn=26)
        
        # Mission completes
        create_mission_event(
            journal, "Sabotage Facility", "completed", turn=50,
            mission_id=1, reward_xp=500, reward_credits=10000
        )
        
        # Player levels up
        create_progression_event(
            journal, "level_up", turn=51, details="Reached Level 6"
        )
        
        assert len(journal) == 5
        assert journal.statistics['total_events'] == 5
        
        # Get mission 1 events
        m1_events = journal.get_mission_events(1)
        assert len(m1_events) == 2  # accepted, completed
        
        # Get critical events only
        critical = journal.get_entries(severity=EventSeverity.CRITICAL)
        assert len(critical) == 0  # No deaths in this scenario
