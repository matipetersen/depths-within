"""Captain's orders (DESIGN.md section 5). Every order has a benefit and a hidden cost."""
from .state import clamp


def _live(world):
    return world.active_crew()


def silence_sonar(world):
    s = world.ship
    s.sonar_on = False
    world.deck.mute_all()
    for c in _live(world):
        if c.role == "sonar":
            c.fear = clamp(c.fear - 0.15)
    return "Sonar off. The headsets go quiet."


def restore_sonar(world):
    world.ship.sonar_on = True
    return "Sonar back on."


def isolate(world, cid):
    c = world.crew_by_id(cid)
    if c is None or not c.active or c.isolated:
        return "Nothing to do."
    c.isolated = True
    c.trust = clamp(c.trust - 0.25)
    c.guilt = clamp(c.guilt + 0.15)
    for r in world.ship.rumors.values():
        r.believers.discard(cid)
    for other in _live(world):
        other.trust = clamp(other.trust - 0.03)
    world.ship.attention = clamp(world.ship.attention + 0.03)
    return f"{c.name} is confined to the forward berth."


def release(world, cid):
    c = world.crew_by_id(cid)
    if c is None or not c.isolated:
        return "Nothing to do."
    c.isolated = False
    c.isolated_ticks = 0
    return f"{c.name} is back on the watch bill."


def force_compartment(world, cid):
    """Order a sailor into a flooded compartment. The job gets done; people remember."""
    c = world.crew_by_id(cid)
    if c is None or not c.active:
        return "Nothing to do."
    s = world.ship
    s.hull = clamp(s.hull + 0.05)
    c.fear = clamp(c.fear + 0.2)
    c.guilt = clamp(c.guilt + 0.1)
    for other in _live(world):
        other.trust = clamp(other.trust - 0.12)
        other.guilt = clamp(other.guilt + 0.05)
    return f"{c.name} goes in. The repair holds."


def cancel_rest(world):
    if not world.ship.rest_cancelled:
        for c in _live(world):
            c.trust = clamp(c.trust - 0.03)
    world.ship.rest_cancelled = True
    return "Rest is cancelled for all hands."


def grant_rest(world):
    world.ship.rest_cancelled = False
    return "Normal watch rotation resumes."


def ration(world, item):
    s = world.ship
    s.discipline = clamp(s.discipline + 0.1)
    s.routines["coffee" if item == "tobacco" else "cards"] = clamp(
        s.routines["coffee" if item == "tobacco" else "cards"] - 0.25)
    for c in _live(world):
        c.trust = clamp(c.trust - 0.04)
    return f"{item.capitalize()} is rationed."


def hold_ritual(world):
    """Mess, music, cards: costs mission time, restores routine."""
    s = world.ship
    for item in sorted(s.routines, key=s.routines.get)[:2]:
        s.routines[item] = clamp(s.routines[item] + 0.4)
    world.time_cost += 1.5 / world.patrol_ticks
    for c in _live(world):
        c.fear = clamp(c.fear - 0.03)
    return "The crew eats together. Someone finds a deck of cards."


def address_crew(world):
    """Speak to the boat. Works in proportion to the trust you still have."""
    live = _live(world)
    if not live:
        return "No one to address."
    avg_trust = sum(c.trust for c in live) / len(live)
    for r in world.ship.rumors.values():
        r.intensity = clamp(r.intensity - 0.35 * avg_trust)
    for c in live:
        c.trust = clamp(c.trust - 0.03 + 0.05 * avg_trust)
    return "The captain speaks over the intercom."


def scrub_air(world):
    s = world.ship
    if s.scrubber < 0.12:
        return "The absorbent is spent."
    s.scrubber = clamp(s.scrubber - 0.12)
    s.co2 = clamp(s.co2 - 0.004, 0.005, 0.1)
    return "Fresh absorbent in the scrubbers."


def surface(world):
    s = world.ship
    s.surfaced = True
    s.co2 = max(0.005, s.co2 - 0.01)
    s.attention = clamp(s.attention - 0.1)
    for c in _live(world):
        c.fear = clamp(c.fear - 0.1)
    return "Surfacing. The hatch opens on cold air."


def dive(world):
    world.ship.surfaced = False
    return "Diving."


def active_ping(world):
    s = world.ship
    s.noise = clamp(s.noise + 0.35)
    s.attention = clamp(s.attention + 0.02)
    return "One ping. The hull rings with it."


def silent_running(world, on=True):
    world.ship.silent_running = on
    return "Silent running." if on else "Resuming normal running."


ORDERS = {
    "silence_sonar": silence_sonar, "restore_sonar": restore_sonar, "isolate": isolate,
    "release": release, "force_compartment": force_compartment, "cancel_rest": cancel_rest,
    "grant_rest": grant_rest, "ration": ration, "hold_ritual": hold_ritual,
    "address_crew": address_crew, "scrub_air": scrub_air, "surface": surface, "dive": dive,
    "active_ping": active_ping, "silent_running": silent_running,
}
