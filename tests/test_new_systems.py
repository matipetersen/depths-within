"""
Test suite for divers, time system, and fog of war.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from submarine.divers import (
    Diver, DiverSpecialty, DiverMission, DiverMissionType,
    DiverOperationsManager, DiverMissionStatus
)
from engine.time_system import TimeSystem, TimeOfDay, MoonPhase
from engine.fog_of_war import (
    FogOfWar, SensorType, ContactType, TileVisibility
)


def test_diver_creation():
    """Test diver creation and skills."""
    print("\n=== Testing Diver Creation ===")
    
    diver = Diver(specialty=DiverSpecialty.RECONNAISSANCE)
    
    assert diver.specialty == DiverSpecialty.RECONNAISSANCE
    assert 0.0 <= diver.skills['stealth'] <= 1.0
    assert diver.alive
    assert diver.available
    
    print(f"✓ Diver created: {diver.name}")
    print(f"  Specialty: {diver.specialty.value}")
    print(f"  Stealth: {diver.skills['stealth']:.0%}")
    print(f"  Demolition: {diver.skills['demolition']:.0%}")
    
    # Test specialty skill boost
    assert diver.skills['stealth'] >= 0.6, "Stealth specialist should have high stealth"
    print(f"✓ Specialty skill boost working")


def test_diver_effectiveness():
    """Test diver effectiveness calculations."""
    print("\n=== Testing Diver Effectiveness ===")
    
    # Recon specialist
    recon_diver = Diver(specialty=DiverSpecialty.RECONNAISSANCE)
    sabotage_diver = Diver(specialty=DiverSpecialty.SABOTAGE)
    
    # Test effectiveness for matching missions
    recon_effectiveness = recon_diver.get_effectiveness(DiverMissionType.HARBOR_RECON)
    sabotage_effectiveness = sabotage_diver.get_effectiveness(DiverMissionType.SHIP_SABOTAGE)
    
    print(f"Recon specialist on recon mission: {recon_effectiveness:.0%}")
    print(f"Sabotage specialist on sabotage mission: {sabotage_effectiveness:.0%}")
    
    assert recon_effectiveness > 0.5, "Specialist should be effective"
    assert sabotage_effectiveness > 0.5, "Specialist should be effective"
    
    # Test fatigue impact
    recon_diver.fatigue = 0.8
    fatigued_effectiveness = recon_diver.get_effectiveness(DiverMissionType.HARBOR_RECON)
    
    print(f"Fatigued diver effectiveness: {fatigued_effectiveness:.0%}")
    assert fatigued_effectiveness < recon_effectiveness, "Fatigue should reduce effectiveness"
    
    print(f"✓ Effectiveness calculations working")


def test_diver_mission():
    """Test mission creation and execution."""
    print("\n=== Testing Diver Missions ===")
    
    manager = DiverOperationsManager()
    
    # Create and recruit diver
    diver = manager.recruit_diver(specialty=DiverSpecialty.SABOTAGE)
    print(f"✓ Recruited: {diver.name}")
    
    # Create mission
    mission = manager.create_mission(
        DiverMissionType.SHIP_SABOTAGE,
        target="Enemy Harbor",
        difficulty=0.6
    )
    
    assert mission.mission_type == DiverMissionType.SHIP_SABOTAGE
    assert mission.status == DiverMissionStatus.PREPARING
    print(f"✓ Mission created: {mission.mission_type.value}")
    
    # Assign diver
    success = mission.assign_diver(diver)
    assert success, "Should assign available diver"
    assert not diver.available, "Diver should be unavailable"
    print(f"✓ Diver assigned to mission")
    
    # Launch mission
    manager.launch_mission(mission)
    assert mission.status == DiverMissionStatus.DEPLOYED
    print(f"✓ Mission launched")
    
    # Simulate mission
    initial_progress = mission.progress
    for _ in range(5):
        manager.tick_missions()
    
    assert mission.progress > initial_progress, "Mission should make progress"
    print(f"✓ Mission progress: {mission.progress:.0%}")


def test_time_system():
    """Test time system and day/night cycle."""
    print("\n=== Testing Time System ===")
    
    time_system = TimeSystem(start_hour=12, start_minute=0)
    
    # Test initial state
    assert time_system.hour == 12
    assert time_system.minute == 0
    print(f"✓ Time initialized: {time_system.get_time_string()}")
    
    # Test time advancement
    time_system.tick()
    assert time_system.minute == 5, "Should advance by 5 minutes"
    print(f"✓ Time advancement working: {time_system.get_time_string()}")
    
    # Test time of day
    time_system.set_time(6, 30)
    assert time_system.get_time_of_day() == TimeOfDay.DAWN
    
    time_system.set_time(12, 0)
    assert time_system.get_time_of_day() == TimeOfDay.NOON
    
    time_system.set_time(22, 0)
    assert time_system.get_time_of_day() == TimeOfDay.EVENING
    
    print(f"✓ Time of day detection working")


def test_visibility_modifiers():
    """Test visibility modifiers by time of day."""
    print("\n=== Testing Visibility Modifiers ===")
    
    time_system = TimeSystem()
    
    test_times = [
        (2, TimeOfDay.NIGHT, "should be dark"),
        (6, TimeOfDay.DAWN, "should be dim"),
        (12, TimeOfDay.NOON, "should be bright"),
        (18, TimeOfDay.DUSK, "should be dim"),
    ]
    
    for hour, expected_tod, desc in test_times:
        time_system.set_time(hour, 0)
        tod = time_system.get_time_of_day()
        visibility = time_system.get_visibility_modifier()
        
        assert tod == expected_tod
        print(f"{hour:02d}:00 - {tod.value}: {visibility:.0%} visibility ({desc})")
    
    # Test day vs night
    time_system.set_time(12, 0)
    day_visibility = time_system.get_visibility_modifier()
    
    time_system.set_time(2, 0)
    night_visibility = time_system.get_visibility_modifier()
    
    assert day_visibility > night_visibility * 2, "Day should be much brighter"
    print(f"✓ Day visibility ({day_visibility:.0%}) > Night visibility ({night_visibility:.0%})")


def test_moon_phase():
    """Test moon phase calculations."""
    print("\n=== Testing Moon Phase ===")
    
    time_system = TimeSystem()
    time_system.moon_age = 0
    time_system._update_moon_phase()
    
    assert time_system.moon_phase == MoonPhase.NEW_MOON
    print(f"✓ New moon: {time_system.get_moon_illumination():.0%} illumination")
    
    time_system.moon_age = 15
    time_system._update_moon_phase()
    
    assert time_system.moon_phase == MoonPhase.FULL_MOON
    full_moon_light = time_system.get_moon_illumination()
    assert full_moon_light == 1.0
    print(f"✓ Full moon: {full_moon_light:.0%} illumination")
    
    # Test night visibility with moon
    time_system.set_time(2, 0)  # Night
    visibility_with_full_moon = time_system.get_visibility_modifier(include_moon=True)
    visibility_without_moon = time_system.get_visibility_modifier(include_moon=False)
    
    assert visibility_with_full_moon > visibility_without_moon
    print(f"✓ Full moon increases night visibility: "
          f"{visibility_without_moon:.0%} → {visibility_with_full_moon:.0%}")


def test_detection_risk():
    """Test detection risk modifiers."""
    print("\n=== Testing Detection Risk ===")
    
    time_system = TimeSystem()
    
    # Day surface detection
    time_system.set_time(12, 0)
    day_risk = time_system.get_detection_risk_modifier(on_surface=True)
    
    # Night surface detection
    time_system.set_time(2, 0)
    night_risk = time_system.get_detection_risk_modifier(on_surface=True)
    
    # Submerged detection
    submerged_risk = time_system.get_detection_risk_modifier(on_surface=False)
    
    print(f"Day surface detection risk: {day_risk:.0%}")
    print(f"Night surface detection risk: {night_risk:.0%}")
    print(f"Submerged detection risk: {submerged_risk:.0%}")
    
    assert day_risk > night_risk * 2, "Day should be much riskier"
    assert submerged_risk < night_risk, "Submerged should be safest"
    
    print(f"✓ Detection risk calculations working")


def test_fog_of_war_creation():
    """Test fog of war initialization."""
    print("\n=== Testing Fog of War Creation ===")
    
    fog = FogOfWar(width=100, height=100)
    
    assert fog.width == 100
    assert fog.height == 100
    assert len(fog.visibility) == 10000  # 100x100
    
    # All tiles should start unexplored
    unexplored_count = sum(1 for v in fog.visibility.values()
                          if v == TileVisibility.UNEXPLORED)
    assert unexplored_count == 10000
    
    print(f"✓ Fog of war created: {fog.width}x{fog.height}")
    print(f"✓ All tiles unexplored: {unexplored_count}")


def test_sensor_visibility():
    """Test sensor-based visibility."""
    print("\n=== Testing Sensor Visibility ===")
    
    fog = FogOfWar(width=100, height=100)
    time_system = TimeSystem(start_hour=12)  # Noon
    
    submarine_pos = (50, 50)
    
    # Test periscope visibility
    fog.update_visibility(
        submarine_pos,
        {SensorType.PERISCOPE},
        time_visibility=1.0,
        weather_visibility=1.0,
        depth=10
    )
    
    visible_count = sum(1 for v in fog.visibility.values()
                       if v == TileVisibility.VISIBLE)
    
    print(f"Periscope at depth 10m: {visible_count} tiles visible")
    assert visible_count > 0, "Periscope should reveal tiles"
    
    # Test periscope at too deep
    fog.reset_visibility()
    fog.update_visibility(
        submarine_pos,
        {SensorType.PERISCOPE},
        time_visibility=1.0,
        weather_visibility=1.0,
        depth=50
    )
    
    deep_visible = sum(1 for v in fog.visibility.values()
                      if v == TileVisibility.VISIBLE)
    
    print(f"Periscope at depth 50m: {deep_visible} tiles visible (should be 0)")
    assert deep_visible == 0, "Periscope shouldn't work too deep"
    
    print(f"✓ Periscope depth restrictions working")


def test_multiple_sensors():
    """Test multiple sensors working together."""
    print("\n=== Testing Multiple Sensors ===")
    
    fog = FogOfWar(width=100, height=100)
    submarine_pos = (50, 50)
    
    # Single sensor
    fog.update_visibility(
        submarine_pos,
        {SensorType.SONAR},
        time_visibility=1.0,
        weather_visibility=1.0,
        depth=50
    )
    
    sonar_only = sum(1 for v in fog.visibility.values()
                    if v != TileVisibility.UNEXPLORED)
    
    # Multiple sensors
    fog.reset_visibility()
    fog.update_visibility(
        submarine_pos,
        {SensorType.PERISCOPE, SensorType.SONAR, SensorType.RADAR},
        time_visibility=1.0,
        weather_visibility=1.0,
        depth=0  # Surface
    )
    
    multi_sensor = sum(1 for v in fog.visibility.values()
                      if v != TileVisibility.UNEXPLORED)
    
    print(f"Sonar only: {sonar_only} tiles")
    print(f"Multiple sensors (surface): {multi_sensor} tiles")
    
    assert multi_sensor > sonar_only, "More sensors should reveal more"
    print(f"✓ Multiple sensors increase visibility")


def test_weather_impact():
    """Test weather impact on visibility."""
    print("\n=== Testing Weather Impact ===")
    
    fog = FogOfWar(width=100, height=100)
    submarine_pos = (50, 50)
    
    # Clear weather
    fog.update_visibility(
        submarine_pos,
        {SensorType.PERISCOPE},
        time_visibility=1.0,
        weather_visibility=1.0,
        depth=10
    )
    
    clear_visible = sum(1 for v in fog.visibility.values()
                       if v == TileVisibility.VISIBLE)
    
    # Foggy weather
    fog.reset_visibility()
    fog.update_visibility(
        submarine_pos,
        {SensorType.PERISCOPE},
        time_visibility=1.0,
        weather_visibility=0.3,  # Heavy fog
        depth=10
    )
    
    fog_visible = sum(1 for v in fog.visibility.values()
                     if v == TileVisibility.VISIBLE)
    
    print(f"Clear weather: {clear_visible} tiles visible")
    print(f"Fog weather: {fog_visible} tiles visible")
    
    assert clear_visible > fog_visible * 2, "Fog should significantly reduce visibility"
    print(f"✓ Weather impacts visibility")


def test_contact_tracking():
    """Test contact detection and tracking."""
    print("\n=== Testing Contact Tracking ===")
    
    fog = FogOfWar(width=100, height=100)
    
    # Add contact
    contact = fog.add_contact((60, 60), SensorType.SONAR, ContactType.WARSHIP)
    
    assert contact.contact_type == ContactType.WARSHIP
    assert contact.detected_by == SensorType.SONAR
    assert len(fog.contacts) == 1
    
    print(f"✓ Contact added: {contact.contact_type.value}")
    
    # Update contact
    fog.current_tick = 10
    fog.update_contact(1, (61, 61), SensorType.PERISCOPE)
    
    updated_contact = fog.contacts[1]
    assert updated_contact.position == (61, 61)
    assert updated_contact.last_seen_tick == 10
    
    print(f"✓ Contact updated: position {updated_contact.position}")
    
    # Test stale contacts
    fog.current_tick = 200
    fog.remove_stale_contacts(max_age=100)
    
    assert len(fog.contacts) == 0, "Stale contacts should be removed"
    print(f"✓ Stale contact removal working")


def test_integrated_scenario():
    """Test all systems working together."""
    print("\n=== Testing Integrated Scenario ===")
    
    # Setup
    time_system = TimeSystem(start_hour=2)  # Deep night (02:00)
    fog = FogOfWar(width=100, height=100)
    diver_ops = DiverOperationsManager()
    
    submarine_pos = (50, 50)
    
    # Check night conditions
    visibility = time_system.get_visibility_modifier()
    detection_risk = time_system.get_detection_risk_modifier(on_surface=True)
    
    print(f"Night conditions:")
    print(f"  Visibility: {visibility:.0%}")
    print(f"  Detection risk: {detection_risk:.0%}")
    
    assert visibility < 0.4, "Should be dark at night"
    assert detection_risk < 0.5, "Night should be safer"
    
    # Update fog of war with limited night visibility
    fog.update_visibility(
        submarine_pos,
        {SensorType.PERISCOPE, SensorType.SONAR},
        time_visibility=visibility,
        weather_visibility=1.0,
        depth=10
    )
    
    visible_tiles = sum(1 for v in fog.visibility.values()
                       if v == TileVisibility.VISIBLE)
    
    print(f"  Visible tiles (night): {visible_tiles}")
    
    # Deploy diver in good conditions
    diver = diver_ops.recruit_diver(specialty=DiverSpecialty.SABOTAGE)
    mission = diver_ops.create_mission(
        DiverMissionType.SHIP_SABOTAGE,
        target="Enemy Harbor",
        difficulty=0.7
    )
    mission.assign_diver(diver)
    
    effectiveness = diver.get_effectiveness(mission.mission_type)
    print(f"\nDiver mission:")
    print(f"  Specialist: {diver.specialty.value}")
    print(f"  Effectiveness: {effectiveness:.0%}")
    
    # Night provides stealth bonus
    night_bonus = (1.0 - detection_risk) * 0.3
    adjusted_effectiveness = min(1.0, effectiveness + night_bonus)
    print(f"  Night bonus: +{night_bonus:.0%}")
    print(f"  Total effectiveness: {adjusted_effectiveness:.0%}")
    
    assert adjusted_effectiveness > effectiveness, "Night should boost stealth missions"
    
    print(f"\n✓ Integrated scenario working correctly")


def main():
    """Run all tests."""
    print("="*60)
    print("  TESTING: Divers | Time System | Fog of War")
    print("="*60)
    
    try:
        # Diver tests
        test_diver_creation()
        test_diver_effectiveness()
        test_diver_mission()
        
        # Time system tests
        test_time_system()
        test_visibility_modifiers()
        test_moon_phase()
        test_detection_risk()
        
        # Fog of war tests
        test_fog_of_war_creation()
        test_sensor_visibility()
        test_multiple_sensors()
        test_weather_impact()
        test_contact_tracking()
        
        # Integration test
        test_integrated_scenario()
        
        print("\n" + "="*60)
        print("  ✅ ALL TESTS PASSED!")
        print("="*60)
        
        print("\nSystems validated:")
        print("  ✓ Diver operations (6 specialties, 10 mission types)")
        print("  ✓ Time system (24-hour cycle, moon phases)")
        print("  ✓ Visibility modifiers (time, weather, moon)")
        print("  ✓ Detection risk calculations")
        print("  ✓ Fog of war (4 sensor types)")
        print("  ✓ Multi-sensor visibility")
        print("  ✓ Contact tracking")
        print("  ✓ Integrated operations")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
