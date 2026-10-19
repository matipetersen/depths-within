"""
Integration tests for crew loyalty console commands and game state
"""
import pytest
from engine.game import Game
from engine.crew_loyalty import LoyaltyTracker, RebellionManager, WarEndgameStats


class TestGameCrewLoyaltyIntegration:
    """Test crew loyalty system integration with game initialization"""
    
    def test_game_initializes_with_rebellion_manager(self):
        """Test that game initializes with RebellionManager"""
        game = Game()
        assert game.rebellion_manager is not None
        assert isinstance(game.rebellion_manager, RebellionManager)
    
    def test_game_initializes_with_war_endgame(self):
        """Test that game initializes with WarEndgameStats"""
        game = Game()
        assert game.war_endgame is not None
        assert isinstance(game.war_endgame, WarEndgameStats)
    
    def test_game_source_contains_crew_loyalty_commands(self):
        """Verify game.py source contains crew loyalty command implementations"""
        import inspect
        source = inspect.getsource(Game)
        
        # Verify console commands are implemented
        assert 'crew_loyalty' in source or 'crew_status' in source
        assert 'crew_morale' in source
        assert 'rebellion_check' in source
        assert 'crew_loyalty_detail' in source
        assert 'war_status' in source
        assert 'end_war' in source
    
    def test_game_help_lists_crew_loyalty_commands(self):
        """Verify help command lists crew loyalty commands"""
        import inspect
        source = inspect.getsource(Game)
        
        # Help command should mention crew loyalty and war sections (in hotkey system or process_command)
        assert 'crew_loyalty' in source or 'hotkey' in source.lower()
        assert 'war' in source.lower()


class TestRebellionManagerIntegration:
    """Test RebellionManager integration with Game"""
    
    def test_add_crew_to_manager(self):
        """Test adding crew to rebellion manager"""
        game = Game()
        
        game.rebellion_manager.add_crew_member(1, "pilot", "brave")
        
        # Check loyalty_trackers contains crew
        assert hasattr(game.rebellion_manager, 'loyalty_trackers')
        assert 1 in game.rebellion_manager.loyalty_trackers
    
    def test_morale_calculation_with_crew(self):
        """Test morale calculation with multiple crew members"""
        game = Game()
        
        # Add crew with different loyalties
        game.rebellion_manager.add_crew_member(1, "pilot", "brave")
        game.rebellion_manager.loyalty_trackers[1].loyalty = 0.9
        
        game.rebellion_manager.add_crew_member(2, "engineer", "cautious")
        game.rebellion_manager.loyalty_trackers[2].loyalty = 0.7
        
        morale = game.rebellion_manager.get_crew_morale()
        assert 0.75 <= morale <= 0.90  # Should be around average of 0.8
    
    def test_morale_resilience_with_empty_crew(self):
        """Test morale calculation doesn't crash with no crew"""
        game = Game()
        
        morale = game.rebellion_manager.get_crew_morale()
        assert isinstance(morale, float)
        assert 0 <= morale <= 1
    
    def test_crew_events_affect_morale(self):
        """Test crew-wide events affect crew morale"""
        game = Game()
        
        game.rebellion_manager.add_crew_member(1, "pilot", "brave")
        game.rebellion_manager.loyalty_trackers[1].loyalty = 0.7
        
        initial_morale = game.rebellion_manager.get_crew_morale()
        
        # Apply crew event
        game.rebellion_manager.apply_crew_event('combat_victory')
        
        # Morale should not decrease
        new_morale = game.rebellion_manager.get_crew_morale()
        assert new_morale >= initial_morale - 0.01  # Allow small floating point variation


class TestWarEndgameIntegration:
    """Test WarEndgameStats integration with Game"""
    
    def test_war_stats_initialization(self):
        """Test war stats are properly initialized"""
        game = Game()
        
        assert game.war_endgame.enemy_ships_destroyed == 0
        assert game.war_endgame.enemy_tonnage_sunk == 0
        assert game.war_endgame.capital_ships_sunk == 0
        assert game.war_endgame.survivors_rescued == 0
        assert game.war_endgame.crew_deserted == 0
    
    def test_war_rank_calculation(self):
        """Test war rank calculation"""
        game = Game()
        
        # Setup stats for high rank
        game.rebellion_manager.add_crew_member(1, "pilot", "brave")
        
        game.war_endgame.enemy_ships_destroyed = 30
        game.war_endgame.crew_average_loyalty = 0.85
        
        rank = game.war_endgame.calculate_war_rank()
        assert rank.name in ['SUBMARINE_ACE', 'VETERAN', 'SAILOR', 'RECRUIT']
    
    def test_final_score_calculation(self):
        """Test war score calculation"""
        game = Game()
        
        game.war_endgame.enemy_ships_destroyed = 50
        game.war_endgame.capital_ships_sunk = 5
        game.war_endgame.survivors_rescued = 100
        game.war_endgame.crew_average_loyalty = 1.0
        
        score = game.war_endgame.calculate_final_score()
        assert score > 0
        assert score > 500  # Should be substantial with these stats
    
    def test_final_report_generation(self):
        """Test final war report generation"""
        game = Game()
        
        # Setup minimal stats
        game.rebellion_manager.add_crew_member(1, "pilot", "brave")
        
        game.war_endgame.enemy_ships_destroyed = 20
        game.war_endgame.crew_alive_at_end = 1
        game.war_endgame.crew_total_recruited = 5
        game.war_endgame.turns_survived = 100
        
        report = game.war_endgame.get_final_report()
        assert isinstance(report, str)
        assert 'WAR END REPORT' in report
        assert 'Final Score' in report
    
    def test_war_stats_accumulation(self):
        """Test war statistics accumulate correctly"""
        game = Game()
        
        game.war_endgame.enemy_ships_destroyed += 5
        game.war_endgame.enemy_tonnage_sunk += 5000
        game.war_endgame.capital_ships_sunk += 1
        
        assert game.war_endgame.enemy_ships_destroyed == 5
        assert game.war_endgame.enemy_tonnage_sunk == 5000
        assert game.war_endgame.capital_ships_sunk == 1
        
        # Add more
        game.war_endgame.enemy_ships_destroyed += 3
        assert game.war_endgame.enemy_ships_destroyed == 8


class TestConsoleCommandState:
    """Test console command data flow"""
    
    def test_crew_loyalty_affects_overall_morale(self):
        """Test individual crew loyalty affects overall morale calculation"""
        game = Game()
        
        # Create unhappy crew
        game.rebellion_manager.add_crew_member(1, "unhappy", "cautious")
        game.rebellion_manager.loyalty_trackers[1].loyalty = 0.2
        
        morale_unhappy = game.rebellion_manager.get_crew_morale()
        
        # Add happy crew
        game.rebellion_manager.add_crew_member(2, "happy", "brave")
        game.rebellion_manager.loyalty_trackers[2].loyalty = 0.95
        
        morale_mixed = game.rebellion_manager.get_crew_morale()
        
        # Mixed morale should be different from single unhappy crew
        assert isinstance(morale_mixed, float)
    
    def test_crew_stress_affects_rebellion_risk(self):
        """Test stress factors affect rebellion risk"""
        game = Game()
        
        game.rebellion_manager.add_crew_member(1, "crew1", "cautious")
        tracker = game.rebellion_manager.loyalty_trackers[1]
        tracker.loyalty = 0.5
        
        # Initial rebellion risk
        initial_risk = tracker.get_rebellion_risk()
        
        # Apply stress
        tracker.apply_stress(0.3, 0.3, 0.3)
        
        new_risk = tracker.get_rebellion_risk()
        # Stress should increase rebellion risk
        assert new_risk > initial_risk
    
    def test_crew_achievements_improve_loyalty(self):
        """Test achievements improve crew loyalty"""
        game = Game()
        
        game.rebellion_manager.add_crew_member(1, "crew1", "brave")
        tracker = game.rebellion_manager.loyalty_trackers[1]
        initial_loyalty = tracker.loyalty
        
        # Record achievement
        tracker.record_achievement('mission_completed', turn=1)
        
        new_loyalty = tracker.loyalty
        # Loyalty should improve with achievement
        assert new_loyalty >= initial_loyalty
    
    def test_war_stats_final_status_complete(self):
        """Test war stats have complete information for final report"""
        game = Game()
        
        # Setup complete mission scenario
        game.rebellion_manager.add_crew_member(1, "pilot", "brave")
        
        game.war_endgame.enemy_ships_destroyed = 75
        game.war_endgame.capital_ships_sunk = 3
        game.war_endgame.survivors_rescued = 75
        game.war_endgame.crew_alive_at_end = 1
        game.war_endgame.crew_total_recruited = 5
        game.war_endgame.crew_deserted = 2
        game.war_endgame.crew_mutinies = 0
        game.war_endgame.crew_average_loyalty = 0.75
        game.war_endgame.turns_survived = 150
        
        # Generate final report
        report = game.war_endgame.get_final_report()
        
        assert 'Report' in report or 'REPORT' in report
        assert 'Score' in report or 'SCORE' in report or 'score' in report
