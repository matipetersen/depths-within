"""
Enhanced crew management interface with commands for managing team.
Allows viewing, assigning, and managing crew members through game commands.
Integrated with faction and story systems for richer crew experience.
"""

from typing import List, Optional, Dict
from engine.crew_factions import EnhancedCrewMember, Faction
from engine.crew_stories import get_story_manager


class CrewManagementUI:
    """User interface for crew management."""
    
    @staticmethod
    def format_crew_member(crew_member, show_detailed: bool = False) -> str:
        """Format a crew member for display.
        
        Args:
            crew_member: CrewMember object
            show_detailed: If True, show detailed stats
            
        Returns:
            Formatted crew member string
        """
        from ui.color_system import _color_system
        
        # Basic display
        name = crew_member.name
        rank = crew_member.rank if hasattr(crew_member, 'rank') else "Seaman"
        primary_skill = crew_member.primary_skill if hasattr(crew_member, 'primary_skill') else "general"
        
        # Status indicators
        stress = crew_member.stress if hasattr(crew_member, 'stress') else 0.0
        morale = crew_member.morale if hasattr(crew_member, 'morale') else 0.5
        health = crew_member.health if hasattr(crew_member, 'health') else 1.0
        fatigue = crew_member.fatigue if hasattr(crew_member, 'fatigue') else 0.0
        
        # Color code based on status
        if health < 0.3:
            health_color = "bright_red"
        elif health < 0.6:
            health_color = "bright_yellow"
        else:
            health_color = "bright_green"
        
        if stress > 0.7:
            stress_color = "bright_red"
        elif stress > 0.4:
            stress_color = "bright_yellow"
        else:
            stress_color = "bright_green"
        
        if morale > 0.7:
            morale_color = "bright_green"
        elif morale > 0.4:
            morale_color = "bright_yellow"
        else:
            morale_color = "bright_red"
        
        # Basic line
        line = f"  {_color_system.colorize(name, 'white', 'bold')} | "
        line += f"{_color_system.colorize(rank, 'cyan')} | "
        line += f"Skill: {_color_system.colorize(primary_skill, 'bright_cyan')} | "
        line += f"Health: {_color_system.colorize(f'{health*100:5.1f}%', health_color)}"
        
        if show_detailed:
            line += "\n"
            line += f"    Stress: {_color_system.colorize(f'{stress*100:5.1f}%', stress_color)} | "
            line += f"Morale: {_color_system.colorize(f'{morale*100:5.1f}%', morale_color)} | "
            line += f"Fatigue: {_color_system.colorize(f'{fatigue*100:5.1f}%', 'bright_yellow')}"
            
            if hasattr(crew_member, 'personality'):
                line += f"\n    Personality: {_color_system.colorize(crew_member.personality, 'bright_magenta')}"
            
            if hasattr(crew_member, 'level'):
                line += f" | Level: {crew_member.level}"
            
            if hasattr(crew_member, 'missions'):
                line += f" | Missions: {crew_member.missions}"
        
        return line
    
    @staticmethod
    def show_crew_roster(crew_roster, game, show_detailed: bool = False) -> str:
        """Display the full crew roster.
        
        Args:
            crew_roster: CrewRoster object
            game: Game instance
            show_detailed: If True, show detailed stats
            
        Returns:
            Formatted crew roster
        """
        from ui.color_system import _color_system
        
        lines = []
        lines.append(_color_system.header(f"═══ CREW ROSTER ═══"))
        
        crew_count = crew_roster.crew_count if hasattr(crew_roster, 'crew_count') else len(crew_roster.crew)
        max_crew = crew_roster.max_crew if hasattr(crew_roster, 'max_crew') else 50
        
        lines.append(f"Personnel: {_color_system.value(f'{crew_count}/{max_crew}')}\n")
        
        if hasattr(crew_roster, 'crew_members'):
            crew_list = list(crew_roster.crew_members.values())
        elif hasattr(crew_roster, 'crew'):
            crew_list = crew_roster.crew
        else:
            crew_list = []
        
        if not crew_list:
            lines.append("No crew members on roster.")
            return "\n".join(lines)
        
        for i, member in enumerate(crew_list, 1):
            lines.append(f"{i:2d}. {CrewManagementUI.format_crew_member(member, show_detailed)}")
        
        return "\n".join(lines)
    
    @staticmethod
    def show_crew_by_assignment(crew_roster) -> str:
        """Display crew organized by compartment assignment.
        
        Args:
            crew_roster: CrewRoster object
            
        Returns:
            Formatted crew by assignment
        """
        from ui.color_system import _color_system
        
        lines = []
        lines.append(_color_system.header(f"═══ CREW BY ASSIGNMENT ═══\n"))
        
        if hasattr(crew_roster, 'crew_members'):
            crew_list = list(crew_roster.crew_members.values())
        elif hasattr(crew_roster, 'crew'):
            crew_list = crew_roster.crew
        else:
            return "No crew data available."
        
        # Group by compartment
        by_compartment = {}
        unassigned = []
        
        for member in crew_list:
            compartment = getattr(member, 'compartment_id', None)
            if compartment:
                if compartment not in by_compartment:
                    by_compartment[compartment] = []
                by_compartment[compartment].append(member)
            else:
                unassigned.append(member)
        
        # Display by compartment
        for compartment, members in sorted(by_compartment.items()):
            lines.append(f"{_color_system.label(str(compartment))}:")
            for member in members:
                lines.append(f"  {CrewManagementUI.format_crew_member(member)}")
            lines.append("")
        
        # Display unassigned
        if unassigned:
            lines.append(f"{_color_system.warning('UNASSIGNED')}:")
            for member in unassigned:
                lines.append(f"  {CrewManagementUI.format_crew_member(member)}")
        
        return "\n".join(lines)
    
    @staticmethod
    def show_crew_morale_summary(crew_roster) -> str:
        """Show crew morale summary statistics.
        
        Args:
            crew_roster: CrewRoster object
            
        Returns:
            Formatted morale summary
        """
        from ui.color_system import _color_system
        
        lines = []
        lines.append(_color_system.header(f"═══ CREW MORALE REPORT ═══\n"))
        
        if hasattr(crew_roster, 'crew_members'):
            crew_list = list(crew_roster.crew_members.values())
        elif hasattr(crew_roster, 'crew'):
            crew_list = crew_roster.crew
        else:
            return "No crew data available."
        
        if not crew_list:
            return "No crew members."
        
        # Calculate statistics
        avg_morale = sum(getattr(m, 'morale', 0.5) for m in crew_list) / len(crew_list)
        avg_stress = sum(getattr(m, 'stress', 0.0) for m in crew_list) / len(crew_list)
        avg_fatigue = sum(getattr(m, 'fatigue', 0.0) for m in crew_list) / len(crew_list)
        
        healthy = sum(1 for m in crew_list if getattr(m, 'health', 1.0) > 0.8)
        injured = sum(1 for m in crew_list if getattr(m, 'health', 1.0) < 0.5)
        stressed = sum(1 for m in crew_list if getattr(m, 'stress', 0.0) > 0.7)
        
        # Color code averages
        if avg_morale > 0.7:
            morale_color = "bright_green"
        elif avg_morale > 0.4:
            morale_color = "bright_yellow"
        else:
            morale_color = "bright_red"
        
        lines.append(f"Average Morale: {_color_system.colorize(f'{avg_morale*100:5.1f}%', morale_color)}")
        lines.append(f"Average Stress:  {_color_system.colorize(f'{avg_stress*100:5.1f}%', 'bright_yellow')}")
        lines.append(f"Average Fatigue: {_color_system.colorize(f'{avg_fatigue*100:5.1f}%', 'bright_yellow')}\n")
        
        lines.append(f"Healthy:  {_color_system.colorize(f'{healthy}', 'bright_green')}")
        lines.append(f"Injured:  {_color_system.colorize(f'{injured}', 'bright_red')}")
        lines.append(f"Stressed: {_color_system.colorize(f'{stressed}', 'bright_yellow')}\n")
        
        # Morale trend
        if avg_morale > 0.7:
            lines.append(_color_system.success("Crew morale is excellent!"))
        elif avg_morale > 0.5:
            lines.append(_color_system.info("Crew morale is stable."))
        elif avg_morale > 0.3:
            lines.append(_color_system.warning("Crew morale is declining."))
        else:
            lines.append(_color_system.alert("Crew morale is critical!"))
        
        return "\n".join(lines)
    
    @staticmethod
    def show_stress_management_tips(game) -> str:
        """Show tips for managing crew stress.
        
        Args:
            game: Game instance
            
        Returns:
            Formatted stress management tips
        """
        from ui.color_system import _color_system
        
        lines = []
        lines.append(_color_system.header(f"═══ CREW STRESS MANAGEMENT ═══\n"))
        
        lines.append(_color_system.label("Ways to reduce crew stress:\n"))
        lines.append("  1. Rest crew at safe depths (50-100m)")
        lines.append("  2. Avoid combat when possible")
        lines.append("  3. Surface periodically to refresh air")
        lines.append("  4. Maintain supplies (food, water)")
        lines.append("  5. Complete missions successfully")
        lines.append("  6. Allow crew to socialize (random conversations)")
        lines.append("")
        lines.append(_color_system.label("High stress effects:\n"))
        lines.append("  • Reduced skill effectiveness")
        lines.append("  • Increased mistakes in critical systems")
        lines.append("  • Lower morale (creates stress spiral)")
        lines.append("  • Potential crew injuries")
        
        return "\n".join(lines)


# Management commands
class CrewManagementCommands:
    """Commands for crew management in the game."""
    
    @staticmethod
    def register_commands(game):
        """Register crew management commands with the game.
        
        Args:
            game: Game instance
        """
        # Commands would be registered here if using a command registry
        # For now, they're handled directly in game.process_command()
        pass


class CrewStoryUI:
    """UI methods for displaying crew stories and faction information."""
    
    @staticmethod
    def show_crew_biography(crew_member) -> str:
        """Show detailed biography of crew member."""
        from ui.color_system import _color_system
        
        lines = []
        lines.append(_color_system.header("═══ CREW BIOGRAPHY ═══\n"))
        
        lines.append(_color_system.label(f"{crew_member.name}"))
        
        # Basic info
        lines.append(f"Rank: {_color_system.colorize(crew_member.rank, 'cyan')}")
        
        if hasattr(crew_member, 'faction'):
            lines.append(f"Faction: {_color_system.colorize(crew_member.faction.value, 'bright_magenta')}")
        
        if hasattr(crew_member, 'home_front'):
            lines.append(f"Home: {_color_system.colorize(crew_member.home_front.value, 'bright_cyan')}")
        
        if hasattr(crew_member, 'personality'):
            lines.append(f"Personality: {_color_system.colorize(crew_member.personality.value, 'bright_yellow')}")
        
        if hasattr(crew_member, 'background'):
            lines.append(f"Background: {crew_member.background.value.replace('_', ' ').title()}\n")
        
        # Stories
        if hasattr(crew_member, 'personal_story'):
            lines.append(_color_system.label("Personal Story:"))
            lines.append(f"  {crew_member.personal_story}\n")
        
        if hasattr(crew_member, 'home_story'):
            lines.append(_color_system.label("Home Front:"))
            lines.append(f"  {crew_member.home_story}\n")
        
        # Motivations and fears
        if hasattr(crew_member, 'motivations') and crew_member.motivations:
            lines.append(_color_system.label("Motivations:"))
            for motivation in crew_member.motivations:
                lines.append(f"  • {motivation}")
            lines.append("")
        
        if hasattr(crew_member, 'fears') and crew_member.fears:
            lines.append(_color_system.label("Fears:"))
            for fear in crew_member.fears:
                lines.append(f"  • {fear}")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def show_faction_roster(faction: str, crew_list: List) -> str:
        """Show crew roster organized by faction."""
        from ui.color_system import _color_system
        
        # Filter crew by faction
        faction_crew = [c for c in crew_list if hasattr(c, 'faction') and c.faction.value == faction]
        
        if not faction_crew:
            return f"No crew members from {faction}"
        
        lines = []
        lines.append(_color_system.header(f"═══ {faction.upper()} ═══\n"))
        lines.append(f"Personnel: {len(faction_crew)} members\n")
        
        for i, member in enumerate(faction_crew, 1):
            lines.append(f"{i:2d}. {CrewManagementUI.format_crew_member(member)}")
        
        return "\n".join(lines)
    
    @staticmethod
    def show_crew_story_summary() -> str:
        """Show summary of historical crew stories."""
        from ui.color_system import _color_system
        
        manager = get_story_manager()
        factions = manager.get_all_factions_represented()
        
        lines = []
        lines.append(_color_system.header("═══ HISTORICAL CREW STORIES ═══\n"))
        
        for faction in factions:
            stories = manager.get_stories_by_faction(faction)
            lines.append(_color_system.label(f"{faction}:"))
            for story in stories:
                lines.append(f"  • {story.name} ({story.rank}) - {story.submarine}")
                lines.append(f"    {story.main_story[:120]}...")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def show_patrol_theater_context() -> str:
        """Show context about different patrol theaters."""
        from ui.color_system import _color_system
        
        manager = get_story_manager()
        context = manager.generate_historical_patrol_context()
        
        # Add color
        colored = _color_system.header("═══ PATROL THEATERS ═══\n\n") + context
        return colored


def show_crew_help(game) -> str:
    """Show help for crew management commands."""
    from ui.color_system import _color_system
    
    lines = []
    lines.append(_color_system.header(f"═══ CREW MANAGEMENT COMMANDS ═══\n"))
    
    lines.append(_color_system.label("Viewing:"))
    lines.append("  crew list          - Show all crew members")
    lines.append("  crew detailed      - Show detailed crew stats")
    lines.append("  crew by-assignment - Show crew by compartment")
    lines.append("  crew morale        - Show morale report")
    lines.append("  crew stress-tips   - Show stress management tips")
    lines.append("  crew stories       - Show historical crew stories")
    lines.append("  crew biography <name> - Show crew member biography\n")
    
    lines.append(_color_system.label("Factions:"))
    lines.append("  crew factions      - Show available factions")
    lines.append("  crew faction <name> - Show crew by faction")
    lines.append("  crew theater       - Show patrol theater information\n")
    
    lines.append(_color_system.label("Management:"))
    lines.append("  crew assign <name> <compartment> - Assign crew member")
    lines.append("  crew rest          - Order crew to rest (reduce stress)")
    lines.append("  crew inspire       - Captain's speech (boost morale)")
    lines.append("")
    
    return "\n".join(lines)
