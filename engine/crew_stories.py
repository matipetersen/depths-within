"""
Enhanced Crew Story System with Faction Integration.
Loads historical stories and generates dynamic crew interactions based on stories.
"""

import json
import os
import random
from typing import Dict, List, Optional
from engine.crew_factions import EnhancedCrewMember, Faction, CrewBackground


class CrewStory:
    """Represents an individual crew member's story."""
    
    def __init__(self, story_data: Dict):
        """Initialize crew story from data dictionary."""
        self.id = story_data.get('id', '')
        self.name = story_data.get('name', '')
        self.faction_name = story_data.get('faction', '')
        self.rank = story_data.get('rank', '')
        self.submarine = story_data.get('submarine', '')
        self.home_city = story_data.get('home_city', '')
        self.background = story_data.get('background', '')
        self.main_story = story_data.get('story', '')
        self.personal_background = story_data.get('personal_background', '')
        self.motivations = story_data.get('motivations', [])
        self.fears = story_data.get('fears', [])
        self.combat_record = story_data.get('combat_record', {})
        self.relationships = story_data.get('relationships', {})
        self.unique_aspects = story_data.get('unique_aspects', {})
    
    def get_full_story(self) -> str:
        """Get complete narrative story for this crew member."""
        story = f"═══ {self.name.upper()} ═══\n\n"
        story += f"Rank: {self.rank}\n"
        story += f"Faction: {self.faction_name}\n"
        story += f"Submarine: {self.submarine}\n"
        story += f"Home: {self.home_city}\n\n"
        
        story += "BACKGROUND\n"
        story += f"{self.background}\n\n"
        
        story += "STORY\n"
        story += f"{self.main_story}\n\n"
        
        story += "PERSONAL HISTORY\n"
        story += f"{self.personal_background}\n\n"
        
        if self.combat_record:
            story += "COMBAT RECORD\n"
            for key, value in self.combat_record.items():
                story += f"  {key.replace('_', ' ').title()}: {value}\n"
            story += "\n"
        
        if self.motivations:
            story += "MOTIVATIONS\n"
            for motivation in self.motivations:
                story += f"  • {motivation}\n"
            story += "\n"
        
        if self.fears:
            story += "FEARS AND ANXIETIES\n"
            for fear in self.fears:
                story += f"  • {fear}\n"
            story += "\n"
        
        if self.unique_aspects:
            story += "UNIQUE ASPECTS\n"
            for aspect, detail in self.unique_aspects.items():
                story += f"  {aspect.replace('_', ' ').title()}:\n"
                if isinstance(detail, dict):
                    for key, value in detail.items():
                        story += f"    {key.replace('_', ' ')}: {value}\n"
                elif isinstance(detail, list):
                    for item in detail:
                        story += f"    • {item}\n"
                else:
                    story += f"    {detail}\n"
            story += "\n"
        
        return story
    
    def get_summary(self) -> str:
        """Get brief summary of crew member."""
        return f"{self.name} ({self.rank}, {self.submarine}): {self.main_story[:100]}..."


class CrewStoryManager:
    """Manages crew stories and integrations with crew system."""
    
    def __init__(self, stories_file: str = None):
        """Initialize story manager from JSON file."""
        self.stories: Dict[str, CrewStory] = {}
        self.stories_by_faction: Dict[str, List[CrewStory]] = {}
        self.stories_by_submarine: Dict[str, List[CrewStory]] = {}
        
        if stories_file is None:
            stories_file = os.path.join(os.path.dirname(__file__), '../data/crew_stories.json')
        
        self.load_stories(stories_file)
    
    def load_stories(self, filepath: str):
        """Load stories from JSON file."""
        try:
            with open(filepath, 'r') as f:
                stories_data = json.load(f)
            
            for story_data in stories_data:
                story = CrewStory(story_data)
                self.stories[story.id] = story
                
                # Index by faction
                if story.faction_name not in self.stories_by_faction:
                    self.stories_by_faction[story.faction_name] = []
                self.stories_by_faction[story.faction_name].append(story)
                
                # Index by submarine
                if story.submarine not in self.stories_by_submarine:
                    self.stories_by_submarine[story.submarine] = []
                self.stories_by_submarine[story.submarine].append(story)
        
        except FileNotFoundError:
            print(f"Crew stories file not found: {filepath}")
        except json.JSONDecodeError:
            print(f"Invalid JSON in crew stories file: {filepath}")
    
    def get_story(self, story_id: str) -> Optional[CrewStory]:
        """Get specific story by ID."""
        return self.stories.get(story_id)
    
    def get_stories_by_faction(self, faction: str) -> List[CrewStory]:
        """Get all stories for a faction."""
        return self.stories_by_faction.get(faction, [])
    
    def get_random_story(self, faction: Optional[str] = None) -> Optional[CrewStory]:
        """Get random story, optionally filtered by faction."""
        if faction:
            stories = self.get_stories_by_faction(faction)
        else:
            stories = list(self.stories.values())
        
        return random.choice(stories) if stories else None
    
    def get_stories_by_submarine(self, submarine: str) -> List[CrewStory]:
        """Get all stories for a specific submarine."""
        return self.stories_by_submarine.get(submarine, [])
    
    def create_crew_from_story(self, story_id: str) -> Optional[EnhancedCrewMember]:
        """Create a crew member based on a historical story."""
        story = self.get_story(story_id)
        if not story:
            return None
        
        # Map faction name to Faction enum
        faction_map = {
            'Kriegsmarine': Faction.KRIEGSMARINE,
            'Imperial Japanese Navy': Faction.IMPERIAL_JAPANESE_NAVY,
            'US Navy': Faction.US_NAVY,
            'Royal Navy': Faction.ROYAL_NAVY,
            'Soviet Navy': Faction.SOVIET_NAVY,
            'Regia Marina': Faction.ITALIAN_NAVY,
        }
        
        faction = faction_map.get(story.faction_name, Faction.KRIEGSMARINE)
        
        # Map background descriptions to BackgroundEnums
        background_map = {
            'Naval Academy': CrewBackground.NAVAL_ACADEMY,
            'Merchant marine': CrewBackground.MERCHANT_MARINE,
            'Draftee': CrewBackground.DRAFTEE,
            'Reserve officer': CrewBackground.RESERVE_OFFICER,
            'Technical': CrewBackground.TECHNICAL_SCHOOL,
            'Fishing': CrewBackground.FISHING_INDUSTRY,
        }
        
        background = None
        for key, value in background_map.items():
            if key.lower() in story.background.lower():
                background = value
                break
        
        crew = EnhancedCrewMember(
            name=story.name,
            faction=faction,
            background=background,
            rank=story.rank
        )
        
        # Override generated story with historical story
        crew.personal_story = story.main_story
        crew.home_story = story.personal_background
        crew.motivations = story.motivations
        crew.fears = story.fears
        crew.combat_achievements = [(story.submarine, story.combat_record)]
        
        return crew
    
    def get_faction_story_summary(self, faction: str) -> str:
        """Get summary of all crew stories for a faction."""
        stories = self.get_stories_by_faction(faction)
        if not stories:
            return f"No stories found for faction: {faction}"
        
        summary = f"═══ {faction.upper()} CREW STORIES ═══\n\n"
        for story in stories:
            summary += f"• {story.get_summary()}\n\n"
        
        return summary
    
    def generate_crew_dialogue_from_stories(self, crew1: EnhancedCrewMember, 
                                           crew2: EnhancedCrewMember) -> str:
        """Generate realistic dialogue between two crew members based on their stories."""
        
        # Check if same faction
        same_faction = crew1.faction == crew2.faction
        
        if same_faction:
            # Generate camaraderie dialogue
            dialogues = [
                f"{crew1.name}: Remember the last patrol in {crew1.home_front.value}? {crew2.name}: Those were rough seas.",
                f"{crew1.name}: I heard you're from {crew2.home_front.value}? {crew2.name}: Yes, you?",
                f"{crew1.name}: Keep your head down. {crew2.name}: Always do, Captain.",
                f"{crew1.name}: {crew2.name}, how are the engines holding? {crew2.name}: Running smooth, sir.",
                f"{crew1.name}: My family's still in {crew1.home_front.value}. {crew2.name}: Mine too. We'll get through this.",
            ]
        else:
            # Generate enemy tension (unlikely to occur together, but if they do)
            dialogues = [
                f"{crew1.name}: Stay sharp. {crew2.name}: Always do.",
                f"{crew1.name}: What faction are you from? {crew2.name}: Does it matter now?",
            ]
        
        return random.choice(dialogues)
    
    def get_submarine_crew_context(self, submarine_name: str) -> str:
        """Get context about crew served on a specific submarine."""
        stories = self.get_stories_by_submarine(submarine_name)
        if not stories:
            return f"No documented crews for {submarine_name}"
        
        context = f"═══ CREW OF {submarine_name.upper()} ═══\n\n"
        for story in stories:
            context += f"{story.name}\n"
            context += f"  Rank: {story.rank}\n"
            context += f"  Faction: {story.faction_name}\n"
            if story.combat_record:
                context += f"  Combat Record: {story.combat_record.get('ships_sunk', 'Unknown')} ships sunk\n"
            context += "\n"
        
        return context
    
    def get_all_factions_represented(self) -> List[str]:
        """Get list of all factions with stories."""
        return list(self.stories_by_faction.keys())
    
    def generate_historical_patrol_context(self) -> str:
        """Generate context about different historical patrol theaters."""
        context = "═══ HISTORICAL PATROL CONTEXT ═══\n\n"
        
        theater_info = {
            "North Atlantic": "Primary hunting ground for German U-boats. Cold, rough seas. Convoys heavily defended. German: U-96, British: HMS Upholder",
            "Pacific Theater": "American dominance. Japanese submarines suffered attrition. Vast distances, limited supply. US: USS Tang, Japan: I-58",
            "Mediterranean": "Shallow waters limited submarine advantages. Heavy air cover. British had tactical advantage. UK: HMS Upholder",
            "Baltic Sea": "Soviet domain. Frozen in winter, mined throughout. German patrols rare. USSR: Shch-303, Shch-302",
        }
        
        for theater, description in theater_info.items():
            context += f"{theater}:\n  {description}\n\n"
        
        return context


# Global story manager instance
_story_manager = None


def get_story_manager() -> CrewStoryManager:
    """Get or create global story manager instance."""
    global _story_manager
    if _story_manager is None:
        _story_manager = CrewStoryManager()
    return _story_manager


def load_crew_story(story_id: str) -> Optional[CrewStory]:
    """Load a specific crew story."""
    manager = get_story_manager()
    return manager.get_story(story_id)


def get_random_crew_story(faction: Optional[str] = None) -> Optional[CrewStory]:
    """Get a random crew story, optionally filtered by faction."""
    manager = get_story_manager()
    return manager.get_random_story(faction)
