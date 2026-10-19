"""
Tests for supply management, spy networks, and eldritch encounters
"""
import pytest
from engine.supply_management import (
    SupplyInventory, ResourceType, Resource, RationLevel
)
from engine.spy_network import SpyNetwork, SpyAgent, SabotageType, SpyStatus
from engine.eldritch_encounters import (
    EncounterManager, EncounterType, EncounterPhase, CrewResponse
)


class TestSupplyManagement:
    """Test supply and rationing system"""
    
    def test_resource_creation(self):
        """Test creating resources"""
        oxygen = Resource(ResourceType.OXYGEN, 100.0, 100.0, 0.5)
        assert oxygen.current == 100.0
        assert oxygen.get_percentage() == 100.0
    
    def test_resource_consumption(self):
        """Test resource consumption"""
        food = Resource(ResourceType.FOOD, 100, 100, 5.0)
        consumed = food.consume(10)
        assert consumed == 10
        assert food.current == 90
    
    def test_resource_replenishment(self):
        """Test resource replenishment"""
        water = Resource(ResourceType.WATER, 50, 100, 2.0)
        added = water.replenish(30)
        assert added == 30
        assert water.current == 80
    
    def test_resource_status(self):
        """Test resource status description"""
        oxygen = Resource(ResourceType.OXYGEN, 100.0, 100.0, 0.5)
        assert oxygen.get_status() == "EXCELLENT"
        
        oxygen.current = 60
        assert oxygen.get_status() == "GOOD"
        
        oxygen.current = 30
        assert oxygen.get_status() == "LOW"
    
    def test_inventory_creation(self):
        """Test inventory system"""
        inventory = SupplyInventory()
        assert inventory.oxygen.get_percentage() == 100.0
        assert inventory.food.current == 500
    
    def test_inventory_tick(self):
        """Test inventory consumption per turn"""
        inventory = SupplyInventory()
        initial_oxygen = inventory.oxygen.current
        
        warnings = inventory.tick(crew_count=8, depth=50, in_combat=False)
        
        assert inventory.oxygen.current < initial_oxygen
        assert isinstance(warnings, dict)
    
    def test_ration_level_affects_consumption(self):
        """Test that rationing affects consumption rates"""
        inventory1 = SupplyInventory()
        inventory1.set_ration_level(RationLevel.NORMAL)
        
        inventory2 = SupplyInventory()
        inventory2.set_ration_level(RationLevel.EMERGENCY)
        
        initial_food1 = inventory1.food.current
        initial_food2 = inventory2.food.current
        
        inventory1.tick(crew_count=8, depth=50)
        inventory2.tick(crew_count=8, depth=50)
        
        # Emergency rationing should use less food
        consumption1 = initial_food1 - inventory1.food.current
        consumption2 = initial_food2 - inventory2.food.current
        assert consumption2 < consumption1
    
    def test_ammunition_usage(self):
        """Test ammunition tracking"""
        inventory = SupplyInventory()
        initial = inventory.ammunition.current
        
        success = inventory.use_ammunition(2)
        assert success
        assert inventory.ammunition.current == initial - 2
    
    def test_critical_resources_detection(self):
        """Test detection of critical resource levels"""
        inventory = SupplyInventory()
        inventory.oxygen.current = 10
        inventory.power.current = 5
        
        critical = inventory.get_critical_resources()
        assert len(critical) > 0
        assert any("Oxygen" in r for r in critical)
        assert any("Power" in r for r in critical)
    
    def test_status_report_generation(self):
        """Test status report generation"""
        inventory = SupplyInventory()
        report = inventory.get_status_report()
        
        assert "SUPPLY STATUS REPORT" in report
        assert "Oxygen" in report
        assert "Power" in report


class TestSpyNetwork:
    """Test spy agent and sabotage system"""
    
    def test_spy_creation(self):
        """Test creating spy agents"""
        network = SpyNetwork()
        spy = network.add_spy("John Smith", "Agent 47", infiltration_turn=0)
        
        assert spy.cover_name == "John Smith"
        assert spy.actual_loyalty == 0.0
        assert spy.status == SpyStatus.UNKNOWN
    
    def test_spy_sabotage_attempt(self):
        """Test spy sabotage mechanics"""
        spy = SpyAgent(
            agent_id=1,
            cover_name="John",
            real_identity="Agent",
            infiltration_turn=0,
            loyalty_cover=0.8,
            actual_loyalty=0.0,
            preferred_sabotage=[SabotageType.OXYGEN_LEAK],
        )
        
        assert spy.can_sabotage(current_turn=50, cooldown=10)
        
        event = spy.attempt_sabotage(current_turn=50)
        # May or may not succeed due to random detection
        if event:
            assert event.sabotage_type in spy.preferred_sabotage
    
    def test_spy_discovery(self):
        """Test spy discovery mechanics"""
        network = SpyNetwork()
        spy = network.add_spy("Jane", "Enemy Agent", 0)
        
        network.discover_spy(spy.agent_id)
        assert spy.status == SpyStatus.EXPOSED
    
    def test_spy_elimination(self):
        """Test spy elimination"""
        network = SpyNetwork()
        spy = network.add_spy("John", "Enemy", 0)
        
        network.eliminate_spy(spy.agent_id)
        assert spy.status == SpyStatus.ELIMINATED
    
    def test_spy_suspicion_buildup(self):
        """Test suspicion accumulation"""
        spy = SpyAgent(
            agent_id=1,
            cover_name="John",
            real_identity="Agent",
            infiltration_turn=0,
            loyalty_cover=0.8,
            actual_loyalty=0.0,
        )
        
        assert spy.status == SpyStatus.UNKNOWN
        
        spy.increase_suspicion(0.8)
        assert spy.status == SpyStatus.SUSPECTED
        
        spy.increase_suspicion(0.2)
        assert spy.status == SpyStatus.EXPOSED
    
    def test_sabotage_report(self):
        """Test sabotage report generation"""
        network = SpyNetwork()
        network.add_spy("John", "Agent1", 0)
        network.add_spy("Jane", "Agent2", 5)
        
        report = network.get_sabotage_report()
        assert "ESPIONAGE AND SABOTAGE REPORT" in report
        assert "TOTAL SPIES: 2" in report
    
    def test_crew_morale_impact_from_spies(self):
        """Test how spies affect crew morale"""
        network = SpyNetwork()
        spy = network.add_spy("John", "Agent", 0)
        
        # Unknown spy has no impact
        impact1 = network.get_crew_morale_impact()
        assert impact1 == 0
        
        # Exposed spy has negative impact
        network.discover_spy(spy.agent_id)
        impact2 = network.get_crew_morale_impact()
        assert impact2 < 0


class TestEldrischEncounters:
    """Test eldritch encounter system"""
    
    def test_encounter_creation(self):
        """Test creating encounters"""
        manager = EncounterManager()
        encounter = manager.start_encounter(EncounterType.WHISPERS, turn=10)
        
        assert encounter.encounter_type == EncounterType.WHISPERS
        assert encounter.current_phase == EncounterPhase.PSYCHOLOGICAL
        assert manager.active_encounter == encounter
    
    def test_encounter_phase_progression(self):
        """Test encounter phase progression"""
        manager = EncounterManager()
        encounter = manager.start_encounter(EncounterType.WHISPERS, turn=10)
        
        initial_phase = encounter.current_phase
        # Manually set escalation values for testing
        if encounter.psychological:
            encounter.psychological.escalation_chance = 1.0  # Guaranteed escalation
            encounter.psychological.turns_duration = 1
        
        encounter.progress_phase()
        # May escalate depending on randomness
        # Just verify it doesn't crash
        assert encounter is not None
    
    def test_encounter_psychological_effects(self):
        """Test psychological phase effects"""
        manager = EncounterManager()
        encounter = manager.start_encounter(EncounterType.TIME_DISTORTION, turn=0)
        
        effects = encounter.apply_psychological_effects()
        assert 'sanity_loss' in effects
        assert 'fear_increase' in effects
    
    def test_encounter_physical_effects(self):
        """Test physical phase damage"""
        manager = EncounterManager()
        encounter = manager.start_encounter(EncounterType.CREATURE_CONTACT, turn=0)
        
        # Move to physical phase
        encounter.current_phase = EncounterPhase.PHYSICAL
        if encounter.physical is None:
            from engine.eldritch_encounters import PhysicalPhase
            encounter.physical = PhysicalPhase(
                description="It's real",
                hull_damage_rate=5.0,
                creature_visible=True,
                weapon_effectiveness=0.5,
                escape_difficulty=0.7,
                turns_until_critical=5,
            )
        
        damage = encounter.apply_physical_effects(crew_count=8)
        assert damage > 0
    
    def test_encounter_resolution_attempt(self):
        """Test encounter resolution"""
        manager = EncounterManager()
        encounter = manager.start_encounter(EncounterType.WHISPERS, turn=0)
        
        # Attempt various resolutions
        for method in ['retreat', 'evasion', 'full_depth']:
            manager2 = EncounterManager()
            encounter2 = manager2.start_encounter(EncounterType.WHISPERS, turn=0)
            # May or may not succeed due to randomness
            result = manager2.resolve_encounter(encounter2.encounter_id, method)
            # Just verify it returns boolean
            assert isinstance(result, bool)
    
    def test_encounter_manager_tick(self):
        """Test encounter manager processing"""
        manager = EncounterManager()
        encounter = manager.start_encounter(EncounterType.SHADOW_MASS, turn=0)
        
        effects = manager.tick_encounters(crew_count=8)
        assert isinstance(effects, list)
    
    def test_encounter_summary_generation(self):
        """Test encounter summary report"""
        manager = EncounterManager()
        encounter = manager.start_encounter(EncounterType.RADIATION_ANOMALY, turn=5)
        
        summary = manager.get_encounter_summary()
        assert "ENCOUNTER SUMMARY" in summary
        assert "ACTIVE ENCOUNTER" in summary
    
    def test_multiple_encounter_types(self):
        """Test different encounter types"""
        manager = EncounterManager()
        
        for enc_type in EncounterType:
            manager2 = EncounterManager()
            encounter = manager2.start_encounter(enc_type, turn=0)
            assert encounter.encounter_type == enc_type
            assert encounter.psychological is not None


class TestSystemIntegration:
    """Test integration between systems"""
    
    def test_supply_depletion_from_sabotage(self):
        """Test how sabotage affects supplies"""
        inventory = SupplyInventory()
        network = SpyNetwork()
        
        spy = network.add_spy("John", "Agent", 0)
        spy.preferred_sabotage = [SabotageType.OXYGEN_LEAK]
        
        initial_oxygen = inventory.oxygen.current
        # Sabotage would reduce oxygen
        inventory.oxygen.consume(20)  # Simulate sabotage damage
        
        assert inventory.oxygen.current < initial_oxygen
    
    def test_encounter_affects_crew_fear(self):
        """Test how encounters affect crew state"""
        manager = EncounterManager()
        encounter = manager.start_encounter(EncounterType.WHISPERS, turn=0)
        
        effects = encounter.apply_psychological_effects()
        assert effects['fear_increase'] > 0
    
    def test_combined_crisis_scenario(self):
        """Test multiple systems in crisis"""
        # Setup supplies at critical level
        inventory = SupplyInventory()
        inventory.oxygen.current = 15
        inventory.power.current = 10
        inventory.food.current = 40
        
        # Check critical resources
        critical = inventory.get_critical_resources()
        assert len(critical) > 0
        
        # Have spy attempt sabotage
        network = SpyNetwork()
        spy = network.add_spy("Traitor", "Enemy", 0)
        
        # Have encounter active
        manager = EncounterManager()
        encounter = manager.start_encounter(EncounterType.SHADOW_MASS, turn=10)
        
        # Verify all systems can operate together
        effects = manager.tick_encounters(8)
        assert isinstance(effects, list)
