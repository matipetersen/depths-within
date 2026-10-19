# Submarine compartments and damage
class Compartment:
    def __init__(self, name):
        self.name = name
        self.flooding = 0.0  # 0.0..1.0
        self.integrity = 1.0  # 0.0..1.0
        self.crew = []
        self.equipment = {}
        # neighboring compartments (references)
        self.neighbors = []

    def apply_damage(self, amount):
        # reduce integrity, increase flooding if hull compromised
        self.integrity = max(0.0, self.integrity - amount)
        if self.integrity < 0.5:
            # leaking proportional to damage
            self.flooding = min(1.0, self.flooding + (0.5 - self.integrity) * 0.5)

    def repair(self, amount):
        self.integrity = min(1.0, self.integrity + amount)
        if self.integrity > 0.8:
            # repairs reduce flooding gradually
            self.flooding = max(0.0, self.flooding - amount * 0.5)

    def propagate_to_neighbors(self):
        """Return a list of (neighbor, delta) pairs representing water
        that should transfer to neighbors this tick.
        """
        transfers = []
        if self.flooding <= 0.0:
            return transfers
        # transfer proportionally to integrity (more damaged neighbors take more)
        for n in self.neighbors:
            if n is None:
                continue
            # fraction to transfer this tick
            frac = 0.05 * (1.0 - n.integrity)
            if frac <= 0.0:
                continue
            delta = min(self.flooding, frac * (1.0 - self.integrity + 0.1))
            if delta > 0:
                transfers.append((n, delta))
        return transfers
