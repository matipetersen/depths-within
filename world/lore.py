# Lore and story integration for logs, encounters, and crew
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

class LoreManager:
    def __init__(self):
        self.crew_stories = self._load_json('crew_stories.json')
        self.historical_encounters = self._load_json('historical_encounters.json')
        self.lore_snippets = self._load_json('lore_snippets.json')

    def _load_json(self, filename):
        path = os.path.join(DATA_DIR, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def get_random_crew_story(self):
        import random
        return random.choice(self.crew_stories) if self.crew_stories else None

    def get_random_encounter(self):
        import random
        return random.choice(self.historical_encounters) if self.historical_encounters else None

    def get_lore_snippet(self, snippet_type=None):
        import random
        if snippet_type:
            filtered = [s for s in self.lore_snippets if s['type'] == snippet_type]
            return random.choice(filtered) if filtered else None
        return random.choice(self.lore_snippets) if self.lore_snippets else None
