"""
Fog of War System.
Sensor-based visibility system using periscope, sonar, and radar.
"""

import math
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class SensorType(Enum):
    """Types of detection sensors."""
    PERISCOPE = 'periscope'  # Visual, surface only, time/weather dependent
    SONAR = 'sonar'          # Acoustic, omnidirectional, limited detail
    RADAR = 'radar'          # Surface contacts, long range, weather independent
    HYDROPHONE = 'hydrophone'  # Passive acoustic, very long range


class ContactType(Enum):
    """Types of contacts."""
    UNKNOWN = 'unknown'
    MERCHANT = 'merchant'
    WARSHIP = 'warship'
    SUBMARINE = 'submarine'
    AIRCRAFT = 'aircraft'
    COASTAL = 'coastal'
    BIOLOGICAL = 'biological'
    GHOST = 'ghost'  # Hallucination/False Contact


class Contact:
    """Represents a detected contact."""
    
    def __init__(self, position: Tuple[int, int], sensor: SensorType,
                 contact_type: ContactType = ContactType.UNKNOWN, depth: int = 0):
        """Initialize contact."""
        self.position = position
        self.depth = depth
        self.detected_by = sensor
        self.contact_type = contact_type
        
        # Detection quality
        self.confidence = 0.5  # 0.0-1.0
        self.detail_level = 1  # 1-5 (how much info we have)
        
        # Tracking
        self.first_detected_tick = 0
        self.last_seen_tick = 0
        self.heading = None
        self.speed = None
        
        # Classification
        self.classification_attempts = 0
        self.is_classified = False
        
        # Threat assessment
        self.threat_level = 0.0  # 0.0-1.0
        
        # Ghost properties
        self.is_hallucination = (contact_type == ContactType.GHOST)
    
    def update(self, tick: int, sensor: SensorType, position: Tuple[int, int] = None, depth: int = None):
        """Update contact with new detection."""
        self.last_seen_tick = tick
        self.detected_by = sensor
        if position:
            self.position = position
        if depth is not None:
            self.depth = depth
        
        # Improve confidence with repeated detections
        self.confidence = min(1.0, self.confidence + 0.1)
        
        # Ghost contacts fade if investigated closely with active sensors
        if self.is_hallucination and sensor in [SensorType.PERISCOPE, SensorType.SONAR]:
            # High chance to disappear when "seen" clearly
            if random.random() < 0.8:
                self.confidence = 0.0 # Will be removed as stale/invalid
    
    def to_ui_dict(self) -> Dict:
        """Convert to dictionary format expected by UI."""
        x, y = self.position
        return {
            'id': id(self), # Use object id as temporary unique id
            'x': x,
            'y': y,
            'depth': self.depth,
            'type': self.contact_type.value,
            'detected_by': self.detected_by.value,
            'confidence': self.confidence,
            'stale': False,
            'is_ghost': self.is_hallucination
        }

    def is_stale(self, current_tick: int, max_age: int = 100) -> bool:
        """Check if contact is stale (not seen recently)."""
        return (current_tick - self.last_seen_tick) > max_age
    
    def get_position_uncertainty(self, current_tick: int) -> float:
        """Get position uncertainty in km."""
        ticks_since_seen = current_tick - self.last_seen_tick
        
        # Uncertainty grows over time
        base_uncertainty = 0.5
        time_uncertainty = ticks_since_seen * 0.1
        
        return base_uncertainty + time_uncertainty
    
    def __repr__(self):
        return f"<Contact {self.contact_type.value} at {self.position}>"


class TileVisibility(Enum):
    """Visibility state of map tiles."""
    UNEXPLORED = 'unexplored'    # Never seen
    EXPLORED = 'explored'        # Seen before, not currently visible
    VISIBLE = 'visible'          # Currently visible
    SONAR_CONTACT = 'sonar_contact'  # Detected by sonar (limited info)


class FogOfWar:
    """Manages fog of war and sensor-based visibility."""
    
    def __init__(self, width: int, height: int):
        """Initialize fog of war system."""
        self.width = width
        self.height = height
        
        # Tile visibility grid
        self.visibility: Dict[Tuple[int, int], TileVisibility] = {}
        for x in range(width):
            for y in range(height):
                self.visibility[(x, y)] = TileVisibility.UNEXPLORED
        
        # Contacts
        self.contacts: Dict[int, Contact] = {}  # contact_id -> Contact
        self.next_contact_id = 1
        self.current_tick = 0
        
        # Sensor ranges (in tiles)
        self.sensor_ranges = {
            SensorType.PERISCOPE: 15,
            SensorType.SONAR: 30,
            SensorType.RADAR: 50,
            SensorType.HYDROPHONE: 60,
        }
        
        # Active sensors
        self.active_sensors: Set[SensorType] = set()
        
        # Thermal Layer
        self.thermal_layer_depth = 150  # Depth in meters where thermocline exists
    
    def reset_visibility(self):
        """Reset current visibility (keep explored status)."""
        for pos in self.visibility:
            if self.visibility[pos] == TileVisibility.VISIBLE:
                self.visibility[pos] = TileVisibility.EXPLORED
            elif self.visibility[pos] == TileVisibility.SONAR_CONTACT:
                self.visibility[pos] = TileVisibility.EXPLORED
    
    def update_visibility(self, submarine_pos: Tuple[int, int],
                         active_sensors: Set[SensorType],
                         time_visibility: float = 1.0,
                         weather_visibility: float = 1.0,
                         depth: float = 0.0):
        """
        Update fog of war based on submarine position and active sensors.
        
        Args:
            submarine_pos: (x, y) position of submarine
            active_sensors: Set of currently active sensors
            time_visibility: Visibility modifier from time of day (0.0-1.0)
            weather_visibility: Visibility modifier from weather (0.0-1.0)
            depth: Submarine depth in meters (affects periscope)
        """
        self.current_tick += 1
        self.active_sensors = active_sensors
        
        # Reset current visibility
        self.reset_visibility()
        
        # Update based on each active sensor
        for sensor in active_sensors:
            self._update_sensor_visibility(
                submarine_pos, sensor, time_visibility, 
                weather_visibility, depth
            )
    
    def _update_sensor_visibility(self, sub_pos: Tuple[int, int],
                                  sensor: SensorType,
                                  time_vis: float, weather_vis: float,
                                  depth: float):
        """Update visibility for specific sensor."""
        base_range = self.sensor_ranges.get(sensor, 10)
        
        # Sensor-specific range modifiers
        if sensor == SensorType.PERISCOPE:
            # Periscope requires shallow depth
            if depth > 15:  # Can't use periscope below 15m
                return
            
            # Affected by time and weather
            effective_range = base_range * time_vis * weather_vis
            self._reveal_circular_area(sub_pos, effective_range, 
                                      TileVisibility.VISIBLE)
        
        elif sensor == SensorType.SONAR:
            # Sonar less affected by time/weather
            effective_range = base_range * (0.7 + weather_vis * 0.3)
            
            # Thermal Layer Effect (Active Sonar)
            # If sub and target are on opposite sides of the layer, range is reduced
            # Since we don't know target depth here (this reveals area), we assume
            # we are scanning for targets at similar depth or crossing the layer reduces power.
            # For area reveal, we'll just reduce range if we are deep to simulate difficulty
            # penetrating the layer upwards/downwards effectively.
            if abs(depth - self.thermal_layer_depth) > 50:
                # Deep or shallow, crossing layer is hard.
                # But here we are just revealing tiles.
                # Let's say if we are below layer, we see less surface area?
                # For simplicity, just reduce range slightly if deep
                if depth > self.thermal_layer_depth:
                    effective_range *= 0.7
            
            self._reveal_circular_area(sub_pos, effective_range,
                                      TileVisibility.SONAR_CONTACT)
        
        elif sensor == SensorType.RADAR:
            # Radar only works on surface
            if depth > 0:
                return
            
            # Long range, weather independent
            effective_range = base_range
            self._reveal_circular_area(sub_pos, effective_range,
                                      TileVisibility.VISIBLE)
        
        elif sensor == SensorType.HYDROPHONE:
            # Passive listening, very long range
            effective_range = base_range
            # Hydrophone gives less detail
            self._reveal_circular_area(sub_pos, effective_range,
                                      TileVisibility.SONAR_CONTACT)
    
    def _reveal_circular_area(self, center: Tuple[int, int], radius: float,
                             visibility_type: TileVisibility):
        """Reveal circular area around center point."""
        cx, cy = center
        radius_sq = radius * radius
        
        # Calculate bounding box
        min_x = max(0, int(cx - radius))
        max_x = min(self.width - 1, int(cx + radius))
        min_y = max(0, int(cy - radius))
        max_y = min(self.height - 1, int(cy + radius))
        
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                # Check if within radius
                dx = x - cx
                dy = y - cy
                dist_sq = dx * dx + dy * dy
                
                if dist_sq <= radius_sq:
                    # Update visibility
                    current = self.visibility.get((x, y), TileVisibility.UNEXPLORED)
                    
                    # Visible > Sonar > Explored > Unexplored
                    if visibility_type == TileVisibility.VISIBLE:
                        self.visibility[(x, y)] = TileVisibility.VISIBLE
                    elif visibility_type == TileVisibility.SONAR_CONTACT:
                        if current in [TileVisibility.UNEXPLORED, TileVisibility.EXPLORED]:
                            self.visibility[(x, y)] = TileVisibility.SONAR_CONTACT
    
    def generate_ghost_contact(self, sub_pos: Tuple[int, int], horror_stage: int) -> Optional[Contact]:
        """Generate a hallucination contact based on horror stage."""
        # Chance depends on stage (1-5)
        chance = horror_stage * 0.05  # 5% to 25%
        
        if random.random() < chance:
            # Random position near sub
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(10, 30)
            gx = int(sub_pos[0] + math.cos(angle) * dist)
            gy = int(sub_pos[1] + math.sin(angle) * dist)
            
            # Ensure within bounds
            gx = max(0, min(self.width - 1, gx))
            gy = max(0, min(self.height - 1, gy))
            
            # Random type
            g_type = random.choice([ContactType.WARSHIP, ContactType.SUBMARINE, ContactType.BIOLOGICAL])
            
            # Create ghost
            contact = self.add_contact((gx, gy), SensorType.HYDROPHONE, ContactType.GHOST, depth=random.randint(0, 300))
            contact.is_hallucination = True
            return contact
        return None

    def is_visible(self, position: Tuple[int, int]) -> bool:
        """Check if position is currently visible."""
        vis = self.visibility.get(position, TileVisibility.UNEXPLORED)
        return vis in [TileVisibility.VISIBLE, TileVisibility.SONAR_CONTACT]
    
    def is_explored(self, position: Tuple[int, int]) -> bool:
        """Check if position has been explored."""
        vis = self.visibility.get(position, TileVisibility.UNEXPLORED)
        return vis != TileVisibility.UNEXPLORED
    
    def get_visibility(self, position: Tuple[int, int]) -> TileVisibility:
        """Get visibility state of position."""
        return self.visibility.get(position, TileVisibility.UNEXPLORED)
    
    def add_contact(self, position: Tuple[int, int], sensor: SensorType,
                   contact_type: ContactType = ContactType.UNKNOWN, depth: int = 0, contact_id: int = None) -> Contact:
        """Add new contact."""
        # Check if contact already exists (by ID if provided, or proximity)
        if contact_id and contact_id in self.contacts:
            self.update_contact(contact_id, position, sensor, depth)
            return self.contacts[contact_id]

        contact = Contact(position, sensor, contact_type, depth)
        contact.first_detected_tick = self.current_tick
        contact.last_seen_tick = self.current_tick
        
        # Use provided ID or generate new one
        cid = contact_id if contact_id is not None else self.next_contact_id
        if contact_id is None:
            self.next_contact_id += 1
        
        self.contacts[cid] = contact
        return contact
    
    def update_contact(self, contact_id: int, position: Tuple[int, int],
                      sensor: SensorType, depth: int = None):
        """Update existing contact."""
        if contact_id in self.contacts:
            contact = self.contacts[contact_id]
            contact.update(self.current_tick, sensor, position, depth)
    
    def remove_stale_contacts(self, max_age: int = 100):
        """Remove contacts that haven't been seen recently."""
        stale_ids = [cid for cid, contact in self.contacts.items()
                    if contact.is_stale(self.current_tick, max_age)]
        
        for cid in stale_ids:
            del self.contacts[cid]
    
    def get_contacts_in_range(self, position: Tuple[int, int],
                             range_km: float) -> List[Contact]:
        """Get all contacts within range of position."""
        contacts = []
        px, py = position
        
        for contact in self.contacts.values():
            cx, cy = contact.position
            dist = math.sqrt((px - cx)**2 + (py - cy)**2)
            
            if dist <= range_km:
                contacts.append(contact)
        
        return contacts
    
    def get_nearest_contact(self, position: Tuple[int, int],
                           contact_type: ContactType = None) -> Optional[Contact]:
        """Get nearest contact to position."""
        nearest = None
        nearest_dist = float('inf')
        px, py = position
        
        for contact in self.contacts.values():
            # Filter by type if specified
            if contact_type and contact.contact_type != contact_type:
                continue
            
            cx, cy = contact.position
            dist = math.sqrt((px - cx)**2 + (py - cy)**2)
            
            if dist < nearest_dist:
                nearest = contact
                nearest_dist = dist
        
        return nearest
    
    def classify_contact(self, contact_id: int) -> bool:
        """Attempt to classify contact (requires time and good sensors)."""
        if contact_id not in self.contacts:
            return False
        
        contact = self.contacts[contact_id]
        contact.classification_attempts += 1
        
        # Better sensors and more attempts increase success chance
        base_chance = 0.3
        
        if contact.detected_by == SensorType.PERISCOPE:
            base_chance = 0.7  # Visual is best
        elif contact.detected_by == SensorType.RADAR:
            base_chance = 0.5  # Radar gives good info
        elif contact.detected_by == SensorType.SONAR:
            base_chance = 0.4  # Sonar profile
        
        # More attempts help
        attempt_bonus = min(0.3, contact.classification_attempts * 0.1)
        
        success_chance = base_chance + attempt_bonus
        
        if random.random() < success_chance:
            contact.is_classified = True
            contact.detail_level = min(5, contact.detail_level + 1)
            return True
        
        return False
    
    def get_sensor_display_info(self, submarine_pos: Tuple[int, int]) -> Dict:
        """Get display information for sensors UI."""
        info = {
            'active_sensors': list(self.active_sensors),
            'contacts_count': len(self.contacts),
            'visible_tiles': sum(1 for v in self.visibility.values() 
                               if v == TileVisibility.VISIBLE),
            'explored_tiles': sum(1 for v in self.visibility.values()
                                if v != TileVisibility.UNEXPLORED),
            'contacts': []
        }
        
        # Add contact info
        for contact in self.contacts.values():
            cx, cy = contact.position
            sx, sy = submarine_pos
            dist = math.sqrt((cx - sx)**2 + (cy - sy)**2)
            
            bearing = math.degrees(math.atan2(cy - sy, cx - sx))
            if bearing < 0:
                bearing += 360
            
            info['contacts'].append({
                'type': contact.contact_type.value,
                'distance': dist,
                'bearing': int(bearing),
                'confidence': contact.confidence,
                'sensor': contact.detected_by.value,
            })
        
        return info
    
    def get_exploration_percentage(self) -> float:
        """Get percentage of map explored."""
        total_tiles = self.width * self.height
        explored = sum(1 for v in self.visibility.values()
                      if v != TileVisibility.UNEXPLORED)
        
        return (explored / total_tiles) * 100.0


# Import for classify_contact random
import random
