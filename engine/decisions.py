"""
Captain's Decision System
Handles interactive dilemmas and choices that the player must make.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional, Any
import random

@dataclass
class DecisionOption:
    """A single choice within a decision."""
    key: str  # '1', '2', '3', etc.
    text: str
    tooltip: str = ""
    
    # Effects (can be positive or negative)
    morale_change: float = 0.0
    stress_change: float = 0.0
    supplies_change: Dict[str, float] = field(default_factory=dict)
    hull_damage: float = 0.0
    xp_reward: int = 0
    
    # Logic hooks
    required_skill: Optional[str] = None  # e.g. 'medical' > 0.5
    required_item: Optional[str] = None
    
    # Outcome description
    success_message: str = "Success!"
    failure_message: str = "Failed."
    
    # Probability of success (if skill check involved)
    success_chance: float = 1.0

@dataclass
class Decision:
    """A decision event presented to the captain."""
    id: str
    title: str
    description: str
    options: List[DecisionOption]
    source: str = "event"  # 'event', 'crew', 'mission'
    # Called with the chosen option key once resolved (used by dread/bridge.py
    # so a choice actually changes the simulation state).
    on_resolve: Optional[Callable[[str], None]] = None

class DecisionManager:
    """Manages the generation and resolution of decisions."""
    
    def __init__(self):
        self.pending_decision: Optional[Decision] = None
    
    def generate_random_decision(self, context: str = "patrol") -> Optional[Decision]:
        """Generate a random decision based on context."""
        # This would typically pull from a data file or larger pool
        # For now, we'll hardcode a few examples
        
        pool = [
            Decision(
                id="spoiled_food",
                title="Food Spoilage",
                description="The cook reports that a crate of potatoes has gone bad. The smell is awful, but we are low on supplies.",
                options=[
                    DecisionOption(
                        key="1",
                        text="Throw it overboard",
                        tooltip="Lose supplies, maintain morale",
                        supplies_change={"food": -0.1},
                        morale_change=0.05,
                        success_message="The crew is relieved to see the rotting food go."
                    ),
                    DecisionOption(
                        key="2",
                        text="Salvage what we can",
                        tooltip="Risk illness, save some supplies",
                        supplies_change={"food": -0.05},
                        stress_change=0.1,
                        success_chance=0.7,
                        success_message="The cook manages to save the edible parts.",
                        failure_message="Several crew members get sick from the bad food."
                    ),
                    DecisionOption(
                        key="3",
                        text="Eat it anyway (Strict Rationing)",
                        tooltip="Save supplies, major morale hit",
                        morale_change=-0.2,
                        stress_change=0.2,
                        success_message="The crew grumbles but eats the slop."
                    )
                ]
            ),
            Decision(
                id="distress_signal",
                title="Faint Distress Signal",
                description="Radio operator picks up a faint SOS from a neutral merchant ship. It's far off course.",
                options=[
                    DecisionOption(
                        key="1",
                        text="Ignore it (Maintain Stealth)",
                        tooltip="Stay hidden, crew may question it",
                        morale_change=-0.05,
                        success_message="We continue on our patrol, undetected."
                    ),
                    DecisionOption(
                        key="2",
                        text="Investigate",
                        tooltip="Risk detection, potential reward",
                        xp_reward=50,
                        success_chance=0.6,
                        success_message="We found survivors and gathered intel on enemy movements.",
                        failure_message="It was a trap! Enemy destroyer spotted!"
                    )
                ]
            ),
            Decision(
                id="crew_dispute",
                title="Crew Dispute",
                description="Two sailors are fighting over a game of cards. Tensions are high.",
                options=[
                    DecisionOption(
                        key="1",
                        text="Discipline both men",
                        tooltip="Restore order, lower morale",
                        morale_change=-0.1,
                        stress_change=-0.1,
                        success_message="Order is restored, but the crew is resentful."
                    ),
                    DecisionOption(
                        key="2",
                        text="Let them sort it out",
                        tooltip="Risk injury, no morale loss",
                        success_chance=0.5,
                        success_message="They shake hands after a brief scuffle.",
                        failure_message="The fight escalates! One man is injured."
                    ),
                    DecisionOption(
                        key="3",
                        text="Intervene personally (Leadership)",
                        tooltip="Requires Leadership skill",
                        required_skill="leadership",
                        morale_change=0.1,
                        success_message="Your presence calms the situation immediately."
                    )
                ]
            )
        ]
        
        return random.choice(pool)

    def resolve_option(self, decision: Decision, option_key: str, game_state: Any) -> str:
        """Apply the effects of a chosen option."""
        option = next((o for o in decision.options if o.key == option_key), None)
        if not option:
            return "Invalid option."
            
        # Check success chance
        success = random.random() < option.success_chance
        
        result_msg = ""
        
        if success:
            result_msg = option.success_message
            # Apply positive effects
            if option.morale_change != 0 and hasattr(game_state, 'crew_roster'):
                # Simplified morale application
                pass 
            if option.xp_reward > 0 and hasattr(game_state, 'player_stats'):
                # Simplified XP application
                pass
        else:
            result_msg = option.failure_message
            # Apply failure effects (could be double stress, damage, etc)
            
        if decision.on_resolve is not None:
            decision.on_resolve(option_key)
        self.pending_decision = None
        return result_msg

