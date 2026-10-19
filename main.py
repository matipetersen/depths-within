# Entry point for Depths Within
from engine.game import Game
from ui.setup_screen import run_setup_screen, quick_setup
import sys

def main():
    """Main entry point with setup screen."""
    print("\033[2J\033[H")  # Clear screen
    print("Initializing Depths Within...\n")
    
    # Check if we should skip setup (for testing)
    skip_setup = '--skip-setup' in sys.argv or '--quick' in sys.argv
    
    if skip_setup:
        # Quick setup for testing
        print("Quick setup mode...")
        faction, crew_list = quick_setup("Germany")
    else:
        # Run interactive setup screen
        setup_result = run_setup_screen()
        
        if setup_result is None:
            print("Setup cancelled. Exiting.")
            return
        
        faction, crew_list = setup_result
    
    # Create game and initialize with setup data
    print(f"\nStarting game as {faction['name']}...")
    print(f"Crew: {len(crew_list)} personnel\n")
    
    game = Game()
    game.initialize_from_setup(faction, crew_list)
    game.run()

if __name__ == "__main__":
    main()
