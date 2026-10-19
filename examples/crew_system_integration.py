"""
Integration Example: Enhanced Crew System in Game Loop
Demonstrates how to integrate the new crew system into existing game.
"""

# This is a reference example showing integration patterns
# Adapt to your existing game architecture

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from submarine.crew_skills import (
    SkilledCrewMember, CrewQuality, Specialization
)
from submarine.crew_recruitment_enhanced import (
    RecruitmentPool, CrewRosterManager
)
from submarine.engineer_repairs import (
    EngineerRepairSystem, RepairType
)


class GameState:
    """Example game state with crew system integration."""
    
    def __init__(self):
        # Existing game systems
        self.submarine = None  # Your submarine instance
        self.player = None     # Player stats/progression
        self.journal = None    # Event logging
        
        # NEW: Crew systems
        self.crew_roster = CrewRosterManager("U-96", max_crew=50)
        self.repair_system = EngineerRepairSystem()
        self.recruitment_pool = None  # Created at port
        
        # Player progression
        self.captain_level = 1
        self.reputation = 0
    
    def enter_port(self, port_name: str, port_quality: int = 3):
        """Called when player enters a port."""
        print(f"\n=== Entering {port_name} ===\n")
        
        # Create/refresh recruitment pool
        self.recruitment_pool = RecruitmentPool(port_name, port_quality)
        self.recruitment_pool.refresh_pool(
            self.captain_level,
            self.reputation
        )
        
        # Show available crew
        print(self.recruitment_pool.get_summary())
        
        # Example: Show specialists
        specialists = self.recruitment_pool.get_specialists()
        if specialists:
            print(f"\n🌟 {len(specialists)} Specialists Available:")
            for spec in specialists:
                print(f"  - {spec.name}: {spec.specialization.value.replace('_', ' ').title()}")
                print(f"    Quality: {spec.quality.name}, Cost: ", end="")
                _, cost = self.recruitment_pool.recruit(spec)
                print(f"{cost} points")
    
    def recruit_crew_ui(self):
        """UI function for crew recruitment."""
        while True:
            print("\n=== Recruitment Menu ===")
            print("1. View available crew")
            print("2. Filter by quality")
            print("3. Filter by skill")
            print("4. View specialists only")
            print("5. Recruit crew")
            print("6. Exit to port menu")
            
            choice = input("\nChoice: ")
            
            if choice == '1':
                self._show_all_crew()
            elif choice == '2':
                self._filter_by_quality()
            elif choice == '3':
                self._filter_by_skill()
            elif choice == '4':
                self._show_specialists()
            elif choice == '5':
                self._recruit_selected_crew()
            elif choice == '6':
                break
    
    def _show_all_crew(self):
        """Show all available crew."""
        crew_list = self.recruitment_pool.get_available_crew()
        
        print(f"\n{len(crew_list)} crew members available:")
        for i, crew in enumerate(crew_list, 1):
            print(f"\n{i}. {crew.name}")
            print(f"   Quality: {crew.quality.name}")
            print(f"   Primary Skill: {crew.primary_skill.title()}")
            
            if crew.specialization:
                print(f"   Specialization: {crew.specialization.value.replace('_', ' ').title()}")
            
            # Show recruitment info
            _, cost = self.recruitment_pool.recruit(crew)
            print(f"   Cost: {cost} points")
    
    def take_damage(self, damage_type: str, severity: float, 
                   compartment_id: str = None):
        """Called when submarine takes damage."""
        print(f"\n⚠️  Damage: {damage_type} (Severity: {severity:.0%})")
        
        # Map damage type to repair type
        repair_type_map = {
            'hull_breach': RepairType.HULL_BREACH,
            'flooding': RepairType.FLOODING,
            'electrical': RepairType.ELECTRICAL,
            'engine': RepairType.MECHANICAL,
            'torpedo_tube': RepairType.TORPEDO_TUBE,
            'sonar': RepairType.SONAR,
            'periscope': RepairType.PERISCOPE,
        }
        
        repair_type = repair_type_map.get(damage_type, RepairType.COMPARTMENT)
        
        # Create repair task
        priority = severity > 0.6 or damage_type == 'hull_breach'
        task = self.repair_system.create_repair(
            repair_type=repair_type,
            severity=severity,
            compartment_id=compartment_id,
            priority=priority
        )
        
        print(f"   Repair queued: {task.repair_type.value}")
        print(f"   Priority: {'HIGH' if priority else 'Normal'}")
        
        # Auto-assign engineers if available
        self._auto_assign_repairs()
    
    def _auto_assign_repairs(self):
        """Auto-assign available engineers to queued repairs."""
        # Get available engineers (not currently assigned)
        all_engineers = self.crew_roster.get_crew_by_skill('engineering')
        assigned = {task.assigned_engineer for task in self.repair_system.active_repairs}
        available = [e for e in all_engineers if e not in assigned]
        
        if available and self.repair_system.repair_queue:
            assignments = self.repair_system.auto_assign_engineers(available)
            if assignments > 0:
                print(f"\n🔧 Auto-assigned {assignments} engineers to repairs")
                
                # Log assignments
                for task in self.repair_system.active_repairs:
                    if task.assigned_engineer:
                        engineer = task.assigned_engineer
                        skill = engineer.effective_skill('engineering')
                        print(f"   {engineer.name} → {task.repair_type.value} (Skill: {skill:.0%})")
    
    def game_tick(self):
        """Main game loop tick - call every turn/second."""
        # Process repairs
        repair_events = self.repair_system.tick_all_repairs()
        
        for event in repair_events:
            if event['complete']:
                # Repair finished!
                self._handle_repair_complete(event)
        
        # Update crew status
        self.crew_roster.tick()
        
        # Check for level ups
        for crew in self.crew_roster.crew:
            old_level = crew.level
            # Crew leveling happens automatically in gain_xp()
            # But we can check if it happened
            if hasattr(crew, '_just_leveled'):
                self._handle_crew_level_up(crew)
                delattr(crew, '_just_leveled')
    
    def _handle_repair_complete(self, event: dict):
        """Handle completed repair."""
        repair_type = event['repair_type']
        engineer_name = event['engineer']
        
        print(f"\n✅ Repair Complete!")
        print(f"   {repair_type.replace('_', ' ').title()}")
        print(f"   Engineer: {engineer_name}")
        
        # Apply repair to submarine systems
        # (This connects to your existing submarine damage system)
        if repair_type == 'hull_breach':
            # Example: restore hull integrity
            # self.submarine.systems.hull_integrity += 0.2
            pass
        elif repair_type == 'flooding':
            # Example: reduce flooding
            # compartment.flooding -= 0.3
            pass
        
        # Log to journal
        if self.journal:
            self.journal.log(event['message'])
    
    def _handle_crew_level_up(self, crew: SkilledCrewMember):
        """Handle crew member leveling up."""
        print(f"\n🎉 {crew.name} leveled up to Level {crew.level}!")
        print(f"   New Rank: {crew.rank}")
        
        # Check for specialization eligibility
        if crew.level >= 5 and not crew.specialization:
            available_specs = self._get_available_specializations(crew)
            if available_specs:
                print(f"\n   Can now specialize as:")
                for spec in available_specs:
                    print(f"   - {spec.value.replace('_', ' ').title()}")
                
                # Could prompt player to choose specialization
                # self._offer_specialization_choice(crew, available_specs)
    
    def _get_available_specializations(self, crew: SkilledCrewMember) -> list:
        """Get specializations crew can acquire."""
        available = []
        for spec in Specialization:
            if crew.can_specialize(spec):
                available.append(spec)
        return available
    
    def award_xp(self, crew: SkilledCrewMember, skill: str, amount: int = 10):
        """Award XP to crew member for action."""
        old_level = crew.level
        crew.gain_xp(skill, amount)
        
        # Check if leveled up
        if crew.level > old_level:
            crew._just_leveled = True  # Flag for tick handler
        
        print(f"   {crew.name} gained {amount} {skill} XP")
    
    def fire_torpedo(self):
        """Example: Fire torpedo, award XP to torpedo crew."""
        # Get best torpedo crew
        torpedo_crew = self.crew_roster.get_best_crew_for_skill('torpedoes')
        
        if torpedo_crew:
            # Award XP for action
            self.award_xp(torpedo_crew, 'torpedoes', 20)
            
            # Torpedo crew's skill affects accuracy
            skill = torpedo_crew.effective_skill('torpedoes')
            
            # Apply skill to torpedo calculation
            # accuracy_bonus = skill * 0.3  # Up to 30% better
            # torpedo.accuracy += accuracy_bonus
    
    def detect_contact(self):
        """Example: Detect enemy contact, award XP to sonar operator."""
        sonar_crew = self.crew_roster.get_best_crew_for_skill('sonar')
        
        if sonar_crew:
            # Award XP
            self.award_xp(sonar_crew, 'sonar', 5)
            
            # Sonar skill affects detection
            skill = sonar_crew.effective_skill('sonar')
            
            # Apply to detection range/accuracy
            # detection_range *= (1.0 + skill * 0.5)  # Up to 50% better
    
    def show_crew_roster(self):
        """Display crew roster UI."""
        print("\n" + "="*80)
        print(self.crew_roster.get_roster_summary())
        print("="*80)
        
        # Show active repairs
        if self.repair_system.active_repairs:
            print("\n" + self.repair_system.get_repair_summary())
    
    def show_repair_status(self):
        """Display repair status UI."""
        print("\n" + "="*80)
        print(self.repair_system.get_repair_summary())
        print("="*80)
        
        # Show engineer status
        print("\nENGINEER STATUS:")
        engineers = self.crew_roster.get_crew_by_skill('engineering')
        for eng in engineers:
            workload = self.repair_system.get_engineer_workload(eng)
            status = f"{'🔧 Working' if workload > 0 else '💤 Available'}"
            print(f"  {eng.name:20s} {status:15s} "
                  f"(Skill: {eng.effective_skill('engineering'):.0%}, "
                  f"Stress: {eng.stress:.0%})")


def example_game_session():
    """Example game session demonstrating crew system."""
    print("="*80)
    print("EXAMPLE GAME SESSION - Enhanced Crew System")
    print("="*80)
    
    # Initialize game
    game = GameState()
    game.captain_level = 5  # Mid-game captain
    game.reputation = 60    # Good reputation
    
    # 1. PORT PHASE
    print("\n### PHASE 1: PORT VISIT ###")
    game.enter_port("Kiel Naval Base", port_quality=5)
    
    # Simulate recruiting a specialist
    specialists = game.recruitment_pool.get_specialists()
    if specialists:
        engineer_spec = next((s for s in specialists 
                             if s.primary_skill == 'engineering'), None)
        
        if engineer_spec:
            print(f"\n💰 Recruiting {engineer_spec.name} "
                  f"({engineer_spec.specialization.value.replace('_', ' ').title()})")
            success, cost = game.recruitment_pool.recruit(engineer_spec)
            if success:
                game.crew_roster.add_crew(engineer_spec)
                print(f"   Cost: {cost} points")
                print(f"   ✅ Added to roster")
    
    # Also recruit some regular crew
    experienced = game.recruitment_pool.get_available_crew(
        quality_filter=CrewQuality.EXPERIENCED,
        skill_filter='engineering'
    )
    if experienced:
        game.recruitment_pool.recruit(experienced[0])
        game.crew_roster.add_crew(experienced[0])
        print(f"\n💰 Recruited {experienced[0].name} (Experienced Engineer)")
    
    # 2. MISSION PHASE
    print("\n\n### PHASE 2: MISSION START ###")
    game.show_crew_roster()
    
    # 3. COMBAT - Take damage
    print("\n\n### PHASE 3: COMBAT DAMAGE ###")
    game.take_damage('hull_breach', 0.75, 'forward_torpedo')
    game.take_damage('flooding', 0.5, 'engine_room')
    game.take_damage('electrical', 0.3, 'control_room')
    
    # 4. REPAIR PROGRESS
    print("\n\n### PHASE 4: REPAIR SIMULATION ###")
    game.show_repair_status()
    
    print("\nSimulating 10 game ticks...")
    for tick in range(10):
        game.game_tick()
        
        # Show progress every 3 ticks
        if (tick + 1) % 3 == 0:
            print(f"\n--- Tick {tick + 1} ---")
            for task in game.repair_system.active_repairs:
                if task.assigned_engineer:
                    print(f"  {task.repair_type.value}: {task.progress:.0%} complete "
                          f"({task.assigned_engineer.name})")
    
    # 5. FINAL STATUS
    print("\n\n### PHASE 5: FINAL STATUS ###")
    game.show_crew_roster()
    game.show_repair_status()
    
    print("\n" + "="*80)
    print("✅ Example session complete!")
    print("="*80)
    print("\nKey Takeaways:")
    print("  ✅ Specialists repair 2-3x faster than regular crew")
    print("  ✅ Auto-assignment picks best engineer for each task")
    print("  ✅ Crew gains XP and levels up")
    print("  ✅ Reputation affects recruitment quality")
    print("  ✅ System integrates seamlessly with existing game")


if __name__ == '__main__':
    example_game_session()
