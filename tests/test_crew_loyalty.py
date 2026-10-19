"""Tests for crew loyalty and rebellion system."""

import pytest
from engine.crew_loyalty import (
    LoyaltyTracker, RebellionManager, WarEndgameStats,
    CrewLoyaltyStatus, RebellionType, WarRank
)


class TestLoyaltyTracker:
    """Test individual crew member loyalty tracking."""
    
    def test_loyalty_tracker_creation(self):
        tracker = LoyaltyTracker(crew_id=1, crew_name="Hans", personality="disciplined")
        assert tracker.crew_name == "Hans"
        assert tracker.loyalty == 0.75
        assert tracker.personality == "disciplined"
    
    def test_loyalty_status_loyal(self):
        tracker = LoyaltyTracker(1, "Hans")
        tracker.loyalty = 0.8
        assert tracker.get_loyalty_status() == CrewLoyaltyStatus.LOYAL
    
    def test_loyalty_status_content(self):
        tracker = LoyaltyTracker(1, "Hans")
        tracker.loyalty = 0.6
        assert tracker.get_loyalty_status() == CrewLoyaltyStatus.CONTENT
    
    def test_loyalty_status_dissatisfied(self):
        tracker = LoyaltyTracker(1, "Hans")
        tracker.loyalty = 0.4
        assert tracker.get_loyalty_status() == CrewLoyaltyStatus.DISSATISFIED
    
    def test_loyalty_status_mutinous(self):
        tracker = LoyaltyTracker(1, "Hans")
        tracker.loyalty = 0.2
        assert tracker.get_loyalty_status() == CrewLoyaltyStatus.MUTINOUS
    
    def test_loyalty_status_deserter(self):
        tracker = LoyaltyTracker(1, "Hans")
        tracker.loyalty = 0.05
        assert tracker.get_loyalty_status() == CrewLoyaltyStatus.DESERTER
    
    def test_rebellion_risk_calculation(self):
        tracker = LoyaltyTracker(1, "Hans", personality="calm")
        tracker.loyalty = 0.5
        risk = tracker.get_rebellion_risk()
        assert 0.0 <= risk <= 1.0
    
    def test_rebellion_risk_personality_disciplined(self):
        tracker_disciplined = LoyaltyTracker(1, "Hans", personality="disciplined")
        tracker_aggressive = LoyaltyTracker(2, "Klaus", personality="aggressive")
        
        tracker_disciplined.loyalty = 0.3
        tracker_aggressive.loyalty = 0.3
        
        risk_disciplined = tracker_disciplined.get_rebellion_risk()
        risk_aggressive = tracker_aggressive.get_rebellion_risk()
        
        assert risk_disciplined < risk_aggressive
    
    def test_apply_stress(self):
        tracker = LoyaltyTracker(1, "Hans")
        initial_fear = tracker.fear_level
        
        tracker.apply_stress(fear=0.2)
        assert tracker.fear_level > initial_fear
    
    def test_relieve_stress(self):
        tracker = LoyaltyTracker(1, "Hans")
        tracker.apply_stress(fear=0.5, hunger=0.5, exhaustion=0.5)
        
        tracker.relieve_stress(amount=0.1)
        assert tracker.fear_level < 0.5
        assert tracker.hunger_level < 0.5
        assert tracker.exhaustion_level < 0.5
    
    def test_add_loyalty_event_positive(self):
        tracker = LoyaltyTracker(1, "Hans")
        initial_loyalty = tracker.loyalty
        
        tracker.add_loyalty_event(turn=10, event="rescued_comrade", loyalty_change=0.15)
        assert tracker.loyalty > initial_loyalty
    
    def test_add_loyalty_event_negative(self):
        tracker = LoyaltyTracker(1, "Hans")
        initial_loyalty = tracker.loyalty
        
        tracker.add_loyalty_event(turn=10, event="comrade_died", loyalty_change=-0.20)
        assert tracker.loyalty < initial_loyalty
    
    def test_record_achievement(self):
        tracker = LoyaltyTracker(1, "Hans")
        initial_loyalty = tracker.loyalty
        
        tracker.record_achievement("mission_completed", turn=20)
        assert tracker.loyalty > initial_loyalty
    
    def test_record_tragedy(self):
        tracker = LoyaltyTracker(1, "Hans")
        initial_loyalty = tracker.loyalty
        
        tracker.record_tragedy("comrade_died", turn=30)
        assert tracker.loyalty < initial_loyalty
    
    def test_record_rebellion(self):
        tracker = LoyaltyTracker(1, "Hans")
        initial_loyalty = tracker.loyalty
        
        tracker.record_rebellion(turn=40, rebellion_type=RebellionType.WORK_SLOWDOWN)
        assert tracker.loyalty < initial_loyalty
        assert len(tracker.rebellion_incidents) == 1


class TestRebellionManager:
    """Test crew-wide rebellion management."""
    
    def test_rebellion_manager_creation(self):
        manager = RebellionManager()
        assert len(manager.loyalty_trackers) == 0
    
    def test_add_crew_member(self):
        manager = RebellionManager()
        manager.add_crew_member(crew_id=1, crew_name="Hans", personality="calm")
        
        assert 1 in manager.loyalty_trackers
        assert manager.loyalty_trackers[1].crew_name == "Hans"
    
    def test_remove_crew_member(self):
        manager = RebellionManager()
        manager.add_crew_member(1, "Hans")
        assert 1 in manager.loyalty_trackers
        
        manager.remove_crew_member(1)
        assert 1 not in manager.loyalty_trackers
    
    def test_get_crew_morale_empty(self):
        manager = RebellionManager()
        morale = manager.get_crew_morale()
        assert morale == 0.5
    
    def test_get_crew_morale_single(self):
        manager = RebellionManager()
        manager.add_crew_member(1, "Hans")
        manager.loyalty_trackers[1].loyalty = 0.8
        
        morale = manager.get_crew_morale()
        assert 0.7 < morale <= 0.8
    
    def test_get_crew_morale_multiple(self):
        manager = RebellionManager()
        manager.add_crew_member(1, "Hans")
        manager.add_crew_member(2, "Klaus")
        
        manager.loyalty_trackers[1].loyalty = 0.8
        manager.loyalty_trackers[2].loyalty = 0.6
        
        morale = manager.get_crew_morale()
        assert 0.6 < morale < 0.8
    
    def test_check_all_rebellions(self):
        manager = RebellionManager()
        manager.add_crew_member(1, "Hans", personality="aggressive")
        manager.loyalty_trackers[1].loyalty = 0.15  # High rebellion risk
        
        rebellions = manager.check_all_rebellions(turn=10)
        # May or may not have rebellion due to randomness
        assert isinstance(rebellions, list)
    
    def test_apply_crew_event_combat_victory(self):
        manager = RebellionManager()
        manager.add_crew_member(1, "Hans")
        initial_loyalty = manager.loyalty_trackers[1].loyalty
        
        manager.apply_crew_event("combat_victory", severity=0.1)
        assert manager.loyalty_trackers[1].loyalty > initial_loyalty
    
    def test_apply_crew_event_combat_defeat(self):
        manager = RebellionManager()
        manager.add_crew_member(1, "Hans")
        initial_loyalty = manager.loyalty_trackers[1].loyalty
        
        manager.apply_crew_event("combat_defeat", severity=0.1)
        assert manager.loyalty_trackers[1].loyalty < initial_loyalty
    
    def test_apply_crew_event_starvation(self):
        manager = RebellionManager()
        manager.add_crew_member(1, "Hans")
        
        manager.apply_crew_event("starvation", severity=0.2)
        assert manager.loyalty_trackers[1].hunger_level > 0
    
    def test_apply_crew_event_shore_leave(self):
        manager = RebellionManager()
        manager.add_crew_member(1, "Hans")
        manager.loyalty_trackers[1].apply_stress(fear=0.3, hunger=0.3)
        
        initial_fear = manager.loyalty_trackers[1].fear_level
        manager.apply_crew_event("shore_leave", severity=0.1)
        assert manager.loyalty_trackers[1].fear_level < initial_fear


class TestWarEndgameStats:
    """Test war endgame statistics and ranking."""
    
    def test_endgame_stats_creation(self):
        stats = WarEndgameStats()
        assert stats.enemy_ships_destroyed == 0
        assert stats.crew_alive_at_end == 0
    
    def test_calculate_war_rank_civilian(self):
        stats = WarEndgameStats()
        stats.enemy_ships_destroyed = 0
        rank = stats.calculate_war_rank()
        assert rank == WarRank.CIVILIAN
    
    def test_calculate_war_rank_recruit(self):
        stats = WarEndgameStats()
        stats.enemy_ships_destroyed = 2
        rank = stats.calculate_war_rank()
        assert rank == WarRank.RECRUIT
    
    def test_calculate_war_rank_sailor(self):
        stats = WarEndgameStats()
        stats.enemy_ships_destroyed = 7
        rank = stats.calculate_war_rank()
        assert rank == WarRank.SAILOR
    
    def test_calculate_war_rank_veteran(self):
        stats = WarEndgameStats()
        stats.enemy_ships_destroyed = 15
        rank = stats.calculate_war_rank()
        assert rank == WarRank.VETERAN
    
    def test_calculate_war_rank_ace(self):
        stats = WarEndgameStats()
        stats.enemy_ships_destroyed = 30
        rank = stats.calculate_war_rank()
        assert rank == WarRank.SUBMARINE_ACE
    
    def test_calculate_war_rank_capital_ship_killer(self):
        stats = WarEndgameStats()
        stats.capital_ships_sunk = 5
        rank = stats.calculate_war_rank()
        assert rank == WarRank.CAPITAL_SHIP_KILLER
    
    def test_calculate_war_rank_legendary(self):
        stats = WarEndgameStats()
        stats.enemy_ships_destroyed = 50
        stats.perfect_loyalty_end = True
        stats.crew_average_loyalty = 0.9
        stats.survivors_rescued = 15
        rank = stats.calculate_war_rank()
        assert rank == WarRank.LEGENDARY_COMMANDER
    
    def test_calculate_final_score_civilian(self):
        stats = WarEndgameStats()
        score = stats.calculate_final_score()
        assert score >= 0  # Some baseline score
    
    def test_calculate_final_score_with_kills(self):
        stats = WarEndgameStats()
        stats.enemy_ships_destroyed = 10
        score_without = WarEndgameStats().calculate_final_score()
        score_with = stats.calculate_final_score()
        assert score_with > score_without
    
    def test_calculate_final_score_with_loyalty_bonus(self):
        stats = WarEndgameStats()
        stats.crew_average_loyalty = 0.9
        score_high = stats.calculate_final_score()
        
        stats.crew_average_loyalty = 0.3
        score_low = stats.calculate_final_score()
        
        assert score_high > score_low
    
    def test_calculate_final_score_perfect_loyalty(self):
        stats = WarEndgameStats()
        stats.perfect_loyalty_end = True
        score_perfect = stats.calculate_final_score()
        
        stats.perfect_loyalty_end = False
        score_imperfect = stats.calculate_final_score()
        
        assert score_perfect > score_imperfect
    
    def test_calculate_final_score_war_victory(self):
        stats = WarEndgameStats()
        stats.war_victory = True
        score_victory = stats.calculate_final_score()
        
        stats.war_victory = False
        score_no_victory = stats.calculate_final_score()
        
        assert score_victory > score_no_victory
    
    def test_get_final_report(self):
        stats = WarEndgameStats()
        stats.enemy_ships_destroyed = 15
        stats.crew_alive_at_end = 40
        stats.crew_total_recruited = 50
        
        report = stats.get_final_report()
        assert "WAR END REPORT" in report
        assert "Final Rank:" in report
        assert "Final Score:" in report
        assert "Enemy Ships Destroyed: 15" in report


class TestCrewLoyaltyIntegration:
    """Test integration of loyalty system with crew events."""
    
    def test_full_mission_lifecycle(self):
        """Test crew loyalty through complete mission."""
        manager = RebellionManager()
        
        # Recruit crew
        for i in range(5):
            manager.add_crew_member(i, f"Crew{i}")
        
        # Combat victory
        manager.apply_crew_event("combat_victory", severity=0.15)
        avg_loyalty_after_victory = manager.get_crew_morale()
        
        # Mission completion
        for tracker in manager.loyalty_trackers.values():
            tracker.record_achievement("mission_completed", turn=50)
        
        avg_loyalty_final = manager.get_crew_morale()
        assert avg_loyalty_final > avg_loyalty_after_victory
    
    def test_crew_rebellion_scenario(self):
        """Test crew rebellion under stress."""
        manager = RebellionManager()
        manager.add_crew_member(1, "Hans", personality="aggressive")
        tracker = manager.loyalty_trackers[1]
        
        # Apply extreme stress
        tracker.apply_stress(fear=0.5, hunger=0.4, exhaustion=0.3)
        tracker.loyalty = 0.2  # Very low loyalty
        
        # Check rebellion risk
        risk = tracker.get_rebellion_risk()
        assert risk > 0.5
    
    def test_perfect_war_scenario(self):
        """Test perfect war ending."""
        stats = WarEndgameStats()
        stats.enemy_ships_destroyed = 50
        stats.capital_ships_sunk = 5
        stats.crew_total_recruited = 50
        stats.crew_alive_at_end = 50
        stats.crew_deserted = 0
        stats.crew_mutinies = 0
        stats.crew_average_loyalty = 0.95
        stats.perfect_loyalty_end = True
        stats.survivors_rescued = 20
        stats.missions_completed = 15
        stats.turns_survived = 5000
        stats.war_victory = True
        
        rank = stats.calculate_war_rank()
        assert rank == WarRank.LEGENDARY_COMMANDER
        
        score = stats.calculate_final_score()
        assert score > 3000
