#!/usr/bin/env python3
"""
Test script for the new tactical UI panels.
Demonstrates time system, diver operations, and sensor panels.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.time_system import TimeSystem, TimeOfDay, Season
from engine.fog_of_war import FogOfWar, SensorType, ContactType
from submarine.divers import DiverOperationsManager, DiverSpecialty, DiverMissionType
from ui.tactical_panels import TacticalPanels

class MockGame:
    """Mock game object for testing panels."""
    
    def __init__(self):
        # Initialize time system at dawn
        self.time_system = TimeSystem(start_hour=6, start_minute=0, start_day=1, season=Season.SUMMER)
        
        # Initialize fog of war (100x100 map)
        self.fog_of_war = FogOfWar(width=100, height=100)
        
        # Initialize diver operations
        self.diver_ops = DiverOperationsManager()
        
        # Active sensors
        self.active_sensors = {SensorType.SONAR, SensorType.PERISCOPE}
        
        # Mock submarine position
        self.submarine = type('MockSubmarine', (), {'x': 50, 'y': 50})()
        
        # Recruit some divers
        self.diver_ops.recruit_diver(specialty=DiverSpecialty.RECONNAISSANCE)
        self.diver_ops.recruit_diver(specialty=DiverSpecialty.SABOTAGE)
        self.diver_ops.recruit_diver(specialty=DiverSpecialty.RESCUE)
        
        # Launch a test mission
        mission = self.diver_ops.create_mission(
            DiverMissionType.HARBOR_RECON,
            target="Scapa Flow",
            difficulty=0.6
        )
        available = self.diver_ops.get_available_divers()
        if available:
            mission.assign_diver(available[0])
            self.diver_ops.launch_mission(mission)
        
        # Add some mock contacts to fog of war
        self.fog_of_war.add_contact(
            position=(55, 50),
            sensor=SensorType.PERISCOPE,
            contact_type=ContactType.MERCHANT
        )
        self.fog_of_war.add_contact(
            position=(45, 55),
            sensor=SensorType.SONAR,
            contact_type=ContactType.WARSHIP
        )
        
        # Update fog of war visibility
        self.fog_of_war.update_visibility(
            submarine_pos=(50, 50),
            active_sensors=self.active_sensors,
            time_visibility=0.5,  # Dawn visibility
            weather_visibility=1.0,
            depth=15
        )


def test_individual_panels():
    """Test each panel individually."""
    print("=" * 80)
    print("TESTING INDIVIDUAL TACTICAL PANELS")
    print("=" * 80)
    print()
    
    game = MockGame()
    
    # Test time panel
    print("1. TIME PANEL (Dawn)")
    print("-" * 80)
    print(TacticalPanels.render_time_panel(game))
    print()
    
    input("Press Enter to advance to noon...")
    print()
    
    # Advance time to noon
    for _ in range(72):  # 6 hours = 72 ticks (5 min per tick)
        game.time_system.tick()
    
    print("2. TIME PANEL (Noon)")
    print("-" * 80)
    print(TacticalPanels.render_time_panel(game))
    print()
    
    input("Press Enter to continue...")
    print()
    
    # Test diver panel
    print("3. DIVER OPERATIONS PANEL")
    print("-" * 80)
    print(TacticalPanels.render_diver_panel(game))
    print()
    
    input("Press Enter to continue...")
    print()
    
    # Test sensor panel
    print("4. SENSOR STATUS PANEL")
    print("-" * 80)
    print(TacticalPanels.render_sensor_panel(game))
    print()
    
    input("Press Enter to continue...")
    print()


def test_combined_display():
    """Test the combined tactical display (all three panels side by side)."""
    print("=" * 120)
    print("TESTING COMBINED TACTICAL DISPLAY")
    print("=" * 120)
    print()
    
    game = MockGame()
    
    # Advance to evening for more interesting display
    for _ in range(168):  # 14 hours
        game.time_system.tick()
    
    print(TacticalPanels.render_combined_tactical_display(game))
    print()
    
    input("Press Enter to continue...")
    print()


def test_compact_status_bar():
    """Test the compact status bar."""
    print("=" * 80)
    print("TESTING COMPACT STATUS BAR")
    print("=" * 80)
    print()
    
    game = MockGame()
    
    print("Compact Status Bar:")
    print(TacticalPanels.render_compact_status_bar(game))
    print()
    
    input("Press Enter to continue...")
    print()


def test_help_displays():
    """Test the help displays."""
    print("=" * 80)
    print("TESTING HELP DISPLAYS")
    print("=" * 80)
    print()
    
    print("1. DIVER OPERATIONS HELP")
    print("-" * 80)
    print(TacticalPanels.show_diver_mission_help())
    print()
    
    input("Press Enter to continue...")
    print()
    
    print("2. SENSOR SYSTEMS HELP")
    print("-" * 80)
    print(TacticalPanels.show_sensor_help())
    print()
    
    input("Press Enter to continue...")
    print()
    
    print("3. TIME SYSTEM HELP")
    print("-" * 80)
    print(TacticalPanels.show_time_help())
    print()


def test_time_progression():
    """Test time progression through a full day."""
    print("=" * 80)
    print("TESTING TIME PROGRESSION (Full 24-hour cycle)")
    print("=" * 80)
    print()
    
    game = MockGame()
    
    # Show panels at key times throughout the day
    times_to_show = [
        (0, "NIGHT (00:00)"),
        (36, "DAWN (03:00)"),
        (72, "MORNING (06:00)"),
        (144, "NOON (12:00)"),
        (216, "AFTERNOON (18:00)"),
        (252, "DUSK (21:00)"),
        (276, "EVENING (23:00)")
    ]
    
    for tick_count, label in times_to_show:
        # Advance to the target time
        while game.time_system.hour * 12 + game.time_system.minute // 5 < tick_count:
            game.time_system.tick()
        
        print(f"\n{label}")
        print("-" * 80)
        print(TacticalPanels.render_time_panel(game))
        print()
        
        if label != times_to_show[-1][1]:  # Don't wait after last
            input("Press Enter for next time period...")


def test_mission_progress():
    """Test diver mission progress over time."""
    print("=" * 80)
    print("TESTING DIVER MISSION PROGRESS")
    print("=" * 80)
    print()
    
    game = MockGame()
    
    print("Initial State:")
    print(TacticalPanels.render_diver_panel(game))
    print()
    
    input("Press Enter to advance mission...")
    print()
    
    # Progress mission
    for i in range(10):
        events = game.diver_ops.tick_missions()
        
        if events:
            print(f"\nTurn {i + 1}:")
            for event in events:
                print(f"  - {event['message']}")
            
            print()
            print(TacticalPanels.render_diver_panel(game))
            print()
            
            input("Press Enter to continue...")
            print()
        else:
            # Just advance quietly
            pass


def main():
    """Run all tests."""
    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║        TACTICAL UI PANELS - INTERACTIVE TEST SUITE             ║")
    print("║                                                                ║")
    print("║  This script demonstrates the new tactical UI panels:         ║")
    print("║    • Time & Environmental Conditions                           ║")
    print("║    • Diver Operations Status                                   ║")
    print("║    • Sensor & Fog of War Status                                ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    
    tests = [
        ("Individual Panels", test_individual_panels),
        ("Combined Tactical Display", test_combined_display),
        ("Compact Status Bar", test_compact_status_bar),
        ("Help Displays", test_help_displays),
        ("Time Progression", test_time_progression),
        ("Mission Progress", test_mission_progress)
    ]
    
    print("Select a test to run:")
    for i, (name, _) in enumerate(tests, 1):
        print(f"  {i}. {name}")
    print(f"  {len(tests) + 1}. Run all tests")
    print()
    
    try:
        choice = input("Enter choice (1-{}): ".format(len(tests) + 1))
        choice = int(choice)
        
        if choice == len(tests) + 1:
            # Run all tests
            for name, test_func in tests:
                print()
                test_func()
        elif 1 <= choice <= len(tests):
            # Run selected test
            tests[choice - 1][1]()
        else:
            print("Invalid choice.")
    except (ValueError, KeyboardInterrupt):
        print("\nExiting.")


if __name__ == '__main__':
    main()
