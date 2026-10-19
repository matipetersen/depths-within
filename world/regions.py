"""World map regions and navigation.

Regions may be loaded from `data/regions.json` and provide routing
information for convoys, minefields, and depth contours.
"""
import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


class Region:
    def __init__(self, name, data=None):
        self.name = name
        self.convoy_routes = []
        self.minefields = []
        self.depth_contours = []
        if data:
            self.convoy_routes = data.get('convoy_routes', [])
            self.minefields = data.get('minefields', [])
            self.depth_contours = data.get('depth_contours', [])


def load_regions():
    path = os.path.join(DATA_DIR, 'regions.json')
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            regs = [Region(r.get('name', 'Unnamed'), r) for r in data]
            return regs
    except Exception:
        return []
