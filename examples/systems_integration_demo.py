"""
Integration example for divers, time system, and fog of war.
Demonstrates how these systems work together in gameplay.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from submarine.divers import (
    Diver, DiverSpecialty, DiverMission, DiverMissionType,
    DiverOperationsManager
)
from engine.time_system import TimeSystem, TimeOfDay
from engine.fog_of_war import (
    FogOfWar, SensorType, ContactType, TileVisibility
)


def print_separator(title: str):
    """Print section separator."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def scenario_1_diver_operations():
    """Scenario: Night harbor reconnaissance mission."""
    print_separator("SCENARIO 1: Night Harbor Reconnaissance")
    
    # Initialize systems
    time_system = TimeSystem(start_hour=22, start_minute=0)  # 22:00 (night)
    diver_ops = DiverOperationsManager()
    
    print("\n1. Current Conditions:")
    print(time_system.get_ui_display())
    
    # Recruit reconnaissance specialist
    print("\n2. Recruiting Combat Diver:")
    diver = diver_ops.recruit_diver(specialty=DiverSpecialty.RECONNAISSANCE)
    print(f"   ✓ Recruited: {diver.name}")
    print(f"   Specialty: {diver.specialty.value}")
    print(f"   Stealth Skill: {diver.skills['stealth']:.0%}")
    print(f"   Swimming Skill: {diver.skills['swimming']:.0%}")
    
    # Create harbor recon mission
    print("\n3. Planning Mission:")
    mission = diver_ops.create_mission(
        DiverMissionType.HARBOR_RECON,
        target="Scapa Flow Naval Base",
        difficulty=0.7
    )
    
    print(mission.get_mission_info())
    
    # Assign diver
    mission.assign_diver(diver)
    effectiveness = diver.get_effectiveness(mission.mission_type)
    print(f"\n   Diver Effectiveness: {effectiveness:.0%}")
    
    # Check if good time for mission
    is_good, reason = time_system.is_good_time_for_surface()
    detection_risk = time_system.get_detection_risk_modifier(on_surface=True)
    print(f"\n   Surface Conditions: {reason}")
    print(f"   Detection Risk: {detection_risk:.0%}")
    
    # Launch mission
    print("\n4. Launching Mission...")
    diver_ops.launch_mission(mission)
    
    # Simulate mission
    print("\n5. Mission Progress:")
    for tick in range(10):
        events = diver_ops.tick_missions()
        
        if tick % 3 == 0:
            print(f"   Tick {tick}: {mission.progress:.0%} complete, "
                  f"Diver fatigue: {diver.fatigue:.0%}")
        
        if events:
            for event in events:
                print(f"\n{event['message']}")
                if event['intelligence']:
                    intel = event['intelligence']
                    print(f"\n   Intelligence Gathered:")
                    for key, value in intel.items():
                        print(f"     {key}: {value}")


def scenario_2_day_night_cycle():
    """Scenario: 24-hour patrol with changing visibility."""
    print_separator("SCENARIO 2: 24-Hour Patrol - Day/Night Cycle")
    
    time_system = TimeSystem(start_hour=6, start_minute=0)  # Dawn
    
    print("\n1. Starting Dawn Patrol:")
    print(time_system.get_ui_display())
    
    # Simulate 24 hours
    print("\n2. Time Progression (every 3 hours):")
    
    key_times = [6, 9, 12, 15, 18, 21, 0, 3]
    
    for target_hour in key_times:
        time_system.advance_to_time(target_hour)
        
        tod = time_system.get_time_of_day()
        visibility = time_system.get_visibility_modifier()
        detection_risk = time_system.get_detection_risk_modifier(on_surface=True)
        periscope_range = time_system.get_periscope_range('clear')
        
        print(f"\n   {time_system.get_time_string()} - {tod.value.upper()}")
        print(f"     Visibility: {visibility:.0%}")
        print(f"     Detection Risk (surface): {detection_risk:.0%}")
        print(f"     Periscope Range: {periscope_range:.1f} km")
        
        # Tactical recommendation
        if detection_risk < 0.3:
            print(f"     ✓ SAFE: Good time to surface for battery charge")
        elif detection_risk < 0.6:
            print(f"     ⚠ CAUTION: Moderate risk, stay alert")
        else:
            print(f"     ✗ DANGER: Remain submerged, high detection risk")


def scenario_3_fog_of_war():
    """Scenario: Fog of war with multiple sensors."""
    print_separator("SCENARIO 3: Sensor-Based Fog of War")
    
    # Initialize systems
    time_system = TimeSystem(start_hour=14, start_minute=0)  # Afternoon
    fog = FogOfWar(width=100, height=100)
    
    submarine_pos = (50, 50)  # Center of map
    
    print("\n1. Initial Conditions:")
    print(f"   Submarine Position: {submarine_pos}")
    print(f"   Time: {time_system.get_time_string()}")
    print(f"   Visibility: {time_system.get_visibility_modifier():.0%}")
    
    # Test different sensor configurations
    scenarios = [
        {
            'name': 'Periscope Depth (Daylight)',
            'sensors': {SensorType.PERISCOPE, SensorType.SONAR},
            'depth': 10,
            'weather': 'clear'
        },
        {
            'name': 'Periscope Depth (Fog)',
            'sensors': {SensorType.PERISCOPE, SensorType.SONAR},
            'depth': 10,
            'weather': 'fog'
        },
        {
            'name': 'Deep Dive (Sonar Only)',
            'sensors': {SensorType.SONAR, SensorType.HYDROPHONE},
            'depth': 100,
            'weather': 'clear'
        },
        {
            'name': 'Surface (All Sensors)',
            'sensors': {SensorType.PERISCOPE, SensorType.SONAR, SensorType.RADAR},
            'depth': 0,
            'weather': 'clear'
        },
    ]
    
    print("\n2. Testing Sensor Configurations:\n")
    
    for scenario in scenarios:
        print(f"   {scenario['name']}:")
        print(f"     Depth: {scenario['depth']}m")
        print(f"     Weather: {scenario['weather']}")
        print(f"     Active Sensors: {', '.join(s.value for s in scenario['sensors'])}")
        
        # Update fog of war
        visibility = time_system.get_visibility_modifier()
        weather_vis = 1.0 if scenario['weather'] == 'clear' else 0.3
        
        fog.update_visibility(
            submarine_pos,
            scenario['sensors'],
            time_visibility=visibility,
            weather_visibility=weather_vis,
            depth=scenario['depth']
        )
        
        # Count visible tiles
        visible_count = sum(1 for v in fog.visibility.values()
                          if v == TileVisibility.VISIBLE)
        sonar_count = sum(1 for v in fog.visibility.values()
                         if v == TileVisibility.SONAR_CONTACT)
        
        print(f"     Visible Tiles: {visible_count}")
        print(f"     Sonar Contacts: {sonar_count}")
        print(f"     Total Detection Area: {visible_count + sonar_count} tiles\n")


def scenario_4_combined_operations():
    """Scenario: Complete mission combining all systems."""
    print_separator("SCENARIO 4: Combined Night Sabotage Operation")
    
    # Initialize all systems
    time_system = TimeSystem(start_hour=2, start_minute=0)  # 02:00 (deep night)
    diver_ops = DiverOperationsManager()
    fog = FogOfWar(width=100, height=100)
    
    submarine_pos = (45, 55)
    target_harbor = (60, 65)
    
    print("\n1. Mission Briefing:")
    print(f"   Objective: Sabotage enemy ships in harbor")
    print(f"   Target: Brest Harbor")
    print(f"   Submarine Position: {submarine_pos}")
    print(f"   Target Position: {target_harbor}")
    print(time_system.get_ui_display())
    
    # Check conditions
    print("\n2. Conditions Assessment:")
    visibility = time_system.get_visibility_modifier()
    detection_risk = time_system.get_detection_risk_modifier(on_surface=True)
    moon_light = time_system.get_moon_illumination()
    
    print(f"   Visibility: {visibility:.0%}")
    print(f"   Moon Illumination: {moon_light:.0%}")
    print(f"   Detection Risk: {detection_risk:.0%}")
    
    if detection_risk < 0.3 and visibility < 0.4:
        print("   ✓ OPTIMAL: Dark conditions, low detection risk")
    else:
        print("   ⚠ SUBOPTIMAL: Consider waiting for better conditions")
    
    # Approach target with periscope up
    print("\n3. Approaching Target:")
    fog.update_visibility(
        submarine_pos,
        {SensorType.PERISCOPE, SensorType.SONAR},
        time_visibility=visibility,
        weather_visibility=1.0,
        depth=10
    )
    
    periscope_range = time_system.get_periscope_range('clear')
    print(f"   Periscope Range: {periscope_range:.1f} km (limited by darkness)")
    print(f"   Sonar Active: 30 km range")
    
    # Add enemy contacts
    print("\n4. Detecting Contacts:")
    contacts_data = [
        ((62, 67), ContactType.WARSHIP, "Destroyer"),
        ((58, 64), ContactType.MERCHANT, "Freighter"),
        ((61, 63), ContactType.COASTAL, "Patrol Boat"),
    ]
    
    for pos, ctype, name in contacts_data:
        contact = fog.add_contact(pos, SensorType.SONAR, ctype)
        print(f"   Contact: {name} at {pos} ({ctype.value})")
    
    # Deploy diver
    print("\n5. Deploying Combat Diver:")
    diver = diver_ops.recruit_diver(specialty=DiverSpecialty.SABOTAGE)
    print(f"   Diver: {diver.name}")
    print(f"   Demolition Skill: {diver.skills['demolition']:.0%}")
    print(f"   Stealth Skill: {diver.skills['stealth']:.0%}")
    
    # Create sabotage mission
    mission = diver_ops.create_mission(
        DiverMissionType.SHIP_SABOTAGE,
        target="Brest Harbor",
        difficulty=0.8
    )
    mission.assign_diver(diver)
    
    effectiveness = diver.get_effectiveness(mission.mission_type)
    print(f"   Mission Effectiveness: {effectiveness:.0%}")
    
    # Night bonus for stealth
    night_bonus = (1.0 - detection_risk) * 0.3
    adjusted_effectiveness = min(1.0, effectiveness + night_bonus)
    print(f"   Night Stealth Bonus: +{night_bonus:.0%}")
    print(f"   Total Effectiveness: {adjusted_effectiveness:.0%}")
    
    # Launch mission
    diver_ops.launch_mission(mission)
    
    print("\n6. Mission Execution:")
    print("   Diver deployed...")
    
    # Simulate mission
    for tick in range(8):
        events = diver_ops.tick_missions()
        
        if tick % 2 == 0:
            print(f"   Tick {tick}: {mission.progress:.0%} complete")
        
        if events:
            for event in events:
                print(f"\n{event['message']}")
                
                if event['success'] and event['intelligence']:
                    intel = event['intelligence']
                    print(f"\n   Mission Results:")
                    print(f"     Ships Damaged: {intel.get('ships_damaged', 0)}")
                    print(f"     Estimated Tonnage: {intel.get('estimated_tonnage', 0):,} tons")
                    print(f"     Detection: {intel.get('detection_risk', 'none')}")
    
    # Withdraw
    print("\n7. Withdrawal:")
    print("   Recovering diver...")
    print("   Diving to 100m...")
    print("   Setting course for home port")
    
    # Advance time
    time_system.tick()
    time_system.tick()
    print(f"   Current Time: {time_system.get_time_string()}")
    print(f"   ✓ Mission Complete!")


def main():
    """Run all scenarios."""
    print("\n" + "="*60)
    print("  DEPTHS WITHIN - NEW SYSTEMS DEMONSTRATION")
    print("  Divers | Day/Night Cycle | Fog of War")
    print("="*60)
    
    try:
        scenario_1_diver_operations()
        input("\n\nPress Enter to continue to next scenario...")
        
        scenario_2_day_night_cycle()
        input("\n\nPress Enter to continue to next scenario...")
        
        scenario_3_fog_of_war()
        input("\n\nPress Enter to continue to next scenario...")
        
        scenario_4_combined_operations()
        
        print_separator("DEMONSTRATION COMPLETE")
        print("\n✅ All systems working correctly!")
        print("\nKey Features Demonstrated:")
        print("  • Combat divers with specializations")
        print("  • Mission planning and execution")
        print("  • 24-hour day/night cycle")
        print("  • Time-based visibility modifiers")
        print("  • Sensor-based fog of war")
        print("  • Multi-sensor detection systems")
        print("  • Integrated tactical operations")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
