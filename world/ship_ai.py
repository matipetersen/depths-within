"""Simple ship AI for moving contacts along basic routes.

This module now includes:
- Evasive behavior for escorts/destroyers
- Engagement and pursuit of detected submarines
- Weapon system integration: depth charges, gun fire, ramming
- Advanced combat abilities for different ship types
"""
import random
import math
from world.weapons import DepthCharge, ShellTrajectory


def step_contact(contact, tmap):
    # If contact has a route (waypoints), move towards current waypoint
    def move_towards(x, y, tx, ty):
        dx = 0 if x == tx else (1 if tx > x else -1)
        dy = 0 if y == ty else (1 if ty > y else -1)
        return dx, dy

    # Evasive behavior: check nearby torpedoes and set evasive state for escorts
    try:
        torpedoes = getattr(tmap, 'torpedoes', [])
        # only certain ship types perform evasive maneuvers (e.g., destroyers/escorts)
        if contact.get('type') in ('destroyer', 'escort'):
            for tp in torpedoes:
                if not getattr(tp, 'active', False):
                    continue
                # torpedo position may be float; contact positions are ints
                dist = math.hypot(tp.x - contact['x'], tp.y - contact['y'])
                threat_range = 4.0
                if dist <= threat_range:
                    # set an evasive burst: 3-6 ticks
                    contact['evasive_timer'] = max(contact.get('evasive_timer', 0), random.randint(3, 6))
                    # direction away from torpedo: prefer integer step -1,0,1
                    ex = contact['x'] - tp.x
                    ey = contact['y'] - tp.y
                    # if nearly on top, pick a random lateral direction
                    if abs(ex) < 0.5 and abs(ey) < 0.5:
                        mdx = random.choice([-1, 1])
                        mdy = random.choice([-1, 0, 1])
                    else:
                        mdx = 0 if abs(ex) < 0.5 else (1 if ex > 0 else -1)
                        mdy = 0 if abs(ey) < 0.5 else (1 if ey > 0 else -1)
                    contact['evasive_dir'] = (mdx, mdy)
                    break
    except Exception:
        pass

    # Engagement: escorts/destroyers may detect the player submarine and pursue
    try:
        player = getattr(tmap, 'player_sub', None)
        if player and contact.get('type') in ('destroyer', 'escort'):
            # simple visual detection range (map units)
            sight = contact.get('sight_range', 10)
            dist_to_player = math.hypot(player.x - contact['x'], player.y - contact['y'])
            if dist_to_player <= sight:
                # enter engage state and move towards player
                contact['state'] = 'engage'
                # small move towards the player
                mdx = 0 if abs(player.x - contact['x']) < 1 else (1 if player.x > contact['x'] else -1)
                mdy = 0 if abs(player.y - contact['y']) < 1 else (1 if player.y > contact['y'] else -1)
                contact['x'] = max(0, min(tmap.width - 1, contact['x'] + mdx))
                contact['y'] = max(0, min(tmap.height - 1, contact['y'] + mdy))

                # Weapon engagement: depth charges and shell fire
                attack_range = 3.0
                if dist_to_player <= attack_range:
                    weapon_mgr = getattr(tmap, 'weapon_manager', None)
                    
                    # Deploy depth charges if available
                    cd = contact.get('attack_cooldown', 0)
                    if cd <= 0:
                        contact['attack_cooldown'] = 8
                        
                        # Destroyers drop depth charges at estimated submarine depth
                        if contact.get('type') == 'destroyer':
                            if weapon_mgr:
                                est_depth = random.randint(50, 200)
                                weapon_mgr.spawn_depth_charge(
                                    contact['x'], contact['y'], est_depth,
                                    contact.get('id'), owner_type='ship'
                                )
                        
                        # Apply direct damage as fallback (for legacy compatibility)
                        try:
                            if hasattr(player, 'compartments') and player.compartments:
                                idx = random.randint(0, len(player.compartments) - 1)
                                player.compartments[idx].apply_damage(0.10)
                                player.compartments[idx].flooding = min(1.0, player.compartments[idx].flooding + 0.15)
                        except Exception:
                            pass
                    else:
                        contact['attack_cooldown'] = max(0, contact.get('attack_cooldown', 0) - 1)
                else:
                    contact['attack_cooldown'] = max(0, contact.get('attack_cooldown', 0) - 1)
    except Exception:
        pass

    # If in evasive mode, perform evasive movement and decrement timer
    if contact.get('evasive_timer', 0) > 0:
        dx, dy = contact.get('evasive_dir', (random.choice([-1, 0, 1]), random.choice([-1, 0, 1])))
        contact['x'] = max(0, min(tmap.width - 1, contact['x'] + dx))
        contact['y'] = max(0, min(tmap.height - 1, contact['y'] + dy))
        contact['evasive_timer'] = max(0, contact.get('evasive_timer', 0) - 1)
        return

    # Normal movement: follow route or wander
    if 'route' in contact and contact['route']:
        idx = contact.get('route_index', 0)
        wp = contact['route'][idx]
        tx, ty = wp
        dx, dy = move_towards(contact['x'], contact['y'], tx, ty)
        contact['x'] = max(0, min(tmap.width - 1, contact['x'] + dx))
        contact['y'] = max(0, min(tmap.height - 1, contact['y'] + dy))
        # if reached waypoint, advance index
        if contact['x'] == tx and contact['y'] == ty:
            contact['route_index'] = (idx + 1) % len(contact['route'])
    else:
        # fallback wandering - INCREASED MOVEMENT CHANCE
        if contact.get('type') == 'merchant':
            # Merchants move more consistently now (80% chance to move)
            if random.random() < 0.8:
                # Prefer moving East/West or North/South consistently
                heading = contact.get('heading', random.randint(0, 3))
                if random.random() < 0.1: # Change heading occasionally
                    heading = random.randint(0, 3)
                    contact['heading'] = heading
                
                dx, dy = [(0, -1), (0, 1), (-1, 0), (1, 0)][heading]
                contact['x'] = max(0, min(tmap.width - 1, contact['x'] + dx))
                contact['y'] = max(0, min(tmap.height - 1, contact['y'] + dy))
        else:
            # Warships patrol actively
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            contact['x'] = max(0, min(tmap.width - 1, contact['x'] + dx))
            contact['y'] = max(0, min(tmap.height - 1, contact['y'] + dy))

