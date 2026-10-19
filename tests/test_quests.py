"""
Tests for quest and mission system.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.quests import Quest, MissionType, MissionStatus, QuestGenerator, QuestManager


class TestQuest:
    """Test individual quest functionality."""
    
    def test_quest_creation(self):
        """Test creating a quest."""
        data = {
            'name': 'Test Mission',
            'type': 'patrol',
            'description': 'Test description',
            'objective': 'Test objective',
            'reward_xp': 100,
            'reward_credits': 1000,
            'difficulty': 2
        }
        quest = Quest('test_1', data)
        
        assert quest.id == 'test_1'
        assert quest.name == 'Test Mission'
        assert quest.type == MissionType.PATROL
        assert quest.status == MissionStatus.AVAILABLE
        assert quest.reward_xp == 100
    
    def test_quest_lifecycle(self):
        """Test quest start, complete, fail."""
        data = {'name': 'Test', 'type': 'patrol', 'reward_xp': 100}
        quest = Quest('test_1', data)
        
        # Start quest
        quest.start()
        assert quest.status == MissionStatus.ACTIVE
        
        # Complete quest
        quest.complete()
        assert quest.status == MissionStatus.COMPLETED
        assert quest.progress == 1.0
    
    def test_quest_time_limit(self):
        """Test time limit enforcement."""
        data = {'name': 'Test', 'type': 'patrol', 'time_limit': 100}
        quest = Quest('test_1', data)
        quest.start()
        
        # Advance within limit
        quest.advance(50)
        assert quest.status == MissionStatus.ACTIVE
        
        # Exceed limit
        quest.advance(60)
        assert quest.status == MissionStatus.FAILED
    
    def test_quest_serialization(self):
        """Test quest to_dict."""
        data = {'name': 'Test', 'type': 'patrol', 'reward_xp': 100}
        quest = Quest('test_1', data)
        quest.start()
        
        d = quest.to_dict()
        assert d['id'] == 'test_1'
        assert d['name'] == 'Test'
        assert d['status'] == 'active'


class TestQuestGenerator:
    """Test quest generation."""
    
    def test_generate_standard_mission(self):
        """Test generating standard missions."""
        gen = QuestGenerator()
        quest = gen.generate_standard_mission(MissionType.PATROL)
        
        assert quest is not None
        assert quest.type == MissionType.PATROL
        assert quest.reward_xp > 0
    
    def test_generate_all_mission_types(self):
        """Test generating each mission type."""
        gen = QuestGenerator()
        
        for mission_type in MissionType:
            if mission_type != MissionType.ELDRITCH:
                quest = gen.generate_standard_mission(mission_type)
                assert quest.type == mission_type
    
    def test_generate_eldritch_encounter(self):
        """Test generating eldritch encounter."""
        gen = QuestGenerator()
        quest = gen.generate_eldritch_encounter()
        
        assert quest is not None
        assert quest.type == MissionType.ELDRITCH
        assert quest.difficulty == 5 or 3 <= quest.difficulty <= 5
    
    def test_quest_uniqueness(self):
        """Test that generated quests get unique IDs."""
        gen = QuestGenerator()
        q1 = gen.generate_standard_mission()
        q2 = gen.generate_standard_mission()
        
        assert q1.id != q2.id
    
    def test_get_quest_by_id(self):
        """Test retrieving quest by ID."""
        gen = QuestGenerator()
        quest = gen.generate_standard_mission()
        
        retrieved = gen.get_quest(quest.id)
        assert retrieved is quest
    
    def test_get_available_quests(self):
        """Test filtering available quests."""
        gen = QuestGenerator()
        q1 = gen.generate_standard_mission()
        q2 = gen.generate_standard_mission()
        
        available = gen.get_available_quests()
        assert len(available) == 2
        assert q1 in available
        assert q2 in available
    
    def test_get_active_quests(self):
        """Test filtering active quests."""
        gen = QuestGenerator()
        q1 = gen.generate_standard_mission()
        q2 = gen.generate_standard_mission()
        
        q1.start()
        
        active = gen.get_active_quests()
        assert len(active) == 1
        assert q1 in active


class TestQuestManager:
    """Test quest management."""
    
    def test_manager_creation(self):
        """Test creating quest manager."""
        manager = QuestManager()
        assert manager.active_quest is None
        assert len(manager.history) == 0
    
    def test_generate_mission(self):
        """Test generating missions through manager."""
        manager = QuestManager()
        quest = manager.generate_mission(MissionType.SABOTAGE)
        
        assert quest is not None
        assert quest.type == MissionType.SABOTAGE
    
    def test_generate_eldritch(self):
        """Test generating eldritch encounter."""
        manager = QuestManager()
        quest = manager.generate_eldritch()
        
        assert quest is not None
        assert quest.type == MissionType.ELDRITCH
    
    def test_accept_quest(self):
        """Test accepting a quest."""
        manager = QuestManager()
        quest = manager.generate_mission()
        
        success = manager.accept_quest(quest.id)
        assert success
        assert manager.active_quest is quest
        assert quest.status == MissionStatus.ACTIVE
    
    def test_cannot_accept_without_id(self):
        """Test that invalid quest ID fails."""
        manager = QuestManager()
        success = manager.accept_quest('nonexistent')
        assert not success
    
    def test_cannot_accept_if_active(self):
        """Test that can't accept multiple quests."""
        manager = QuestManager()
        q1 = manager.generate_mission()
        q2 = manager.generate_mission()
        
        manager.accept_quest(q1.id)
        success = manager.accept_quest(q2.id)
        
        assert not success
        assert manager.active_quest is q1
    
    def test_complete_quest_rewards(self):
        """Test completing quest awards rewards."""
        manager = QuestManager()
        quest = manager.generate_mission()
        manager.accept_quest(quest.id)
        
        rewards = manager.complete_active_quest()
        
        assert rewards['xp'] > 0
        assert rewards['credits'] > 0
        assert manager.active_quest is None
        assert quest in manager.history
    
    def test_fail_quest_penalties(self):
        """Test failing quest applies penalties."""
        manager = QuestManager()
        quest = manager.generate_mission()
        manager.accept_quest(quest.id)
        
        penalties = manager.fail_active_quest('Test failure')
        
        assert penalties['xp'] < 0
        assert penalties['credits'] < 0
        assert manager.active_quest is None
    
    def test_abandon_quest(self):
        """Test abandoning active quest."""
        manager = QuestManager()
        quest = manager.generate_mission()
        manager.accept_quest(quest.id)
        
        name = manager.abandon_active_quest()
        
        assert name == quest.name
        assert manager.active_quest is None
        assert quest.status == MissionStatus.ABANDONED
    
    def test_advance_time(self):
        """Test advancing quest time."""
        manager = QuestManager()
        quest = manager.generate_mission()
        manager.accept_quest(quest.id)
        
        manager.advance_time(50)
        assert quest.turns_elapsed == 50
    
    def test_get_active_quest_info(self):
        """Test getting active quest info."""
        manager = QuestManager()
        quest = manager.generate_mission()
        manager.accept_quest(quest.id)
        
        info = manager.get_active_quest_info()
        assert info['name'] == quest.name
        assert info['status'] == 'active'
    
    def test_career_stats(self):
        """Test career statistics tracking."""
        manager = QuestManager()
        
        # Complete one quest
        q1 = manager.generate_mission()
        manager.accept_quest(q1.id)
        manager.complete_active_quest()
        
        # Fail another
        q2 = manager.generate_mission()
        manager.accept_quest(q2.id)
        manager.fail_active_quest()
        
        stats = manager.get_career_stats()
        assert stats['quests_completed'] == 1
        assert stats['quests_failed'] == 1
        assert stats['total_rewards_xp'] > 0
    
    def test_manager_serialization(self):
        """Test manager to_dict."""
        manager = QuestManager()
        quest = manager.generate_mission()
        manager.accept_quest(quest.id)
        
        d = manager.to_dict()
        assert d['active_quest'] is not None
        assert isinstance(d['history'], list)
        assert isinstance(d['stats'], dict)


class TestMissionTypes:
    """Test all mission types."""
    
    def test_all_mission_types_exist(self):
        """Test that all mission types are defined."""
        types = [
            MissionType.PATROL,
            MissionType.SMUGGLE,
            MissionType.SABOTAGE,
            MissionType.RESCUE,
            MissionType.ESCORT,
            MissionType.HUNT,
            MissionType.SUPPLY_RUN,
            MissionType.RECONNAISSANCE,
            MissionType.ELDRITCH,
        ]
        
        for t in types:
            assert t is not None
    
    def test_mission_type_values(self):
        """Test mission type string values."""
        assert MissionType.PATROL.value == 'patrol'
        assert MissionType.SMUGGLE.value == 'smuggle'
        assert MissionType.SABOTAGE.value == 'sabotage'
        assert MissionType.ELDRITCH.value == 'eldritch'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
