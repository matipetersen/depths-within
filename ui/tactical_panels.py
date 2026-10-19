"""
UI panels for displaying new tactical systems (time, divers, fog of war).
"""

from engine.time_system import TimeOfDay
from submarine.divers import DiverMissionStatus
from engine.fog_of_war import SensorType


class TacticalPanels:
    """Renders panels for time, diver operations, and sensor status."""
    
    @staticmethod
    def render_time_panel(game):
        """Render time and environmental conditions panel."""
        if not game.time_system:
            return "Time system not available"
        
        time_info = game.time_system.get_time_info()
        
        # Create panel
        lines = []
        lines.append("╔═══════════════════════════════════╗")
        lines.append("║    TIME & CONDITIONS              ║")
        lines.append("╠═══════════════════════════════════╣")
        
        # Time display
        time_str = time_info['time']
        date_str = time_info['date']
        tod = time_info['time_of_day'].upper()
        
        # Time icon based on period
        time_icons = {
            'night': '🌙',
            'dawn': '🌅',
            'morning': '☀️',
            'noon': '☀️',
            'afternoon': '☀️',
            'dusk': '🌇',
            'evening': '🌙'
        }
        icon = time_icons.get(time_info['time_of_day'], '⏰')
        
        lines.append(f"║ {icon} {time_str} - {date_str:<14} ║")
        lines.append(f"║ Period: {tod:<24} ║")
        lines.append("║                                   ║")
        
        # Moon phase
        moon = time_info['moon_phase'].replace('_', ' ').title()
        moon_illum = time_info['moon_illumination']
        lines.append(f"║ Moon: {moon:<15} {moon_illum:>4.0%} ║")
        
        # Visibility and detection
        visibility = time_info['visibility']
        detection_risk = time_info['detection_risk']
        
        # Visibility bar
        vis_bars = int(visibility * 20)
        vis_bar = '█' * vis_bars + '░' * (20 - vis_bars)
        lines.append(f"║ Visibility: [{vis_bar}] ║")
        
        # Detection risk bar
        risk_bars = int(detection_risk * 20)
        risk_bar = '█' * risk_bars + '░' * (20 - risk_bars)
        lines.append(f"║ Detection:  [{risk_bar}] ║")
        
        lines.append("║                                   ║")
        
        # Tactical assessment
        is_safe, reason = game.time_system.is_good_time_for_surface()
        periscope_range = game.time_system.get_periscope_range('clear')
        
        if detection_risk < 0.3:
            status = "✓ SAFE"
            color_marker = "G"
        elif detection_risk < 0.6:
            status = "⚠ CAUTION"
            color_marker = "Y"
        else:
            status = "✗ DANGER"
            color_marker = "R"
        
        lines.append(f"║ Surface: {status:<23} ║")
        lines.append(f"║ Periscope Range: {periscope_range:>4.1f} km      ║")
        
        lines.append("╚═══════════════════════════════════╝")
        
        return '\n'.join(lines)
    
    @staticmethod
    def render_diver_panel(game):
        """Render diver operations panel."""
        if not game.diver_ops:
            return "Diver operations not available"
        
        lines = []
        lines.append("╔═══════════════════════════════════╗")
        lines.append("║    DIVER OPERATIONS               ║")
        lines.append("╠═══════════════════════════════════╣")
        
        # Available divers
        available = game.diver_ops.get_available_divers()
        total = len(game.diver_ops.divers)
        
        lines.append(f"║ Available: {len(available):>2}/{total:<2}               ║")
        lines.append("║                                   ║")
        
        # Show divers
        if game.diver_ops.divers:
            lines.append("║ Personnel:                        ║")
            for diver in game.diver_ops.divers[:3]:  # Show first 3
                specialty = diver.specialty.value[:12]
                status = "READY" if diver.available else "BUSY"
                fatigue = int(diver.fatigue * 100)
                lines.append(f"║  {diver.name[:12]:<12} {specialty:<12} ║")
                lines.append(f"║   Status: {status:<8} Fatigue: {fatigue:>3}% ║")
            
            if total > 3:
                lines.append(f"║   ... and {total - 3} more                ║")
        else:
            lines.append("║ No divers recruited               ║")
            lines.append("║ Use: recruit_diver <specialty>    ║")
        
        lines.append("║                                   ║")
        
        # Active missions
        if game.diver_ops.active_missions:
            lines.append("║ Active Missions:                  ║")
            for mission in game.diver_ops.active_missions[:2]:
                mission_type = mission.mission_type.value.replace('_', ' ')[:16]
                progress = int(mission.progress * 100)
                lines.append(f"║  {mission_type:<16} {progress:>3}%       ║")
        else:
            lines.append("║ No active missions                ║")
        
        # Completed missions
        completed_count = len(game.diver_ops.completed_missions)
        if completed_count > 0:
            lines.append("║                                   ║")
            lines.append(f"║ Completed Missions: {completed_count:>2}           ║")
        
        lines.append("╚═══════════════════════════════════╝")
        
        return '\n'.join(lines)
    
    @staticmethod
    def render_sensor_panel(game):
        """Render sensor and fog of war panel."""
        if not game.fog_of_war:
            return "Fog of war system not available"
        
        lines = []
        lines.append("╔═══════════════════════════════════╗")
        lines.append("║    SENSOR STATUS                  ║")
        lines.append("╠═══════════════════════════════════╣")
        
        # Active sensors
        lines.append("║ Active Sensors:                   ║")
        
        sensors = [
            (SensorType.PERISCOPE, "Periscope", "Visual"),
            (SensorType.SONAR, "Sonar", "Acoustic"),
            (SensorType.RADAR, "Radar", "Surface"),
            (SensorType.HYDROPHONE, "Hydrophone", "Passive")
        ]
        
        for sensor_type, name, desc in sensors:
            status = "ON " if sensor_type in game.active_sensors else "OFF"
            marker = "●" if sensor_type in game.active_sensors else "○"
            lines.append(f"║  {marker} {name:<12} {status:<4} {desc:<8} ║")
        
        lines.append("║                                   ║")
        
        # Get sensor info
        sub_pos = (game.submarine.x, game.submarine.y) if game.submarine else (0, 0)
        sensor_info = game.fog_of_war.get_sensor_display_info(sub_pos)
        
        # Contacts
        contact_count = sensor_info['contacts_count']
        visible_tiles = sensor_info['visible_tiles']
        exploration = game.fog_of_war.get_exploration_percentage()
        
        lines.append(f"║ Contacts: {contact_count:>2}                      ║")
        lines.append(f"║ Visible Tiles: {visible_tiles:>4}              ║")
        lines.append(f"║ Map Explored: {exploration:>5.1f}%             ║")
        
        # Show contacts
        if sensor_info['contacts']:
            lines.append("║                                   ║")
            lines.append("║ Tracked Contacts:                 ║")
            
            for contact in sensor_info['contacts'][:3]:  # Show first 3
                ctype = contact['type'][:10]
                bearing = int(contact['bearing'])
                dist = contact['distance']
                conf = int(contact['confidence'] * 100)
                
                lines.append(f"║  {ctype:<10} {bearing:>3}° {dist:>4.1f}km {conf:>3}%   ║")
        
        lines.append("╚═══════════════════════════════════╝")
        
        return '\n'.join(lines)
    
    @staticmethod
    def render_combined_tactical_display(game):
        """Render all three panels side by side."""
        time_panel = TacticalPanels.render_time_panel(game)
        diver_panel = TacticalPanels.render_diver_panel(game)
        sensor_panel = TacticalPanels.render_sensor_panel(game)
        
        # Split into lines
        time_lines = time_panel.split('\n')
        diver_lines = diver_panel.split('\n')
        sensor_lines = sensor_panel.split('\n')
        
        # Combine side by side
        max_lines = max(len(time_lines), len(diver_lines), len(sensor_lines))
        
        combined = []
        for i in range(max_lines):
            line = ""
            if i < len(time_lines):
                line += time_lines[i]
            else:
                line += " " * 37
            
            line += "  "  # Spacing
            
            if i < len(diver_lines):
                line += diver_lines[i]
            else:
                line += " " * 37
            
            line += "  "  # Spacing
            
            if i < len(sensor_lines):
                line += sensor_lines[i]
            
            combined.append(line)
        
        return '\n'.join(combined)
    
    @staticmethod
    def render_compact_status_bar(game):
        """Render a compact single-line status bar with key info."""
        parts = []
        
        # Time
        if game.time_system:
            time_info = game.time_system.get_time_info()
            time_str = time_info['time']
            tod = time_info['time_of_day'][:4].upper()
            vis = int(time_info['visibility'] * 100)
            parts.append(f"⏰{time_str} {tod} Vis:{vis}%")
        
        # Divers
        if game.diver_ops:
            available = len(game.diver_ops.get_available_divers())
            total = len(game.diver_ops.divers)
            active_missions = len(game.diver_ops.active_missions)
            parts.append(f"👤{available}/{total} 🎯{active_missions}")
        
        # Sensors
        if game.fog_of_war:
            sub_pos = (game.submarine.x, game.submarine.y) if game.submarine else (0, 0)
            sensor_info = game.fog_of_war.get_sensor_display_info(sub_pos)
            contacts = sensor_info['contacts_count']
            sensor_count = len(game.active_sensors)
            parts.append(f"📡{sensor_count} 🎯{contacts}")
        
        return " │ ".join(parts)
    
    @staticmethod
    def show_diver_mission_help():
        """Show help for diver missions."""
        help_text = """
╔═══════════════════════════════════════════════════════════════╗
║                    DIVER OPERATIONS HELP                      ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ COMMANDS:                                                     ║
║   recruit_diver [specialty]  - Recruit a new diver           ║
║   diver_mission <type> <target> [difficulty]                 ║
║                              - Launch diver mission           ║
║   divers                     - Show diver status              ║
║                                                               ║
║ SPECIALIZATIONS:                                              ║
║   reconnaissance  - Scout enemy positions, gather intel       ║
║   sabotage        - Plant limpet mines, damage ships          ║
║   rescue          - Recover downed pilots, stranded crew      ║
║   infiltration    - Harbor penetration, facility entry        ║
║   demolition      - Underwater demolition, clear obstacles    ║
║   combat          - Underwater combat specialist              ║
║                                                               ║
║ MISSION TYPES:                                                ║
║   harbor_recon           - Scout harbor defenses              ║
║   ship_sabotage          - Plant limpet mines on ships        ║
║   net_cutting            - Cut anti-submarine nets            ║
║   beach_recon            - Coastal reconnaissance             ║
║   pilot_rescue           - Recover downed aircrew             ║
║   mine_placement         - Place mines in shipping lanes      ║
║   facility_infiltration  - Shore facility entry               ║
║   wreck_salvage          - Salvage from sunken ships          ║
║   cable_cutting          - Cut underwater cables              ║
║   obstacle_clearing      - Clear underwater obstacles         ║
║                                                               ║
║ EXAMPLES:                                                     ║
║   recruit_diver sabotage                                      ║
║   diver_mission harbor_recon "Scapa Flow" 0.7                ║
║   diver_mission ship_sabotage "Brest Harbor" 0.8             ║
║                                                               ║
║ TIPS:                                                         ║
║   • Night operations have lower detection risk                ║
║   • Specialists are more effective at matching missions       ║
║   • Check time status before launching missions               ║
║   • Divers gain fatigue - let them rest between missions      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
        return help_text
    
    @staticmethod
    def show_sensor_help():
        """Show help for sensor systems."""
        help_text = """
╔═══════════════════════════════════════════════════════════════╗
║                     SENSOR SYSTEMS HELP                       ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ COMMANDS:                                                     ║
║   sensor <type>   - Toggle sensor on/off                      ║
║   sensors         - Show sensor status                        ║
║                                                               ║
║ SENSOR TYPES:                                                 ║
║                                                               ║
║   PERISCOPE                                                   ║
║     • Visual detection                                        ║
║     • Range: 15 tiles (time/weather dependent)                ║
║     • Requires: Depth ≤ 15m                                   ║
║     • Best for: Visual identification, daylight               ║
║                                                               ║
║   SONAR                                                       ║
║     • Acoustic detection                                      ║
║     • Range: 30 tiles (omnidirectional)                       ║
║     • Works at: Any depth                                     ║
║     • Best for: Underwater detection, limited detail          ║
║                                                               ║
║   RADAR                                                       ║
║     • Surface contacts                                        ║
║     • Range: 50 tiles (weather independent)                   ║
║     • Requires: Surface (depth = 0m)                          ║
║     • Best for: Long-range surface detection                  ║
║                                                               ║
║   HYDROPHONE                                                  ║
║     • Passive acoustic listening                              ║
║     • Range: 60 tiles (very long range)                       ║
║     • Works at: Any depth                                     ║
║     • Best for: Silent detection, gives less detail           ║
║                                                               ║
║ FOG OF WAR:                                                   ║
║   • Unexplored - Never seen                                   ║
║   • Explored - Seen before, not currently visible             ║
║   • Visible - Currently in visual range                       ║
║   • Sonar - Detected acoustically                             ║
║                                                               ║
║ EXAMPLES:                                                     ║
║   sensor periscope    - Toggle periscope                      ║
║   sensor sonar        - Toggle sonar                          ║
║   sensor radar        - Toggle radar                          ║
║                                                               ║
║ TIPS:                                                         ║
║   • Multiple sensors reveal more                              ║
║   • Daylight increases periscope range                        ║
║   • Fog/weather reduces visual sensors                        ║
║   • Sonar works better at certain depths                      ║
║   • Contacts become stale if not re-detected                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
        return help_text
    
    @staticmethod
    def show_time_help():
        """Show help for time system."""
        help_text = """
╔═══════════════════════════════════════════════════════════════╗
║                       TIME SYSTEM HELP                        ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ COMMANDS:                                                     ║
║   time            - Show current time and conditions          ║
║                                                               ║
║ TIME PERIODS:                                                 ║
║   Night (00:00-05:59)    - 5-20% visibility, safest          ║
║   Dawn (06:00-07:59)     - 50% visibility                     ║
║   Morning (08:00-11:59)  - 100% visibility                    ║
║   Noon (12:00-13:59)     - 100% visibility, most dangerous    ║
║   Afternoon (14:00-17:59)- 100% visibility                    ║
║   Dusk (18:00-19:59)     - 50% visibility                     ║
║   Evening (20:00-23:59)  - 15-30% visibility                  ║
║                                                               ║
║ MOON PHASES:                                                  ║
║   New Moon        - 0% illumination (darkest nights)          ║
║   Waxing Crescent - 25% illumination                          ║
║   First Quarter   - 50% illumination                          ║
║   Waxing Gibbous  - 75% illumination                          ║
║   Full Moon       - 100% illumination (brightest nights)      ║
║   Waning phases   - Decreasing illumination                   ║
║                                                               ║
║ VISIBILITY:                                                   ║
║   • Affects periscope range                                   ║
║   • Modified by time of day                                   ║
║   • Moon adds up to 30% at night                              ║
║   • Weather further reduces visibility                        ║
║                                                               ║
║ DETECTION RISK:                                               ║
║   • Very high during day (90-100%)                            ║
║   • Low at night (20-35%)                                     ║
║   • Moderate during dawn/dusk (50%)                           ║
║   • Full moon increases night risk                            ║
║   • Always low when submerged (10%)                           ║
║                                                               ║
║ TACTICAL IMPLICATIONS:                                        ║
║   NIGHT OPERATIONS                                            ║
║     ✓ Safe to surface                                         ║
║     ✓ Ideal for diver missions                                ║
║     ✓ Battery charging                                        ║
║     ⚠ Limited visual range                                    ║
║                                                               ║
║   DAY OPERATIONS                                              ║
║     ✓ Maximum periscope range                                 ║
║     ✓ Easy target identification                              ║
║     ⚠ Very dangerous to surface                               ║
║     ⚠ High detection risk                                     ║
║                                                               ║
║   DAWN/DUSK                                                   ║
║     • Balanced conditions                                     ║
║     • Good for transitioning depth                            ║
║     • Moderate risk                                           ║
║                                                               ║
║ TIPS:                                                         ║
║   • Plan sabotage for new moon nights                         ║
║   • Surface at night to charge batteries                      ║
║   • Use periscope attacks at dawn/dusk                        ║
║   • Stay deep during daylight                                 ║
║   • Time advances 5 minutes per game turn                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
        return help_text
