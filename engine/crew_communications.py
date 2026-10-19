"""
Crew member thoughts, conversations, and dynamic dialogue system.
Provides randomized, contextual crew interactions and internal monologues.
"""

import random
from typing import List, Dict, Optional


class CrewThought:
    """Represents a crew member's internal thought."""
    
    # Thoughts based on crew status
    ANXIOUS_THOUGHTS = [
        "I hope we make it back to port...",
        "How long can our air last?",
        "The pressure at this depth is crushing.",
        "Every creak and groan sounds like the hull failing.",
        "What if we hit something?",
        "Is the CO making the right decision?",
        "My hands won't stop shaking.",
    ]
    
    CALM_THOUGHTS = [
        "All systems nominal. We've got this.",
        "Just another patrol. Stay steady.",
        "The crew is performing well today.",
        "Time to focus on the mission.",
        "Navigation is smooth. Good heading.",
    ]
    
    STRESSED_THOUGHTS = [
        "This is too much pressure!",
        "I can't take much more of this!",
        "Someone get me out of this coffin!",
        "Will this nightmare ever end?",
        "I'm barely holding it together.",
        "Maybe I should've joined the surface fleet.",
    ]
    
    HAPPY_THOUGHTS = [
        "Great work by the crew today!",
        "I love this boat and this crew.",
        "Nothing beats a successful patrol.",
        "The commander makes smart decisions.",
        "Our chances are looking good.",
        "This is what we trained for!",
    ]
    
    COMBAT_THOUGHTS = [
        "Battle stations! This is it!",
        "Keep your nerve, soldier.",
        "Fire when ready!",
        "Evasive maneuvers - now!",
        "The enemy is close. Very close.",
        "Don't let them get a fix on us.",
        "Return fire! Return fire!",
    ]
    
    DAMAGE_THOUGHTS = [
        "Torpedo hit! Compartment breach!",
        "We're taking on water!",
        "Get the damage control team moving!",
        "Hull is compromised! All hands secure!",
        "The reactor's unstable!",
        "We're going down!",
    ]
    
    SUPPLIES_THOUGHTS = [
        "How much air do we have left?",
        "The food rations are running low.",
        "We should surface soon for supplies.",
        "Did anyone check the fuel reserves?",
        "I'm starving. When do we eat?",
        "Water is getting low too.",
    ]
    
    BOREDOM_THOUGHTS = [
        "Nothing but empty ocean out there.",
        "Wake me when something happens.",
        "Another uneventful patrol.",
        "Any contact? No? Still nothing.",
        "How much longer on this watch?",
        "The waiting is the worst part.",
    ]
    
    @staticmethod
    def get_thought_for_state(stress: float, morale: float, context: str = "normal") -> str:
        """Get a thought based on crew member's current state.
        
        Args:
            stress: Stress level (0.0-1.0)
            morale: Morale level (0.0-1.0)
            context: Current game context (normal, combat, damage, supplies, etc.)
            
        Returns:
            A random thought string appropriate to the state
        """
        # Determine thought pool based on context
        if context == "combat":
            pool = CrewThought.COMBAT_THOUGHTS
        elif context == "damage":
            pool = CrewThought.DAMAGE_THOUGHTS
        elif context == "supplies":
            pool = CrewThought.SUPPLIES_THOUGHTS
        elif context == "boredom":
            pool = CrewThought.BOREDOM_THOUGHTS
        elif stress > 0.7:
            pool = CrewThought.STRESSED_THOUGHTS
        elif stress > 0.4:
            pool = CrewThought.ANXIOUS_THOUGHTS
        elif morale > 0.7:
            pool = CrewThought.HAPPY_THOUGHTS
        else:
            pool = CrewThought.CALM_THOUGHTS
        
        return random.choice(pool)


class CrewDialogue:
    """Conversations between crew members."""
    
    # Conversations about the submarine
    SUB_CONVERSATIONS = [
        ("Klaus", "This U-boat is the finest submarine ever built."),
        ("Friedrich", "She's held up well. Better than most."),
        ("Werner", "I've heard the British fear U-boats more than anything."),
        ("Otto", "That's because we're damn good at what we do."),
    ]
    
    # Conversations about the war
    WAR_CONVERSATIONS = [
        ("Helmut", "How long do you think this war will last?"),
        ("Wilhelm", "Nobody knows. Could be months. Could be years."),
        ("Rudolf", "As long as we sink their ships, we're doing our part."),
    ]
    
    # Conversations about food
    FOOD_CONVERSATIONS = [
        ("Ernst", "When's the next meal?"),
        ("Karl", "Complaining again? We all eat the same."),
        ("Georg", "But do we have to eat it at the same time?"),
    ]
    
    # Conversations about morale
    MORALE_CONVERSATIONS = [
        ("Klaus", "The crew's holding up well."),
        ("Friedrich", "Morale is high. We trust our commander."),
        ("Günther", "That's what matters most down here."),
    ]
    
    # Conversations about fear
    FEAR_CONVERSATIONS = [
        ("Werner", "You ever think about what happens if we get hit?"),
        ("Otto", "Every day. That's why I double-check everything."),
        ("Hans", "We're safer than you think. The boat's solid."),
    ]
    
    # Conversations about home
    HOME_CONVERSATIONS = [
        ("Klaus", "I miss home. My family must be worried."),
        ("Friedrich", "We all do. But we're needed here."),
        ("Wilhelm", "At least we'll have stories to tell when this is over."),
    ]
    
    # Congratulations and victories
    VICTORY_CONVERSATIONS = [
        ("Helmut", "Direct hit! Enemy vessel is going down!"),
        ("Rudolf", "Excellent shot, torpedo team!"),
        ("Ernst", "That's another one for our tally!"),
    ]
    
    # Tension and danger
    TENSION_CONVERSATIONS = [
        ("Otto", "Destroyer approaching on intercept course!"),
        ("Klaus", "Battle stations! All hands to battle stations!"),
        ("Friedrich", "How long can we hold this course?"),
        ("Werner", "Just give us time. We'll make it through."),
    ]
    
    @staticmethod
    def get_dialogue_for_context(context: str = "normal") -> tuple:
        """Get a conversation pair based on context.
        
        Args:
            context: Game context (normal, morale, fear, victory, danger, etc.)
            
        Returns:
            Tuple of (speaker_name, dialogue_text)
        """
        dialogues = {
            "normal": CrewDialogue.SUB_CONVERSATIONS,
            "morale": CrewDialogue.MORALE_CONVERSATIONS,
            "fear": CrewDialogue.FEAR_CONVERSATIONS,
            "war": CrewDialogue.WAR_CONVERSATIONS,
            "food": CrewDialogue.FOOD_CONVERSATIONS,
            "home": CrewDialogue.HOME_CONVERSATIONS,
            "victory": CrewDialogue.VICTORY_CONVERSATIONS,
            "danger": CrewDialogue.TENSION_CONVERSATIONS,
        }
        
        pool = dialogues.get(context, CrewDialogue.SUB_CONVERSATIONS)
        return random.choice(pool)


class CrewCommunicationManager:
    """Manages all crew member thoughts and conversations during gameplay."""
    
    def __init__(self):
        """Initialize communication manager."""
        self.recent_thoughts = []
        self.recent_conversations = []
        self.thought_cooldown = 0  # Prevent too many thoughts at once
        self.conversation_cooldown = 0
    
    def trigger_random_thought(self, crew_member, stress: float, morale: float, 
                               context: str = "normal") -> Optional[str]:
        """Generate a random thought from a crew member.
        
        Args:
            crew_member: CrewMember object or name string
            stress: Current stress level
            morale: Current morale level
            context: Game context
            
        Returns:
            Formatted thought string or None if cooldown active
        """
        if self.thought_cooldown > 0:
            self.thought_cooldown -= 1
            return None
        
        name = crew_member.name if hasattr(crew_member, 'name') else str(crew_member)
        thought = CrewThought.get_thought_for_state(stress, morale, context)
        
        from ui.color_system import _color_system
        formatted = f"{_color_system.crew_thought(name)}: {_color_system.colorize(thought, 'bright_cyan')}"
        
        self.recent_thoughts.append(formatted)
        if len(self.recent_thoughts) > 20:
            self.recent_thoughts.pop(0)
        
        self.thought_cooldown = random.randint(3, 8)  # Cooldown 3-8 ticks
        return formatted
    
    def trigger_conversation(self, context: str = "normal") -> Optional[str]:
        """Generate a random conversation between crew members.
        
        Args:
            context: Game context
            
        Returns:
            Formatted conversation string or None if cooldown active
        """
        if self.conversation_cooldown > 0:
            self.conversation_cooldown -= 1
            return None
        
        speaker, dialogue = CrewDialogue.get_dialogue_for_context(context)
        
        from ui.color_system import _color_system
        formatted = f"{_color_system.crew_thought(speaker)}: {_color_system.colorize(dialogue, 'bright_cyan')}"
        
        self.recent_conversations.append(formatted)
        if len(self.recent_conversations) > 20:
            self.recent_conversations.pop(0)
        
        self.conversation_cooldown = random.randint(10, 20)  # Longer cooldown
        return formatted
    
    def get_recent_communications(self, limit: int = 5) -> List[str]:
        """Get recent crew communications.
        
        Args:
            limit: Maximum number of communications to return
            
        Returns:
            List of recent thought and conversation strings
        """
        combined = self.recent_thoughts + self.recent_conversations
        return combined[-limit:]
    
    def clear_communications(self):
        """Clear all stored communications."""
        self.recent_thoughts = []
        self.recent_conversations = []
        self.thought_cooldown = 0
        self.conversation_cooldown = 0


# Global instance
_communication_manager = CrewCommunicationManager()


def get_communication_manager() -> CrewCommunicationManager:
    """Get the global crew communication manager."""
    return _communication_manager


def trigger_crew_thought(crew_member, stress: float = 0.5, morale: float = 0.5, 
                        context: str = "normal") -> Optional[str]:
    """Convenience function to trigger a crew thought."""
    return _communication_manager.trigger_random_thought(crew_member, stress, morale, context)


def trigger_crew_dialogue(context: str = "normal") -> Optional[str]:
    """Convenience function to trigger crew dialogue."""
    return _communication_manager.trigger_conversation(context)
