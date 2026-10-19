# Handles switching between game states (menu, tactical, strategic, etc.)
class StateManager:
    def __init__(self):
        self.current_state = None
        self.states = {}

    def register(self, name, state_obj):
        self.states[name] = state_obj

    def change_state(self, new_state_name):
        self.current_state = self.states.get(new_state_name)
        if hasattr(self.current_state, 'on_enter'):
            self.current_state.on_enter()

    def tick(self):
        if self.current_state and hasattr(self.current_state, 'tick'):
            self.current_state.tick()
