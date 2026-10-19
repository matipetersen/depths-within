# Main game loop and state transitions
import time
import sys
import os
import random

from engine.state_manager import StateManager
from engine.events import EventQueue, Event
from ui.renderer import Renderer
from ui.persistent_renderer import PersistentRenderer, ScreenManager
from ui.controls import Controls
from ui.term_input import getkey
from submarine.submarine import Submarine
from submarine.crew_recruitment import CrewRoster
from world.lore import LoreManager
from engine.logger import Logger
from engine.progression import PlayerStats, SubmariueUpgradeTree
from engine.quests import QuestManager, MissionType
from engine.journal import Journal, EventCategory, EventSeverity, create_mission_event, create_crew_event
from engine.crew_loyalty import RebellionManager, WarEndgameStats
from engine.supply_management import SupplyInventory, RationLevel
from engine.spy_network import SpyNetwork
from engine.eldritch_encounters import EncounterManager
from engine.hotkeys import HotkeySystem, QuickCommandParser, GameUIHelper, HotkeyCategory
from ui.color_system import _color_system
from engine.crew_communications import get_communication_manager
from engine.crew_management import CrewManagementUI, CrewStoryUI, show_crew_help
from engine.game_statistics import get_statistics
from ui.panels.statistics_panel import StatisticsPanel
from ui.panels.tactical_systems_panel import TacticalSystemsPanel, render_tactical_systems_help
from engine.game_flow import GameFlowManager, WarStatus
from engine.decisions import DecisionManager
from ui.tactical_display import render_tactical_mode, render_sonar_mode, TacticalDisplay, SonarView
from ui.hud_display import render_dashboard_mode, render_status_bar, DashboardView, DetailedPanel

# Import new systems
from submarine.divers import DiverOperationsManager
from engine.time_system import TimeSystem, TimeOfDay, Season
from engine.fog_of_war import FogOfWar, SensorType, ContactType, TileVisibility
from ui.tactical_panels import TacticalPanels

try:
    import tcod
    TCOD = True
except Exception:
    tcod = None
    TCOD = False


class Game:
    def __init__(self):
        self.state_manager = StateManager()
        self.event_queue = EventQueue()
        # Use persistent renderer instead of old print-based renderer
        self.renderer = PersistentRenderer()
        self.screen_manager = ScreenManager()
        self.controls = Controls()
        self.lore = LoreManager()
        self.logger = Logger()
        
        # Initialize hotkey system
        self.hotkey_system = HotkeySystem()
        self.command_parser = QuickCommandParser(self.hotkey_system)
        self.ui_helper = GameUIHelper(self.hotkey_system)
        # create a tactical map for the game and default submarine bound to it
        try:
            from world.tactical_map import TacticalMap
            self.tactical_map = TacticalMap(width=200, height=100)
        except Exception:
            self.tactical_map = None

        self.submarine = Submarine.from_json_default(tactical_map=self.tactical_map)
        # allow submarine to log events back to the game
        try:
            self.submarine.logger = self.logger
        except Exception:
            pass
        
        # Depth change tracking
        self.target_depth = 0  # Target depth for diving/surfacing
        self.depth_change_rate = 10  # meters per turn
        
        # Initialize crew and progression systems
        try:
            self.crew_roster = CrewRoster(submarine_id=self.submarine.id, max_crew=50)
        except Exception:
            self.crew_roster = None
        
        try:
            self.player_stats = PlayerStats()
            self.upgrade_tree = SubmariueUpgradeTree()
        except Exception:
            self.player_stats = None
            self.upgrade_tree = None
        
        # Initialize quest system
        try:
            self.quest_manager = QuestManager()
        except Exception:
            self.quest_manager = None
        
        # Initialize journal system
        try:
            self.journal = Journal(max_entries=500)
        except Exception:
            self.journal = None
        
        # Initialize crew loyalty and rebellion system
        try:
            self.rebellion_manager = RebellionManager()
            self.war_endgame = WarEndgameStats()
        except Exception:
            self.rebellion_manager = None
            self.war_endgame = None
        
        # Initialize supply management system
        try:
            self.supply_inventory = SupplyInventory()
        except Exception:
            self.supply_inventory = None
        
        # Initialize spy network system
        try:
            self.spy_network = SpyNetwork()
        except Exception:
            self.spy_network = None
        
        # Initialize eldritch encounter manager
        try:
            self.encounter_manager = EncounterManager()
        except Exception:
            self.encounter_manager = None
        
        # Initialize game statistics system
        try:
            self.statistics = get_statistics()
        except Exception:
            self.statistics = None
        
        # Initialize game flow manager (war progression, objectives, events)
        try:
            self.game_flow = GameFlowManager()
        except Exception:
            self.game_flow = None
            
        # Initialize decision system
        try:
            self.decision_manager = DecisionManager()
        except Exception:
            self.decision_manager = None
        
        # Initialize sonar system for player submarine (historical detection)
        try:
            from world.sonar_systems import SonarManager, SonarOperator, SONAR_SYSTEMS
            self.sonar_manager = SonarManager()
            # Assign sonar based on submarine nation
            if self.submarine and hasattr(self.submarine, 'nation'):
                if self.submarine.nation == 'Germany':
                    sonar_type = 'GHG'
                elif self.submarine.nation == 'USA':
                    sonar_type = 'JT'
                elif self.submarine.nation == 'Japan':
                    sonar_type = 'Type_93'
                elif self.submarine.nation == 'Britain':
                    sonar_type = 'Type_128'
                else:
                    sonar_type = 'JT'
                self.sonar_manager.set_sonar_type(sonar_type)
            
            # Create sonar operator from crew
            if self.crew_roster:
                sonar_crew = self.crew_roster.crew_members.get('sonar_operator')
                if sonar_crew:
                    sonar_op = SonarOperator(skill_level=0.7, fatigue=0.0, name="Sonarman First Class")
                    self.sonar_manager.set_operator(sonar_op)
        except Exception:
            self.sonar_manager = None
        
        self.running = False
        self.turn = 0
        # Faction and crew info (set by setup screen)
        self.faction = None
        self.initial_crew = []
        # ascii gui toggle
        self.ascii_gui = False
        # ascii cursor for aiming (map coordinates)
        self.ascii_cursor = (self.submarine.x if self.submarine else 0, self.submarine.y if self.submarine else 0)
        # ascii color output (ANSI) toggle
        self.ascii_use_color = True
        # currently selected target id for firing homing torpedoes
        self.selected_target_id = None
        # Console-mode flag to show compartments when requested
        self.show_compartments = False
        self.show_help = False  # New flag for help overlay
        
        # Initialize graphical display systems
        try:
            self.tactical_display = TacticalDisplay(width=160, height=55)
            self.sonar_view = SonarView(width=60, height=40)
            self.dashboard_view = DashboardView()
            self.current_view = 'tactical'  # 'tactical', 'sonar', 'dashboard', 'status_bar'
        except Exception as e:
            self.tactical_display = None
            self.sonar_view = None
            self.dashboard_view = None
            self.current_view = 'status_bar'
        
        # Initialize new tactical systems
        try:
            # Time system (start at dawn) - SLOWED DOWN FOR HORROR
            self.time_system = TimeSystem(start_hour=6, start_minute=0, start_day=1, season=Season.SUMMER)
            self.time_system.minutes_per_tick = 60  # 1 hour per turn (was 5 minutes)
            
            # Fog of war (100x100 tactical map)
            map_width = self.tactical_map.width if self.tactical_map else 100
            map_height = self.tactical_map.height if self.tactical_map else 100
            self.fog_of_war = FogOfWar(width=map_width, height=map_height)
            
            # Diver operations manager
            self.diver_ops = DiverOperationsManager()
            
            # Set initial active sensors
            self.active_sensors = {SensorType.HYDROPHONE}  # Start with passive sonar (hydrophone)
            
            # HORROR PROGRESSION SYSTEM
            from engine.horror_progression import HorrorManager
            self.horror_manager = HorrorManager()
            try:
                from dread.bridge import DreadBridge
                self.horror_manager.attach_dread(DreadBridge(getattr(self, 'crew_roster', None)))
            except Exception as dread_err:   # fall back to the legacy model, but say so
                self.logger.log(f"[dread] disabled, using legacy horror model: {dread_err!r}")
            
            self.logger.log("New tactical systems initialized: Time, Fog of War, Divers, HORROR")
        except Exception as e:
            self.time_system = None
            self.fog_of_war = None
            self.diver_ops = None
            self.active_sensors = set()
            self.horror_manager = None
            print(f"Warning: Could not initialize new tactical systems: {e}")
    
    def initialize_from_setup(self, faction: dict, crew_list: list):
        """Initialize game state from setup screen selections."""
        self.faction = faction
        self.initial_crew = crew_list
        
        # Update submarine with faction
        if self.submarine:
            self.submarine.nation = faction.get('id', 'Germany')
            self.submarine.faction_name = faction.get('name', 'Unknown')
        
        # Initialize crew members in submarine
        if self.submarine and hasattr(self.submarine, 'crew'):
            from submarine.crew import CrewMember
            self.submarine.crew = []
            for crew_data in crew_list:
                crew_member = CrewMember(
                    name=crew_data.get('name', 'Unknown'),
                    rank=crew_data.get('rank', 'Seaman'),
                    skills=crew_data.get('skills', {}),
                    traits=crew_data.get('traits', [])
                )
                self.submarine.crew.append(crew_member)
            
            # Assign crew to compartments (distribute evenly)
            if hasattr(self.submarine, 'compartments') and self.submarine.compartments:
                crew_per_compartment = len(self.submarine.crew) // len(self.submarine.compartments)
                for i, compartment in enumerate(self.submarine.compartments):
                    start_idx = i * crew_per_compartment
                    end_idx = start_idx + crew_per_compartment
                    if i == len(self.submarine.compartments) - 1:  # Last compartment gets remainder
                        end_idx = len(self.submarine.crew)
                    compartment.crew = self.submarine.crew[start_idx:end_idx]
        
        # Update crew roster if available
        if self.crew_roster:
            from submarine.crew import CrewMember
            # Add to main crew list
            for crew_data in crew_list:
                crew_member = CrewMember(
                    name=crew_data.get('name', 'Unknown'),
                    rank=crew_data.get('rank', 'Seaman'),
                    skills=crew_data.get('skills', {}),
                    traits=crew_data.get('traits', [])
                )
                # CrewRoster has a 'crew' list attribute
                if hasattr(self.crew_roster, 'crew'):
                    self.crew_roster.crew.append(crew_member)
        
        # Log initial crew
        if self.logger:
            self.logger.log(f"Submarine commissioned: {faction.get('name')}")
            self.logger.log(f"Crew complement: {len(crew_list)} personnel")

    def get_visible_contacts(self):
        """Get list of contacts currently visible to the player."""
        if not self.fog_of_war:
            # Fallback to truth data if FoW not initialized
            return self.tactical_map.get_contacts() if self.tactical_map else []
        
        # Convert FoW contacts to UI-friendly format
        return [c.to_ui_dict() for c in self.fog_of_war.contacts.values()]

    def active_sonar_ping(self):
        """Perform an active sonar ping to reveal contacts."""
        if not self.fog_of_war or not self.tactical_map:
            return []
            
        # Active sonar range (e.g., 40 tiles)
        ping_range = 40
        detected_count = 0
        
        # Get truth contacts
        truth_contacts = self.tactical_map.get_contacts()
        
        for contact in truth_contacts:
            cx, cy = contact.get('x', 0), contact.get('y', 0)
            
            # Calculate distance
            dist = ((cx - self.submarine.x)**2 + (cy - self.submarine.y)**2)**0.5
            
            if dist <= ping_range:
                # Determine contact type
                c_type = ContactType.UNKNOWN
                if contact.get('type') == 'merchant':
                    c_type = ContactType.MERCHANT
                elif contact.get('type') == 'warship':
                    c_type = ContactType.WARSHIP
                elif contact.get('is_submarine'):
                    c_type = ContactType.SUBMARINE
                
                # Add to FoW
                self.fog_of_war.add_contact(
                    contact_id=contact.get('id'),
                    position=(cx, cy),
                    contact_type=c_type,
                    sensor=SensorType.SONAR,
                    depth=contact.get('depth', 0)
                )
                detected_count += 1
        
        self.logger.log(f"ACTIVE SONAR PING: {detected_count} contacts returned.")
        return self.get_visible_contacts()

    def _tick(self):
        # Advance world / submarine systems by one turn
        self.turn += 1
        # process a single event for demo
        e = Event('turn_advance', {'turn': self.turn})
        self.event_queue.push(e)
        
        # Advance time system
        if self.time_system:
            try:
                self.time_system.tick()
                # Log time changes at key periods
                if self.turn % 12 == 0:  # Every 12 turns = 12 hours
                    time_info = self.time_system.get_time_info()
                    if time_info['time_of_day'] in ['dawn', 'dusk', 'night']:
                        visibility = time_info['visibility']
                        detection_risk = time_info['detection_risk']
                        self.logger.log(f"{time_info['time']} - {time_info['time_of_day'].upper()}: "
                                      f"Vis {visibility:.0%}, Risk {detection_risk:.0%}")
            except Exception:
                pass
        
        # HORROR PROGRESSION - The war is just the beginning...
        if self.horror_manager and self.submarine and self.time_system:
            try:
                # Get current depth
                depth = getattr(self.submarine.systems, 'depth', 0) if hasattr(self.submarine, 'systems') else 0
                
                # Check for horror recovery conditions
                if depth < 10:  # Surfaced or very shallow
                    # For now, just assume surfacing provides minor recovery
                    # Port recovery is triggered explicitly by 'D' key
                    if self.turn % 6 == 0:  # Every 6 hours
                        recovery = self.horror_manager.surface_near_land()
                        for msg in recovery.get('messages', []):
                            self.logger.log(msg)
                
                # Advance horror (1 hour per turn)
                horror_results = self.horror_manager.advance_turn(
                    time_passed_hours=1.0,
                    current_depth=depth,
                    submarine=self.submarine
                )
                
                # Display horror messages
                for msg in horror_results.get('messages', []):
                    self.logger.log(msg)
                
                # Spawn eldritch encounter if horror demands it
                if horror_results.get('spawn_encounter') and self.encounter_manager:
                    encounter_type = horror_results.get('encounter_type')
                    if encounter_type:
                        # Trigger encounter based on horror progression
                        self.logger.log(f"[CONTACT] Something approaching on sensors...")
                        # TODO: Actually spawn encounter via encounter_manager
                
                # Apply sanity effects to crew
                if horror_results.get('sanity_effects') and hasattr(self, 'crew_roster'):
                    for effect in horror_results['sanity_effects']:
                        # TODO: Apply to crew_roster when sanity system is integrated
                        pass
                        
                # A dread event is waiting for the captain
                dread = self.horror_manager.dread
                if dread is not None and self.decision_manager and not self.decision_manager.pending_decision:
                    decision = dread.pending_decision()
                    if decision:
                        self.decision_manager.pending_decision = decision
                        self.logger.log(f"CAPTAIN! {decision.title} (Input required)")

            except Exception as horror_err:
                # Don't let the horror system crash the game, but never swallow it silently
                self.logger.log(f"[horror] error on turn {self.turn}: {horror_err!r}")
        
        # Update fog of war with current sensors
        if self.fog_of_war and self.submarine and self.time_system:
            try:
                # Get submarine position
                sub_pos = (self.submarine.x, self.submarine.y)
                
                # Get visibility modifiers
                time_visibility = self.time_system.get_visibility_modifier()
                weather_visibility = 1.0  # TODO: Connect to weather system
                
                # Get submarine depth
                depth = getattr(self.submarine.systems, 'depth', 0) if hasattr(self.submarine, 'systems') else 0
                
                # Update fog of war
                self.fog_of_war.update_visibility(
                    submarine_pos=sub_pos,
                    active_sensors=self.active_sensors,
                    time_visibility=time_visibility,
                    weather_visibility=weather_visibility,
                    depth=depth
                )
                
                # Generate Ghost Contacts (Horror)
                if self.horror_manager and self.turn % 5 == 0:
                    stage_val = self.horror_manager.current_stage.value
                    if stage_val >= 2: # UNEASE or higher
                        ghost = self.fog_of_war.generate_ghost_contact(sub_pos, stage_val)
                        if ghost:
                            self.logger.log("SONAR: Faint contact detected...")

                # Check for passive detections (Visual/Periscope/Passive Sonar)
                if self.tactical_map:
                    truth_contacts = self.tactical_map.get_contacts()
                    for contact in truth_contacts:
                        cx, cy = contact.get('x', 0), contact.get('y', 0)
                        cdepth = contact.get('depth', 0)
                        
                        # Thermal Layer Check for Passive Sonar
                        # If on opposite sides of layer, detection is harder
                        layer_depth = self.fog_of_war.thermal_layer_depth
                        crosses_layer = (depth < layer_depth < cdepth) or (cdepth < layer_depth < depth)
                        
                        # Check visibility state of the tile
                        vis_state = self.fog_of_war.get_visibility((cx, cy))
                        
                        if vis_state == TileVisibility.VISIBLE:
                            # Visual/Radar - High detail
                            c_type = ContactType.UNKNOWN
                            t = contact.get('type', 'unknown')
                            if t == 'merchant': c_type = ContactType.MERCHANT
                            elif t == 'warship': c_type = ContactType.WARSHIP
                            elif contact.get('is_submarine'): c_type = ContactType.SUBMARINE
                            elif t == 'whale': c_type = ContactType.BIOLOGICAL
                            
                            self.fog_of_war.add_contact(
                                contact_id=contact.get('id'),
                                position=(cx, cy),
                                contact_type=c_type,
                                sensor=SensorType.PERISCOPE,
                                depth=cdepth
                            )
                        elif vis_state == TileVisibility.SONAR_CONTACT:
                            # Passive Sonar / Hydrophone
                            
                            # If crossing thermal layer, chance to miss contact entirely
                            if crosses_layer and random.random() < 0.6: # 60% chance to miss if crossing layer
                                continue
                                
                            # Check if we already know what it is
                            existing = self.fog_of_war.contacts.get(contact.get('id'))
                            known_type = existing.contact_type if existing else ContactType.UNKNOWN
                            
                            self.fog_of_war.add_contact(
                                contact_id=contact.get('id'),
                                position=(cx, cy),
                                contact_type=known_type, # Keep existing knowledge or UNKNOWN
                                sensor=SensorType.HYDROPHONE,
                                depth=cdepth
                            )

                # Remove stale contacts every 10 turns
                if self.turn % 10 == 0:
                    self.fog_of_war.remove_stale_contacts(max_age=100)
            except Exception:
                pass
        
        # Process diver missions
        if self.diver_ops:
            try:
                events = self.diver_ops.tick_missions()
                for event in events:
                    self.logger.log(event['message'])
                    
                    # Process intelligence from successful missions
                    if event['success'] and event['intelligence']:
                        intel = event['intelligence']
                        intel_type = intel.get('type', 'unknown')
                        
                        if intel_type == 'harbor_layout':
                            self.logger.log(f"Intel: Harbor has {intel['ship_count']} ships, "
                                          f"{intel['defenses']} defenses")
                        elif intel_type == 'sabotage_result':
                            self.logger.log(f"Sabotage: {intel['ships_damaged']} ships damaged, "
                                          f"~{intel['estimated_tonnage']} tons")
            except Exception:
                pass
        
        # Update game flow (war progression, missions, random events, endgame check)
        if self.game_flow:
            try:
                flow_events = self.game_flow.tick(self)
                for flow_event in flow_events:
                    if flow_event.get('type') == 'random_event':
                        event_obj = flow_event.get('event')
                        if event_obj and self.logger:
                            self.logger.log(event_obj.trigger())
                    elif flow_event.get('type') == 'mission_completed':
                        mission = flow_event.get('mission')
                        if self.logger:
                            self.logger.log(f"✓ Mission complete: {mission.get('name')}")
                    elif flow_event.get('type') == 'mission_failed':
                        mission = flow_event.get('mission')
                        if self.logger:
                            self.logger.log(f"✗ Mission failed: {mission.get('name')}")
                    elif flow_event.get('type') == 'game_over':
                        reason = flow_event.get('reason', 'Unknown')
                        if self.logger:
                            self.logger.log(f"GAME OVER: {reason}")
                    elif flow_event.get('type') == 'war_ended':
                        victory_type = flow_event.get('victory_type', 'survivor')
                        if self.logger:
                            self.logger.log(f"WAR ENDED: Victory type - {victory_type}")
            except Exception as e:
                pass
        
        # Update submarine depth towards target depth (gradual depth change)
        self._update_depth()
        
        # Check for collisions
        self._check_collisions()
    
    def _process_sonar(self):
        """Process sonar detections (historical detection system with thermocline)."""
        try:
            if not self.sonar_manager or not self.tactical_map or not self.submarine:
                return
            
            # Update operator fatigue
            if self.sonar_manager.operator:
                self.sonar_manager.operator.fatigue = min(
                    1.0,
                    self.sonar_manager.operator.fatigue + 0.002  # Gradually accumulates over ~500 turns = ~8 hours
                )
            
            # Check for detections of enemy submarines
            contacts = self.tactical_map.get_contacts() if hasattr(self.tactical_map, 'get_contacts') else []
            for contact in contacts:
                if contact.get('is_submarine'):
                    detection = self.sonar_manager.detect_submarine(
                        target_position=(contact.get('x', 0), contact.get('y', 0)),
                        target_speed_kmh=contact.get('speed', 10),
                        target_depth_m=contact.get('depth', 100),
                        hunter_depth_m=getattr(self.submarine.systems, 'depth', 100) if hasattr(self.submarine, 'systems') else 100
                    )
                    
                    if detection:
                        # Log detection
                        msg = f"SONAR: Contact bearing {int(detection.bearing):03d}°, range {int(detection.range)}m"
                        if detection.detection_quality == 'certain':
                            msg += " [CERTAIN]"
                        elif detection.detection_quality == 'probable':
                            msg += " [PROBABLE]"
                        else:
                            msg += " [UNCERTAIN]"
                        
                        if detection.false_positive:
                            msg += " (false contact suspected)"
                        
                        self.logger.log(msg)
                        
                        # Update contact with detection info
                        contact['detected'] = True
                        contact['detection_bearing'] = detection.bearing
                        contact['detection_range'] = detection.range
                        contact['detection_quality'] = detection.detection_quality
        
        except Exception:
            pass
    
    def _check_collisions(self):
        
        # Process sonar detections (historical detection system)
        self._process_sonar()
        
        # Process all weapons (depth charges, shells, aircraft attacks)
        self._process_weapons()
        
        # advance tactical map AI
        try:
            if self.tactical_map:
                events = self.tactical_map.step()
                # process simple events returned by tactical_map (e.g., torpedo hits)
                for ev in events:
                    try:
                        if ev.get('type') == 'hit':
                            contact = ev.get('contact')
                            self.logger.log(f"Torpedo hit contact: {contact.get('type')} at {contact.get('x')},{contact.get('y')}")
                        elif ev.get('type') == 'timeout':
                            self.logger.log('Torpedo timed out')
                        elif ev.get('type') == 'wall':
                            self.logger.log('Torpedo left map and deactivated')
                    except Exception:
                        pass
        except Exception:
            pass
        # let submarine step
        self.submarine.step()
        # tick crew roster (stress relief, fatigue, morale updates)
        if self.crew_roster:
            try:
                self.crew_roster.tick()
            except Exception:
                pass
        
        # tick supply inventory (resource consumption, rationing effects)
        if self.supply_inventory:
            try:
                crew_count = self.crew_roster.crew_count if self.crew_roster else 0
                depth = self.submarine.current_depth if self.submarine else 0
                in_combat = self.tactical_map and self.tactical_map.any_contacts() if self.tactical_map else False
                supply_warnings = self.supply_inventory.tick(crew_count, depth, in_combat)
                # Log critical supply warnings
                if supply_warnings and supply_warnings.get('critical_resources'):
                    for resource_type in supply_warnings['critical_resources']:
                        self.logger.log(f"CRITICAL: {resource_type.name} running dangerously low!")
            except Exception:
                pass
        
        # tick spy network (sabotage attempts, detection)
        if self.spy_network:
            try:
                sabotage_events = self.spy_network.check_sabotage_attempts(self.turn)
                for sabotage in sabotage_events:
                    self.logger.log(f"Sabotage detected: {sabotage.sabotage_type.name} - Severity: {sabotage.severity}")
                    # Apply sabotage effects to submarine/crew
                    if self.supply_inventory:
                        # Sabotage reduces supplies based on severity
                        from engine.spy_network import SabotageType
                        if sabotage.sabotage_type == SabotageType.OXYGEN_LEAK:
                            self.supply_inventory.resources[0].consume(sabotage.severity * 10)
                        elif sabotage.sabotage_type == SabotageType.POWER_DRAIN:
                            self.supply_inventory.resources[1].consume(sabotage.severity * 8)
            except Exception:
                pass
        
        # tick encounter manager (encounter progression, phase changes)
        if self.encounter_manager:
            try:
                crew_count = self.crew_roster.crew_count if self.crew_roster else 0
                encounter_effects = self.encounter_manager.tick_encounters(crew_count)
                if encounter_effects:
                    for effect in encounter_effects:
                        self.logger.log(f"Encounter effect: {effect}")
            except Exception:
                pass
        
        # tick crew communications (random thoughts and conversations)
        try:
            comm_manager = get_communication_manager()
            # Trigger random thoughts occasionally (every 5-15 turns on average)
            import random
            if random.random() < 0.1:  # 10% chance per tick
                if self.crew_roster and hasattr(self.crew_roster, 'crew_members') and self.crew_roster.crew_members:
                    crew_member = random.choice(list(self.crew_roster.crew_members.values()))
                    stress = getattr(crew_member, 'stress', 0.0)
                    morale = getattr(crew_member, 'morale', 0.5)
                    # Get context based on current game state
                    context = 'calm'
                    if self.tactical_map and self.tactical_map.any_contacts():
                        context = 'combat'
                    elif stress > 0.7:
                        context = 'stressed'
                    elif morale > 0.7:
                        context = 'happy'
                    thought = comm_manager.trigger_random_thought(crew_member, stress, morale, context)
                    if thought:
                        self.logger.log(f"Crew thought: {thought}")
            
            # Trigger conversations occasionally (every 20-40 turns on average)
            if random.random() < 0.03:  # 3% chance per tick
                context = 'sub'
                if self.tactical_map and self.tactical_map.any_contacts():
                    context = 'danger'
                dialogue = comm_manager.trigger_conversation(context)
                if dialogue:
                    self.logger.log(f"Crew: {dialogue}")
        except Exception:
            pass

        # Trigger random captain's decisions
        if self.decision_manager and not self.decision_manager.pending_decision:
            # Only trigger if not in combat
            in_combat = self.tactical_map and self.tactical_map.any_contacts() if self.tactical_map else False
            dread_active = bool(self.horror_manager and getattr(self.horror_manager, 'dread', None))
            # With the dread model attached, decisions come from state-driven events instead
            if not dread_active and not in_combat and random.random() < 0.015:  # 1.5% chance per turn
                decision = self.decision_manager.generate_random_decision()
                if decision:
                    self.decision_manager.pending_decision = decision
                    self.logger.log(f"CAPTAIN! {decision.title} (Input required)")

    def _check_collisions(self):
        """Check for collisions between submarine and ships/other subs."""
        try:
            if not self.tactical_map or not self.submarine:
                return
            
            sx = getattr(self.submarine, 'x', -1)
            sy = getattr(self.submarine, 'y', -1)
            current_depth = getattr(self.submarine.systems, 'depth', 0) if hasattr(self.submarine, 'systems') else 0
            
            if sx < 0 or sy < 0:
                return
            
            # Check for ship collisions at surface (depth 0)
            if current_depth == 0:
                contacts = self.tactical_map.get_contacts() if hasattr(self.tactical_map, 'get_contacts') else []
                for contact in contacts:
                    cx = contact.get('x', -1)
                    cy = contact.get('y', -1)
                    if cx == sx and cy == sy:
                        # Collision with ship at surface!
                        ship_type = contact.get('type', 'ship')
                        self.logger.log(f"⚠ COLLISION! Hit a {ship_type} at surface!")
                        # Damage submarine slightly
                        if hasattr(self.submarine.systems, 'hull'):
                            self.submarine.systems.hull = max(0, self.submarine.systems.hull - 0.05)
                        return
            
            # Check for submarine collisions underwater
            subs = self.tactical_map.get_submarines() if hasattr(self.tactical_map, 'get_submarines') else []
            for enemy_sub in subs:
                ex = enemy_sub.get('x', -1)
                ey = enemy_sub.get('y', -1)
                ed = enemy_sub.get('depth', 200)
                
                if ex == sx and ey == sy and abs(ed - current_depth) < 50:
                    # Collision with another submarine!
                    sub_type = enemy_sub.get('type', 'unknown')
                    nation = enemy_sub.get('nation', 'unknown')
                    self.logger.log(f"⚠ COLLISION! Hit a {sub_type} submarine ({nation}) at similar depth!")
                    # Damage submarine
                    if hasattr(self.submarine.systems, 'hull'):
                        self.submarine.systems.hull = max(0, self.submarine.systems.hull - 0.1)
                    return
        except Exception:
            pass

    def _update_depth(self):
        """Gradually change submarine depth towards target depth."""
        try:
            if not self.submarine or not hasattr(self.submarine, 'systems'):
                return
            
            current_depth = getattr(self.submarine.systems, 'depth', 0)
            
            # If already at target depth, do nothing
            if current_depth == self.target_depth:
                return
            
            # Move towards target depth at the dive/surface rate
            if current_depth < self.target_depth:
                # Diving: move down
                new_depth = min(current_depth + self.depth_change_rate, self.target_depth)
                self.submarine.systems.depth = new_depth
                
                # Only log if significant change
                if new_depth % 50 == 0 or new_depth == self.target_depth:
                    if new_depth == self.target_depth:
                        self.logger.log(f"Reached target depth: {new_depth}m")
                    else:
                        self.logger.log(f"Descending... now at {new_depth}m")
            else:
                # Surfacing: move up
                new_depth = max(current_depth - self.depth_change_rate, self.target_depth)
                self.submarine.systems.depth = new_depth
                
                # Only log if significant change
                if new_depth % 50 == 0 or new_depth == self.target_depth:
                    if new_depth == self.target_depth:
                        self.logger.log(f"Reached target depth: {new_depth}m")
                    else:
                        self.logger.log(f"Ascending... now at {new_depth}m")
        except Exception:
            pass

    def _process_weapons(self):
        """Process all active weapons on tactical map (depth charges, shells, aircraft attacks)."""
        try:
            if not self.tactical_map or not self.submarine:
                return
            
            weapon_mgr = getattr(self.tactical_map, 'weapon_manager', None)
            if not weapon_mgr:
                return
            
            # Get hits on submarine
            hits = weapon_mgr.tick(self.submarine, self.tactical_map)
            
            for weapon_type, damage, location in hits:
                self.logger.log(f"HIT! {weapon_type} impact: {damage*100:.0f}% damage at {location}")
                
                # Apply damage to random compartment
                if self.submarine.compartments:
                    try:
                        idx = random.randint(0, len(self.submarine.compartments) - 1)
                        compartment = self.submarine.compartments[idx]
                        compartment.apply_damage(damage)
                        compartment.flooding = min(1.0, compartment.flooding + damage * 0.3)
                        self.logger.log(f"Compartment {compartment.name} damaged!")
                        
                        # Record hit in statistics
                        if self.statistics:
                            if weapon_type == 'depth_charge':
                                self.statistics.record_depth_charge_survived(self.turn, 1, damage)
                            elif weapon_type == 'aircraft_attack':
                                self.statistics.record_stat('damage_taken', self.turn, value=damage)
                    except Exception as e:
                        pass
        except Exception:
            pass

    def process_command(self, user_input: str) -> bool:
        """
        Process a user command using the hotkey system.
        Returns True if game should continue, False to quit.
        """
        # Handle pending decisions first
        if self.decision_manager and self.decision_manager.pending_decision:
            # Check if input matches an option key
            decision = self.decision_manager.pending_decision
            if user_input.strip() in [opt.key for opt in decision.options]:
                result = self.decision_manager.resolve_option(decision, user_input.strip(), self)
                self.logger.log(f"Decision: {result}")
                print(f"\n> {result}\n")
                return True
            elif user_input.strip().lower() in ('help', '?', 'look'):
                # Re-display decision
                pass
            else:
                print(f"\n[!] CAPTAIN, A DECISION IS REQUIRED: {decision.title}")
                print(f"    {decision.description}")
                for opt in decision.options:
                    print(f"    [{opt.key}] {opt.text}")
                return True

        if not user_input or not user_input.strip():
            # Empty input = wait/tick
            self._tick()
            return True
        
        # Parse input using hotkey system
        cmd, args = self.command_parser.parse(user_input.strip().lower())
        should_auto_tick = self.command_parser.should_auto_tick(cmd)
        
        # Handle commands
        if cmd in ('q', 'quit', 'exit'):
            print('Quitting.')
            return False
        
        elif cmd == 'help':
            # Show help by category or full
            if args and args[0] in ('full', 'all'):
                print(self.hotkey_system.print_hotkeys())
            elif args and args[0] in ('tactical', 'systems', 'new'):
                # Show tactical systems overview
                print("\n╔══════════════════════════════════════════════════════════════╗")
                print("║            TACTICAL SYSTEMS QUICK REFERENCE                  ║")
                print("╠══════════════════════════════════════════════════════════════╣")
                print("║                                                              ║")
                print("║  TIME SYSTEM:                                                ║")
                print("║    time                - Show time and conditions            ║")
                print("║    time_help           - Detailed time system help           ║")
                print("║                                                              ║")
                print("║  SENSOR SYSTEMS:                                             ║")
                print("║    sensors             - Show sensor status                  ║")
                print("║    sensor <type>       - Toggle sensor on/off                ║")
                print("║    sensor_help         - Detailed sensor help                ║")
                print("║                                                              ║")
                print("║  DIVER OPERATIONS:                                           ║")
                print("║    divers              - Show diver operations               ║")
                print("║    recruit_diver [specialty] - Recruit diver                 ║")
                print("║    diver_mission <type> <target> - Launch mission            ║")
                print("║    diver_help          - Detailed diver help                 ║")
                print("║                                                              ║")
                print("║  INTEGRATED DISPLAYS:                                        ║")
                print("║    tactical_status     - Full tactical display (all panels)  ║")
                print("║    tactical_hud        - Compact status bar                  ║")
                print("║                                                              ║")
                print("╚══════════════════════════════════════════════════════════════╝\n")
            elif args and args[0] == 'divers':
                print(TacticalPanels.show_diver_mission_help())
            elif args and args[0] == 'sensors':
                print(TacticalPanels.show_sensor_help())
            elif args and args[0] == 'time':
                print(TacticalPanels.show_time_help())
            elif args:
                # Try to match category
                try:
                    cat = HotkeyCategory[args[0].upper()]
                    print(self.hotkey_system.print_hotkeys(cat))
                except KeyError:
                    print("Category not found. Try: navigation, combat, systems, crew, info, supplies, espionage, encounters, game, tactical, divers, sensors, time")
            else:
                print(self.hotkey_system.get_quick_reference())
            return True
        
        elif cmd == 'tick' or cmd == 'wait':
            self._tick()
        
        elif cmd == 'move':
            # Move submarine: 'move dx dy' or arrow key commands
            if args and len(args) >= 2:
                try:
                    dx = int(args[0])
                    dy = int(args[1])
                    self.submarine.move(dx, dy)
                    self.logger.log(f"Moved to ({self.submarine.x}, {self.submarine.y})")
                except (ValueError, IndexError):
                    print('Usage: move <dx> <dy>')
                    return True
            else:
                print('Usage: move <dx> <dy>')
                return True
            should_auto_tick = True  # Movement is an action, so auto-tick
        
        elif cmd == 'dive':
            # Dive to target depth
            if args:
                try:
                    target_depth = int(args[0])
                    self.target_depth = target_depth
                    self.logger.log(f"Diving to {target_depth}m")
                except ValueError:
                    print("Usage: dive <depth>")
            else:
                # Default dive if no arg (e.g. periscope depth)
                self.target_depth = 15
                self.logger.log("Diving to periscope depth (15m)")
            should_auto_tick = True
            return True

        elif cmd == 'surface':
            # Surface the boat
            self.target_depth = 0
            self.logger.log("Surfacing!")
            should_auto_tick = True
            return True
        
        elif cmd == 'status':
            print(self.ui_helper.show_status_with_hints(self))
        
        elif cmd == 'dashboard':
            # Show full tactical dashboard with all info
            try:
                from ui.ascii_gui import draw_full_dashboard
                draw_full_dashboard(self, use_color=True)
            except Exception as e:
                print(f'Dashboard display error: {e}')
        
        elif cmd == 'legend':
            # Show tactical and command legend
            try:
                from ui.enhanced_gui import ASCIILegend
                print()
                print(ASCIILegend.draw_tile_legend())
                print()
                print(ASCIILegend.draw_command_legend())
            except Exception as e:
                print(f'Legend display error: {e}')
        
        elif cmd in ('tactical', 'tactical_map', 't'):
            # Switch to tactical map view (persistent)
            self.renderer.switch_view(self, 'tactical')
            return True
        
        elif cmd in ('sonar', 'sonar_mode'):
            # Switch to sonar view (persistent)
            self.renderer.switch_view(self, 'sonar')
            return True
        
        elif cmd == 's':
            # 's' could be sonar or another command, check context
            if len(args) == 0:
                self.renderer.switch_view(self, 'sonar')
                return True
        
        elif cmd in ('compartment_map', 'map', 'comp_map', 'cm'):
            # Switch to compartment map view
            self.renderer.switch_view(self, 'compartment_map')
            return True
        
        elif cmd in ('dashboard', 'dash'):
            # Switch to dashboard view (persistent)
            self.renderer.switch_view(self, 'dashboard')
            return True
        
        elif cmd == 'd':
            # 'd' for dashboard
            self.renderer.switch_view(self, 'dashboard')
            return True
        
        elif cmd == 'view':
            # Show available views
            print("\n--- AVAILABLE VIEWS ---")
            print("  tactical, t  - Large tactical map with contacts")
            print("  sonar        - Circular sonar display")
            print("  dashboard    - Full system dashboard")
            print("  compartments - Compartment detail panel")
            print("  crew_detail  - Crew roster detail panel")
            print("  sonar_detail - Sonar system detail panel")
            print("  legend       - Map legend and hotkey reference")
            print("")
            return True
        
        elif cmd == 'compartment_detail' or cmd == 'compartments':
            # Show detailed compartment panel (one-time display)
            try:
                output = DetailedPanel.render_compartment_details(self)
                self.screen_manager.render_frame(output)
            except Exception as e:
                print(f'Compartment detail error: {e}')
            return True
        
        elif cmd == 'crew_detail':
            # Show detailed crew panel (one-time display)
            try:
                output = DetailedPanel.render_crew_details(self)
                self.screen_manager.render_frame(output)
            except Exception as e:
                print(f'Crew detail error: {e}')
            return True
        
        elif cmd == 'sonar_detail':
            # Show detailed sonar panel (one-time display)
            try:
                output = DetailedPanel.render_sonar_details(self)
                self.screen_manager.render_frame(output)
            except Exception as e:
                print(f'Sonar detail error: {e}')
            return True
        
        elif cmd == 'lore':
            s = self.lore.get_random_crew_story()
            print('\n--- CREW STORY ---')
            print(s.get('story') if s else 'No story loaded')
            print('------------------\n')
        
        elif cmd == 'sonar':
            contacts = self.submarine.sonar.detect()
            print(f'Sonar contacts: {len(contacts)} detected')
            for c in contacts:
                print(f" - [{c.get('id')}] {c.get('type'):10s} | Bearing: {c.get('bearing', 0):6.1f}° | Range: {c.get('range', 0):6.0f}m")
        
        elif cmd == 'compartments' or cmd == 'compartment':
            self.show_compartments = not self.show_compartments
            print(f"Show compartments: {self.show_compartments}")
            if self.show_compartments:
                try:
                    for comp in self.submarine.compartments:
                        bar_len = 20
                        int_bar = int(comp.integrity * bar_len)
                        flood_bar = int(comp.flooding * bar_len)
                        int_vis = '█' * int_bar + ' ' * (bar_len - int_bar)
                        flood_vis = '█' * flood_bar + ' ' * (bar_len - flood_bar)
                        print(f"- {comp.name:15s} | Int: [{int_vis}] {comp.integrity:.2f} | Flood: [{flood_vis}] {comp.flooding:.2f}")
                except Exception:
                    print('No compartment data available')
        
        elif cmd == 'supplies' or cmd == 'supply_status':
            if not self.supply_inventory:
                print('Supply system not available')
                return True
            print(self.supply_inventory.get_status_report())
        
        elif cmd == 'ration_level':
            if not self.supply_inventory:
                print('Supply system not available')
                return True
            if not args:
                print('Usage: ration_level <NORMAL|REDUCED|STRICT|EMERGENCY|CRITICAL>')
                return True
            level_name = args[0].upper()
            try:
                level = RationLevel[level_name]
                self.supply_inventory.set_ration_level(level)
                print(f'Ration level set to {level.name} (consumption multiplier: {level.value})')
            except KeyError:
                print(f'Invalid ration level: {level_name}')
            return True
        
        elif cmd == 'spy_status' or cmd == 'spies':
            if not self.spy_network:
                print('Spy system not available')
                return True
            print(self.spy_network.get_sabotage_report())
            print("\nKnown Spies:")
            exposed_spies = self.spy_network.get_exposed_spies()
            suspected_spies = self.spy_network.get_suspected_spies()
            if not exposed_spies and not suspected_spies:
                print("  No known or suspected spies")
            else:
                for spy in exposed_spies:
                    print(f"  EXPOSED: {spy.cover_name} (real: {spy.real_identity}) - {spy.get_status_string()}")
                for spy in suspected_spies:
                    print(f"  SUSPECTED: {spy.cover_name} - {spy.get_status_string()}")
        
        elif cmd == 'encounter_status' or cmd == 'encounter':
            if not self.encounter_manager:
                print('Encounter system not available')
                return True
            print(self.encounter_manager.get_encounter_summary())
        
        elif cmd == 'crew_list':
            if not self.crew_roster:
                print('No crew available')
                return True
            print(f"\nCrew Roster ({self.crew_roster.crew_count}/{self.crew_roster.max_crew}):")
            for member in list(self.crew_roster.crew_members.values())[:10]:
                print(f"  {member.crew_id}: {member.name:15s} | Skill: {member.skill:10s} | Morale: {member.morale:.0f}%")
        
        elif cmd == 'crew_morale' or cmd == 'morale':
            if not self.crew_roster:
                print('Crew system not available')
                return True
            morale = self.crew_roster.get_average_morale()
            print(f"Average crew morale: {morale:.0f}%")
        
        elif cmd == 'crew' or cmd == 'crew_help':
            # New enhanced crew management commands
            if not args or args[0] in ('help', '?'):
                print(show_crew_help(self))
            elif args[0] == 'list':
                print(CrewManagementUI.show_crew_roster(self.crew_roster, self))
            elif args[0] == 'detailed':
                print(CrewManagementUI.show_crew_roster(self.crew_roster, self, show_detailed=True))
            elif args[0] == 'by-assignment':
                print(CrewManagementUI.show_crew_by_assignment(self.crew_roster))
            elif args[0] == 'morale':
                print(CrewManagementUI.show_crew_morale_summary(self.crew_roster))
            elif args[0] == 'stress-tips':
                print(CrewManagementUI.show_stress_management_tips(self))
            elif args[0] == 'assign' and len(args) >= 3:
                # crew assign <name> <compartment>
                crew_name = args[1]
                compartment_id = args[2]
                try:
                    # Find crew member by name
                    crew_member = None
                    if hasattr(self.crew_roster, 'crew_members'):
                        for cm in self.crew_roster.crew_members.values():
                            if hasattr(cm, 'name') and cm.name.lower() == crew_name.lower():
                                crew_member = cm
                                break
                    if crew_member:
                        self.crew_roster.assign_to_compartment(crew_member.crew_id, compartment_id)
                        print(_color_system.success(f"Assigned {crew_member.name} to {compartment_id}"))
                    else:
                        print(_color_system.alert(f"Crew member '{crew_name}' not found"))
                except Exception as e:
                    print(_color_system.alert(f"Assignment failed: {e}"))
            elif args[0] == 'rest':
                # Order crew to rest (reduces stress)
                try:
                    if hasattr(self.crew_roster, 'crew_members'):
                        for crew_member in self.crew_roster.crew_members.values():
                            if hasattr(crew_member, 'stress'):
                                crew_member.stress = max(0, crew_member.stress - 0.2)
                    print(_color_system.success("Crew ordered to rest. Stress levels reduced."))
                except Exception as e:
                    print(_color_system.alert(f"Rest command failed: {e}"))
            elif args[0] == 'inspire':
                # Captain's speech to boost morale
                try:
                    if hasattr(self.crew_roster, 'crew_members'):
                        for crew_member in self.crew_roster.crew_members.values():
                            if hasattr(crew_member, 'morale'):
                                crew_member.morale = min(1.0, crew_member.morale + 0.15)
                    print(_color_system.success("Captain's inspiring speech boosts crew morale!"))
                    self.logger.log("Captain's inspiring speech boosts crew morale!")
                except Exception as e:
                    print(_color_system.alert(f"Inspire command failed: {e}"))
            elif args[0] == 'stories':
                # Show historical crew stories
                from engine.crew_management import CrewStoryUI
                print(CrewStoryUI.show_crew_story_summary())
            elif args[0] == 'biography' and len(args) >= 2:
                # crew biography <name>
                crew_name = args[1]
                from engine.crew_management import CrewStoryUI
                try:
                    crew_member = None
                    if hasattr(self.crew_roster, 'crew_members'):
                        for cm in self.crew_roster.crew_members.values():
                            if hasattr(cm, 'name') and cm.name.lower() == crew_name.lower():
                                crew_member = cm
                                break
                    if crew_member:
                        print(CrewStoryUI.show_crew_biography(crew_member))
                    else:
                        print(_color_system.alert(f"Crew member '{crew_name}' not found"))
                except Exception as e:
                    print(_color_system.alert(f"Biography lookup failed: {e}"))
            elif args[0] == 'factions':
                # Show available factions
                print(_color_system.header("═══ AVAILABLE FACTIONS ═══\n"))
                print("  crew faction Kriegsmarine - German Navy")
                print("  crew faction 'Imperial Japanese Navy' - Japanese Navy")
                print("  crew faction 'US Navy' - American Navy")
                print("  crew faction 'Royal Navy' - British Navy")
                print("  crew faction 'Soviet Navy' - Soviet Navy")
                print("  crew faction 'Regia Marina' - Italian Navy")
            elif args[0] == 'faction' and len(args) >= 2:
                # crew faction <faction_name>
                from engine.crew_management import CrewStoryUI
                faction_name = ' '.join(args[1:])
                print(CrewStoryUI.show_faction_roster(faction_name, self.crew_roster.crew_members.values() if hasattr(self.crew_roster, 'crew_members') else []))
            elif args[0] == 'theater':
                # Show patrol theater information
                from engine.crew_management import CrewStoryUI
                print(CrewStoryUI.show_patrol_theater_context())
            else:
                print("Unknown crew command. Try: crew help")
        
        elif cmd == 'stats' or cmd == 'statistics':
            # Statistics commands
            stats_panel = StatisticsPanel()
            if not args or args[0] in ('summary', 'brief'):
                print(stats_panel.show_stats_summary())
            elif args[0] == 'full':
                print(stats_panel.show_full_report())
            elif args[0] == 'detailed':
                print(stats_panel.show_detailed_report())
            elif args[0] == 'combat':
                print(stats_panel.show_combat_record())
            elif args[0] == 'crew':
                print(stats_panel.show_crew_record())
            elif args[0] == 'security':
                print(stats_panel.show_security_record())
            elif args[0] == 'missions':
                print(stats_panel.show_mission_record())
            elif args[0] in ('help', '?'):
                print(stats_panel.show_help())
            else:
                print("Unknown stats command. Try: stats help")

        elif cmd == 'crew_loyalty' or cmd == 'crew_status':
            # Crew loyalty commands
            if not self.rebellion_manager:
                print('Crew loyalty system not available')
                return True
            morale = self.rebellion_manager.get_crew_morale()
            print(_color_system.header(f"CREW MORALE: {morale*100:.1f}%\n"))
            if hasattr(self.rebellion_manager, 'get_summary'):
                print(self.rebellion_manager.get_summary())
        
        elif cmd == 'crew_morale':
            # Crew morale specific
            if not self.rebellion_manager:
                print('Crew morale system not available')
                return True
            morale = self.rebellion_manager.get_crew_morale()
            print(f"Average Crew Morale: {morale*100:.1f}%")
        
        elif cmd == 'rebellion_check':
            # Check rebellion status
            if not self.rebellion_manager:
                print('Rebellion system not available')
                return True
            if hasattr(self.rebellion_manager, 'get_rebellion_status'):
                print(self.rebellion_manager.get_rebellion_status())
            else:
                rebellion_risk = getattr(self.rebellion_manager, 'rebellion_risk', 0)
                print(f"Rebellion Risk: {rebellion_risk*100:.1f}%")
        
        elif cmd == 'crew_loyalty_detail':
            # Detailed crew loyalty information
            if not self.rebellion_manager:
                print('Crew loyalty system not available')
                return True
            if hasattr(self.rebellion_manager, 'get_detailed_summary'):
                print(self.rebellion_manager.get_detailed_summary())
            else:
                print("Detailed crew loyalty summary not available")
        
        elif cmd == 'war_status':
            # War endgame status
            if not self.war_endgame:
                print('War endgame system not available')
                return True
            if hasattr(self.war_endgame, 'get_status'):
                print(self.war_endgame.get_status())
            else:
                print(f"War Status: {self.war_endgame}")
        
        elif cmd == 'end_war':
            # Trigger war end conditions
            if not self.war_endgame:
                print('War endgame system not available')
                return True
            if hasattr(self.war_endgame, 'check_war_end_conditions'):
                result = self.war_endgame.check_war_end_conditions()
                if result:
                    print(_color_system.success("War has ended!"))
                    print(result)
                else:
                    print("War continues...")
            return True
        
        elif cmd == 'war_status' or cmd == 'war':
            # Display war progression and current status
            if not self.game_flow:
                print('Game flow system not available')
                return True
            print(self.game_flow.get_war_summary())
            return True
        
        elif cmd == 'objectives' or cmd == 'goal':
            # Display current objectives
            if not self.game_flow:
                print('Game flow system not available')
                return True
            print(self.game_flow.get_objectives_status())
            return True
        
        elif cmd == 'captain_log' or cmd == 'captains_log' or cmd == 'log':
            # Display captain's log entries
            if not self.game_flow:
                print('Game flow system not available')
                return True
            entries = self.game_flow.get_captain_log(last_n=15 if not args else int(args[0]))
            print("\n" + _color_system.header("═══ CAPTAIN'S LOG ═══\n"))
            for entry in entries:
                date = entry.get('date', '???')
                msg = entry.get('message', '')
                print(f"[{date}] {msg}")
            return True
        
        elif cmd == 'missions' or cmd == 'mission':
            # Display mission status
            if not self.game_flow:
                print('Missions not available')
                return True
            
            if args and args[0] == 'active':
                print(_color_system.header("═══ ACTIVE MISSIONS ═══\n"))
                if self.game_flow.active_missions:
                    for mission in self.game_flow.active_missions:
                        progress = mission.get('progress', 0) * 100
                        print(f"  • {mission.get('name', 'Unknown')} - {progress:.0f}% complete")
                else:
                    print("  No active missions")
            elif args and args[0] == 'completed':
                print(_color_system.header("═══ COMPLETED MISSIONS ═══\n"))
                if self.game_flow.completed_missions:
                    for mission in self.game_flow.completed_missions:
                        print(f"  ✓ {mission.get('name', 'Unknown')}")
                else:
                    print("  No completed missions")
            elif args and args[0] == 'failed':
                print(_color_system.header("═══ FAILED MISSIONS ═══\n"))
                if self.game_flow.failed_missions:
                    for mission in self.game_flow.failed_missions:
                        print(f"  ✗ {mission.get('name', 'Unknown')}")
                else:
                    print("  No failed missions")
            else:
                # Show summary
                print(_color_system.header("═══ MISSION STATUS ═══\n"))
                print(f"Active: {len(self.game_flow.active_missions)}")
                print(f"Completed: {len(self.game_flow.completed_missions)}")
                print(f"Failed: {len(self.game_flow.failed_missions)}")
                print(f"Random Events Triggered: {self.game_flow.event_counter}")
            return True
        
        elif cmd == 'sonar_status':
            # Display sonar system status
            if not self.sonar_manager:
                print('Sonar system not available')
                return True
            
            sonar_type = self.sonar_manager.sonar_type
            operator = self.sonar_manager.operator
            
            print(_color_system.header("═══ SONAR STATUS ═══\n"))
            print(f"System: {sonar_type.name if sonar_type else 'Unknown'}")
            print(f"Nation: {sonar_type.nation if sonar_type else 'Unknown'}")
            print(f"Type: {sonar_type.tech_type if sonar_type else 'Unknown'}")
            print(f"Base Range (passive): {sonar_type.passive_range if sonar_type else 0}m")
            print(f"Reliability: {(sonar_type.reliability*100 if sonar_type else 0):.0f}%")
            
            if operator:
                print(f"\nOperator: {operator.name}")
                print(f"Skill: {(operator.get_effective_skill()*100):.0f}%")
                print(f"Fatigue: {(operator.fatigue*100):.0f}%")
                print(f"Contacts Detected: {operator.contacts_detected}")
            
            return True
        
        # NEW SYSTEMS COMMANDS
        
        elif cmd == 'time' or cmd == 'time_status':
            # Display current time and conditions using tactical panel
            if not self.time_system:
                print('Time system not available')
                return True
            
            print(TacticalPanels.render_time_panel(self))
            
            return True
        
        elif cmd == 'sensors' or cmd == 'sensor_status':
            # Display sensor and fog of war status using tactical panel
            if not self.fog_of_war:
                print('Fog of war system not available')
                return True
            
            print(TacticalPanels.render_sensor_panel(self))
            
            return True
        
        elif cmd == 'sensor':
            # Toggle sensor on/off
            if not self.fog_of_war or not args:
                print('Usage: sensor <periscope|sonar|radar|hydrophone>')
                return True
            
            sensor_name = args[0].upper()
            try:
                sensor = SensorType[sensor_name]
                if sensor in self.active_sensors:
                    self.active_sensors.remove(sensor)
                    self.logger.log(f"{sensor.value.title()} deactivated")
                else:
                    self.active_sensors.add(sensor)
                    self.logger.log(f"{sensor.value.title()} activated")
            except KeyError:
                print(f"Unknown sensor: {sensor_name}")
            
            return True
        
        elif cmd == 'diver_ops' or cmd == 'divers':
            # Display diver operations status
            if not self.diver_ops:
                print('Diver operations not available')
                return True
            
            print(TacticalPanels.render_diver_panel(self))
            
            return True
        
        elif cmd == 'tactical_hud':
            # Display compact tactical systems HUD
            print(TacticalPanels.render_compact_status_bar(self))
            return True
        
        elif cmd == 'tactical_full' or cmd == 'tactical_status':
            # Display full detailed tactical panel (all three panels side by side)
            print(TacticalPanels.render_combined_tactical_display(self))
            return True
        
        elif cmd == 'diver_help':
            # Display help for diver operations
            print(TacticalPanels.show_diver_mission_help())
            return True
        
        elif cmd == 'sensor_help':
            # Display help for sensor systems
            print(TacticalPanels.show_sensor_help())
            return True
        
        elif cmd == 'time_help':
            # Display help for time system
            print(TacticalPanels.show_time_help())
            return True
        
        elif cmd == 'recruit_diver':
            # Recruit a new diver
            if not self.diver_ops:
                print('Diver operations not available')
                return True
            
            from submarine.divers import DiverSpecialty
            
            if args:
                try:
                    specialty = DiverSpecialty[args[0].upper()]
                except KeyError:
                    print(f"Unknown specialty: {args[0]}")
                    print("Available: reconnaissance, sabotage, rescue, infiltration, demolition, combat")
                    return True
            else:
                specialty = None
            
            diver = self.diver_ops.recruit_diver(specialty=specialty)
            self.logger.log(f"Recruited diver: {diver.name} ({diver.specialty.value})")
            print(f"✓ Recruited: {diver.name} - {diver.specialty.value}")
            print(f"  Skills: Stealth {diver.skills['stealth']:.0%}, "
                  f"Demolition {diver.skills['demolition']:.0%}, "
                  f"Swimming {diver.skills['swimming']:.0%}")
            
            return True
        
        elif cmd == 'diver_mission' or cmd == 'launch_diver':
            # Create and launch diver mission
            if not self.diver_ops:
                print('Diver operations not available')
                return True
            
            from submarine.divers import DiverMissionType
            
            if not args or len(args) < 2:
                print('Usage: diver_mission <type> <target> [difficulty]')
                print('Types: harbor_recon, ship_sabotage, net_cutting, beach_recon, pilot_rescue, '
                      'mine_placement, facility_infiltration, wreck_salvage, cable_cutting, obstacle_clearing')
                return True
            
            mission_type_name = args[0].upper()
            target = args[1]
            difficulty = float(args[2]) if len(args) > 2 else 0.5
            
            try:
                mission_type = DiverMissionType[mission_type_name]
            except KeyError:
                print(f"Unknown mission type: {mission_type_name}")
                return True
            
            # Get available divers
            available = self.diver_ops.get_available_divers()
            if not available:
                print("No divers available! Recruit divers first.")
                return True
            
            # Create mission
            mission = self.diver_ops.create_mission(mission_type, target, difficulty)
            
            # Assign best diver
            best_diver = max(available, key=lambda d: d.get_effectiveness(mission_type))
            mission.assign_diver(best_diver)
            
            # Launch
            self.diver_ops.launch_mission(mission)
            
            effectiveness = best_diver.get_effectiveness(mission_type)
            
            # Check if night provides bonus
            night_bonus = 0.0
            if self.time_system:
                detection_risk = self.time_system.get_detection_risk_modifier(on_surface=True)
                if detection_risk < 0.5:
                    night_bonus = (1.0 - detection_risk) * 0.3
            
            self.logger.log(f"Mission launched: {mission_type.value} at {target}")
            print(f"✓ Mission Launched: {mission_type.value.replace('_', ' ').title()}")
            print(f"  Target: {target}")
            print(f"  Diver: {best_diver.name} ({best_diver.specialty.value})")
            print(f"  Effectiveness: {effectiveness:.0%}")
            if night_bonus > 0:
                print(f"  Night Stealth Bonus: +{night_bonus:.0%}")
            print(f"  Duration: ~{mission.duration} minutes")
            print(f"  Risk: {mission.risk_level:.0%}")
            
            should_auto_tick = True
            return True

        
        elif cmd == 'player_status' or cmd == 'status':
            if not self.player_stats:
                print('Player stats not available')
                return True
            print(f"Turns survived: {self.turn}")
            print(f"Crew count: {self.crew_roster.crew_count if self.crew_roster else 0}")
            return True
        
        else:
            return False
    
    def _in_visual_range(self, contact: dict) -> bool:
        """Check if contact is within visual range"""
        if not self.submarine or not contact:
            return False
        
        cx, cy = contact.get('x', 0), contact.get('y', 0)
        sx, sy = self.submarine.x, self.submarine.y
        
        # Calculate distance
        dx = cx - sx
        dy = cy - sy
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Visual range depends on conditions (5-10 tiles typically)
        visual_range = 8
        if self.time_system:
            visibility = self.time_system.get_visibility_modifier()
            visual_range = int(5 + visibility * 5)
        
        return distance <= visual_range
    
    def _bearing_to(self, contact: dict) -> float:
        """Calculate bearing to contact in degrees (0=north, 90=east)"""
        if not self.submarine or not contact:
            return 0.0
        
        cx, cy = contact.get('x', 0), contact.get('y', 0)
        sx, sy = self.submarine.x, self.submarine.y
        
        import math
        dx = cx - sx
        dy = cy - sy
        
        # Calculate angle (0=east in math, convert to 0=north for navigation)
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Convert to navigation bearing (0=north, clockwise)
        bearing = (90 - angle_deg) % 360
        
        return bearing
    
    def _in_visual_range(self, contact: dict) -> bool:
        """Check if contact is within visual range"""
        if not self.submarine or not contact:
            return False
        
        cx, cy = contact.get('x', 0), contact.get('y', 0)
        sx, sy = self.submarine.x, self.submarine.y
        
        # Calculate distance
        dx = cx - sx
        dy = cy - sy
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Visual range depends on conditions (5-10 tiles typically)
        visual_range = 8
        if self.time_system:
            visibility = self.time_system.get_visibility_modifier()
            visual_range = int(5 + visibility * 5)
        
        return distance <= visual_range
    
    def _bearing_to(self, contact: dict) -> float:
        """Calculate bearing to contact in degrees (0=north, 90=east)"""
        if not self.submarine or not contact:
            return 0.0
        
        cx, cy = contact.get('x', 0), contact.get('y', 0)
        sx, sy = self.submarine.x, self.submarine.y
        
        import math
        dx = cx - sx
        dy = cy - sy
        
        # Calculate angle (0=east in math, convert to 0=north for navigation)
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Convert to navigation bearing (0=north, clockwise)
        bearing = (90 - angle_deg) % 360
        
        return bearing
    
    def _run_pixel_mode(self):
        """Run game in modern pixel-based rendering mode."""
        try:
            import tcod.sdl.render
            import tcod.sdl.video
        except ImportError:
            print("[Game] SDL rendering not available, falling back to console mode")
            os.environ['PIXEL_MODE'] = '0'
            self.run()
            return
        
        # Initialize SDL window
        window_width = int(os.environ.get('WINDOW_WIDTH', '1280'))
        window_height = int(os.environ.get('WINDOW_HEIGHT', '800'))
        
        print(f"[Game] Creating {window_width}x{window_height} pixel window...")
        
        # Create SDL window and renderer
        window = tcod.sdl.video.new_window(
            window_width, window_height,
            title="Depths Within",
            flags=tcod.sdl.video.WindowFlags.RESIZABLE
        )
        renderer = tcod.sdl.render.new_renderer(window)
        
        # Load tileset as texture
        from ui.graphics_renderer import GraphicsRenderer
        from PIL import Image
        import numpy as np
        
        graphics = GraphicsRenderer()
        
        tileset_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tilesets', 'submarine_tileset.png')
        tileset_img = Image.open(tileset_path).convert('RGBA')
        tileset_array = np.array(tileset_img)
        
        # Create SDL surface from numpy array
        tileset_texture = renderer.upload_texture(tileset_array)
        
        TILE_SIZE = 32
        tiles_x = window_width // TILE_SIZE
        tiles_y = window_height // TILE_SIZE
        
        print(f"[Game] Rendering {tiles_x}x{tiles_y} tiles per screen")
        
        running = True
        try:
            while running:
                # Handle events
                for event in tcod.sdl.video.get_events():
                    if event.type == "QUIT":
                        running = False
                    elif event.type == "KEYDOWN":
                        should_tick = False
                        
                        # Handle input
                        if event.sym == tcod.event.KeySym.UP:
                            self.submarine.move(0, -1)
                            should_tick = True
                        elif event.sym == tcod.event.KeySym.DOWN:
                            self.submarine.move(0, 1)
                            should_tick = True
                        elif event.sym == tcod.event.KeySym.LEFT:
                            self.submarine.move(-1, 0)
                            should_tick = True
                        elif event.sym == tcod.event.KeySym.RIGHT:
                            self.submarine.move(1, 0)
                            should_tick = True
                        elif event.sym == tcod.event.KeySym.SPACE:
                            should_tick = True
                        elif event.sym == tcod.event.KeySym.Q:
                            running = False
                        
                        if should_tick:
                            self._tick()
                
                # Clear screen
                renderer.draw_color = (5, 15, 25, 255)
                renderer.clear()
                
                # Get submarine position for camera
                try:
                    sub_x = int(self.submarine.x)
                    sub_y = int(self.submarine.y)
                except:
                    sub_x, sub_y = 0, 0
                
                camera_x = sub_x - tiles_x // 2
                camera_y = sub_y - tiles_y // 2
                
                # Render ocean tiles
                for screen_y in range(tiles_y):
                    for screen_x in range(tiles_x):
                        world_x = screen_x + camera_x
                        world_y = screen_y + camera_y
                        
                        depth = self.tactical_map.get_depth(world_x, world_y)
                        if depth is None:
                            depth = 500
                        
                        tile_name = graphics.get_ocean_tile_for_depth(depth)
                        tile_coords = graphics.get_tile_coords(tile_name)
                        
                        if tile_coords:
                            col, row = tile_coords
                            src_x = col * TILE_SIZE
                            src_y = row * TILE_SIZE
                            dst_x = screen_x * TILE_SIZE
                            dst_y = screen_y * TILE_SIZE
                            
                            renderer.copy(
                                tileset_texture,
                                srcrect=(src_x, src_y, TILE_SIZE, TILE_SIZE),
                                dstrect=(dst_x, dst_y, TILE_SIZE, TILE_SIZE)
                            )
                
                # Draw submarine
                sub_screen_x = tiles_x // 2
                sub_screen_y = tiles_y // 2
                heading = getattr(self.submarine, 'heading', 0)
                depth = getattr(self.submarine.systems, 'depth', 0) if hasattr(self.submarine, 'systems') else 0
                
                sub_tile = graphics.get_submarine_tile_for_angle(heading, depth > 10)
                sub_coords = graphics.get_tile_coords(sub_tile)
                if sub_coords:
                    col, row = sub_coords
                    src_x = col * TILE_SIZE
                    src_y = row * TILE_SIZE
                    dst_x = sub_screen_x * TILE_SIZE
                    dst_y = sub_screen_y * TILE_SIZE
                    
                    renderer.copy(
                        tileset_texture,
                        srcrect=(src_x, src_y, TILE_SIZE, TILE_SIZE),
                        dstrect=(dst_x, dst_y, TILE_SIZE, TILE_SIZE)
                    )
                
                # Present
                renderer.present()
        
        finally:
            tileset_texture.destroy()
            renderer.destroy()
            window.destroy()
            print("[Game] Pixel mode shut down")

    def run(self):
        # If tcod available, run a simple tcod-driven loop that uses PanelManager
        if TCOD:
            try:
                from ui.panels.panel_manager import PanelManager
                from ui.tileset import load_preferred_tileset
            except Exception:
                PanelManager = None

            # Check if user wants to use the graphical tileset
            # Default to FALSE for pure ASCII mode as requested
            USE_GRAPHICS_TILESET = os.environ.get('USE_TILESET', '0') == '1'
            
            tileset = None
            try:
                if USE_GRAPHICS_TILESET:
                    print("[Game] Loading graphical tileset mode...")
                    tileset = load_preferred_tileset()
                    # Get actual tile size from atlas if possible
                    try:
                        from ui.tileset import load_atlas
                        atlas = load_atlas()
                        ts = atlas.get('tile_size', 32) if atlas else 32
                        print(f"[Game] Using {ts}x{ts} pixel tiles!")
                    except:
                        print("[Game] Using graphical tiles!")
                else:
                    # Use a font-based tileset that supports text
                    # This allows us to render text in the HUD while still using our custom tiles for graphics
                    # Try to load a bolder/larger font for better readability
                    try:
                        # Try Courier New Bold (very readable, bold monospace)
                        # Check common locations
                        possible_fonts = [
                            '/System/Library/Fonts/Supplemental/Courier New Bold.ttf',
                            '/Library/Fonts/Courier New Bold.ttf',
                            '/System/Library/Fonts/Courier New Bold.ttf',
                            '/System/Library/Fonts/Menlo.ttc', # Fallback to Menlo
                            '/System/Library/Fonts/Monaco.ttf'
                        ]
                        
                        font_path = None
                        for p in possible_fonts:
                            if os.path.exists(p):
                                font_path = p
                                break
                        
                        if font_path:
                            print(f"[Game] Loading font: {font_path}")
                            # Increased size to 32 for better readability
                            tileset = tcod.tileset.load_truetype_font(font_path, 32, 32)
                        else:
                            raise FileNotFoundError("No suitable bold font found")
                            
                    except Exception as e:
                        print(f"[Game] Font loading failed: {e}")
                        # Fallback to built-in
                        print("[Game] Using default tcod font")
                        tileset = None
            except Exception as e:
                print(f"[Game] Tileset loading failed: {e}")
                tileset = None

            # Larger default screen size for better visibility
            SCREEN_W = int(os.environ.get('TW_SW', '160'))
            SCREEN_H = int(os.environ.get('TW_SH', '60'))

            if tileset is not None:
                ctx_args = dict(tileset=tileset, title="Depths Within", vsync=True, sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE)
            else:
                ctx_args = dict(title="Depths Within", vsync=True, sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE)

            with tcod.context.new_terminal(
                SCREEN_W, SCREEN_H, **ctx_args
            ) as context:
                console = tcod.console.Console(SCREEN_W, SCREEN_H, order="F")
                pm = PanelManager() if PanelManager else None
                running = True
                try:
                    while running:
                        console.clear()
                        if pm:
                            pm.render(console, self)
                        else:
                            # fallback to text rendering onto console
                            self.renderer.render(self)
                        context.present(console)

                        # Wait for events (blocking) - game only advances when player acts
                        for event in tcod.event.wait():
                            if event.type == 'KEYDOWN':
                                k = event.sym
                                # when ascii GUI active, allow cursor movement and firing
                                if getattr(self, 'ascii_gui', False):
                                    try:
                                        if k == tcod.event.KeySym.UP:
                                            x, y = self.ascii_cursor; self.ascii_cursor = (x, max(0, y - 1))
                                            continue
                                        elif k == tcod.event.KeySym.DOWN:
                                            x, y = self.ascii_cursor; self.ascii_cursor = (x, min(self.tactical_map.height - 1, y + 1))
                                            continue
                                        elif k == tcod.event.KeySym.LEFT:
                                            x, y = self.ascii_cursor; self.ascii_cursor = (max(0, x - 1), y)
                                            continue
                                        elif k == tcod.event.KeySym.RIGHT:
                                            x, y = self.ascii_cursor; self.ascii_cursor = (min(self.tactical_map.width - 1, x + 1), y)
                                            continue
                                        elif k == tcod.event.KeySym.H:
                                            # Toggle Help Overlay
                                            self.show_help = not self.show_help
                                            continue
                                            
                                        elif k == tcod.event.KeySym.F:
                                            # Fire torpedo at selected target or cursor
                                            try:
                                                if self.selected_target_id:
                                                    # Fire at selected target
                                                    self.submarine.selected_target_id = self.selected_target_id
                                                    self.submarine.fire_torpedo(bearing_deg=0) # Bearing ignored if target_id set
                                                    self.logger.log(f"Torpedo fired at Target {self.selected_target_id}!")
                                                    should_tick = True
                                                else:
                                                    # Fire at cursor (manual aim)
                                                    self.submarine.fire_torpedo(target_xy=self.ascii_cursor)
                                                    self.logger.log(f'Fired torpedo at {self.ascii_cursor}')
                                                    should_tick = True
                                            except Exception as e:
                                                self.logger.log(f"Fire failed: {e}")
                                            continue
                                    except Exception:
                                        pass
                                    
                                # Flag to track if action should advance time
                                should_tick = False
                                
                                # movement
                                if k == tcod.event.KeySym.UP:
                                    self.submarine.move(0, -1)
                                    should_tick = True
                                elif k == tcod.event.KeySym.DOWN:
                                    self.submarine.move(0, 1)
                                    should_tick = True
                                elif k == tcod.event.KeySym.LEFT:
                                    self.submarine.move(-1, 0)
                                    should_tick = True
                                elif k == tcod.event.KeySym.RIGHT:
                                    self.submarine.move(1, 0)
                                    should_tick = True
                                # toggle compartments/log panel
                                elif k == tcod.event.KeySym.C:
                                    if pm:
                                        pm.show_compartments = not pm.show_compartments
                                        self.logger.log(f"Show compartments: {pm.show_compartments}")
                                    else:
                                        print('PanelManager not available to toggle compartments')
                                # actions
                                elif k == tcod.event.KeySym.P:
                                    # active ping
                                    try:
                                        contacts = self.active_sonar_ping()
                                        if contacts:
                                            self.logger.log(f"PING RETURNED {len(contacts)} CONTACTS!")
                                        else:
                                            self.logger.log("Ping returned no contacts.")
                                        should_tick = True
                                    except Exception as e:
                                        print(f'Active ping failed: {e}')
                                elif k == tcod.event.KeySym.T:
                                    # Cycle targets (don't fire)
                                    try:
                                        tm = self.tactical_map or self.submarine.tactical_map
                                        contacts = tm.get_contacts() if tm else []
                                        
                                        # Filter to only visible contacts if FoW is active
                                        if self.fog_of_war:
                                            visible_ids = list(self.fog_of_war.contacts.keys())
                                            contacts = [c for c in contacts if c['id'] in visible_ids]
                                        
                                        if not contacts:
                                            self.selected_target_id = None
                                            self.logger.log("No targets available.")
                                        else:
                                            ids = [c.get('id') for c in contacts]
                                            if self.selected_target_id in ids:
                                                i = ids.index(self.selected_target_id)
                                                self.selected_target_id = ids[(i + 1) % len(ids)]
                                            else:
                                                self.selected_target_id = ids[0]
                                            
                                            # Log selected target info
                                            tgt = next((c for c in contacts if c['id'] == self.selected_target_id), None)
                                            if tgt:
                                                t_type = tgt.get('type', 'Unknown')
                                                dist = ((tgt['x'] - self.submarine.x)**2 + (tgt['y'] - self.submarine.y)**2)**0.5
                                                self.logger.log(f"Target Selected: {t_type} (ID:{self.selected_target_id}) - Range: {dist:.1f}")
                                    except Exception as e:
                                        self.logger.log(f"Targeting error: {e}")
                                elif k == tcod.event.KeySym.N:
                                    # cycle selected target to next contact (Legacy binding, same as T now)
                                    try:
                                        tm = self.tactical_map or self.submarine.tactical_map
                                        contacts = tm.get_contacts() if tm else []
                                        if not contacts:
                                            self.selected_target_id = None
                                        else:
                                            ids = [c.get('id') for c in contacts]
                                            if self.selected_target_id in ids:
                                                i = ids.index(self.selected_target_id)
                                                self.selected_target_id = ids[(i + 1) % len(ids)]
                                            else:
                                                self.selected_target_id = ids[0]
                                        self.logger.log(f"Selected target: {self.selected_target_id}")
                                    except Exception:
                                        pass
                                elif k == tcod.event.KeySym.S:
                                    # surface
                                    self.submarine.surface()
                                    should_tick = True
                                elif k == tcod.event.KeySym.SPACE:
                                    # Wait/skip turn - just advance time without moving
                                    self.logger.log("Waiting... maintaining position.")
                                    should_tick = True
                                elif k == tcod.event.KeySym.PAGEDOWN or k == tcod.event.KeySym.MINUS:
                                    # Dive deeper
                                    try:
                                        # Update target depth instead of immediate dive
                                        self.target_depth += 25
                                        max_depth = getattr(self.submarine, 'max_depth', 300)
                                        self.target_depth = min(self.target_depth, max_depth)
                                        self.logger.log(f"Target depth set to {self.target_depth}m")
                                        should_tick = True
                                    except Exception as e:
                                        self.logger.log(f"Dive failed: {e}")
                                elif k == tcod.event.KeySym.PAGEUP or k == tcod.event.KeySym.EQUALS:
                                    # Ascend (surface)
                                    try:
                                        # Update target depth instead of immediate ascend
                                        self.target_depth -= 25
                                        self.target_depth = max(0, self.target_depth)
                                        self.logger.log(f"Target depth set to {self.target_depth}m")
                                        should_tick = True
                                    except Exception as e:
                                        self.logger.log(f"Ascend failed: {e}")
                                elif k == tcod.event.KeySym.B:
                                    # Battery/System status report
                                    try:
                                        battery = getattr(self.submarine.systems, 'battery', 1.0) * 100
                                        oxygen = getattr(self.submarine.systems, 'oxygen', 1.0) * 100
                                        hull = getattr(self.submarine.systems, 'hull', 1.0) * 100
                                        depth = getattr(self.submarine.systems, 'depth', 0)
                                        self.logger.log(f"═══ SYSTEM STATUS ═══")
                                        self.logger.log(f"Battery: {battery:.1f}%  Oxygen: {oxygen:.1f}%  Hull: {hull:.1f}%")
                                        self.logger.log(f"Depth: {depth}m  Horror: {self.horror_manager.current_stage.name if self.horror_manager else 'N/A'}")
                                    except Exception as e:
                                        self.logger.log(f"Status check failed: {e}")
                                elif k == tcod.event.KeySym.E:
                                    # Emergency surface (fast ascend)
                                    try:
                                        current_depth = getattr(self.submarine.systems, 'depth', 0)
                                        if current_depth > 0:
                                            self.submarine.systems.depth = 0
                                            self.logger.log("!!! EMERGENCY SURFACE !!!")
                                            self.logger.log("Ballast blown! Submarine surfacing rapidly!")
                                            # Costs battery
                                            self.submarine.systems.battery = max(0, self.submarine.systems.battery - 0.05)
                                            should_tick = True
                                        else:
                                            self.logger.log("Already at surface!")
                                    except Exception as e:
                                        self.logger.log(f"Emergency surface failed: {e}")
                                elif k == tcod.event.KeySym.N1:
                                    # Speed: SLOW
                                    msg = self.submarine.set_speed_mode('SLOW')
                                    self.logger.log(msg)
                                elif k == tcod.event.KeySym.N2:
                                    # Speed: STANDARD
                                    msg = self.submarine.set_speed_mode('STANDARD')
                                    self.logger.log(msg)
                                elif k == tcod.event.KeySym.N3:
                                    # Speed: FULL
                                    msg = self.submarine.set_speed_mode('FULL')
                                    self.logger.log(msg)
                                elif k == tcod.event.KeySym.N4:
                                    # Speed: FLANK (emergency speed)
                                    msg = self.submarine.set_speed_mode('FLANK')
                                    self.logger.log(msg)
                                elif k == tcod.event.KeySym.X:
                                    # Toggle silent running
                                    msg = self.submarine.toggle_silent_running()
                                    self.logger.log(msg)
                                elif k == tcod.event.KeySym.R:
                                    # Repair most damaged compartment
                                    msg = self.submarine.repair_compartment()
                                    self.logger.log(msg)
                                elif k == tcod.event.KeySym.V:
                                    # Periscope view / Visual scan
                                    self.logger.log("═══ PERISCOPE VIEW ═══")
                                    try:
                                        depth = getattr(self.submarine.systems, 'depth', 0)
                                        if depth > 15:
                                            self.logger.log("Too deep for periscope! (Max 15m)")
                                        else:
                                            # Render ASCII periscope view
                                            from ui.periscope import render_periscope_view
                                            view_lines = render_periscope_view(self)
                                            print("\n" * 2)
                                            for line in view_lines:
                                                print(line)
                                            print("\nPress ENTER to continue...")
                                            input() # Pause to let user see it
                                            should_tick = False # Viewing doesn't take a turn
                                    except Exception as e:
                                        self.logger.log(f"Periscope view failed: {e}")
                                elif k == tcod.event.KeySym.D:
                                    # Dock at port (if near one)
                                    try:
                                        if self.horror_manager:
                                            # For now, assume we're at a friendly port when docking
                                            # TODO: Add proper port detection once map terrain is implemented
                                            at_port = True
                                            port_type = 'friendly'
                                            
                                            if at_port:
                                                self.submarine.surface()  # Must surface to dock
                                                is_friendly = (port_type == 'friendly')
                                                recovery = self.horror_manager.reach_port(at_friendly_port=is_friendly)
                                                for msg in recovery.get('messages', []):
                                                    self.logger.log(msg)
                                                self.logger.log("Press any key to continue...")
                                            else:
                                                self.logger.log("No port nearby. Move closer to dock.")
                                    except Exception as dock_err:
                                        self.logger.log(f"Docking failed: {dock_err}")
                                elif k == tcod.event.KeySym.A:
                                    # toggle ascii GUI rendering
                                    self.ascii_gui = not self.ascii_gui
                                    self.logger.log(f"ASCII GUI: {self.ascii_gui}")
                                elif k == tcod.event.KeySym.LEFTBRACKET:
                                    # decrease sonar sensitivity
                                    try:
                                        s = getattr(self.submarine, 'sonar', None)
                                        if s is not None:
                                            s.sensitivity = max(0.1, getattr(s, 'sensitivity', 1.0) - 0.1)
                                            self.logger.log(f"Sonar sensitivity: {s.sensitivity:.2f}")
                                    except Exception:
                                        pass
                                elif k == tcod.event.KeySym.RIGHTBRACKET:
                                    # increase sonar sensitivity
                                    try:
                                        s = getattr(self.submarine, 'sonar', None)
                                        if s is not None:
                                            s.sensitivity = getattr(s, 'sensitivity', 1.0) + 0.1
                                            self.logger.log(f"Sonar sensitivity: {s.sensitivity:.2f}")
                                    except Exception:
                                        pass
                                elif k == tcod.event.KeySym.K:
                                    # toggle ascii ANSI color
                                    self.ascii_use_color = not getattr(self, 'ascii_use_color', True)
                                    self.logger.log(f"ASCII color: {self.ascii_use_color}")
                                elif k in (tcod.event.KeySym.Q, tcod.event.KeySym.ESCAPE):
                                        running = False
                                
                                # Advance game time if action was taken
                                if should_tick:
                                    self._tick()
                                    
                            elif event.type == 'QUIT':
                                running = False
                except KeyboardInterrupt:
                    pass
        else:
            # Fallback console loop - NOW WITH PERSISTENT SCREEN!
            self.running = True
            
            # Hide cursor for cleaner display
            self.screen_manager.hide_cursor()
            
            # Clear screen and show initial tactical display
            self.screen_manager.clear_screen()
            
            # Enable raw input for arrow keys and movement
            self.controls.enable_raw_input = True
            
            try:
                # Initial render
                self.renderer.render(self)
                
                while self.running:
                    # Get user input (with timeout to allow periodic updates)
                    user_input = self.controls.get_command()
                    
                    # Process command using unified command handler
                    should_continue = self.process_command(user_input)
                    if not should_continue:
                        self.running = False
                        break
                    
                    # Render after command processed (renderer will check if update needed)
                    self.renderer.render(self)
            except KeyboardInterrupt:
                self.screen_manager.show_cursor()
                self.screen_manager.clear_screen()
                print('Game interrupted. Exiting.')
                sys.exit(0)
