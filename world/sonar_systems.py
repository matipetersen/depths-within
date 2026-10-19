"""Historical sonar technology and submarine detection systems from WWII era.

Implements:
- Active sonar (ASDIC) with realistic limitations
- Passive hydrophone listening systems
- Surface detection and radar
- Thermocline interference (realistic thermal layers)
- Realistic detection ranges by sonar type
- Historical design flaws and failure modes
"""
import random
import math


class SonarType:
    """Different WWII-era sonar/detection technologies."""
    
    def __init__(self, name, nation, tech_type, active_range, passive_range, reliability, year):
        """Initialize sonar type.
        
        Args:
            name: Sonar system name (e.g., "Balkongerät")
            nation: Nation that developed it
            tech_type: 'active', 'passive', or 'combined'
            active_range: Active sonar range in meters (0 if no active sonar)
            passive_range: Passive listening range in meters
            reliability: 0-1.0, how often it detects correctly
            year: Year introduced
        """
        self.name = name
        self.nation = nation
        self.tech_type = tech_type
        self.active_range = active_range
        self.passive_range = passive_range
        self.reliability = reliability
        self.year = year


# Historical Sonar Systems
SONAR_SYSTEMS = {
    # German systems
    'Balkongerät': SonarType(
        name='Balkongerät',
        nation='Germany',
        tech_type='passive',
        active_range=0,
        passive_range=8000,
        reliability=0.65,
        year=1935
    ),
    'GHG': SonarType(
        name='GHG Active Sonar',
        nation='Germany',
        tech_type='active',
        active_range=4000,
        passive_range=8000,
        reliability=0.55,
        year=1940
    ),
    'S-Gerät': SonarType(
        name='S-Gerät (Metox)',
        nation='Germany',
        tech_type='passive',
        active_range=0,
        passive_range=12000,
        reliability=0.70,
        year=1941
    ),
    
    # British systems
    'Type 128': SonarType(
        name='Type 128 Hydrophone',
        nation='UK',
        tech_type='passive',
        active_range=0,
        passive_range=10000,
        reliability=0.75,
        year=1939
    ),
    'ASDIC': SonarType(
        name='ASDIC',
        nation='UK',
        tech_type='active',
        active_range=2000,
        passive_range=8000,
        reliability=0.60,
        year=1937
    ),
    
    # American systems
    'JT_Hydrophone': SonarType(
        name='JT Hydrophone',
        nation='USA',
        tech_type='passive',
        active_range=0,
        passive_range=12000,
        reliability=0.80,
        year=1941
    ),
    'QC_Sonar': SonarType(
        name='QC Active Sonar',
        nation='USA',
        tech_type='active',
        active_range=4500,
        passive_range=12000,
        reliability=0.75,
        year=1943
    ),
    
    # Japanese systems
    'Type_93': SonarType(
        name='Type 93 Hydrophone',
        nation='Japan',
        tech_type='passive',
        active_range=0,
        passive_range=6000,
        reliability=0.55,
        year=1935
    ),
    
    # Italian systems
    'Tipo_128': SonarType(
        name='Tipo 128 Hydrophone',
        nation='Italy',
        tech_type='passive',
        active_range=0,
        passive_range=5000,
        reliability=0.50,
        year=1939
    ),
}


class RadarSystem:
    """Historical radar systems (mostly surface search)."""
    
    def __init__(self, name, nation, range_m, reliability, year, detection_type='surface'):
        """Initialize radar system.
        
        Args:
            name: Radar system name
            nation: Nation
            range_m: Detection range in meters
            reliability: 0-1.0 reliability
            year: Year introduced
            detection_type: 'surface', 'air', 'both'
        """
        self.name = name
        self.nation = nation
        self.range_m = range_m
        self.reliability = reliability
        self.year = year
        self.detection_type = detection_type


RADAR_SYSTEMS = {
    'FuMO_30': RadarSystem('FuMO 30', 'Germany', 6000, 0.65, 1941, 'surface'),
    'FuMO_65': RadarSystem('FuMO 65 Hohentwiel', 'Germany', 8000, 0.60, 1943, 'surface'),
    'Type_21': RadarSystem('Type 21 Air Search', 'UK', 10000, 0.70, 1939, 'both'),
    'Type_24': RadarSystem('Type 24 Surface Search', 'UK', 12000, 0.75, 1942, 'surface'),
    'SG_Radar': RadarSystem('SG Surface Search', 'USA', 15000, 0.80, 1941, 'surface'),
    'SK_Radar': RadarSystem('SK Air Search', 'USA', 20000, 0.75, 1942, 'air'),
}


class DetectionEvent:
    """Represents a detection (target found by sonar/radar)."""
    
    def __init__(self, target_id, target_type, range_m, bearing_deg, sonar_type, false_positive=False):
        """Initialize detection event.
        
        Args:
            target_id: ID of detected target
            target_type: 'submarine', 'ship', 'contact'
            range_m: Distance to target
            bearing_deg: Bearing in degrees (0-360)
            sonar_type: Sonar system that made detection
            false_positive: Whether this is a false detection (noise)
        """
        self.target_id = target_id
        self.target_type = target_type
        self.range_m = range_m
        self.bearing_deg = bearing_deg
        self.sonar_type = sonar_type
        self.false_positive = false_positive
        self.confirmed = not false_positive
        self.age = 0  # Turns this detection has been tracked


class SonarOperator:
    """Represents a trained sonar operator with skill variations."""
    
    def __init__(self, name, skill_level=0.5, fatigue=0.0, nation='American'):
        """Initialize sonar operator.
        
        Args:
            name: Operator name
            skill_level: 0-1.0, operator effectiveness
            fatigue: 0-1.0, fatigue reduces detection ability
            nation: Nation (affects training)
        """
        self.name = name
        self.skill_level = skill_level
        self.fatigue = fatigue
        self.nation = nation
        self.contacts_detected = 0
        self.false_positives = 0
        self.confirmed_sinkings = 0
        
    def get_effective_skill(self):
        """Get current skill accounting for fatigue."""
        return self.skill_level * (1.0 - self.fatigue * 0.5)


class SonarManager:
    """Manages sonar detection and false contacts."""
    
    def __init__(self, sonar_system, radar_system=None, operator=None, depth=0):
        """Initialize sonar manager.
        
        Args:
            sonar_system: SonarType instance
            radar_system: RadarSystem instance (for surface ships)
            operator: SonarOperator instance
            depth: Current depth (affects sonar performance)
        """
        self.sonar_system = sonar_system
        self.radar_system = radar_system
        self.operator = operator or SonarOperator("Default Operator")
        self.depth = depth
        self.detected_contacts = []
        self.false_contacts = []
        self.thermocline_active = False
        self.detection_history = []
        
    def set_thermocline(self, active, depth=None):
        """Set thermocline layer (thermal interference).
        
        Thermocline significantly reduces sonar detection range.
        Realistic: exists at certain depths, created by temperature/salinity layers.
        """
        self.thermocline_active = active
        if depth:
            self.thermocline_depth = depth
    
    def get_effective_range(self, detection_type='passive'):
        """Get effective sonar range accounting for conditions.
        
        Args:
            detection_type: 'passive' or 'active'
        
        Returns:
            Effective range in meters
        """
        if detection_type == 'passive':
            base_range = self.sonar_system.passive_range
        else:
            base_range = self.sonar_system.active_range
        
        # Apply modifiers
        effective_range = base_range * self.sonar_system.reliability
        
        # Thermocline reduces range significantly
        if self.thermocline_active:
            effective_range *= 0.4  # 60% range reduction
        
        # Operator skill improves detection
        effective_range *= (1.0 + self.operator.get_effective_skill() * 0.3)
        
        # Depth affects passive sonar (deeper = quieter)
        depth_factor = max(0.5, 1.0 - (self.depth / 500.0))
        if detection_type == 'passive':
            effective_range *= depth_factor
        
        return int(effective_range)
    
    def detect_submarine(self, sub_x, sub_y, sub_depth, player_x, player_y, player_depth):
        """Attempt to detect a submarine.
        
        Args:
            sub_x, sub_y: Target submarine position
            sub_depth: Target submarine depth
            player_x, player_y: Our submarine position
            player_depth: Our submarine depth
        
        Returns:
            DetectionEvent if detected, None otherwise
        """
        distance = math.hypot(sub_x - player_x, sub_y - player_y)
        
        # Calculate bearing
        bearing_rad = math.atan2(sub_y - player_y, sub_x - player_x)
        bearing_deg = math.degrees(bearing_rad) % 360
        
        # Determine detection method
        use_active = self.sonar_system.tech_type in ('active', 'combined')
        use_passive = self.sonar_system.tech_type in ('passive', 'combined')
        
        # Passive detection (always active, quietest method)
        if use_passive:
            passive_range = self.get_effective_range('passive')
            
            # Target moving fast? Easier to detect
            speed_bonus = 1.0 if distance > 2 else 0.7  # Stationary targets hard to detect
            
            # Depth differential affects detection (different layers)
            depth_diff = abs(sub_depth - player_depth)
            depth_factor = math.exp(-depth_diff / 150.0)  # Exponential decay with depth diff
            
            if distance <= passive_range * speed_bonus * depth_factor:
                if random.random() < self.sonar_system.reliability:
                    return DetectionEvent(
                        target_id=sub_x * 1000 + sub_y,
                        target_type='submarine',
                        range_m=int(distance),
                        bearing_deg=bearing_deg,
                        sonar_type=self.sonar_system.name
                    )
        
        # Active detection (searching, reveals own position)
        if use_active:
            active_range = self.get_effective_range('active')
            
            if distance <= active_range:
                if random.random() < self.sonar_system.reliability:
                    return DetectionEvent(
                        target_id=sub_x * 1000 + sub_y,
                        target_type='submarine',
                        range_m=int(distance),
                        bearing_deg=bearing_deg,
                        sonar_type=self.sonar_system.name + " (ACTIVE)"
                    )
        
        # Chance of false contact (noise, whales, thermal layers)
        false_chance = 0.02 * (1.0 - self.operator.skill_level)
        if random.random() < false_chance:
            # Generate false bearing
            false_bearing = (bearing_deg + random.randint(-45, 45)) % 360
            false_distance = int(distance + random.randint(-500, 500))
            
            self.operator.false_positives += 1
            return DetectionEvent(
                target_id=-1,
                target_type='noise',
                range_m=false_distance,
                bearing_deg=false_bearing,
                sonar_type=self.sonar_system.name,
                false_positive=True
            )
        
        return None
    
    def detect_surface_ship(self, ship_x, ship_y, player_x, player_y):
        """Attempt to detect a surface ship (visual/radar).
        
        Args:
            ship_x, ship_y: Ship position
            player_x, player_y: Our position
        
        Returns:
            DetectionEvent if detected, None otherwise
        """
        distance = math.hypot(ship_x - player_x, ship_y - player_y)
        
        # Calculate bearing
        bearing_rad = math.atan2(ship_y - player_y, ship_x - player_x)
        bearing_deg = math.degrees(bearing_rad) % 360
        
        # Visual detection (surface ships visible from periscope)
        visual_range = 10000  # 10km typical
        
        if distance <= visual_range:
            if random.random() < 0.8:  # 80% chance if in range
                return DetectionEvent(
                    target_id=ship_x * 1000 + ship_y,
                    target_type='ship',
                    range_m=int(distance),
                    bearing_deg=bearing_deg,
                    sonar_type='Visual (Periscope)'
                )
        
        # Radar detection (if we have radar)
        if self.radar_system:
            if distance <= self.radar_system.range_m:
                if random.random() < self.radar_system.reliability:
                    return DetectionEvent(
                        target_id=ship_x * 1000 + ship_y,
                        target_type='ship',
                        range_m=int(distance),
                        bearing_deg=bearing_deg,
                        sonar_type=self.radar_system.name
                    )
        
        return None
    
    def get_detection_quality(self, detection):
        """Evaluate quality/reliability of a detection.
        
        Returns:
            'certain' - Confirmed contact
            'probable' - Likely real contact
            'possible' - Could be false contact
        """
        if detection.false_positive:
            return 'possible'
        
        # Repeated detections are more certain
        age_factor = min(1.0, detection.age / 5.0)
        
        if age_factor > 0.5:
            return 'certain'
        elif detection.sonar_type == 'Visual (Periscope)':
            return 'certain'
        elif 'ACTIVE' in detection.sonar_type:
            return 'probable'
        else:
            return 'probable'


# Historical Detection Scenarios

HISTORICAL_FAILURES = {
    'mark_14_failure': {
        'name': 'Mark 14 Magnetic Detonator Failure',
        'nation': 'USA',
        'description': 'Magnetic detonators failed 60% of the time, running too deep (3-6m), premature detonation',
        'failure_rate': 0.60,
        'historical_impact': 'Wasted thousands of torpedoes early war, cost countless patrol failures',
        'years_active': (1939, 1943)
    },
    'g7a_detection': {
        'name': 'G7a Visible Bubble Trail',
        'nation': 'Germany',
        'description': 'Air-fuel torpedo creates visible bubble trail, easier for escorts to detect and evade',
        'detection_penalty': 1.6,  # 60% harder to detect
        'detection_advantage': -0.4,  # 40% easier for enemy to see and evade
        'years_active': (1940, 1945)
    },
    'asdic_thermocline': {
        'name': 'ASDIC Thermocline Limitation',
        'nation': 'UK',
        'description': 'ASDIC fails completely if submarine crosses thermocline (thermal layer)',
        'thermocline_defeat_range': 2000,
        'years_active': (1937, 1945)
    },
    'type_93_volatility': {
        'name': 'Type 93 Oxygen Fuel Volatility',
        'nation': 'Japan',
        'description': 'If torpedo is hit or struck, oxygen fuel can explode, destroying launching submarine',
        'explosion_chance_on_hit': 0.15,
        'damage_to_launcher': 0.50,
        'years_active': (1933, 1945)
    }
}


class HistoricalDefect:
    """Represents a known historical weapon/system defect."""
    
    def __init__(self, name, torpedo_type, failure_scenario, chance):
        """Initialize historical defect.
        
        Args:
            name: Name of defect
            torpedo_type: Torpedo model affected
            failure_scenario: What happens when defect occurs
            chance: 0-1.0, chance of occurring each shot
        """
        self.name = name
        self.torpedo_type = torpedo_type
        self.failure_scenario = failure_scenario
        self.chance = chance
    
    def occurs(self):
        """Check if defect occurs on this firing."""
        return random.random() < self.chance


# Register historical defects
TORPEDO_DEFECTS = [
    HistoricalDefect(
        'Mark 14 Deep Running',
        'Mk_14',
        'Torpedo runs 3-6m deeper than set, passes under target without detonating',
        0.30
    ),
    HistoricalDefect(
        'Mark 14 Magnetic Detonator Failure',
        'Mk_14',
        'Magnetic detonator fails to trigger on passing under ship',
        0.35
    ),
    HistoricalDefect(
        'G7a Hot Run',
        'G7a',
        'Torpedo motor starts before leaving tube, runs in circle toward launcher',
        0.05
    ),
    HistoricalDefect(
        'G7e Unreliable',
        'G7e',
        'Electric torpedo drops speed mid-run or fails to maintain depth',
        0.08
    ),
    HistoricalDefect(
        'Type 93 Volatile Fuel',
        'Type_93',
        'Oxygen fuel becomes unstable, potential explosion risk',
        0.03
    ),
]
