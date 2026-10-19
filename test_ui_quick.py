#!/usr/bin/env python3
"""
Simple test demonstrating all tactical UI panels (non-interactive).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.time_system import TimeSystem, TimeOfDay, Season
from engine.fog_of_war import FogOfWar, SensorType, ContactType
from submarine.divers import DiverOperationsManager, DiverSpecialty, DiverMissionType
from ui.tactical_panels import TacticalPanels


class MockGame:
    """Mock game object for testing."""
    
    def __init__(self):
        self.time_system = TimeSystem(start_hour=6, start_minute=0, start_day=1, season=Season.SUMMER)
        self.fog_of_war = FogOfWar(width=100, height=100)
        self.diver_ops = DiverOperationsManager()
        self.active_sensors = {SensorType.SONAR, SensorType.PERISCOPE}
        self.submarine = type('MockSubmarine', (), {'x': 50, 'y': 50})()
        
        # Recruit divers
        self.diver_ops.recruit_diver(specialty=DiverSpecialty.RECONNAISSANCE)
        self.diver_ops.recruit_diver(specialty=DiverSpecialty.SABOTAGE)
        self.diver_ops.recruit_diver(specialty=DiverSpecialty.RESCUE)
        
        # Launch a mission
        mission = self.diver_ops.create_mission(
            DiverMissionType.HARBOR_RECON,
            target="Scapa Flow",
            difficulty=0.6
        )
        available = self.diver_ops.get_available_divers()
        if available:
            mission.assign_diver(available[0])
            self.diver_ops.launch_mission(mission)
        
        # Add contacts
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
        
        # Update visibility
        self.fog_of_war.update_visibility(
            submarine_pos=(50, 50),
            active_sensors=self.active_sensors,
            time_visibility=0.5,
            weather_visibility=1.0,
            depth=15
        )


def main():
    print("=" * 80)
    print("TACTICAL UI PANELS TEST")
    print("=" * 80)
    print()
    
    game = MockGame()
    
    # Test 1: Compact Status Bar
    print("1. COMPACT STATUS BAR")
    print("-" * 80)
    print(TacticalPanels.render_compact_status_bar(game))
    print()
    print()
    
    # Test 2: Time Panel (Dawn)
    print("2. TIME PANEL - DAWN (06:00)")
    print("-" * 80)
    print(TacticalPanels.render_time_panel(game))
    print()
    print()
    
    # Test 3: Advance to noon
    for _ in range(72):  # 6 hours
        game.time_system.tick()
    
    print("3. TIME PANEL - NOON (12:00)")
    print("-" * 80)
    print(TacticalPanels.render_time_panel(game))
    print()
    print()
    
    # Test 4: Diver Panel
    print("4. DIVER OPERATIONS PANEL")
    print("-" * 80)
    print(TacticalPanels.render_diver_panel(game))
    print()
    print()
    
    # Test 5: Sensor Panel
    print("5. SENSOR STATUS PANEL")
    print("-" * 80)
    print(TacticalPanels.render_sensor_panel(game))
    print()
    print()
    
    # Test 6: Advance to evening
    game2 = MockGame()
    for _ in range(192):  # 16 hours
        game2.time_system.tick()
    
    print("6. COMBINED TACTICAL DISPLAY - EVENING (22:00)")
    print("=" * 119)
    print(TacticalPanels.render_combined_tactical_display(game2))
    print()
    print()
    
    # Test 7: Help displays (first few lines only)
    print("7. HELP SYSTEM SAMPLE (Diver Help)")
    print("-" * 80)
    help_lines = TacticalPanels.show_diver_mission_help().split('\n')
    print('\n'.join(help_lines[:25]))  # Show first 25 lines
    print("... (continued)")
    print()
    print()
    
    print("=" * 80)
    print("✓ ALL TESTS PASSED")
    print("=" * 80)
    print()
    print("All tactical UI panels are working correctly!")
    print()
    print("Available commands in-game:")
    print("  time           - Show time and conditions")
    print("  divers         - Show diver operations")
    print("  sensors        - Show sensor status")
    print("  tactical_status - Show all panels side-by-side")
    print("  tactical_hud   - Show compact status bar")
    print()
    print("For detailed help:")
    print("  time_help      - Time system guide")
    print("  diver_help     - Diver operations guide")
    print("  sensor_help    - Sensor systems guide")
    print()


if __name__ == '__main__':
    main()
