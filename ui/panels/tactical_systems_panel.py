"""
Tactical Systems Panel for displaying Time, Fog of War, and Diver Operations.
"""

from ui.color_system import _color_system


class TacticalSystemsPanel:
    """Display panel for new tactical systems."""
    
    @staticmethod
    def render_time_display(time_system, compact=False):
        """Render time and conditions display."""
        if not time_system:
            return "Time system not available"
        
        time_info = time_system.get_time_info()
        
        if compact:
            # Single line display
            time_str = time_info['time']
            tod = time_info['time_of_day'][:4].upper()
            vis = time_info['visibility']
            risk = time_info['detection_risk']
            
            # Icon for time of day
            tod_icon = {
                'night': '🌙',
                'dawn': '🌅',
                'morning': '☀️',
                'noon': '☀️',
                'afternoon': '☀️',
                'dusk': '🌇',
                'evening': '🌙'
            }.get(time_info['time_of_day'], '⏰')
            
            return f"{tod_icon} {time_str} {tod} | Vis:{vis:.0%} Risk:{risk:.0%}"
        else:
            # Full display
            output = []
            output.append(_color_system.header("═══ TIME & CONDITIONS ═══\n"))
            output.append(time_system.get_ui_display())
            
            # Add tactical recommendations
            is_safe, reason = time_system.is_good_time_for_surface()
            periscope_range = time_system.get_periscope_range('clear')
            
            if is_safe:
                output.append(_color_system.success(f"\n✓ Surface: {reason}"))
            else:
                output.append(_color_system.alert(f"\n✗ Surface: {reason}"))
            
            output.append(f"Periscope Range: {periscope_range:.1f} km\n")
            
            return ''.join(output)
    
    @staticmethod
    def render_sensor_display(fog_of_war, active_sensors, submarine_pos, compact=False):
        """Render sensor and fog of war display."""
        if not fog_of_war:
            return "Fog of war system not available"
        
        sensor_info = fog_of_war.get_sensor_display_info(submarine_pos)
        
        if compact:
            # Single line display
            sensor_str = ', '.join(s.value[:4].upper() for s in active_sensors) if active_sensors else 'NONE'
            contacts = sensor_info['contacts_count']
            explored = fog_of_war.get_exploration_percentage()
            
            return f"📡 Sensors: {sensor_str} | Contacts:{contacts} | Map:{explored:.0f}%"
        else:
            # Full display
            output = []
            output.append(_color_system.header("═══ SENSORS & CONTACTS ═══\n"))
            
            # Active sensors
            if active_sensors:
                sensor_list = ', '.join(_color_system.success(s.value.title()) for s in active_sensors)
                output.append(f"Active: {sensor_list}\n")
            else:
                output.append(_color_system.alert("Active: None\n"))
            
            # Statistics
            output.append(f"Contacts Tracked: {sensor_info['contacts_count']}\n")
            output.append(f"Visible Tiles: {sensor_info['visible_tiles']}\n")
            output.append(f"Map Explored: {fog_of_war.get_exploration_percentage():.1f}%\n")
            
            # Contacts list
            if sensor_info['contacts']:
                output.append(_color_system.subheader("\nContacts:\n"))
                for contact in sensor_info['contacts'][:8]:  # Show first 8
                    confidence_str = _color_system.success("HIGH") if contact['confidence'] > 0.7 else \
                                   _color_system.warning("MED") if contact['confidence'] > 0.4 else \
                                   _color_system.alert("LOW")
                    
                    output.append(f"  {contact['type']:10s} @ {contact['bearing']:03.0f}° "
                                f"({contact['distance']:.1f}km) [{confidence_str}]\n")
                
                if len(sensor_info['contacts']) > 8:
                    output.append(f"  ... and {len(sensor_info['contacts']) - 8} more\n")
            else:
                output.append("\nNo contacts detected\n")
            
            return ''.join(output)
    
    @staticmethod
    def render_diver_display(diver_ops, time_system=None, compact=False):
        """Render diver operations display."""
        if not diver_ops:
            return "Diver operations not available"
        
        available = diver_ops.get_available_divers()
        
        if compact:
            # Single line display
            total = len(diver_ops.divers)
            avail = len(available)
            active = len(diver_ops.active_missions)
            completed = len(diver_ops.completed_missions)
            
            return f"🤿 Divers: {avail}/{total} avail | Missions: {active} active, {completed} done"
        else:
            # Full display
            output = []
            output.append(_color_system.header("═══ DIVER OPERATIONS ═══\n"))
            
            # Diver status
            output.append(f"Available Divers: {len(available)}/{len(diver_ops.divers)}\n")
            
            # List available divers
            if available:
                output.append(_color_system.subheader("\nAvailable:\n"))
                for diver in available[:5]:  # Show first 5
                    fatigue_str = _color_system.success("Fresh") if diver.fatigue < 0.3 else \
                                _color_system.warning("Tired") if diver.fatigue < 0.7 else \
                                _color_system.alert("Exhausted")
                    
                    output.append(f"  {diver.name:15s} [{diver.specialty.value[:4].upper()}] "
                                f"{fatigue_str} | Stealth:{diver.skills['stealth']:.0%}\n")
            
            # Active missions
            if diver_ops.active_missions:
                output.append(_color_system.subheader(f"\nActive Missions: {len(diver_ops.active_missions)}\n"))
                for mission in diver_ops.active_missions:
                    progress = mission.progress * 100
                    status_color = _color_system.success if progress > 75 else \
                                 _color_system.warning if progress > 25 else \
                                 _color_system.neutral
                    
                    output.append(f"  {mission.mission_type.value.replace('_', ' ').title()}\n")
                    output.append(f"    Progress: {status_color(f'{progress:.0f}%')} | "
                                f"Risk: {mission.risk_level:.0%}\n")
                    
                    # Show night advantage if applicable
                    if time_system:
                        detection_risk = time_system.get_detection_risk_modifier(on_surface=True)
                        if detection_risk < 0.5:
                            night_bonus = (1.0 - detection_risk) * 0.3
                            output.append(f"    {_color_system.success(f'Night Bonus: +{night_bonus:.0%}')}\n")
            
            # Mission stats
            output.append(f"\nCompleted Missions: {len(diver_ops.completed_missions)}")
            if diver_ops.completed_missions:
                successful = sum(1 for m in diver_ops.completed_missions if m.success)
                success_rate = (successful / len(diver_ops.completed_missions)) * 100
                output.append(f" ({success_rate:.0f}% success rate)")
            output.append("\n")
            
            return ''.join(output)
    
    @staticmethod
    def render_combined_tactical_hud(game):
        """Render combined tactical HUD with all systems (compact format)."""
        output = []
        
        # Top bar: Time and conditions
        if game.time_system:
            output.append(TacticalSystemsPanel.render_time_display(game.time_system, compact=True))
            output.append("\n")
        
        # Second bar: Sensors and contacts
        if game.fog_of_war and game.submarine:
            sub_pos = (game.submarine.x, game.submarine.y)
            output.append(TacticalSystemsPanel.render_sensor_display(
                game.fog_of_war, 
                game.active_sensors, 
                sub_pos, 
                compact=True
            ))
            output.append("\n")
        
        # Third bar: Diver operations
        if game.diver_ops:
            output.append(TacticalSystemsPanel.render_diver_display(
                game.diver_ops, 
                game.time_system, 
                compact=True
            ))
            output.append("\n")
        
        return ''.join(output)
    
    @staticmethod
    def render_full_tactical_panel(game):
        """Render full detailed tactical panel."""
        output = []
        
        output.append(_color_system.header("\n╔" + "═" * 78 + "╗\n"))
        output.append(_color_system.header("║" + " " * 25 + "TACTICAL SYSTEMS STATUS" + " " * 30 + "║\n"))
        output.append(_color_system.header("╚" + "═" * 78 + "╝\n\n"))
        
        # Time system
        if game.time_system:
            output.append(TacticalSystemsPanel.render_time_display(game.time_system, compact=False))
            output.append("\n")
        
        # Sensor system
        if game.fog_of_war and game.submarine:
            sub_pos = (game.submarine.x, game.submarine.y)
            output.append(TacticalSystemsPanel.render_sensor_display(
                game.fog_of_war, 
                game.active_sensors, 
                sub_pos, 
                compact=False
            ))
            output.append("\n")
        
        # Diver operations
        if game.diver_ops:
            output.append(TacticalSystemsPanel.render_diver_display(
                game.diver_ops, 
                game.time_system, 
                compact=False
            ))
        
        return ''.join(output)


def render_tactical_systems_help():
    """Render help text for tactical systems commands."""
    output = []
    
    output.append(_color_system.header("\n╔" + "═" * 78 + "╗\n"))
    output.append(_color_system.header("║" + " " * 25 + "TACTICAL SYSTEMS COMMANDS" + " " * 28 + "║\n"))
    output.append(_color_system.header("╚" + "═" * 78 + "╝\n\n"))
    
    output.append(_color_system.subheader("TIME & CONDITIONS:\n"))
    output.append("  time                     - Show current time and conditions\n")
    output.append("  time advance <hours>     - Advance time forward\n")
    output.append("  time night               - Advance to nightfall\n")
    output.append("  time dawn                - Advance to dawn\n\n")
    
    output.append(_color_system.subheader("SENSORS & FOG OF WAR:\n"))
    output.append("  sensors                  - Show sensor status and contacts\n")
    output.append("  sensor <type>            - Toggle sensor (periscope/sonar/radar/hydrophone)\n")
    output.append("  contacts                 - List all tracked contacts\n")
    output.append("  classify <contact_id>    - Attempt to classify contact\n\n")
    
    output.append(_color_system.subheader("DIVER OPERATIONS:\n"))
    output.append("  divers                   - Show diver operations status\n")
    output.append("  recruit_diver [specialty]- Recruit new diver\n")
    output.append("                             (reconnaissance/sabotage/rescue/infiltration/demolition/combat)\n")
    output.append("  diver_mission <type> <target> [difficulty]\n")
    output.append("                           - Launch diver mission\n")
    output.append("    Types: harbor_recon, ship_sabotage, net_cutting, beach_recon,\n")
    output.append("           pilot_rescue, mine_placement, facility_infiltration,\n")
    output.append("           wreck_salvage, cable_cutting, obstacle_clearing\n\n")
    
    output.append(_color_system.subheader("TACTICAL HUD:\n"))
    output.append("  tactical_hud             - Show compact tactical systems HUD\n")
    output.append("  tactical_full            - Show full detailed tactical panel\n\n")
    
    output.append(_color_system.info("💡 TIP: Night operations provide stealth bonuses for divers and reduced detection risk!\n"))
    output.append(_color_system.info("💡 TIP: Use multiple sensors for better contact tracking and classification!\n"))
    
    return ''.join(output)
