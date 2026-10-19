"""Random encounters and event generation for the strategic layer.

This module provides a small generator for historical encounters and
dynamic events that can be integrated into the tactical map.
"""
import random
import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


class Encounter:
    def __init__(self, encounter_type, details=None):
        self.encounter_type = encounter_type
        self.details = details or {}


def load_encounter_templates():
    path = os.path.join(DATA_DIR, 'encounters.json')
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        except Exception:
            return []
    return []


def generate_random_encounter(region=None):
    """Return an Encounter instance chosen randomly from templates.

    `region` is optional and may bias encounter selection.
    """
    templates = load_encounter_templates()
    if not templates:
        # fallback basic encounter
        et = random.choice(['convoy', 'patrol', 'lore_event'])
        details = {'region': getattr(region, 'name', None)}
        return Encounter(et, details)
    tmpl = random.choice(templates)
    etype = tmpl.get('type', 'unknown')
    details = tmpl.get('details', {})
    if region:
        details.setdefault('region', getattr(region, 'name', None))
    return Encounter(etype, details)
