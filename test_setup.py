#!/usr/bin/env python3
"""Quick test to check if crew generation works without errors."""

import sys
sys.path.insert(0, '/Users/matiaspetersen/Documents/Depths within')

from ui.setup_screen import quick_setup

try:
    print("Testing quick setup...")
    faction, crew_list = quick_setup("Germany")
    
    print(f"\nFaction: {faction.get('name')}")
    print(f"Crew count: {len(crew_list)}")
    print(f"\nFirst 5 crew members:")
    
    for i, crew in enumerate(crew_list[:5]):
        if crew is None:
            print(f"  {i+1}. ERROR: None crew member!")
        else:
            name = crew.get('name', 'Unknown')
            rank = crew.get('rank', 'Seaman')
            spec = crew.get('specialization') or 'General'
            print(f"  {i+1}. {name} | {rank} | {spec}")
    
    print("\n✓ Setup test passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
