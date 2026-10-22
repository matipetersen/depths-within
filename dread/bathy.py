"""The sea floor and what the hull can bear (DESIGN.md 16.1). Pure functions of position and hull."""
import math

COAST = (100.0, 12.0)          # the base: the shelf is shallow here and falls away with distance
KEEL_MARGIN = 8                # the boat cannot sit closer to the bottom than this
MAX_DEPTH = 900


def seabed(x: float, y: float) -> int:
    """Metres of water under the surface at a chart position: a shelf by the coast, a trench far out."""
    d = math.hypot(x - COAST[0], y - COAST[1])
    ripple = 20 * ((int(x) // 7 + int(y) // 5) % 3)
    return int(min(MAX_DEPTH, 45 + 4.0 * d + ripple))


def crush_depth(hull: float) -> int:
    """How deep this hull, as it is now, can go before it gives: 300 m when sound, 100 m when it is barely there."""
    return int(100 + 200 * max(0.0, min(1.0, hull)))
