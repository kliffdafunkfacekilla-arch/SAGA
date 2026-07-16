import sqlite3
import random
import json
import narrative_engine

DB_PATH = 'okasha_world.db'

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
    
    # Check if cluster exists by checking sector 13
    c.execute("SELECT id FROM map_sectors WHERE location_type = ? AND location_id = ? AND sector_index = 13", 
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
        INSERT INTO map_sectors (location_type, location_id, sector_index, base_biome, feature_archetype, seed)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sectors_to_insert)
    
    # 4. Generate Micro-Entities for the Blueprint
    c.execute("SELECT id, sector_index, feature_archetype FROM map_sectors WHERE location_type=? AND location_id=?", (location_type, location_id))
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
            INSERT INTO map_deltas (sector_id, local_x, local_y, change_type, details)
            VALUES (?, ?, ?, ?, ?)
        ''', deltas_to_insert)
    
    conn.commit()
    conn.close()
    return True

def query_local_state(location_type, location_id, sector_index=1):
    """
    Returns full state for the LLM to narrate:
    Hooks, Weather, Chaos, Paragons, Map Data
    """
    conn = get_db()
    c = conn.cursor()
    state = {}
    
    # 1. Base Stats and Map Seed
    if location_type == 'Burg':
        c.execute('''
            SELECT b.name, b.morale, b.chaos_level, b.current_weather, m.id, m.base_biome, m.feature_archetype, m.seed 
            FROM burgs b
            LEFT JOIN map_sectors m ON m.location_id = b.id AND m.location_type = 'Burg' AND m.sector_index = ?
            WHERE b.id = ?
        ''', (sector_index, location_id))
        row = c.fetchone()
        if row:
            state['name'] = row[0]
            state['morale'] = row[1]
            state['chaos'] = row[2]
            state['weather'] = row[3]
            state['sector_id'] = row[4]
            state['base_biome'] = row[5]
            state['feature_archetype'] = row[6]
            state['seed'] = row[7]
            state['sector_index'] = sector_index
            
            # Fetch Deltas
            if row[4]:
                c.execute("SELECT local_x, local_y, change_type, details FROM map_deltas WHERE sector_id = ?", (row[4],))
                state['deltas'] = [{'x': d[0], 'y': d[1], 'type': d[2], 'details': d[3]} for d in c.fetchall()]
            else:
                state['deltas'] = []
                
    elif location_type in ['Zone', 'Prison', 'Marker']:
        c.execute('''
            SELECT m.id, m.base_biome, m.feature_archetype, m.seed 
            FROM map_sectors m
            WHERE m.location_id = ? AND m.location_type = ? AND m.sector_index = ?
        ''', (location_id, location_type, sector_index))
        row = c.fetchone()
        if row:
            state['sector_id'] = row[0]
            state['base_biome'] = row[1]
            state['feature_archetype'] = row[2]
            state['seed'] = row[3]
            state['sector_index'] = sector_index
            state['deltas'] = [] # Need proper delta fetch for zones too if needed
            
    # 2. Paragons
    c.execute("SELECT id, name, role, trait_1, flaw_1, local_x, local_y FROM paragons WHERE location_id = ? AND sector_index = ?", (location_id, sector_index))
    state['paragons'] = [{'id': r[0], 'name': r[1], 'role': r[2], 'trait': r[3], 'flaw': r[4], 'x': r[5], 'y': r[6]} for r in c.fetchall()]
    
    # 3. Hooks
    c.execute("SELECT hook_category, description FROM story_hooks WHERE location_type = ? AND location_id = ?", (location_type, location_id))
    state['hooks'] = [{'category': r[0], 'description': r[1]} for r in c.fetchall()]
    
    conn.close()
    return state

def roll_dice(paragon_id, stat_name, difficulty):
    """
    Pulls a stat from a Paragon, rolls a d20 + modifier, compares to difficulty.
    """
    valid_stats = ['might', 'endurance', 'finesse', 'reflex', 'vitality', 'fortitude', 
                   'knowledge', 'logic', 'awareness', 'intuition', 'charm', 'willpower']
                   
    if stat_name.lower() not in valid_stats:
        return {"error": f"Invalid stat {stat_name}"}
        
    conn = get_db()
    c = conn.cursor()
    c.execute(f"SELECT name, {stat_name.lower()} FROM paragons WHERE id = ?", (paragon_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return {"error": "Paragon not found"}
        
    name, stat_val = row
    modifier = (stat_val - 10) // 2
    roll = random.randint(1, 20)
    total = roll + modifier
    
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
    result = {"status": "success", "action": action_type}
    
    if action_type == 'WALK':
        # kwargs should contain 'dx' and 'dy' (-1, 0, or 1)
        dx = kwargs.get('dx', 0)
        dy = kwargs.get('dy', 0)
        
        c.execute("SELECT location_id, sector_index, local_x, local_y FROM paragons WHERE id = ?", (actor_id,))
        row = c.fetchone()
        if not row: return {"status": "error", "message": "Paragon not found"}
        loc_id, sector, x, y = row
        
        nx, ny = x + dx, y + dy
        
        # Sector Transition Logic (Assuming a 5x5 cluster for sectors 1-25)
        if nx < 0:
            nx = 99
            if (sector - 1) % 5 == 0:
                result['message'] = "Player walked off the West edge of the Regional Hex! Entering new Hex..."
                # Here we would look up the adjacent Hex to the West, but for now we just wrap or stay.
                # loc_id = get_west_hex(loc_id)
                sector += 4 # Move to eastern edge of new hex
            else:
                sector -= 1
        elif nx > 99:
            nx = 0
            if sector % 5 == 0:
                result['message'] = "Player walked off the East edge of the Regional Hex! Entering new Hex..."
                sector -= 4
            else:
                sector += 1
                
        if ny < 0:
            ny = 99
            if sector <= 5:
                result['message'] = "Player walked off the North edge of the Regional Hex! Entering new Hex..."
                sector += 20
            else:
                sector -= 5
        elif ny > 99:
            ny = 0
            if sector > 20:
                result['message'] = "Player walked off the South edge of the Regional Hex! Entering new Hex..."
                sector -= 20
            else:
                sector += 5

        # Update position
        c.execute("UPDATE paragons SET location_id=?, sector_index=?, local_x=?, local_y=? WHERE id=?", 
                  (loc_id, sector, nx, ny, actor_id))
        result['message'] = result.get('message', f"Paragon walked to ({nx}, {ny}) in Sector {sector}")
        result['new_state'] = {"location_id": loc_id, "sector": sector, "x": nx, "y": ny}
        
    elif action_type == 'MOVE':
        # target_id is the new location_id
        c.execute("UPDATE paragons SET location_id = ? WHERE id = ?", (target_id, actor_id))
        result['message'] = f"Paragon {actor_id} moved to location {target_id}"
        
    elif action_type == 'ALTER_CHAOS':
        # target_id is burg_id
        amount = kwargs.get('amount', 1.0)
        c.execute("UPDATE burgs SET chaos_level = chaos_level + ? WHERE id = ?", (amount, target_id))
        result['message'] = f"Burg {target_id} chaos altered by {amount}"
        
    else:
        result = {"status": "error", "message": "Unknown action type"}
        
    conn.commit()
    conn.close()
    return result
