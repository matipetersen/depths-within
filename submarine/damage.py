"""Damage system coordinates compartment damage and propagation."""

class DamageSystem:
    def __init__(self):
        self.damage_events = []

    def apply_damage(self, compartment, amount):
        # Apply damage to a compartment and record event
        compartment.apply_damage(amount)
        self.damage_events.append({'compartment': compartment.name, 'amount': amount})

        # Simple propagation: if integrity very low, spread to adjacent compartments
        # (adjacency model is not implemented here; this is a placeholder)
        if compartment.integrity < 0.2:
            # mark a flag or create secondary effects in a real implementation
            pass
