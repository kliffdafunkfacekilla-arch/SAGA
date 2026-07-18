"""
command_parser.py

Translates abstracted AI intents and player actions into precise 
database queries against the SAGA Engine. Also handles 
the 25-cluster map blueprint generation and delta-state retrieval.
"""
import sqlite3
import random
import json
import narrative_engine
import math
import interaction_matrix
from tag_manager import TagManager
import config

def get_db():
    return sqlite3.connect(config.ACTIVE_DB_PATH)

def calculate_gear_tax(inventory_list):
    """
    Calculates total weight of inventory and returns the Loadout classification.
    Light: <= 3 weight
    Medium: 4-7 weight
    Heavy: 8+ weight
    """
    total_weight = 0
    for item in inventory_list:
        if isinstance(item, dict) and 'weight' in item:
            total_weight += int(item['weight'])
            
    if total_weight <= 3:
        return "Light"
    elif total_weight <= 7:
        return "Medium"
    else:
        return "Heavy"

def get_db():
    return sqlite3.connect(DB_PATH)

def generate_local_map(location_type, location_id, sector_index=1):
    """
    On-the-fly generation of the 25-Sector Cluster Blueprint.
    If Sector 13 (the core) exists, the cluster is already generated.
    Otherwise, we generate all 25 sectors at once with archetypes and seeds.
    """
    conn = get_db()
    c = conn.cursor()
    
    # Check if cluster exists by checking cluster 13 (the core)
    c.execute("SELECT id FROM map_tiles WHERE location_type = ? AND location_id = ? AND cluster_id = 13", 
              (location_type, location_id))
    if c.fetchone():
        conn.close()
        return True # Cluster already exists
        
    # 1. Fetch Location Stats to determine Archetypes
    base_biome = 'Temperate'
    morale = 50
    chaos = 0
    
    if location_type == 'Burg':
        c.execute("SELECT morale, chaos_level FROM burgs WHERE id = ?", (location_id,))
        row = c.fetchone()
        if row:
            morale = row[0]
            chaos = row[1]
    elif location_type == 'Zone': 
        base_biome = 'Chaos Wastes'
        chaos = 100
    elif location_type == 'Prison': 
        base_biome = 'Obsidian Expanse'
        
    # 2. Fetch Hex Hooks for Micro-Narratives
    c.execute("SELECT hook_category, description FROM story_hooks WHERE location_type = ? AND location_id = ?", (location_type, location_id))
    hex_hooks = [{'category': r[0], 'description': r[1]} for r in c.fetchall()]
    
    # 3. Generate 25 Sectors
    sectors_to_insert = []
    
    for s in range(1, 26):
        archetype = 'Wilderness'
        
        # Spatial Cluster Logic
        if s == 13:
            if location_type == 'Burg': archetype = 'City Core'
            elif location_type == 'Zone': archetype = 'Zone Core'
            elif location_type == 'Prison': archetype = 'Sealed Pillar'
        elif s in [8, 12, 14, 18]: # Cross adjacent to center
            if location_type == 'Burg':
                archetype = 'Suburbs' if morale > 40 else 'Slums'
            elif location_type == 'Prison':
                archetype = 'Warden Camp'
        else: # Edges and Corners
            if location_type == 'Burg':
                archetype = random.choice(['Farmland', 'Forest', 'Dirt Road'])
            else:
                archetype = 'Wastes'
                
        # Dynamic POI Overrides for Edges
        if location_type == 'Burg' and chaos > 15 and s not in [13, 8, 12, 14, 18]:
            if random.random() < 0.1: # 10% chance per edge sector
                archetype = 'Bandit Hideout'
                
        seed = random.randint(100000, 999999)
        sectors_to_insert.append((location_type, location_id, s, base_biome, archetype, seed))
        
    c.executemany('''
        INSERT INTO map_tiles (location_type, location_id, cluster_id, base_biome, feature_archetype, seed)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sectors_to_insert)
    
    # 4. Generate Micro-Entities for the Blueprint
    c.execute("SELECT id, cluster_id, feature_archetype FROM map_tiles WHERE location_type=? AND location_id=?", (location_type, location_id))
    new_sectors = c.fetchall()
    
    deltas_to_insert = []
    
    for s_id, s_idx, arch in new_sectors:
        num_buildings = 0
        if arch == 'City Core': num_buildings = 15
        elif arch == 'Suburbs' or arch == 'Slums': num_buildings = 8
        elif arch == 'Farmland': num_buildings = 3
        elif arch == 'Bandit Hideout': num_buildings = 4
        
        for _ in range(num_buildings):
            bx = random.randint(10, 90)
            by = random.randint(10, 90)
            
            b_hook = narrative_engine.generate_micro_hook('Building', arch, hex_hooks)
            deltas_to_insert.append((s_id, bx, by, 'Building', json.dumps({"description": b_hook})))
            
            # Spawn 1-2 NPCs per building
            num_npcs = random.randint(1, 2)
            for _ in range(num_npcs):
                nx = min(99, max(0, bx + random.randint(-2, 2)))
                ny = min(99, max(0, by + random.randint(-2, 2)))
                
                n_hook = narrative_engine.generate_micro_hook('NPC', arch, hex_hooks)
                npc_name = random.choice(["Citizen", "Farmer", "Guard", "Bandit", "Merchant", "Urchin"])
                if arch == 'Bandit Hideout': npc_name = "Bandit"
                elif arch == 'Farmland': npc_name = "Farmer"
                elif arch == 'Slums': npc_name = "Urchin"
                
                deltas_to_insert.append((s_id, nx, ny, 'NPC', json.dumps({"name": npc_name, "hook": n_hook})))
                
    if deltas_to_insert:
        c.executemany('''
            INSERT INTO map_deltas (tile_id, local_x, local_y, change_type, details)
            VALUES (?, ?, ?, ?, ?)
        ''', deltas_to_insert)
    
    conn.commit()
    conn.close()
    return True

def query_local_state(location_type, location_id, cluster_id=13):
    """
    Returns full state for the LLM to narrate:
    Hooks, Weather, Chaos, Paragons, Map Data, and Narrative Seeding (Lore).
    """
    conn = get_db()
    c = conn.cursor()
    state = {}
    
    # 1. Base Stats and Map Seed
    if location_type == 'Burg':
        c.execute('''
            SELECT b.name, b.morale, b.chaos_level, b.current_weather, m.id, m.base_biome, m.feature_archetype, m.seed 
            FROM burgs b
            LEFT JOIN map_tiles m ON m.location_id = b.id AND m.location_type = 'Burg' AND m.cluster_id = ?
            WHERE b.id = ?
        ''', (cluster_id, location_id))
        row = c.fetchone()
        if row:
            state['name'] = row[0]
            state['morale'] = row[1]
            state['chaos'] = row[2]
            state['weather'] = row[3]
            state['tile_id'] = row[4]
            state['base_biome'] = row[5]
            state['feature_archetype'] = row[6]
            state['seed'] = row[7]
            state['cluster_id'] = cluster_id
            
            # Fetch Deltas
            # Fetch Deltas
            if row[4]:
                c.execute("SELECT local_x, local_y, change_type, details FROM map_deltas WHERE tile_id = ?", (row[4],))
                state['deltas'] = [{'x': d[0], 'y': d[1], 'type': d[2], 'details': d[3]} for d in c.fetchall()]
                
                # WIDENING EYE: Perception Check for Hidden Cultists
                c.execute("SELECT awareness, skills FROM player_characters WHERE id = 1")
                pc = c.fetchone()
                if pc:
                    aw, skills_json = pc
                    skills = []
                    if skills_json:
                        try:
                            skills = json.loads(skills_json)
                        except:
                            pass
                    modifier = (aw - 10) // 2
                    skill_bonus = 2 if 'perception' in skills or 'awareness' in skills else 0
                    roll = random.randint(1, 20) + modifier + skill_bonus
                    
                    if roll >= 12: # Difficulty 12 to see hidden cultists
                        c.execute("SELECT local_x, local_y, type, details FROM cult_forces WHERE location_id = ? AND cluster_id = ?", (location_id, cluster_id))
                        cultists = c.fetchall()
                        for cultist in cultists:
                            state['deltas'].append({
                                'x': cultist[0], 
                                'y': cultist[1], 
                                'type': 'CULT_FORCE', 
                                'details': cultist[3]
                            })
            else:
                state['deltas'] = []
                
    elif location_type in ['Zone', 'Prison', 'Marker']:
        c.execute('''
            SELECT m.id, m.base_biome, m.feature_archetype, m.seed 
            FROM map_tiles m
            WHERE m.location_id = ? AND m.location_type = ? AND m.cluster_id = ?
        ''', (location_id, location_type, cluster_id))
        row = c.fetchone()
        if row:
            state['tile_id'] = row[0]
            state['base_biome'] = row[1]
            state['feature_archetype'] = row[2]
            state['seed'] = row[3]
            state['cluster_id'] = cluster_id
            state['deltas'] = [] # Need proper delta fetch for zones too if needed
            
    # 2. Paragons
    c.execute("SELECT id, name, role, trait_1, flaw_1, local_x, local_y FROM paragons WHERE location_id = ? AND cluster_id = ?", (location_id, cluster_id))
    state['paragons'] = [{'id': r[0], 'name': r[1], 'role': r[2], 'trait': r[3], 'flaw': r[4], 'local_x': r[5], 'local_y': r[6]} for r in c.fetchall()]
    
    # 3. Hooks & Narrative Seeding (world_lore)
    c.execute("SELECT id, hook_category, description FROM story_hooks WHERE location_type = ? AND location_id = ?", (location_type, location_id))
    hooks_data = []
    for r in c.fetchall():
        hook_dict = {'category': r[1], 'description': r[2]}
        
        # Look up crosslinked lore
        c.execute('''
            SELECT l.subject, l.content 
            FROM world_lore l
            JOIN lore_crosslinks c ON c.lore_id = l.lore_id
            WHERE c.hook_id = ?
        ''', (r[0],))
        lore_entries = c.fetchall()
        if lore_entries:
            hook_dict['lore'] = [{'subject': l[0], 'content': l[1]} for l in lore_entries]
        hooks_data.append(hook_dict)
        
    state['hooks'] = hooks_data
    
    # 4. Fetch player position
    c.execute("SELECT local_x, local_y FROM player_characters WHERE id = 1")
    p_row = c.fetchone()
    if p_row:
        state['player_x'] = p_row[0]
        state['player_y'] = p_row[1]
    
    conn.close()
    return state

def create_character(name, origin, skill):
    """
    Creates a new Player Character with BRUTAL stats.
    """
    conn = sqlite3.connect('okasha_world.db')
    c = conn.cursor()
    
    # 3d6 for core stats
    stats = {
        'might': sum(random.randint(1, 6) for _ in range(3)),
        'endurance': sum(random.randint(1, 6) for _ in range(3)),
        'finesse': sum(random.randint(1, 6) for _ in range(3)),
        'reflex': sum(random.randint(1, 6) for _ in range(3)),
        'vitality': sum(random.randint(1, 6) for _ in range(3)),
        'fortitude': sum(random.randint(1, 6) for _ in range(3)),
        'knowledge': sum(random.randint(1, 6) for _ in range(3)),
        'logic': sum(random.randint(1, 6) for _ in range(3)),
        'awareness': sum(random.randint(1, 6) for _ in range(3)),
        'intuition': sum(random.randint(1, 6) for _ in range(3)),
        'charm': sum(random.randint(1, 6) for _ in range(3)),
        'willpower': sum(random.randint(1, 6) for _ in range(3))
    }
    
    # BRUTAL Stats Calculation
    health = stats['endurance'] + stats['fortitude'] + stats['vitality']
    composure = stats['willpower'] + stats['logic'] + stats['charm']
    stamina = stats['might'] + stats['reflex'] + stats['finesse']
    focus = stats['knowledge'] + stats['awareness'] + stats['intuition']
    
    c.execute('''
        INSERT INTO player_characters (name, origin, loadout, health, max_health, 
                              composure, max_composure, stamina, max_stamina, focus, max_focus,
                              level, xp, shards, inventory, skills,
                              might, endurance, finesse, reflex, vitality, fortitude,
                              knowledge, logic, awareness, intuition, charm, willpower,
                              trait_1, flaw_1, location_id, cluster_id, local_x, local_y)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0, 0, '[]', ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                'Determined', 'Reckless', 1, 13, 50, 50)
    ''', (name, origin, 'Light', health, health, composure, composure, stamina, stamina, focus, focus, json.dumps([skill]),
          stats['might'], stats['endurance'], stats['finesse'], stats['reflex'], stats['vitality'], stats['fortitude'],
          stats['knowledge'], stats['logic'], stats['awareness'], stats['intuition'], stats['charm'], stats['willpower']))
          
    char_id = c.lastrowid
    conn.commit()
    conn.close()
    return {"status": "success", "character_id": char_id, "name": name, "stats": stats, "derived": {"hp": health, "stamina": stamina, "focus": focus}}

def roll_dice(paragon_id, stat_name, difficulty, skill_check=None, focus_surge=False):
    """
    Pulls a stat from a Paragon or Player, rolls a d20 + modifier + skill bonus + focus surge.
    """
    valid_stats = ['might', 'endurance', 'finesse', 'reflex', 'vitality', 'fortitude', 
                   'knowledge', 'logic', 'awareness', 'intuition', 'charm', 'willpower']
                   
    if stat_name.lower() not in valid_stats:
        return {"error": f"Invalid stat {stat_name}"}
        
    conn = get_db()
    c = conn.cursor()
    # Try player first
    c.execute(f"SELECT name, {stat_name.lower()}, skills, focus FROM player_characters WHERE id = ?", (paragon_id,))
    row = c.fetchone()
    
    focus_bonus = 0
    if not row:
        # Fallback to paragon (paragons don't have JSON skills in our current schema yet, so default to empty)
        c.execute(f"SELECT name, {stat_name.lower()} FROM paragons WHERE id = ?", (paragon_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return {"error": "Paragon/Player not found"}
        name, stat_val = row
        skills_json = "[]"
    else:
        name, stat_val, skills_json, focus_val = row
        if focus_surge and focus_val >= 1:
            c.execute("UPDATE player_characters SET focus = focus - 1 WHERE id = ?", (paragon_id,))
            conn.commit()
            focus_bonus = 2
        
    conn.close()
    
    skills = []
    if skills_json:
        try:
            skills = json.loads(skills_json)
        except Exception:
            pass
    
    if not row:
        return {"error": "Paragon not found"}
        
    modifier = (stat_val - 10) // 2
    
    skill_bonus = 2 if skill_check in skills else 0
    
    roll = random.randint(1, 20)
    total = roll + modifier + skill_bonus + focus_bonus
    
    success = total >= difficulty
    is_crit = (roll == 20)
    is_fail = (roll == 1)
    
    if is_crit: success = True
    if is_fail: success = False
    
    return {
        "character": name,
        "stat": stat_name,
        "roll": roll,
        "modifier": modifier,
        "skill_bonus": skill_bonus,
        "focus_bonus": focus_bonus,
        "total": total,
        "difficulty": difficulty,
        "success": success,
        "critical": is_crit,
        "fumble": is_fail
    }

def execute_action(actor_id, action_type, target_id=None, **kwargs):
    """
    Executes structural DB actions resulting from the narrative.
    action_type: 'WALK', 'MOVE', 'ALTER_CHAOS'
    """
    conn = get_db()
    c = conn.cursor()
    
    # --- TAG-BASED MATRIX CHECK ---
    # 1. Get Actor's Location Tags
    query_id = actor_id if actor_id else 1
    c.execute("SELECT location_id, cluster_id FROM player_characters WHERE id = ?", (query_id,))
    p_row = c.fetchone()
    
    if p_row:
        loc_id, cluster = p_row
        c.execute("SELECT id FROM map_tiles WHERE location_id = ? AND cluster_id = ?", (loc_id, cluster))
        tile_row = c.fetchone()
        
        if tile_row:
            tile_id = tile_row[0]
            # 2. Map Action to a Power
            power_tag = interaction_matrix.map_action_to_power(action_type)
            
            # 3. Resolve Interaction
            outcome = TagManager.resolve(power_tag, tile_id, 'map_tiles', c)
            
            if outcome == 'BLOCK':
                conn.close()
                return {"status": "error", "message": "The environment forbids this action (Matrix: BLOCK)."}
            elif outcome == 'IGNITE':
                TagManager.add_state(tile_id, 'map_tiles', 'Burning', c)
                result['message'] = "The area catches fire."
            elif outcome == 'SHATTER':
                result['message'] = "The environment shatters."
    # --- END TAG-BASED MATRIX CHECK ---
    
    result = {"status": "success", "action": action_type}
    
    if action_type == 'WALK':
        # kwargs should contain 'dx' and 'dy' (-1, 0, or 1)
        dx = kwargs.get('dx', 0)
        dy = kwargs.get('dy', 0)
        
        c.execute("SELECT location_id, cluster_id, local_x, local_y FROM paragons WHERE id = ?", (actor_id,))
        row = c.fetchone()
        if not row: return {"status": "error", "message": "Paragon not found"}
        loc_id, cluster, x, y = row
        
        nx, ny = x + dx, y + dy
        
        # Sector Transition Logic (Assuming a 5x5 cluster for sectors 1-25)
        if nx < 0:
            nx = 99
            if (cluster - 1) % 5 == 0:
                result['message'] = "Player walked off the West edge of the Regional Hex! Entering new Hex..."
                # loc_id = get_west_hex(loc_id)
                cluster += 4 # Move to eastern edge of new hex
            else:
                cluster -= 1
        elif nx > 99:
            nx = 0
            if cluster % 5 == 0:
                result['message'] = "Player walked off the East edge of the Regional Hex! Entering new Hex..."
                cluster -= 4
            else:
                cluster += 1
                
        if ny < 0:
            ny = 99
            if cluster <= 5:
                result['message'] = "Player walked off the North edge of the Regional Hex! Entering new Hex..."
                cluster += 20
            else:
                cluster -= 5
        elif ny > 99:
            ny = 0
            if cluster > 20:
                result['message'] = "Player walked off the South edge of the Regional Hex! Entering new Hex..."
                cluster -= 20
            else:
                cluster += 5

        # Update position
        c.execute("UPDATE paragons SET location_id=?, cluster_id=?, local_x=?, local_y=? WHERE id=?", 
                  (loc_id, cluster, nx, ny, actor_id))
        result['message'] = result.get('message', f"Paragon walked to ({nx}, {ny}) in Cluster {cluster}")
        result['new_state'] = {"location_id": loc_id, "cluster": cluster, "x": nx, "y": ny}
        
    elif action_type == 'MOVE':
        # target_id is the new location_id
        c.execute("UPDATE paragons SET location_id = ? WHERE id = ?", (target_id, actor_id))
        result['message'] = f"Paragon {actor_id} moved to location {target_id}"
        
    elif action_type == 'ALTER_CHAOS':
        # target_id is burg_id
        amount = kwargs.get('amount', 1.0)
        c.execute("UPDATE burgs SET chaos_level = chaos_level + ? WHERE id = ?", (amount, target_id))
        result['message'] = f"Burg {target_id} chaos altered by {amount}"
        
    elif action_type == 'SPAWN_ENTITY':
        # DM injects a new entity into the world
        tile_id = kwargs.get('tile_id')
        x = kwargs.get('x', 50)
        y = kwargs.get('y', 50)
        entity_type = kwargs.get('entity_type', 'NPC')
        details = kwargs.get('details', {})
        
        c.execute('''
            INSERT INTO map_deltas (tile_id, local_x, local_y, change_type, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (tile_id, x, y, entity_type, json.dumps(details)))
        result['message'] = f"DM spawned {entity_type} at ({x}, {y}) in tile {tile_id}"
    elif action_type == 'TAKE_DAMAGE':
        amount = kwargs.get('amount', 0)
        c.execute("UPDATE player_characters SET health = health - ? WHERE id = ?", (amount, target_id))
        c.execute("SELECT health FROM player_characters WHERE id = ?", (target_id,))
        new_health = c.fetchone()[0]
        result['message'] = f"PC {target_id} took {amount} damage. Health is now {new_health}."
        if new_health <= 0:
            result['message'] += " PC has fallen!"
            
    elif action_type == 'LOOT_ITEM':
        item = kwargs.get('item', {})
        # Fallback if string is passed
        if isinstance(item, str):
            try:
                item = json.loads(item.replace("'", '"'))
            except Exception:
                item = {"name": item, "weight": 1}
                
        c.execute("SELECT inventory FROM player_characters WHERE id = ?", (target_id,))
        row = c.fetchone()
        inv = json.loads(row[0]) if row and row[0] else []
        inv.append(item)
        
        loadout = calculate_gear_tax(inv)
        
        c.execute("UPDATE player_characters SET inventory = ?, loadout = ? WHERE id = ?", (json.dumps(inv), loadout, target_id))
        result['message'] = f"PC {target_id} looted {item.get('name', 'Item')}. Current Loadout: {loadout}."
        
    elif action_type == 'USE_ITEM':
        item_name = kwargs.get('item_name')
        c.execute("SELECT inventory FROM player_characters WHERE id = ?", (target_id,))
        row = c.fetchone()
        inv = json.loads(row[0]) if row and row[0] else []
        
        item = next((i for i in inv if isinstance(i, dict) and i.get('name') == item_name), None)
        if item:
            inv.remove(item)
            if 'heal' in item:
                c.execute("UPDATE player_characters SET health = MIN(max_health, health + ?) WHERE id = ?", (item['heal'], target_id))
            
            loadout = calculate_gear_tax(inv)
            c.execute("UPDATE player_characters SET inventory = ?, loadout = ? WHERE id = ?", (json.dumps(inv), loadout, target_id))
            result['message'] = f"Used {item_name}. Effect applied. Loadout is now {loadout}."
        else:
            result = {"status": "error", "message": "Item not found in inventory."}
        
    elif action_type == 'TRANSACT':
        amount = kwargs.get('amount', 0)
        c.execute("UPDATE player_characters SET shards = shards + ? WHERE id = ?", (amount, target_id))
        c.execute("SELECT shards FROM player_characters WHERE id = ?", (target_id,))
        new_shards = c.fetchone()[0]
        result['message'] = f"PC {target_id} transacted {amount} shards. New balance: {new_shards}."
        
    elif action_type == 'GAIN_XP':
        amount = kwargs.get('amount', 0)
        c.execute("UPDATE player_characters SET xp = xp + ? WHERE id = ?", (amount, target_id))
        c.execute("SELECT xp FROM player_characters WHERE id = ?", (target_id,))
        new_xp = c.fetchone()[0]
        result['message'] = f"PC {target_id} gained {amount} XP. Total: {new_xp}."
        if new_xp >= 100:
            result['message'] += " Player is ready to LEVEL UP!"
            
    elif action_type == 'LEVEL_UP':
        stat_increase = kwargs.get('stat_increase', 'might').lower()
        new_skill = kwargs.get('new_skill', '')
        
        # We need to dynamically update the stat
        valid_stats = ['might', 'endurance', 'finesse', 'reflex', 'vitality', 'fortitude', 
                       'knowledge', 'logic', 'awareness', 'intuition', 'charm', 'willpower']
        
        if stat_increase in valid_stats:
            c.execute(f"UPDATE player_characters SET {stat_increase} = {stat_increase} + 1, level = level + 1, xp = xp - 100 WHERE id = ?", (target_id,))
        else:
            c.execute("UPDATE player_characters SET level = level + 1, xp = xp - 100 WHERE id = ?", (target_id,))
            
        c.execute("SELECT skills FROM player_characters WHERE id = ?", (target_id,))
        row = c.fetchone()
        skills = json.loads(row[0]) if row and row[0] else []
        if new_skill:
            skills.append(new_skill)
            c.execute("UPDATE player_characters SET skills = ? WHERE id = ?", (json.dumps(skills), target_id))
            
        result['message'] = f"PC {target_id} Leveled Up! Increased {stat_increase.capitalize()} and learned {new_skill}."
        
    elif action_type == 'SET_LOCATION':
        import math
        x = kwargs.get('x', 50)
        y = kwargs.get('y', 50)
        c.execute("SELECT local_x, local_y, reflex FROM player_characters WHERE id = ?", (target_id,))
        row = c.fetchone()
        if row:
            old_x, old_y, reflex = row
            max_dist = 5 + (reflex // 2)
            dist = math.dist((old_x, old_y), (x, y))
            if dist > max_dist:
                result['status'] = 'error'
                result['message'] = f"Target is {dist:.1f} tiles away. You can only move {max_dist} tiles per Beat."
            else:
                c.execute("UPDATE player_characters SET local_x = ?, local_y = ? WHERE id = ?", (x, y, target_id))
                result['message'] = f"PC {target_id} moved to ({x}, {y})."
        else:
            result['status'] = 'error'
            result['message'] = 'PC not found.'
            
    elif action_type == 'TICK_WORLD':
        import engine
        import ai_director
        engine.run_world_tick('okasha_world.db')
        
        # Trigger the AI Director after the mechanical simulation ticks
        # (Defaulting to player 1 for now)
        director_res = ai_director.pulse_scene(1, action_context="The simulation just advanced one beat based on the player's recent actions.", db_path='okasha_world.db')
        narrative = director_res.get('narrative', '')
        
        result['message'] = f"DM advanced the global clock. World simulated 1 interval.\n\nAI Director: {narrative}"
        
    else:
        result = {"status": "error", "message": "Unknown action type"}
        
    conn.commit()
    conn.close()
    return result
