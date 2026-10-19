"""
Statistics Panel UI - Displays game statistics and achievement summaries.
"""

from engine.game_statistics import get_statistics, StatisticType
from ui.color_system import _color_system


class StatisticsPanel:
    """Displays game statistics in various formats."""
    
    def show_stats_summary(self) -> str:
        """Show abbreviated statistics summary for status display."""
        stats = get_statistics()
        
        summary = _color_system.header("STATISTICS:\n")
        summary += f"  Ships Sunk: {_color_system.colorize(str(stats.get_stat(StatisticType.SHIPS_SUNK)), 'bright_red')}"
        tonnage = stats.get_stat(StatisticType.TOTAL_TONNAGE_SUNK)
        summary += f" | Tonnage: {_color_system.colorize(str(tonnage) + 't', 'bright_yellow')}"
        summary += f" | Deaths: {_color_system.colorize(str(stats.get_stat(StatisticType.CREW_DEATHS)), 'bright_red')}\n"
        summary += f"  Missions: {_color_system.colorize(str(stats.get_stat(StatisticType.MISSIONS_COMPLETED)), 'bright_green')} done"
        summary += f" | Spies: {_color_system.colorize(str(stats.get_stat(StatisticType.SPIES_CAUGHT)), 'bright_yellow')} caught"
        summary += f" | Sabotage: {_color_system.colorize(str(stats.get_stat(StatisticType.SABOTAGES_DETECTED)), 'bright_yellow')} detected\n"
        
        return summary
    
    def show_full_report(self) -> str:
        """Show full statistics report."""
        return get_statistics().get_summary_report()
    
    def show_detailed_report(self) -> str:
        """Show detailed statistics with event logs."""
        return get_statistics().get_detailed_report()
    
    def show_combat_record(self) -> str:
        """Show combat-specific statistics."""
        stats = get_statistics()
        
        report = _color_system.header("═══ COMBAT RECORD ═══\n\n")
        
        report += _color_system.label("OFFENSIVE:\n")
        report += f"  Ships Sunk: {_color_system.colorize(str(stats.get_stat(StatisticType.SHIPS_SUNK)), 'bright_red')}\n"
        tonnage_str = str(stats.get_stat(StatisticType.TOTAL_TONNAGE_SUNK)) + 't'
        report += f"  Total Tonnage: {_color_system.colorize(tonnage_str, 'bright_yellow')}\n"
        report += f"  Torpedoes Fired: {stats.get_stat(StatisticType.TORPEDOES_FIRED)}\n"
        report += f"  Torpedoes Hit: {_color_system.colorize(str(stats.get_stat(StatisticType.TORPEDOES_HIT)), 'bright_green')}\n"
        
        if stats.get_stat(StatisticType.TORPEDOES_FIRED) > 0:
            hit_rate = (stats.get_stat(StatisticType.TORPEDOES_HIT) / stats.get_stat(StatisticType.TORPEDOES_FIRED)) * 100
            hit_rate_str = f'{hit_rate:.1f}%'
            report += f"  Accuracy: {_color_system.colorize(hit_rate_str, 'bright_green')}\n"
        
        report += f"  Naval Battles: {stats.get_stat(StatisticType.NAVAL_BATTLES)}\n"
        report += f"  Convoy Engagements: {stats.get_stat(StatisticType.CONVOY_ENGAGEMENTS)}\n"
        report += "\n"
        
        report += _color_system.label("DEFENSIVE:\n")
        report += f"  Depth Charges Survived: {stats.get_stat(StatisticType.DEPTH_CHARGES_SURVIVED)}\n"
        report += f"  Successful Escapes: {_color_system.colorize(str(stats.get_stat(StatisticType.SUCCESSFUL_ESCAPES)), 'bright_green')}\n"
        report += f"  Surface Sightings: {stats.get_stat(StatisticType.SURFACE_SIGHTINGS)}\n"
        report += f"  Compartments Flooded: {_color_system.colorize(str(stats.get_stat(StatisticType.COMPARTMENTS_FLOODED)), 'bright_red')}\n"
        report += f"  Equipment Failures: {stats.get_stat(StatisticType.EQUIPMENT_FAILURES)}\n"
        report += "\n"
        
        report += _color_system.label("ACHIEVEMENTS:\n")
        if stats.ship_kills:
            report += f"  Notable Kills: {len(stats.ship_kills)} ships documented\n"
            for i, kill in enumerate(stats.ship_kills[-3:], 1):  # Last 3
                report += f"    • {kill['type']} ({kill['tonnage']}t)\n"
            if len(stats.ship_kills) > 3:
                report += f"    • ... and {len(stats.ship_kills) - 3} more\n"
        else:
            report += "  No documented kills yet.\n"
        
        return report
    
    def show_crew_record(self) -> str:
        """Show crew-specific statistics."""
        stats = get_statistics()
        
        report = _color_system.header("═══ CREW RECORD ═══\n\n")
        
        report += _color_system.label("PERSONNEL:\n")
        report += f"  Recruited: {_color_system.colorize(str(stats.get_stat(StatisticType.CREW_RECRUITED)), 'bright_green')}\n"
        report += f"  Deaths: {_color_system.colorize(str(stats.get_stat(StatisticType.CREW_DEATHS)), 'bright_red')}\n"
        report += f"  Injured: {stats.get_stat(StatisticType.CREW_INJURED)}\n"
        report += "\n"
        
        report += _color_system.label("MORALE & STRESS:\n")
        report += f"  Morale Crises: {_color_system.colorize(str(stats.get_stat(StatisticType.CREW_MORALE_CRISES)), 'bright_yellow')}\n"
        report += f"  Stress Incidents: {stats.get_stat(StatisticType.CREW_STRESS_INCIDENTS)}\n"
        report += "\n"
        
        if stats.crew_deaths_log:
            report += _color_system.label("RECENT LOSSES:\n")
            for i, death in enumerate(stats.crew_deaths_log[-5:], 1):  # Last 5
                report += f"  {i}. {death['name']} ({death['rank']}) - {death['cause']}\n"
            if len(stats.crew_deaths_log) > 5:
                report += f"  ... and {len(stats.crew_deaths_log) - 5} more\n"
        
        return report
    
    def show_security_record(self) -> str:
        """Show security incidents and sabotage record."""
        stats = get_statistics()
        
        report = _color_system.header("═══ SECURITY RECORD ═══\n\n")
        
        report += _color_system.label("COUNTERINTELLIGENCE:\n")
        report += f"  Spies Caught: {_color_system.colorize(str(stats.get_stat(StatisticType.SPIES_CAUGHT)), 'bright_yellow')}\n"
        report += f"  Sabotages Detected: {_color_system.colorize(str(stats.get_stat(StatisticType.SABOTAGES_DETECTED)), 'bright_yellow')}\n"
        report += f"  Sabotages Successful: {_color_system.colorize(str(stats.get_stat(StatisticType.SABOTAGES_SUCCESSFUL)), 'bright_red')}\n"
        report += "\n"
        
        if stats.spies_caught_log:
            report += _color_system.label("APPREHENDED AGENTS:\n")
            for i, spy in enumerate(stats.spies_caught_log, 1):
                report += f"  {i}. {spy['real_name']} (Cover: {spy['cover_name']})\n"
        
        if stats.sabotages_log:
            report += _color_system.label("SABOTAGE INCIDENTS:\n")
            report += f"  Detected: {sum(1 for s in stats.sabotages_log if s['status'] == 'detected')}\n"
            report += f"  Successful: {sum(1 for s in stats.sabotages_log if s['status'] == 'successful')}\n"
            
            recent = stats.sabotages_log[-5:]
            if recent:
                report += "\n  Recent Incidents:\n"
                for i, sab in enumerate(recent, 1):
                    status = _color_system.colorize(sab['status'].upper(), 
                                                   'bright_yellow' if sab['status'] == 'detected' else 'bright_red')
                    report += f"    {i}. {sab['type']} - {status}\n"
        
        return report
    
    def show_mission_record(self) -> str:
        """Show mission completion record."""
        stats = get_statistics()
        
        report = _color_system.header("═══ MISSION RECORD ═══\n\n")
        
        completed = stats.get_stat(StatisticType.MISSIONS_COMPLETED)
        failed = stats.get_stat(StatisticType.MISSIONS_FAILED)
        total = completed + failed
        
        report += _color_system.label("SUMMARY:\n")
        report += f"  Completed: {_color_system.colorize(str(completed), 'bright_green')}\n"
        report += f"  Failed: {_color_system.colorize(str(failed), 'bright_red')}\n"
        if total > 0:
            success_rate = (completed / total) * 100
            success_str = f'{success_rate:.1f}%'
            report += f"  Success Rate: {_color_system.colorize(success_str, 'bright_green')}\n"
        report += f"  Successful Patrols: {_color_system.colorize(str(stats.get_stat(StatisticType.SUCCESSFUL_PATROLS)), 'bright_green')}\n"
        report += "\n"
        
        if stats.missions_log:
            report += _color_system.label("RECENT MISSIONS:\n")
            for i, mission in enumerate(stats.missions_log[-10:], 1):  # Last 10
                status_color = 'bright_green' if mission['status'] == 'completed' else 'bright_red'
                status = _color_system.colorize(mission['status'].upper(), status_color)
                report += f"  {i}. {mission['type']} - {status}\n"
            if len(stats.missions_log) > 10:
                report += f"  ... and {len(stats.missions_log) - 10} more\n"
        
        return report
    
    def show_help(self) -> str:
        """Show statistics commands help."""
        help_text = _color_system.header("STATISTICS COMMANDS:\n\n")
        
        help_text += _color_system.label("stats summary\n")
        help_text += "  Show brief statistics overview\n\n"
        
        help_text += _color_system.label("stats full\n")
        help_text += "  Show complete statistics report\n\n"
        
        help_text += _color_system.label("stats detailed\n")
        help_text += "  Show detailed report with event logs\n\n"
        
        help_text += _color_system.label("stats combat\n")
        help_text += "  Show combat record and achievements\n\n"
        
        help_text += _color_system.label("stats crew\n")
        help_text += "  Show crew personnel and morale record\n\n"
        
        help_text += _color_system.label("stats security\n")
        help_text += "  Show security incidents and counterintelligence\n\n"
        
        help_text += _color_system.label("stats missions\n")
        help_text += "  Show mission completion record\n\n"
        
        help_text += _color_system.label("stats help\n")
        help_text += "  Show this help message\n"
        
        return help_text
