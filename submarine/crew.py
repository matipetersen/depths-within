"""Crew system with skills, stress and simple behaviors."""

import random


class CrewMember:
    def __init__(self, name, rank='Seaman', skills=None, traits=None):
        self.name = name
        self.rank = rank
        self.skills = skills or {
            'sonar': 0.5,
            'torpedoes': 0.5,
            'navigation': 0.5,
            'engineering': 0.5,
            'medical': 0.5,
        }
        self.stress = 0.0  # 0..1
        self.morale = 1.0  # 0..1
        self.traits = traits or []
        self.alive = True
        # experience points per skill (increases effective skill)
        self.xp = {k: 0.0 for k in self.skills}
        # if no explicit traits, pick a small random personality set
        if not traits:
            pool = ['brave', 'cautious', 'calm', 'hotheaded', 'methodical', 'quick']
            # assign 1-2 traits
            import random

            self.traits = random.sample(pool, k=random.choice([1, 2]))

    def apply_stress(self, amount):
        self.stress = min(1.0, self.stress + amount)
        # high stress reduces skill effectiveness
        for k in self.skills:
            self.skills[k] = max(0.0, self.skills[k] - amount * 0.1)

    def gain_experience(self, skill, amount=1.0):
        if skill not in self.xp:
            self.xp[skill] = 0.0
        self.xp[skill] += float(amount)
        # small passive improvement to base skill over time
        self.skills[skill] = min(1.0, self.skills.get(skill, 0.0) + (self.xp[skill] ** 0.5) * 0.001)

    def effective_skill(self, skill):
        """Return an effective skill value factoring experience, stress and traits."""
        base = self.skills.get(skill, 0.0)
        xp_bonus = min(0.5, (self.xp.get(skill, 0.0) ** 0.5) * 0.02)
        stress_penalty = max(0.0, 1.0 - self.stress * 0.5)
        trait_bonus = 0.0
        if 'brave' in self.traits and skill == 'torpedoes':
            trait_bonus += 0.03
        if 'methodical' in self.traits and skill in ('engineering', 'sonar'):
            trait_bonus += 0.04
        if 'quick' in self.traits and skill == 'navigation':
            trait_bonus += 0.03
        return max(0.0, min(1.0, (base + xp_bonus + trait_bonus) * stress_penalty))

    def heal(self, amount):
        self.stress = max(0.0, self.stress - amount)

    def __repr__(self):
        return f"<Crew {self.name} {self.rank} skills={self.skills}>"
