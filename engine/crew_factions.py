"""
Enhanced Crew Faction System with Story Integration.
Expands crew members with faction affiliations and deep personal stories.
"""

import random
import json
from enum import Enum
from typing import Dict, List, Optional


class Faction(Enum):
    """Naval faction for crew members."""
    KRIEGSMARINE = "Kriegsmarine"  # German Navy
    IMPERIAL_JAPANESE_NAVY = "Imperial Japanese Navy"
    ITALIAN_NAVY = "Regia Marina"  # Italian Navy
    US_NAVY = "US Navy"
    ROYAL_NAVY = "Royal Navy"  # British
    SOVIET_NAVY = "Soviet Navy"


class CrewBackground(Enum):
    """Pre-war background affecting personality and skills."""
    MERCHANT_MARINE = "merchant_marine"  # Civilian ship experience
    NAVAL_ACADEMY = "naval_academy"  # Career officer
    DRAFTEE = "draftee"  # Conscripted civilian
    RESERVE_OFFICER = "reserve_officer"  # Reserve commission
    TECHNICAL_SCHOOL = "technical_school"  # Engineering background
    FISHING_INDUSTRY = "fishing_industry"  # Commercial fishing experience


class HomeFront(Enum):
    """Home city/region affecting motivation and story."""
    KIEL = "Kiel"  # German submarine base
    HAMBURG = "Hamburg"  # German port city
    BERLIN = "Berlin"  # German capital
    BREMEN = "Bremen"  # German shipbuilding center
    TOKYO = "Tokyo"  # Japanese capital
    YOKOSUKA = "Yokosuka"  # Japanese naval base
    ROME = "Rome"  # Italian capital
    LA_SPEZIA = "La Spezia"  # Italian submarine base
    NEW_YORK = "New York"  # US city
    NORFOLK = "Norfolk"  # US naval base
    LONDON = "London"  # British capital
    GIBRALTAR = "Gibraltar"  # British strategic point
    LENINGRAD = "Leningrad"  # Soviet city
    VLADIVOSTOK = "Vladivostok"  # Soviet far east


class CrewPersonality(Enum):
    """Crew personality archetypes affecting behavior and dialogue."""
    BRAVE = "brave"  # Takes risks, high combat effectiveness
    CAUTIOUS = "cautious"  # Careful, prefers safety, high defense
    CALM = "calm"  # Steady under pressure, stress resistance
    AGGRESSIVE = "aggressive"  # Offensive tactics preferred
    DISCIPLINED = "disciplined"  # Follows orders precisely
    CURIOUS = "curious"  # Learns quickly, high XP gain
    LOYAL = "loyal"  # High morale, bonuses to team actions
    CYNICAL = "cynical"  # Suspicious, morale affected by losses
    CHEERFUL = "cheerful"  # Boosts crew morale
    MELANCHOLIC = "melancholic"  # Affected by stress, lower morale baseline


class CrewRelationship(Enum):
    """Relationships between crew members for dialogue and interaction."""
    BEST_FRIENDS = "best_friends"  # Work well together, morale boost
    FRIENDS = "friends"  # Compatible team members
    NEUTRAL = "neutral"  # No particular relationship
    RIVALS = "rivals"  # Competitive, can improve performance
    ENEMIES = "enemies"  # Conflict, reduced effectiveness together


class EnhancedCrewMember:
    """Extended crew member with faction, background, and deep story."""
    
    def __init__(self, name: str, faction: Faction, background: CrewBackground = None,
                 home_front: HomeFront = None, personality: CrewPersonality = None,
                 rank: str = "Seaman", primary_skill: str = None):
        """
        Initialize enhanced crew member.
        
        Args:
            name: Crew member name
            faction: Naval faction
            background: Pre-war background
            home_front: Home city/region
            personality: Personality archetype
            rank: Military rank
            primary_skill: Primary specialization
        """
        self.id = random.randint(100000, 999999)
        self.name = name
        self.faction = faction
        self.background = background or random.choice(list(CrewBackground))
        self.home_front = home_front or self._get_default_home_front()
        self.personality = personality or random.choice(list(CrewPersonality))
        self.rank = rank
        
        # Skills
        self.primary_skill = primary_skill or random.choice(
            ['sonar', 'torpedo', 'navigation', 'engineering', 'damage_control']
        )
        self.secondary_skills = random.sample(['general', 'leadership', 'repair'], 2)
        
        # Status
        self.stress = 0.0
        self.morale = self._calculate_base_morale()
        self.fatigue = 0.0
        self.health = 1.0
        
        # Experience
        self.xp = {}
        self.level = 1
        self.missions_completed = 0
        self.ships_sunk = 0
        self.tonnage_sunk = 0
        
        # Story elements
        self.personal_story = self._generate_personal_story()
        self.home_story = self._generate_home_story()
        self.motivations = self._generate_motivations()
        self.fears = self._generate_fears()
        self.combat_achievements = []
        self.relationships: Dict[str, CrewRelationship] = {}
        
        # Assignment
        self.compartment_id = None
        self.role = 'unassigned'
    
    def _get_default_home_front(self) -> HomeFront:
        """Get default home front based on faction."""
        faction_homes = {
            Faction.KRIEGSMARINE: random.choice([HomeFront.KIEL, HomeFront.HAMBURG, HomeFront.BREMEN]),
            Faction.IMPERIAL_JAPANESE_NAVY: random.choice([HomeFront.TOKYO, HomeFront.YOKOSUKA]),
            Faction.ITALIAN_NAVY: random.choice([HomeFront.ROME, HomeFront.LA_SPEZIA]),
            Faction.US_NAVY: random.choice([HomeFront.NEW_YORK, HomeFront.NORFOLK]),
            Faction.ROYAL_NAVY: random.choice([HomeFront.LONDON, HomeFront.GIBRALTAR]),
            Faction.SOVIET_NAVY: random.choice([HomeFront.LENINGRAD, HomeFront.VLADIVOSTOK]),
        }
        return faction_homes.get(self.faction, HomeFront.BERLIN)
    
    def _calculate_base_morale(self) -> float:
        """Calculate base morale based on personality and background."""
        base = 0.6
        
        if self.personality in [CrewPersonality.CHEERFUL, CrewPersonality.LOYAL]:
            base += 0.2
        elif self.personality == CrewPersonality.MELANCHOLIC:
            base -= 0.1
        elif self.personality == CrewPersonality.CYNICAL:
            base -= 0.05
        
        return min(1.0, max(0.3, base))
    
    def _generate_personal_story(self) -> str:
        """Generate personal backstory based on background and personality."""
        background_stories = {
            CrewBackground.MERCHANT_MARINE: f"{self.name} served on merchant vessels before the war, experiencing {self.faction.value} naval power firsthand.",
            CrewBackground.NAVAL_ACADEMY: f"{self.name} graduated from naval academy with distinction, trained in {self.faction.value} military doctrine.",
            CrewBackground.DRAFTEE: f"{self.name} was conscripted into {self.faction.value}, leaving behind family in {self.home_front.value}.",
            CrewBackground.RESERVE_OFFICER: f"{self.name} held a reserve commission before being called to active duty in {self.faction.value}.",
            CrewBackground.TECHNICAL_SCHOOL: f"{self.name} trained as an engineer, later recruited into {self.faction.value} submarine service.",
            CrewBackground.FISHING_INDUSTRY: f"{self.name} comes from fishing industry background near {self.home_front.value}, skilled in navigation and sea survival.",
        }
        return background_stories.get(self.background, f"{self.name} joined {self.faction.value} to serve.")
    
    def _generate_home_story(self) -> str:
        """Generate story about crew member's home and family."""
        family_situations = [
            f"Has wife and two children waiting in {self.home_front.value}",
            f"Comes from a naval family in {self.home_front.value}",
            f"Left aging parents and younger siblings in {self.home_front.value}",
            f"Fiancée waiting in {self.home_front.value}",
            f"Orphaned during childhood, raised in orphanage in {self.home_front.value}",
            f"Has older brother also serving in {self.faction.value}",
            f"Wife works as nurse near {self.home_front.value}",
            f"Left family business in {self.home_front.value} to serve",
        ]
        return random.choice(family_situations)
    
    def _generate_motivations(self) -> List[str]:
        """Generate crew member's motivations for service."""
        personality_motivations = {
            CrewPersonality.BRAVE: ["prove valor in combat", "honor the flag", "fear dishonor more than death"],
            CrewPersonality.CAUTIOUS: ["protect crew safety", "complete missions with minimal losses", "preserve submarine"],
            CrewPersonality.CALM: ["maintain order", "support team morale", "steady leadership"],
            CrewPersonality.AGGRESSIVE: ["sink enemy ships", "achieve high kill count", "tactical superiority"],
            CrewPersonality.DISCIPLINED: ["obey orders perfectly", "maintain submarine readiness", "military honor"],
            CrewPersonality.CURIOUS: ["learn enemy tactics", "improve submarine technology", "scientific discovery"],
            CrewPersonality.LOYAL: ["support crew", "follow captain's vision", "naval brotherhood"],
            CrewPersonality.CYNICAL: ["survive to go home", "avoid unnecessary risks", "question high command"],
            CrewPersonality.CHEERFUL: ["boost crew spirits", "find humor in hardship", "maintain hope"],
            CrewPersonality.MELANCHOLIC: ["honor the fallen", "understand war's cost", "seek meaning in service"],
        }
        base_motivations = personality_motivations.get(self.personality, ["serve nation"])
        return base_motivations + ["return home alive", "support family"]
    
    def _generate_fears(self) -> List[str]:
        """Generate crew member's fears and anxieties."""
        personality_fears = {
            CrewPersonality.BRAVE: ["letting down crew", "appearing cowardly"],
            CrewPersonality.CAUTIOUS: ["reckless orders", "submarine sinking"],
            CrewPersonality.CALM: ["panic spreading", "system failure"],
            CrewPersonality.AGGRESSIVE: ["capture", "being imprisoned"],
            CrewPersonality.DISCIPLINED: ["dereliction of duty", "court martial"],
            CrewPersonality.CURIOUS: ["unknown enemy capabilities", "getting trapped"],
            CrewPersonality.LOYAL: ["betrayal of crew", "captain's death"],
            CrewPersonality.CYNICAL: ["meaningless death", "wasted sacrifice"],
            CrewPersonality.CHEERFUL: ["crew despair", "losing hope"],
            CrewPersonality.MELANCHOLIC: ["causing deaths", "survival guilt"],
        }
        base_fears = personality_fears.get(self.personality, ["depth charges"])
        return base_fears + ["being far from home", "not seeing family again"]
    
    def get_faction_description(self) -> str:
        """Get detailed description of crew member including faction background."""
        desc = f"{self.name}\n"
        desc += f"  Faction: {self.faction.value}\n"
        desc += f"  Rank: {self.rank}\n"
        desc += f"  From: {self.home_front.value}\n"
        desc += f"  Background: {self.background.value.replace('_', ' ').title()}\n"
        desc += f"  Personality: {self.personality.value.title()}\n"
        desc += f"  Primary Skill: {self.primary_skill}\n"
        desc += f"\nStory:\n  {self.personal_story}\n"
        desc += f"\nHome:\n  {self.home_story}\n"
        desc += f"\nMotivations:\n"
        for motivation in self.motivations:
            desc += f"  • {motivation}\n"
        desc += f"\nFears:\n"
        for fear in self.fears:
            desc += f"  • {fear}\n"
        return desc
    
    def set_relationship(self, other_crew_id: str, relationship: CrewRelationship):
        """Set relationship with another crew member."""
        self.relationships[other_crew_id] = relationship
    
    def get_relationship_bonus(self, other_crew_id: str) -> float:
        """Get skill bonus/penalty based on relationship with another crew."""
        relationship = self.relationships.get(other_crew_id)
        if relationship == CrewRelationship.BEST_FRIENDS:
            return 0.15
        elif relationship == CrewRelationship.FRIENDS:
            return 0.08
        elif relationship == CrewRelationship.RIVALS:
            return 0.05  # Competitive can boost performance
        elif relationship == CrewRelationship.ENEMIES:
            return -0.1
        return 0.0
    
    def effective_skill(self, skill: str) -> float:
        """Get effective skill factoring personality and stress."""
        base = 0.5
        
        if skill == self.primary_skill:
            base += 0.3
        elif skill in self.secondary_skills:
            base += 0.15
        
        # Personality bonuses
        if self.personality == CrewPersonality.BRAVE and 'torpedo' in skill:
            base += 0.1
        elif self.personality == CrewPersonality.CAUTIOUS and 'damage_control' in skill:
            base += 0.1
        elif self.personality == CrewPersonality.CALM and 'sonar' in skill:
            base += 0.1
        elif self.personality == CrewPersonality.DISCIPLINED:
            base += 0.08
        elif self.personality == CrewPersonality.CURIOUS:
            base += (self.level - 1) * 0.02
        
        # Apply stress/morale
        stress_penalty = self.stress * 0.3
        morale_bonus = max(0, self.morale - 0.5) * 0.2
        
        effective = base + morale_bonus - stress_penalty
        return max(0.1, min(1.0, effective))
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'faction': self.faction.value,
            'background': self.background.value,
            'home_front': self.home_front.value,
            'personality': self.personality.value,
            'rank': self.rank,
            'primary_skill': self.primary_skill,
            'secondary_skills': self.secondary_skills,
            'stress': self.stress,
            'morale': self.morale,
            'fatigue': self.fatigue,
            'health': self.health,
            'xp': self.xp,
            'level': self.level,
            'missions_completed': self.missions_completed,
            'ships_sunk': self.ships_sunk,
            'tonnage_sunk': self.tonnage_sunk,
            'personal_story': self.personal_story,
            'home_story': self.home_story,
            'motivations': self.motivations,
            'fears': self.fears,
            'compartment_id': self.compartment_id,
            'role': self.role,
        }
    
    def __repr__(self):
        return f"<EnhancedCrewMember {self.name} ({self.rank}, {self.faction.value})>"


class CrewFactionRoster:
    """Manages crews of different factions for historical authenticity."""
    
    def __init__(self):
        """Initialize faction-based crew rosters."""
        self.rosters: Dict[Faction, List[EnhancedCrewMember]] = {
            faction: [] for faction in Faction
        }
        self._load_historical_crew()
    
    def _load_historical_crew(self):
        """Load historical crew members for each faction."""
        historical_crew = {
            Faction.KRIEGSMARINE: [
                ("Klaus Lehmann", "Kapitänleutnant", CrewBackground.NAVAL_ACADEMY),
                ("Friedrich Weber", "Oberleutnant", CrewBackground.NAVAL_ACADEMY),
                ("Werner Schmidt", "Oberbootsmann", CrewBackground.MERCHANT_MARINE),
                ("Otto Müller", "Matrose", CrewBackground.DRAFTEE),
                ("Hans Richter", "Leutnant", CrewBackground.TECHNICAL_SCHOOL),
            ],
            Faction.IMPERIAL_JAPANESE_NAVY: [
                ("Takeshi Yamamoto", "Taisa", CrewBackground.NAVAL_ACADEMY),
                ("Noboru Ishii", "Chusa", CrewBackground.MERCHANT_MARINE),
                ("Kenji Tanaka", "Fukusho", CrewBackground.TECHNICAL_SCHOOL),
                ("Hiroshi Sato", "Heishi", CrewBackground.DRAFTEE),
            ],
            Faction.US_NAVY: [
                ("Richard O'Kane", "Commander", CrewBackground.NAVAL_ACADEMY),
                ("James Mitchell", "Lieutenant", CrewBackground.TECHNICAL_SCHOOL),
                ("William Anderson", "Chief Petty Officer", CrewBackground.MERCHANT_MARINE),
                ("John Smith", "Seaman", CrewBackground.DRAFTEE),
            ],
            Faction.ROYAL_NAVY: [
                ("David Wanklyn", "Lieutenant Commander", CrewBackground.NAVAL_ACADEMY),
                ("George Smith", "Midshipman", CrewBackground.RESERVE_OFFICER),
                ("Thomas Wilson", "Petty Officer", CrewBackground.MERCHANT_MARINE),
            ],
            Faction.SOVIET_NAVY: [
                ("Ivan Travkin", "Kapitan", CrewBackground.NAVAL_ACADEMY),
                ("Alexei Petrov", "Starshina", CrewBackground.TECHNICAL_SCHOOL),
                ("Dmitri Sokolov", "Matros", CrewBackground.DRAFTEE),
            ],
            Faction.ITALIAN_NAVY: [
                ("Gianfranco Gazzana", "Capitano", CrewBackground.NAVAL_ACADEMY),
                ("Marco Rossini", "Sottotenente", CrewBackground.MERCHANT_MARINE),
                ("Antonio Ferrari", "Primo Maresciallo", CrewBackground.TECHNICAL_SCHOOL),
            ],
        }
        
        for faction, crew_data in historical_crew.items():
            for name, rank, background in crew_data:
                crew = EnhancedCrewMember(
                    name=name,
                    faction=faction,
                    background=background,
                    rank=rank
                )
                self.rosters[faction].append(crew)
    
    def get_faction_crew(self, faction: Faction) -> List[EnhancedCrewMember]:
        """Get all crew members for a faction."""
        return self.rosters.get(faction, [])
    
    def get_random_crew(self, faction: Optional[Faction] = None) -> EnhancedCrewMember:
        """Get random crew member, optionally from specific faction."""
        if faction:
            crew_list = self.rosters.get(faction, [])
        else:
            all_crew = [c for crew_list in self.rosters.values() for c in crew_list]
            crew_list = all_crew
        
        return random.choice(crew_list) if crew_list else None
    
    def to_dict(self) -> Dict:
        """Serialize all rosters."""
        return {
            faction.value: [crew.to_dict() for crew in crews]
            for faction, crews in self.rosters.items()
        }
