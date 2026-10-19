"""Small demo scenario runner for the WWII Sub Roguelike starter project.

This script creates a `Game` instance, forces a compartment event, defers
resolution so the player (script) can choose a responder, fires a torpedo,
steps the world for a few ticks, resolves the event, and prints logs and
final submarine state.

Run with:
    python scripts/demo_scenario.py
"""

import os
import sys
import random
# make project root importable when running the script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.game import Game
from submarine.compartment_events import resolve_event


def run_demo(seed=1234, ticks=8):
    random.seed(seed)
    G = Game()
    print('\nDemo: creating game and submarine')
    # ensure we're in console/ascii fallback mode for readable output
    G.ascii_gui = True
    G.ascii_use_color = False

    # defer event resolution so we can show how to list and resolve events
    G.submarine.defer_event_resolution = True
    # ensure there are compartments and crew (some setups may not populate defaults)
    if not getattr(G.submarine, 'compartments', None):
        names = ['Conning Tower', 'Control Room', 'Torpedo Room', 'Engine Room', 'Crew Quarters', 'Battery Room']
        from submarine.compartments import Compartment
        G.submarine.compartments = [Compartment(n) for n in names]
        for i, c in enumerate(G.submarine.compartments):
            nbrs = []
            if i > 0:
                nbrs.append(G.submarine.compartments[i - 1])
            if i < len(G.submarine.compartments) - 1:
                nbrs.append(G.submarine.compartments[i + 1])
            c.neighbors = nbrs

    if not getattr(G.submarine, 'crew', None):
        from submarine.crew import CrewMember
        G.submarine.crew = [CrewMember('Captain'), CrewMember('Chief'), CrewMember('Eng1'), CrewMember('Med1')]

    # create a forced event on a mid ship compartment
    if G.submarine.compartments and len(G.submarine.compartments) >= 3:
        target_comp = G.submarine.compartments[2]
    else:
        target_comp = G.submarine.compartments[0] if G.submarine.compartments else None

    if target_comp:
        ev = {'type': 'flood_burst', 'compartment': target_comp, 'severity': 0.45}
        G.submarine.pending_events.append(ev)
        print(f"Forced event queued: {ev['type']} in {target_comp.name} (sev={ev['severity']:.2f})")

    # list crew
    print('\nCrew:')
    for i, cm in enumerate(G.submarine.crew):
        print(f"  [{i}] {cm.name} - eng eff: {cm.effective_skill('engineering'):.2f}")

    # Fire a torpedo north-east to create activity on the tactical map
    print('\nFiring a test torpedo (bearing 45 deg)')
    try:
        G.submarine.fire_torpedo(bearing_deg=45)
    except Exception as ex:
        print('Failed to fire torpedo:', ex)

    # step the world a few ticks
    print('\nAdvancing world ticks:')
    for t in range(ticks):
        G._tick()
        print(f' Tick {t+1} -> Battery: {G.submarine.systems.battery:.3f}, Pending events: {len(G.submarine.pending_events)}')

    # show pending events
    print('\nPending events:')
    for i, e in enumerate(G.submarine.pending_events):
        cname = e.get('compartment').name if e.get('compartment') else 'unknown'
        print(f"  [{i}] {e.get('type')} in {cname} (sev={e.get('severity'):.2f})")

    # Auto-resolve the first pending event using the best responder
    if G.submarine.pending_events:
        ev = G.submarine.pending_events.pop(0)
        # pick the best available responder automatically
        responder = None
        best_score = -1.0
        for cm in getattr(G.submarine, 'crew', []):
            if not getattr(cm, 'alive', True):
                continue
            score = cm.effective_skill('engineering') - cm.stress * 0.1
            if score > best_score:
                best_score = score
                responder = cm
        print(f"\nResolving event with responder: {responder.name if responder else 'auto'}")
        res = resolve_event(G.submarine, ev, responder=responder, deterministic=True)
        print('Resolve result:', res.get('notes'))

    # advance a couple more ticks to let torpedo/contact activity proceed
    for t in range(3):
        G._tick()

    # print recent logs and final status
    print('\nRecent logs:')
    for l in G.logger.recent()[-10:]:
        print(' -', l['text'])

    print('\nFinal Submarine status:')
    print(G.submarine.status())
    print('\nCompartments:')
    for c in G.submarine.compartments:
        print(f" - {c.name}: integrity={c.integrity:.2f} flooding={c.flooding:.2f}")


if __name__ == '__main__':
    run_demo()
