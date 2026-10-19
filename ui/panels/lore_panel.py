# Panel for displaying historical/lore content
from world.lore import LoreManager

class LorePanel:
    def __init__(self):
        self.lore_manager = LoreManager()
        self.current_story = None
        self.current_encounter = None
        self.current_snippet = None

    def show_random_crew_story(self):
        self.current_story = self.lore_manager.get_random_crew_story()

    def show_random_encounter(self):
        self.current_encounter = self.lore_manager.get_random_encounter()

    def show_lore_snippet(self, snippet_type=None):
        self.current_snippet = self.lore_manager.get_lore_snippet(snippet_type)

    def draw(self):
        # Render the current lore content (stub)
        # For console-mode we provide a minimal textual representation.
        if self.current_story:
            s = self.current_story
            print('--- Crew Story ---')
            print(s.get('story', str(s)))
            print('------------------')
        elif self.current_encounter:
            e = self.current_encounter
            print('--- Encounter ---')
            print(e.get('description', str(e)))
            print('-----------------')
        elif self.current_snippet:
            sn = self.current_snippet
            print('--- Lore ---')
            print(sn.get('text', str(sn)))
            print('------------')
        else:
            print('No lore selected')
