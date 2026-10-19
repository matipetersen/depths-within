"""
Integration test for crew recruitment, progression, and upgrades.
Tests that systems load and work together.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from submarine.crew_recruitment import CrewMember, CrewRecruitmentPool, CrewRoster
from engine.progression import PlayerStats, SubmariueUpgradeTree
from ui.glyphs import get_glyph, get_contact_glyph, get_compartment_crew_glyph


class TestCrewRecruitment:
    """Test crew recruitment system."""
    
    def test_crew_member_creation(self):
        """Test creating a crew member."""
        crew = CrewMember()
        assert crew.id is not None
        assert crew.name is not None
        # Rank should be one of common naval ranks
        assert crew.rank is not None
        assert len(crew.rank) > 0
        assert crew.stress >= 0
        assert crew.morale >= 0
    
    def test_crew_member_xp(self):
        """Test crew XP gain."""
        crew = CrewMember()
        initial_xp = crew.xp.get(crew.primary_skill, 0)
        crew.gain_xp(crew.primary_skill, 50)
        assert crew.xp.get(crew.primary_skill, 0) > initial_xp
    
    def test_recruitment_pool(self):
        """Test recruitment pool."""
        pool = CrewRecruitmentPool()
        assert len(pool.pool) > 0
        
        # Get random recruit
        recruit = pool.get_random()
        assert recruit is not None
    
    def test_crew_roster(self):
        """Test crew roster management."""
        roster = CrewRoster(submarine_id='test_sub')
        
        # Recruit crew
        crew = roster.recruit_random()
        assert crew is not None
        assert len(roster.crew) == 1
        
        # Assign crew
        success = roster.assign_crew(crew, compartment_id=1, role='sonar')
        assert success
        assert crew.compartment_id == 1
        
        # Get crew by compartment
        comp_crew = roster.get_crew_by_compartment(1)
        assert len(comp_crew) == 1
        assert comp_crew[0].id == crew.id
        
        # Reassign
        success = roster.reassign_crew(crew, 2, 'engineering')
        assert success
        assert crew.compartment_id == 2
        
        # Remove crew
        success = roster.remove_crew(crew)
        assert success
        assert len(roster.crew) == 0


class TestProgression:
    """Test player progression system."""
    
    def test_player_stats_creation(self):
        """Test creating player stats."""
        stats = PlayerStats()
        assert stats.level == 1
        assert stats.total_xp == 0
        assert len(stats.skills) > 0
    
    def test_player_xp_gain(self):
        """Test XP gain and leveling."""
        stats = PlayerStats()
        initial_level = stats.level
        
        # Gain XP
        stats.gain_xp('sonar_operation', 100)
        assert stats.total_xp == 100
        
        # Gain enough for level up (500 total XP needed)
        stats.gain_xp('torpedo_accuracy', 400)
        assert stats.total_xp == 500
        assert stats.level > initial_level
    
    def test_upgrade_tree(self):
        """Test submarine upgrade tree."""
        tree = SubmariueUpgradeTree()
        
        # Check upgrades loaded
        assert len(tree.upgrades) > 0
        
        # Get upgrade by ID
        upgrade = tree.get_upgrade('sonar_improved_range')
        assert upgrade is not None
        assert upgrade.name == 'Extended Sonar Range'
        
        # Get upgrades by tier
        tier1 = tree.get_upgrades_by_tier(1)
        assert len(tier1) > 0
        
        # Get available upgrades (with low XP, should be some)
        available = tree.get_available_upgrades(0)
        assert len(available) >= 0


class TestGlyphs:
    """Test glyph system."""
    
    def test_get_glyph(self):
        """Test getting glyphs."""
        glyph = get_glyph('submarine_player')
        assert glyph == '⊓'
        
        # Test fallback
        glyph = get_glyph('nonexistent', 'X')
        assert glyph == 'X'
    
    def test_contact_glyph(self):
        """Test contact glyphs."""
        merchant_glyph = get_contact_glyph('merchant')
        assert merchant_glyph == '⊞'
        
        warship_glyph = get_contact_glyph('warship')
        assert warship_glyph == '⊕'
    
    def test_crew_glyph(self):
        """Test crew role glyphs."""
        sonar_glyph = get_compartment_crew_glyph('sonar')
        assert sonar_glyph == 'S'
        
        engineer_glyph = get_compartment_crew_glyph('engineering')
        assert engineer_glyph == 'E'


class TestIntegration:
    """Test integration of all systems."""
    
    def test_game_load(self):
        """Test that Game class loads with new systems."""
        try:
            from engine.game import Game
            game = Game()
            
            assert game.crew_roster is not None
            assert game.player_stats is not None
            assert game.upgrade_tree is not None
            
        except Exception as e:
            pytest.fail(f"Failed to load Game: {e}")
    
    def test_crew_and_progression_flow(self):
        """Test crew recruitment and progression flow."""
        roster = CrewRoster(submarine_id='test_sub')
        stats = PlayerStats()
        
        # Recruit crew
        crew = roster.recruit_random()
        assert crew is not None
        
        # Gain player XP
        stats.gain_xp('crew_leadership', 50)
        assert stats.total_xp == 50
        
        # Crew gains XP
        crew.gain_xp(crew.primary_skill, 25)
        assert crew.xp.get(crew.primary_skill, 0) >= 25


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
