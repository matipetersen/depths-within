"""Compartment random events and handlers.

This module defines random adverse events that can occur in compartments
(e.g., flooding bursts, fires, short-circuits, crew injuries) and provides
functions to generate and attempt resolution of these events using crew
skills and submarine systems.
"""
import random
import math


def choose_compartment_for_event(sub):
    """Choose a compartment biased towards damaged or flooded ones."""
    comps = sub.compartments if hasattr(sub, 'compartments') else []
    if not comps:
        return None
    weights = []
    for c in comps:
        # more damaged/flooded compartments are more likely to have events
        w = 1.0 + (1.0 - c.integrity) * 4.0 + c.flooding * 3.0
        weights.append(max(0.1, w))
    total = sum(weights)
    r = random.random() * total
    acc = 0.0
    for c, w in zip(comps, weights):
        acc += w
        if r <= acc:
            return c
    return comps[0]


def select_responder(sub, comp, skill):
    """Pick the best available crew member for a given skill. Prefer those
    with lower stress and matching traits.
    """
    best = None
    best_score = -1.0
    for cm in getattr(sub, 'crew', []):
        if not getattr(cm, 'alive', True):
            continue
        eff = cm.effective_skill(skill)
        # trait adjustments
        if 'calm' in cm.traits:
            eff += 0.02
        if 'hotheaded' in cm.traits and skill == 'torpedoes':
            eff -= 0.02
        score = eff - cm.stress * 0.1
        if score > best_score:
            best_score = score
            best = cm
    return best


def generate_event(sub):
    """Possibly generate a random event for the submarine's compartments.

    Returns an event dict if an event occurred, else None.
    """
    # base chance per tick
    chance = 0.015
    # increase chance with overall damage
    avg_integrity = 1.0
    comps = getattr(sub, 'compartments', [])
    if comps:
        avg_integrity = sum(c.integrity for c in comps) / len(comps)
        chance *= (1.0 + (1.0 - avg_integrity) * 3.0)

    if random.random() > chance:
        return None

    comp = choose_compartment_for_event(sub)
    if comp is None:
        return None

    # choose event type weighted by compartment state
    types = ['flood_burst', 'fire', 'short_circuit', 'equipment_failure', 'crew_injury']
    # weight fires slightly more in high battery/electrical areas
    weights = [1, 1, 0.8, 0.8, 0.6]
    idx = random.choices(range(len(types)), weights=weights, k=1)[0]
    etype = types[idx]

    event = {'type': etype, 'compartment': comp, 'severity': random.uniform(0.1, 0.6)}
    return event


def resolve_event(sub, event, responder=None, deterministic=False):
    """Apply event effects and let crew respond. Returns a dict describing
    the outcome for logging.
    - `responder`: optional CrewMember to handle the event (used in tests/UI).
    - `deterministic`: if True, use deterministic thresholds instead of RNG.
    """
    comp = event.get('compartment')
    etype = event.get('type')
    sev = event.get('severity', 0.2)

    outcome = {'event': etype, 'compartment': comp.name if comp else 'unknown', 'severity': sev, 'handled': False, 'notes': ''}

    if etype == 'flood_burst':
        # immediate flooding increase
        inc = sev * 0.5
        comp.flooding = min(1.0, comp.flooding + inc)
        # responder with engineering skill can patch to reduce flooding
        if responder is None:
            responder = select_responder(sub, comp, 'engineering')
        if responder:
            skill = responder.effective_skill('engineering')
            # success probability scales with skill and experience
            prob = min(0.99, 0.2 + skill * 0.6)
            if deterministic:
                hit = prob >= 0.5
            else:
                hit = random.random() < prob
            if hit:
                # successful mitigation reduces flooding
                reduce = sev * 0.5 * skill
                comp.flooding = max(0.0, comp.flooding - reduce)
                responder.gain_experience('engineering', amount=sev * 5)
                outcome['handled'] = True
                outcome['notes'] = f"{responder.name} patched the leak"
            else:
                outcome['notes'] = f"{responder.name} failed to fully secure the leak"
                responder.apply_stress(0.05)
        else:
            outcome['notes'] = 'No crew available to respond'

    elif etype == 'fire':
        # fire damages integrity over time; immediate integrity hit
        hit = sev * 0.3
        comp.integrity = max(0.0, comp.integrity - hit)
        if responder is None:
            responder = select_responder(sub, comp, 'engineering') or select_responder(sub, comp, 'medical')
        if responder:
            skill = responder.effective_skill('engineering')
            prob = min(0.95, 0.15 + skill * 0.65)
            if deterministic:
                hitok = prob >= 0.5
            else:
                hitok = random.random() < prob
            if hitok:
                # extinguished
                outcome['handled'] = True
                outcome['notes'] = f"{responder.name} extinguished the fire"
                responder.gain_experience('engineering', amount=sev * 6)
            else:
                # fire spreads: increase flooding in adjacent compartments (handled elsewhere by propagation)
                outcome['notes'] = f"{responder.name} struggled to contain the fire"
                responder.apply_stress(0.08)
        else:
            outcome['notes'] = 'Fire uncontrolled; no responders'

    elif etype == 'short_circuit':
        # may reduce battery or cause small fires
        drop = sev * 0.2
        try:
            sub.systems.battery = max(0.0, getattr(sub.systems, 'battery', 1.0) - drop)
        except Exception:
            pass
        if responder is None:
            responder = select_responder(sub, comp, 'engineering')
        if responder:
            skill = responder.effective_skill('engineering')
            prob = 0.2 + skill * 0.5
            if deterministic:
                hitok = prob >= 0.5
            else:
                hitok = random.random() < prob
            if hitok:
                outcome['handled'] = True
                outcome['notes'] = f"{responder.name} repaired the short"
                responder.gain_experience('engineering', amount=sev * 4)
            else:
                outcome['notes'] = f"{responder.name} couldn't fully isolate the fault"
                responder.apply_stress(0.04)
        else:
            outcome['notes'] = 'No engineer present'

    elif etype == 'equipment_failure':
        # degrade some equipment (not fully modeled) and increase repair needs
        comp.integrity = max(0.0, comp.integrity - sev * 0.1)
        if responder is None:
            responder = select_responder(sub, comp, 'engineering')
        if responder:
            responder.gain_experience('engineering', amount=sev * 2)
            outcome['handled'] = True
            outcome['notes'] = f"{responder.name} worked to repair equipment"
        else:
            outcome['notes'] = 'No crew to repair equipment'

    elif etype == 'crew_injury':
        # injure a random crew member in sub
        crew = getattr(sub, 'crew', [])
        if crew:
            # if responder specified and deterministic, let that influence victim selection
            if responder is not None and deterministic:
                victim = responder
            else:
                victim = random.choice(crew)
            # injury severity may kill or incapacitate
            if deterministic:
                died = sev * 0.2 >= 0.5
            else:
                died = random.random() < sev * 0.2
            if died:
                victim.alive = False
                outcome['notes'] = f"{victim.name} was killed"
            else:
                victim.apply_stress(0.3)
                victim.morale = max(0.0, victim.morale - 0.2)
                outcome['notes'] = f"{victim.name} injured and shaken"
            outcome['handled'] = True
        else:
            outcome['notes'] = 'No crew present to be injured'

    return outcome