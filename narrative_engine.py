import sqlite3
import random
import re

def generate_micro_hook(entity_type, archetype, hex_hooks):
    """
    Breathes life into a localized entity by taking the overarching Hex Hooks 
    and generating a localized flavor hook for the specific building/NPC.
    """
    hook = ""
    # Look for famine
    is_famine = any('famine' in h.get('description', '').lower() for h in hex_hooks)
    is_crime = any('crime' in h.get('description', '').lower() for h in hex_hooks)
    
    if entity_type == 'NPC':
        if archetype == 'Farmland':
            if is_famine: hook = "Guarding a secret stash of untainted grain."
            else: hook = "Complaining about the recent tax hikes on wheat."
        elif archetype == 'City Core':
            if is_crime: hook = "Looking over their shoulder constantly."
            else: hook = "Heading to the market with a satchel of coins."
        elif archetype == 'Bandit Hideout':
            hook = "Cleaning a bloody blade, whispering about a recent caravan raid."
        elif archetype == 'Slums':
            if is_famine: hook = "Begging for scraps of Aether-bread."
            elif is_crime: hook = "Selling stolen goods from a makeshift stall."
            else: hook = "Coughing heavily due to the smog."
        else:
            hook = "Wandering aimlessly."
            
    elif entity_type == 'Building':
        if archetype == 'Farmland':
            if is_famine: hook = "The silo is barricaded and locked tight."
            else: hook = "A well-maintained barn smelling of fresh hay."
        elif archetype == 'City Core':
            if is_crime: hook = "Windows are boarded up after a recent break-in."
            else: hook = "A bustling tavern with a bright, welcoming sign."
        elif archetype == 'Bandit Hideout':
            hook = "A large canvas tent filled with plundered crates."
        elif archetype == 'Slums':
            hook = "A dilapidated wooden shack with a leaky roof."
        else:
            hook = "A simple structure."
            
    return hook

def generate_initial_hooks(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Clear old hooks
    try: cursor.execute('DELETE FROM story_hooks')
    except: pass
    try: cursor.execute('DELETE FROM lore_crosslinks')
    except: pass
    
    # 2. Get lore keywords
    cursor.execute('SELECT lore_id, subject, content FROM world_lore')
    lore_entries = cursor.fetchall()
    
    # We will build a simple keyword extractor.
    keywords = {}
    for lid, title, content in lore_entries:
        keywords[title.lower()] = lid
        # add simple keywords
        if 'Engineer' in title: keywords['engineer'] = lid
        if 'Dusk Husk' in title: keywords['dusk husk'] = lid
        if 'Worm' in title: keywords['worm cult'] = lid
        if 'Dragonstone' in title: keywords['dragonstone'] = lid
        if 'Convergence' in title: keywords['convergence'] = lid
        if 'Aether' in title: keywords['aetheric'] = lid
        
    # 3. Generate hooks for Burgs
    cursor.execute('SELECT id, name, morale, chaos_level, population FROM burgs')
    burgs = cursor.fetchall()
    
    for burg in burgs:
        b_id = burg[0]
        morale = burg[2]
        chaos = burg[3]
        
        hooks = []
        if chaos > 20:
            hooks.append(('Crime', f"High crime rate in {burg[1]}. Rumors of a hidden Worm Cult cell operation."))
        if morale < 40:
            hooks.append(('Famine', f"Famine is striking {burg[1]}. Citizens are desperate."))
        if morale > 80:
            hooks.append(('Festival', f"The Convergence Festival is being prepared in {burg[1]}!"))
            
        for h in hooks:
            cursor.execute('INSERT INTO story_hooks (location_type, location_id, hook_category, description) VALUES (?, ?, ?, ?)',
                           ('Burg', b_id, h[0], h[1]))
            hook_id = cursor.lastrowid
            
            # Crosslink
            for kw, l_id in keywords.items():
                if re.search(r'\b' + kw + r'\b', h[1].lower()):
                    cursor.execute('INSERT INTO lore_crosslinks (hook_id, lore_id) VALUES (?, ?)', (hook_id, l_id))
    
    conn.commit()
    conn.close()
