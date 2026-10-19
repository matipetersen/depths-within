"""Simple tactical map with depth contours, thermoclines and contacts."""
import random
from world.ship_ai import step_contact
from world.weapons import WeaponManager
from world.sonar_systems import SonarManager, SonarType, SONAR_SYSTEMS, RADAR_SYSTEMS
from submarine.torpedo import Torpedo


class TacticalMap:
    def __init__(self, width=500, height=500):
        self.width = width
        self.height = height
        # Generate terrain using multi-frequency sine waves for natural islands/trenches
        self.depth = [[self._generate_depth(x, y) for x in range(width)] for y in range(height)]
        # thermocline map: True where thermocline present
        self.thermocline = [[random.random() < 0.03 for x in range(width)] for y in range(height)]
        # contacts: list of dicts with x,y,type
        self.contacts = []
        self._next_contact_id = 1
        # submarines (enemy, allied, neutral)
        self.submarines = []
        self._next_sub_id = 1
        # wildlife (whales, dolphins, large fish - show up on sonar)
        self.wildlife = []
        self._next_wildlife_id = 1
        # active torpedoes in the map
        self.torpedoes = []
        # aircraft: list of dicts with position, type, nation
        self.aircraft = []
        self._next_aircraft_id = 1
        # ports: list of dicts with position, name, nation
        self.ports = []
        # weapon manager for all ship and aircraft weapons
        self.weapon_manager = WeaponManager()
        self.player_sub = None  # Reference to player submarine for AI
        self._populate_contacts()
        self._populate_submarines()
        self._populate_wildlife()
        self._populate_ports()

    def _generate_depth(self, x, y):
        import math
        # Multi-frequency noise simulation using sine waves
        # Scale coordinates to 0-1 range
        nx = x / self.width
        ny = y / self.height
        
        # Base gradient (deeper towards bottom-right)
        base = 100 + (nx + ny) * 100
        
        # Large features (continents/oceans)
        f1 = math.sin(nx * 3 * math.pi) * math.cos(ny * 3 * math.pi) * 200
        
        # Medium features (islands/trenches)
        f2 = math.sin(nx * 10 * math.pi + 1.5) * math.cos(ny * 8 * math.pi) * 100
        
        # Small details
        f3 = math.sin(nx * 25 * math.pi) * math.sin(ny * 25 * math.pi) * 30
        
        # Combine
        val = base + f1 + f2 + f3
        
        # Normalize and clamp
        # Depth 0 = Land/Island
        # Depth > 0 = Water
        
        # Shift so we have some islands (negative values become 0)
        depth = int(val + 50)
        
        # Ensure boundaries are deep water (to avoid getting stuck at edge)
        edge_dist = min(x, y, self.width - 1 - x, self.height - 1 - y)
        if edge_dist < 20:
            depth += (20 - edge_dist) * 20
            
        return max(0, depth)

    def _base_depth(self, x, y):
        return self._generate_depth(x, y)

    def _populate_contacts(self):
        # Scale contacts with map size
        area = self.width * self.height
        # Approx 1 contact per 2000 tiles
        num_contacts = max(10, int(area / 2000))
        
        for _ in range(num_contacts):
            t = 'merchant' if random.random() < 0.7 else 'destroyer'
            
            # Find valid water spawn
            for _ in range(10):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if self.get_depth(x, y) > 20: # Ensure not on land
                    break
            
            # create a simple route
            if t == 'merchant':
                route = [(min(self.width - 1, x + i * 10), min(self.height - 1, y + (i % 5) * 2 - 5)) for i in range(10)]
            else:
                # escorts circle locally
                route = [(max(0, x + dx), max(0, y + dy)) for dx, dy in [(-5,0),(0,5),(5,0),(0,-5)]]
            self.contacts.append({'id': self._next_contact_id, 'x': x, 'y': y, 'type': t, 'route': route, 'route_index': 0})
            self._next_contact_id += 1

    def _populate_submarines(self):
        # Add submarines (mix of enemy and allied)
        if self.width < 12 or self.height < 12:
            return
        
        # Scale subs with map size
        area = self.width * self.height
        num_subs = max(3, int(area / 5000))
        
        for _ in range(num_subs):
            sub_type = random.choice(['enemy', 'enemy', 'allied', 'neutral'])
            
            # Find valid deep water spawn
            for _ in range(10):
                x = random.randint(5, self.width - 6)
                y = random.randint(5, self.height - 6)
                d = self.get_depth(x, y)
                if d > 100:
                    break
            
            depth = random.randint(50, min(300, d - 20))
            nation = random.choice(['German', 'Japanese', 'British', 'American', 'French'])
            
            self.submarines.append({
                'id': self._next_sub_id,
                'x': x,
                'y': y,
                'depth': depth,
                'type': sub_type,
                'nation': nation,
                'heading': random.randint(0, 359),
                'speed': random.uniform(2, 6),
                'active': True,
                'detected': False
            })
            self._next_sub_id += 1

    def _populate_wildlife(self):
        # Add marine wildlife
        area = self.width * self.height
        num_wildlife = max(5, int(area / 1000))
        
        wildlife_types = ['whale', 'whale', 'dolphin', 'dolphin', 'large_fish', 'shark', 'school_of_fish']
        
        for _ in range(num_wildlife):
            # Find valid water spawn
            for _ in range(10):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                d = self.get_depth(x, y)
                if d > 20:
                    break
            
            depth = random.randint(10, min(400, d - 10))
            w_type = random.choice(wildlife_types)
            
            self.wildlife.append({
                'id': self._next_wildlife_id,
                'x': x,
                'y': y,
                'depth': depth,
                'type': w_type,
                'heading': random.randint(0, 359),
                'speed': random.uniform(0.5, 3),
                'active': True
            })
            self._next_wildlife_id += 1

    def _populate_ports(self):
        # Add ports along coastlines
        # Scale ports with map size
        area = self.width * self.height
        num_ports = max(3, int(area / 8000))
        
        port_names = ["Portsmouth", "Brest", "Lorient", "St. Nazaire", "La Rochelle", "Bergen", "Trondheim", "Narvik", "Kiel", "Wilhelmshaven", "Scapa Flow", "Liverpool", "Gibraltar", "Malta", "Alexandria", "Naples", "Taranto", "Pearl Harbor", "Midway", "Yokosuka", "Kure", "Sasebo", "Singapore", "Manila", "Surabaya", "Darwin", "Fremantle"]
        
        for i in range(num_ports):
            # Try to find a coastal spot
            for _ in range(100):
                x = random.randint(2, self.width - 3)
                y = random.randint(2, self.height - 3)
                
                # Check if this is water (depth > 0)
                if self.get_depth(x, y) > 0:
                    # Check neighbors for land (depth 0)
                    has_land = False
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if self.get_depth(x + dx, y + dy) == 0:
                                has_land = True
                                break
                        if has_land: break
                    
                    if has_land:
                        # Found a coastal spot!
                        nation = random.choice(['Allied', 'Axis', 'Neutral'])
                        status = 'neutral'
                        if nation == 'Allied': status = 'friendly'
                        elif nation == 'Axis': status = 'hostile'
                        
                        name = random.choice(port_names) if port_names else f"Port {i+1}"
                        
                        self.ports.append({
                            'id': f"port_{i}",
                            'x': x,
                            'y': y,
                            'name': name,
                            'nation': nation,
                            'status': status,
                            'type': 'port'
                        })
                        break

    def get_ports(self):
        """Get all ports on the map."""
        return list(self.ports)

    def step(self):
        # advance AI for each contact
        for c in self.contacts:
            step_contact(c, self)

        # advance torpedoes
        events = []
        for t in list(self.torpedoes):
            res = t.step(self)
            if res:
                events.append(res)
        # prune inactive torpedoes
        self.torpedoes = [t for t in self.torpedoes if t.active]
        return events

    def get_depth(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.depth[y][x]
        return None

    def has_thermocline_between(self, x1, y1, x2, y2):
        # very simple: sample points along the line and see if any thermocline present
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            t = i / steps
            xi = int(round(x1 + dx * t))
            yi = int(round(y1 + dy * t))
            if 0 <= xi < self.width and 0 <= yi < self.height:
                if self.thermocline[yi][xi]:
                    return True
        return False

    def get_contacts(self):
        return list(self.contacts)
    
    def get_submarines(self):
        """Get all submarines on the map."""
        return list(self.submarines)
    
    def get_wildlife(self):
        """Get all wildlife on the map."""
        return list(self.wildlife)
    
    def get_all_sonar_contacts(self):
        """Get all entities that would show up on sonar (subs, ships, wildlife)."""
        all_contacts = []
        all_contacts.extend([{'type': 'ship', 'subtype': c.get('type'), 'x': c['x'], 'y': c['y'], 'id': c['id']} for c in self.contacts])
        all_contacts.extend([{'type': 'submarine', 'subtype': c.get('type'), 'x': c['x'], 'y': c['y'], 'depth': c['depth'], 'id': c['id']} for c in self.submarines])
        all_contacts.extend([{'type': 'wildlife', 'subtype': c.get('type'), 'x': c['x'], 'y': c['y'], 'depth': c['depth'], 'id': c['id']} for c in self.wildlife])
        return all_contacts

    def spawn_torpedo(self, owner_id, x, y, bearing_deg, speed=1.5, target_id=None, homing_strength=0.20):
        # convert bearing (degrees, 0=north) to dx,dy where angles in math: 0 rad -> +x
        # We treat bearing as compass degrees where 0 is north; convert to map vector
        import math
        ang = math.radians((90 - bearing_deg) % 360)
        dx = math.cos(ang)
        dy = math.sin(ang)
        t = Torpedo(owner_id, x, y, dx, dy, speed=speed, target_id=target_id, homing_strength=homing_strength)
        self.torpedoes.append(t)
        return t
    
    def spawn_aircraft(self, aircraft_id, aircraft_type, nation, x, y, patrol_radius=20):
        """Spawn aircraft on patrol."""
        ac = {
            'id': self._next_aircraft_id,
            'aircraft_id': aircraft_id,
            'type': aircraft_type,
            'nation': nation,
            'x': x,
            'y': y,
            'patrol_radius': patrol_radius,
            'endurance_ticks': 100,  # Rough approximation
            'active': True,
            'detected_contacts': []
        }
        self._next_aircraft_id += 1
        self.aircraft.append(ac)
        return ac
    
    def step_aircraft(self):
        """Update aircraft positions and detect contacts."""
        for ac in self.aircraft:
            if not ac['active']:
                continue
            
            # Reduce endurance
            ac['endurance_ticks'] -= 1
            if ac['endurance_ticks'] <= 0:
                ac['active'] = False
                continue
            
            # Random patrol movement
            ac['x'] = max(0, min(self.width - 1, ac['x'] + random.randint(-2, 2)))
            ac['y'] = max(0, min(self.height - 1, ac['y'] + random.randint(-2, 2)))
            
            # Detect submerged contacts (submarines)
            ac['detected_contacts'] = []
            if self.player_sub and self.player_sub.depth > 0:  # Submerged
                dist = ((ac['x'] - self.player_sub.x) ** 2 + (ac['y'] - self.player_sub.y) ** 2) ** 0.5
                if dist < ac['patrol_radius']:
                    # Chance to detect based on depth (shallower = easier to detect)
                    detect_chance = max(0.3, 1.0 - (self.player_sub.depth / 300.0))
                    if random.random() < detect_chance:
                        ac['detected_contacts'].append(self.player_sub)
        
        # Remove inactive aircraft
        self.aircraft = [a for a in self.aircraft if a['active']]
    
    def get_aircraft(self):
        """Get all active aircraft."""
        return list(self.aircraft)
    
    def get_aircraft_threat_level(self) -> str:
        """Get overall aircraft threat level in this tile."""
        if not self.aircraft:
            return 'none'
        
        threat_counts = {a['nation']: len([ac for ac in self.aircraft if ac['nation'] == a['nation']]) 
                        for a in self.aircraft}
        max_threat = max(threat_counts.values())
        
        if max_threat >= 3:
            return 'critical'
        elif max_threat >= 2:
            return 'high'
        elif max_threat >= 1:
            return 'medium'
        return 'low'
