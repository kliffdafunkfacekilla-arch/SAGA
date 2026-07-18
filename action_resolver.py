import sqlite3
import random
import command_parser
import config

DB_PATH = config.ACTIVE_DB_PATH

# The Clash Matrix Body/Mind pairings
CLASH_MATRIX = {
    'PRESS': ('might', 'knowledge'),
    'HOLD': ('endurance', 'logic'),
    'MANEUVER': ('reflex', 'intuition'),
    'TRICK': ('finesse', 'awareness'),
    'FEINT': ('fortitude', 'willpower'),
    'DISENGAGE': ('vitality', 'charm')
}

def resolve_intent(player_id, intent_dict):
    """
    Takes a structured intent from the LLM Phase 1 and resolves it using strict BRUTAL mechanics.
    Returns a raw string describing the exact mathematical/system outcome.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    intent_type = intent_dict.get('type', 'GENERAL')
    
    # Fetch player stats
    c.execute("SELECT * FROM player_characters WHERE id = ?", (player_id,))
    row = c.fetchone()
    if not row:
        return "System Error: Player not found."
    
    outcome = ""
    
    if intent_type == 'COMBAT_TACTIC':
        tactic = intent_dict.get('tactic', 'PRESS').upper()
        target = intent_dict.get('target', 'Target')
        
        if tactic not in CLASH_MATRIX:
            tactic = 'PRESS'
            
        body_stat, mind_stat = CLASH_MATRIX[tactic]
        
        # Determine which stat to use based on physical vs mental context (default physical)
        stat_used = body_stat
        
        # Execute 3-Beat Pulse Economy
        current_stamina = row['stamina']
        if current_stamina >= 1:
            c.execute("UPDATE player_characters SET stamina = stamina - 1 WHERE id = ?", (player_id,))
            conn.commit()
            pulse_burn = "Burned 1 Stamina."
        else:
            conn.close()
            return f"Action failed: Zero-State. Not enough Stamina to execute a {tactic} beat."
            
        # Get actual stat value
        stat_val = row[stat_used] if row[stat_used] else 5
        
        # Parse Inventory for Weapon and Armor bonuses (Defaulting to 0 for now until full equipment system)
        weapon_bonus = 0
        enemy_stat = 5
        enemy_armor = 2 # Default enemy armor
        
        player_roll = random.randint(1, 20)
        enemy_roll = random.randint(1, 20)
        
        # attack roll is damage roll: dice+stat+weapon vs dice+stat+armor
        player_total = player_roll + stat_val + weapon_bonus
        enemy_total = enemy_roll + enemy_stat + enemy_armor
        
        outcome += f"Tactic: {tactic}. {pulse_burn} "
        
        if player_roll == enemy_roll: 
            # Exact dice tie triggers a clash! (Using player_roll == enemy_roll based on "exact d20 tie")
            current_focus = row['focus']
            if current_focus >= 1 and current_stamina >= 2: # Already burned 1 stamina
                c.execute("UPDATE player_characters SET stamina = stamina - 1, focus = focus - 1 WHERE id = ?", (player_id,))
                conn.commit()
                outcome += f"CLASH! Exact d20 tie (Both rolled {player_roll}). Both combatants enter deadlock and burn 1 additional Stamina and 1 Focus."
            else:
                outcome += f"CLASH! Exact d20 tie (Both rolled {player_roll}), but player lacks resources to sustain deadlock. Target gains advantage."
                
        elif player_total > enemy_total:
            # Player hits! Damage is the difference!
            final_damage = player_total - enemy_total
            
            # Trauma Pipeline
            trauma = ""
            if final_damage >= 11:
                trauma = "CRITICAL (Immediate Bleed/Trauma. Requires Stabilization)"
            elif final_damage >= 7:
                trauma = "MAJOR (Draw 1 card; add Bleed token)"
            elif final_damage >= 3:
                trauma = "MINOR (Disadvantage to target's next roll)"
            else:
                trauma = "Glancing Blow"
                
            outcome += f"Success! Player Attack ({player_roll}+{stat_val}+{weapon_bonus}={player_total}) beat Target Defense ({enemy_roll}+{enemy_stat}+{enemy_armor}={enemy_total}). Dealt {final_damage} damage. Trauma Threshold: {trauma}."
            
        else:
            # Player misses or defense is too great
            defense_margin = enemy_total - player_total
            outcome += f"Failure. Target Defense ({enemy_roll}+{enemy_stat}+{enemy_armor}={enemy_total}) deflected Player Attack ({player_roll}+{stat_val}+{weapon_bonus}={player_total}) by a margin of {defense_margin}."
            
    elif intent_type == 'BARTER':
        item = intent_dict.get('item', 'Supplies')
        action = intent_dict.get('action', 'buy')
        cost = int(intent_dict.get('cost', 5))
        shards = row['shards']
        
        if action == 'buy':
            if shards >= cost:
                command_parser.execute_action('TRANSACT', target_id=player_id, amount=-cost)
                command_parser.execute_action('LOOT_ITEM', target_id=player_id, item={'name': item, 'weight': 1})
                outcome = f"Successfully purchased {item} for {cost} shards. Shards deducted and item added to inventory."
            else:
                outcome = f"Failed to purchase {item}. Cost is {cost} shards, but player only has {shards}."
        else:
            command_parser.execute_action('TRANSACT', target_id=player_id, amount=cost)
            outcome = f"Successfully sold {item} for {cost} shards."
            
    elif intent_type == 'MOVE':
        destination = intent_dict.get('destination', 'Unknown')
        outcome = f"Player executed a Move Beat. Relocated to {destination}."
        
    elif intent_type == 'WAIT':
        command_parser.execute_action('TICK_WORLD')
        outcome = "Player waits. The global world simulation advanced by 1 beat."
        
    else:
        outcome = f"General action recognized: {intent_dict.get('description', 'Unknown interaction')}. No mechanical resolution required."
        
    conn.close()
    return outcome
