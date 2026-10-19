"""Sonar detection math and helpers.

This module implements a simple detection probability calculation used
by the Sonar system. It's intentionally small but models:
- target noise/signature
- range attenuation (1/r^2 simplified)
- thermocline penalty
- active ping (much higher detection)
"""
import math
import random


def detection_probability(range_m, target_noise, own_noise, sea_state=1.0, thermocline=False, active=False, sensitivity=1.0):
    """Return probability of detection (0..1).

    range_m: distance in meters
    target_noise: relative noise signature (0..1)
    own_noise: own noise level (0..1)
    sea_state: multiplier (1.0 calm, >1 noisy)
    thermocline: whether thermocline present between sensors
    active: whether active ping is used
    """
    # Base signal is proportional to target noise, penalized by range^2
    # add small floor to range to avoid div0
    r = max(1.0, float(range_m))
    signal = target_noise / (r * r / 1e6)  # scale factor: 1e6 to keep values reasonable

    # Noise floor combines own_noise and sea_state
    noise = (own_noise + 0.3 * sea_state)

    # thermocline reduces signal sharply for passive
    if thermocline and not active:
        signal *= 0.25

    # active ping multiplies signal considerably but also reveals position
    if active:
        signal *= 8.0

    # sensitivity multiplier (gameplay tuning)
    signal *= float(sensitivity)

    # SNR-like metric
    snr = signal / max(1e-6, noise)

    # convert to probability via logistic function
    # tweak slope and midpoint for playable feel
    prob = 1.0 / (1.0 + math.exp(- (snr - 0.5) * 1.5))
    # clamp
    return max(0.0, min(1.0, prob))


class Sonar:
    def __init__(self, owner, tactical_map=None, sensitivity=1.0, deterministic=False):
        self.owner = owner
        self.tactical_map = tactical_map
        # sensitivity multiplier for detection strength
        self.sensitivity = float(sensitivity)
        # when True, detect() returns deterministic results for testing
        self.deterministic = bool(deterministic)

    def detect(self, active=False, sea_state=None, deterministic=None):
        """Detect contacts and return a list similar to earlier API.

        active: whether the detection is an active ping (higher probability)
        """
        contacts = []
        if self.tactical_map is None or self.owner is None:
            return contacts

        for c in self.tactical_map.get_contacts():
            dx = c['x'] - self.owner.x
            dy = c['y'] - self.owner.y
            dist = int(math.hypot(dx, dy) * 100)
            therm = self.tactical_map.has_thermocline_between(self.owner.x, self.owner.y, c['x'], c['y'])
            # target_noise derived from type
            tnoise = 0.6 if c.get('type') == 'merchant' else 0.9
            own_noise = 0.2
            try:
                own_noise += 0.5 * (getattr(self.owner.systems, 'speed', 0.0) / max(1.0, getattr(self.owner, 'surface_speed', 1.0)))
            except Exception:
                own_noise = own_noise

            # sea_state could come from world/weather — default 1.0
            if sea_state is None:
                sea_state = 1.0

            prob = detection_probability(dist, tnoise, own_noise, sea_state=sea_state, thermocline=therm, active=active, sensitivity=self.sensitivity)

            # deterministic override from method arg or object flag
            det = self.deterministic if deterministic is None else bool(deterministic)
            if det:
                # deterministic decision: compare prob against threshold 0.5
                hit = prob >= 0.5
            else:
                hit = random.random() < prob

            if hit:
                # compute bearing
                angle = (90 - math.degrees(math.atan2(dy, dx))) % 360
                contacts.append({'id': c.get('type'), 'bearing': round(angle, 1), 'range': dist, 'type': c.get('type')})

        return contacts
