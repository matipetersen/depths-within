import json
import os
import random
import math

from submarine.compartments import Compartment
from submarine.crew import CrewMember
from submarine.sonar import Sonar as SonarImpl

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


# sonar implementation moved to submarine/sonar.py


class SubmarineSystems:
    def __init__(self):
        self.battery = 1.0
        self.oxygen = 1.0
        self.hull = 1.0
        self.depth = 0
        self.speed = 0
        self.speed_mode = 'STANDARD'  # SLOW, STANDARD, FULL, FLANK
        self.silent_running = False
        self.noise_level = 1.0  # 0.0 = silent, 1.0 = normal, 2.0+ = loud


class Submarine:
    def __init__(self, id_, nation, torpedoes, max_depth, surface_speed, submerged_speed, sonar_name, radar, tactical_map=None):
        self.id = id_
        self.nation = nation
        self.torpedoes = torpedoes
        self.max_depth = max_depth
        self.surface_speed = surface_speed
        self.submerged_speed = submerged_speed
        self.sonar_name = sonar_name
        self.radar = radar
        self.compartments = []
        self.crew = []
        self.systems = SubmarineSystems()
        # pending compartment events (if deferred) and control flag
        self.pending_events = []
        self.defer_event_resolution = False
        self.tactical_map = tactical_map
        self.x = tactical_map.width // 2 if tactical_map else 10
        self.y = tactical_map.height // 2 if tactical_map else 10
        self.sonar = SonarImpl(owner=self, tactical_map=tactical_map)
        # Speed and stealth settings
        self.speed_multipliers = {
            'SLOW': 0.33,
            'STANDARD': 0.66,
            'FULL': 1.0,
            'FLANK': 1.5
        }
        # register player sub on tactical map for AI reference
        try:
            if tactical_map is not None:
                tactical_map.player_sub = self
        except Exception:
            pass
            # logger will be attached by Game if available

    @classmethod
    def from_json_default(cls, tactical_map=None):
        # Load the first submarine entry from data/submarines.json if present
        try:
            path = os.path.join(DATA_DIR, 'submarines.json')
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    entry = data[0]
                    obj = cls(
                        id_=entry.get('id', 'sub_default'),
                        nation=entry.get('nation', 'unknown'),
                        torpedoes=entry.get('torpedoes', {}),
                        max_depth=entry.get('max_depth', 100),
                        surface_speed=entry.get('surface_speed', 10),
                        submerged_speed=entry.get('submerged_speed', 5),
                        sonar_name=entry.get('sonar', None),
                        radar=entry.get('radar', False),
                        tactical_map=tactical_map,
                    )
                    # Populate compartments even when loading from JSON
                    if not obj.compartments or len(obj.compartments) == 0:
                        names = ['Conning Tower', 'Control Room', 'Torpedo Room', 'Engine Room', 'Crew Quarters', 'Battery Room']
                        obj.compartments = [Compartment(n) for n in names]
                        # simple adjacency: linear chain for default layout
                        for i, c in enumerate(obj.compartments):
                            nbrs = []
                            if i > 0:
                                nbrs.append(obj.compartments[i - 1])
                            if i < len(obj.compartments) - 1:
                                nbrs.append(obj.compartments[i + 1])
                            c.neighbors = nbrs
                    return obj
        except Exception:
            pass
        # fallback default
        obj = cls('demo_sub', 'Neutral', {'bow': 4}, 200, 12, 6, 'BasicSonar', False, tactical_map)
        # populate default compartments
        names = ['Conning Tower', 'Control Room', 'Torpedo Room', 'Engine Room', 'Crew Quarters', 'Battery Room']
        obj.compartments = [Compartment(n) for n in names]
        # simple adjacency: linear chain for default layout
        for i, c in enumerate(obj.compartments):
            nbrs = []
            if i > 0:
                nbrs.append(obj.compartments[i - 1])
            if i < len(obj.compartments) - 1:
                nbrs.append(obj.compartments[i + 1])
            c.neighbors = nbrs
        # populate simple crew from data/crew_names.json
        try:
            with open(os.path.join(DATA_DIR, 'crew_names.json'), 'r', encoding='utf-8') as f:
                names = json.load(f)
                nation = obj.nation if obj.nation in names else list(names.keys())[0]
                sample = names.get(nation, list(names.values())[0])
                for i, nm in enumerate(sample[:6]):
                    obj.crew.append(CrewMember(nm, rank='Petty' if i>0 else 'Captain'))
        except Exception:
            # fallback crew
            obj.crew = [CrewMember('Crew '+str(i)) for i in range(6)]

        return obj

    def dive(self, meters: int):
        self.systems.depth += meters
        # print(f"Diving {meters}m -> depth now {self.systems.depth}m")

    def surface(self):
        self.systems.depth = 0
        # print("Surfaced: depth now 0m")
    
    def calculate_noise_signature(self) -> float:
        """Calculate current noise signature (0.0 to 10.0+)."""
        # Base noise from speed
        base_noise = {
            'SLOW': 2.0,
            'STANDARD': 5.0,
            'FULL': 8.0,
            'FLANK': 15.0
        }.get(self.systems.speed_mode, 5.0)
        
        # Silent running modifier
        if self.systems.silent_running:
            base_noise *= 0.4
        
        # Depth modifier (deeper = slightly quieter due to pressure/density?)
        # Actually, deeper usually means less cavitation, so yes.
        if self.systems.depth > 50:
            base_noise *= 0.9
        if self.systems.depth > 150:
            base_noise *= 0.8
            
        # Action modifiers (transient)
        # TODO: Add transient noise from firing/repairing
        
        self.systems.noise_level = base_noise
        return base_noise

    def set_speed_mode(self, mode: str):
        """Set speed mode: SLOW, STANDARD, FULL, or FLANK"""
        if mode in self.speed_multipliers:
            old_mode = self.systems.speed_mode
            self.systems.speed_mode = mode
            
            # Recalculate noise
            noise = self.calculate_noise_signature()
            
            return f"Speed: {old_mode} → {mode} (Noise Est: {noise:.1f})"
        return f"Invalid speed mode. Use: SLOW, STANDARD, FULL, or FLANK"
    
    def toggle_silent_running(self):
        """Toggle silent running mode - reduces noise but costs more battery"""
        self.systems.silent_running = not self.systems.silent_running
        
        # Recalculate noise
        noise = self.calculate_noise_signature()
        
        if self.systems.silent_running:
            return f"🔇 SILENT RUNNING ENABLED - Noise reduced to {noise:.1f}, increased battery drain"
        else:
            return f"🔊 SILENT RUNNING DISABLED - Noise increased to {noise:.1f}"
    
    def repair_compartment(self, compartment_name: str = None):
        """Attempt to repair a damaged compartment"""
        if not self.compartments:
            return "No compartments to repair"
        
        # Find damaged compartment
        target = None
        if compartment_name:
            target = next((c for c in self.compartments if compartment_name.lower() in c.name.lower()), None)
        else:
            # Auto-select most damaged
            target = min(self.compartments, key=lambda c: c.integrity)
        
        if not target:
            return f"Compartment '{compartment_name}' not found"
        
        if target.integrity >= 1.0 and target.flooding <= 0.0:
            return f"{target.name} is undamaged"
        
        # Repair amount depends on crew
        repair_amount = 0.15
        old_integrity = target.integrity
        old_flooding = target.flooding
        
        target.integrity = min(1.0, target.integrity + repair_amount)
        target.flooding = max(0.0, target.flooding - repair_amount)
        
        # Cost battery
        self.systems.battery = max(0, self.systems.battery - 0.02)
        
        return f"🔧 Repairing {target.name}: Hull {old_integrity:.0%}→{target.integrity:.0%}, Flooding {old_flooding:.0%}→{target.flooding:.0%}"

    def step(self):
        # Called each turn; drains battery/oxygen based on speed and mode
        battery_drain = 0.0005
        
        # Speed mode affects battery drain
        speed_mult = self.speed_multipliers.get(self.systems.speed_mode, 1.0)
        battery_drain *= speed_mult
        
        # Silent running increases battery drain significantly
        if self.systems.silent_running:
            battery_drain *= 2.0
        
        # Submerged drains more battery
        if self.systems.depth > 0:
            battery_drain *= 1.5
        
        self.systems.battery = max(0.0, self.systems.battery - battery_drain)
        self.systems.oxygen = max(0.0, self.systems.oxygen - 0.0002)
        # propagate flooding between adjacent compartments slowly
        try:
            transfers = []
            for c in self.compartments:
                for n, delta in c.propagate_to_neighbors():
                    transfers.append((c, n, delta))
            for src, dst, d in transfers:
                src.flooding = max(0.0, src.flooding - d)
                dst.flooding = min(1.0, dst.flooding + d)
                # severe flooding reduces integrity over time
                if dst.flooding > 0.6:
                    dst.integrity = max(0.0, dst.integrity - 0.01 * dst.flooding)
        except Exception:
            pass
        # random compartment events
        try:
            from submarine.compartment_events import generate_event, resolve_event
            ev = generate_event(self)
            if ev:
                # if event resolution is deferred (UI assignment), queue the event
                if getattr(self, 'defer_event_resolution', False):
                    try:
                        self.pending_events.append(ev)
                        if hasattr(self, 'logger') and getattr(self, 'logger') is not None:
                            self.logger.log(f"Deferred event: {ev.get('type')} in {ev.get('compartment').name}")
                    except Exception:
                        pass
                else:
                    res = resolve_event(self, ev)
                    # log via attached logger if present
                    try:
                        if hasattr(self, 'logger') and getattr(self, 'logger') is not None:
                            self.logger.log(f"Event: {res.get('event')} in {res.get('compartment')}: {res.get('notes')}")
                    except Exception:
                        pass
        except Exception:
            pass

    def status(self):
        return (
            f"Submarine {self.id} | Depth: {self.systems.depth}m | Speed: {self.systems.speed}kn | "
            f"Battery: {self.systems.battery:.2f} | O2: {self.systems.oxygen:.2f}"
        )

    def move(self, dx, dy):
        if self.tactical_map:
            self.x = max(0, min(self.tactical_map.width - 1, self.x + dx))
            self.y = max(0, min(self.tactical_map.height - 1, self.y + dy))
        else:
            self.x += dx
            self.y += dy

    def fire_torpedo(self, bearing_deg=None, target_xy=None, speed=1.5):
        """Fire a torpedo from the submarine.

        Provide either `bearing_deg` (compass degrees, 0=north) or `target_xy` tuple
        (x,y) to aim directly. Returns the spawned Torpedo object or None on failure.
        """
        if not self.tactical_map:
            print('No tactical map available to spawn torpedo')
            return None

        # check ammo in simple bow rack
        try:
            if isinstance(self.torpedoes, dict):
                # assume 'bow' key
                if self.torpedoes.get('bow', 0) <= 0:
                    print('No bow torpedoes available')
                    return None
                self.torpedoes['bow'] = max(0, self.torpedoes.get('bow', 0) - 1)
        except Exception:
            pass

        # compute bearing if target given
        target_id = None
        if target_xy is not None and bearing_deg is None:
            tx, ty = target_xy
            import math

            dx = tx - self.x
            dy = ty - self.y
            # bearing: compass degrees where 0 = north
            bearing_deg = (90 - math.degrees(math.atan2(dy, dx))) % 360

        if bearing_deg is None:
            print('No aim specified for torpedo')
            return None

        # if calling code passed a selected target id (via attribute), prefer that
        try:
            if hasattr(self, 'selected_target_id') and getattr(self, 'selected_target_id'):
                target_id = getattr(self, 'selected_target_id')
        except Exception:
            target_id = None

        # spawn at submarine position; pass target id for homing behavior
        torp = self.tactical_map.spawn_torpedo(self.id, self.x, self.y, bearing_deg, speed=speed, target_id=target_id)
        print(f'Fired torpedo bearing {bearing_deg:.1f} from ({self.x},{self.y})')
        return torp