"""
ai_director.py

This module contains the AI Director for the SAGA Engine.
The Director acts as an intelligent, asynchronous actor that synthesizes 
the global environment, active hooks, and player state to inject physical 
entities, hazards, and storylines directly into the world via the command parser.
"""
import sqlite3
import json
import re
import urllib.request
import urllib.error
import command_parser
from llm_gm import parse_llm_commands, OLLAMA_URL, OLLAMA_MODEL

DIRECTOR_PROMPT = """
You are the AI Story Director for the B.R.U.T.A.L. Engine.
Your job is to synthesize the global timeline, local hex conditions, and active story hooks to create interesting, fun storylines that react to the player's actions.

CRITICAL INSTRUCTIONS:
- Do NOT generate entities on every pulse. Only spawn entities when it makes narrative sense or to introduce a challenge.
- Allow the player to follow whatever story thread they are interested in. Be an adaptable sandbox.
- Output [EXECUTE: SPAWN_ENTITY] ONLY when a physical entity (NPC, trap, loot) must be injected into the player's immediate path.

Supported Commands:
- [EXECUTE: SPAWN_ENTITY, tile_id: <id>, x: <int>, y: <int>, entity_type: <string>, details: <json_string>]
- [EXECUTE: ALTER_CHAOS, target_id: <burg_id>, amount: <int>]

Example Output:
The air grows cold. A cartel enforcer steps out from the shadowed alley, clutching a rust-pitted shotgun.
[EXECUTE: SPAWN_ENTITY, tile_id: 1, x: 55, y: 50, entity_type: 'NPC', details: '{"name": "Cartel Enforcer", "hook": "Looking to collect a debt"}']
"""

def pulse_scene(player_id, action_context="", db_path='okasha_world.db'):
    """
    Synthesizes the local environment and triggers an AI Director event.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Get Player Location
    c.execute("SELECT location_id, cluster_id, local_x, local_y FROM player_characters WHERE id = ?", (player_id,))
    p_row = c.fetchone()
    if not p_row:
        conn.close()
        return {"status": "error", "message": "Player not found."}
        
    burg_id, cluster_id, px, py = p_row
    
    # 2. Get Burg / Hex Data
    c.execute("SELECT name, population, morale, chaos_level FROM burgs WHERE id = ?", (burg_id,))
    b_row = c.fetchone()
    burg_info = {"id": burg_id}
    if b_row:
        burg_info = {"id": burg_id, "name": b_row[0], "population": b_row[1], "morale": b_row[2], "chaos_level": b_row[3]}
        
    # 3. Get Active Story Hooks
    c.execute("SELECT hook_category, description FROM story_hooks WHERE status = 'active' OR status = 'emerging' LIMIT 3")
    hooks = [{"title": r[0], "description": r[1]} for r in c.fetchall()]
    
    conn.close()
    
    # 4. Construct Director State
    state = {
        "recent_player_action": action_context,
        "player_location": f"Burg ID: {burg_id}, Cluster: {cluster_id}, Coordinates: ({px}, {py})",
        "local_conditions": burg_info,
        "active_global_hooks": hooks
    }
    
    state_str = json.dumps(state, indent=2)
    full_prompt = f"{DIRECTOR_PROMPT}\n\nCURRENT WORLD STATE:\n{state_str}\n\nDIRECTOR, generate the next scene and inject entities into the world:"
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False
    }
    
    response_text = ""
    try:
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode('utf-8'))
            response_text = result.get('response', '')
            
    except (urllib.error.URLError, TimeoutError) as e:
        # Graceful Fallback if Ollama is offline
        print(f"Ollama Connection Error: {e}. Falling back to mock Director logic.")
        response_text = f"The shadows shift. An anomaly spawns nearby. [EXECUTE: SPAWN_ENTITY, tile_id: {cluster_id}, x: {px+2}, y: {py+2}, entity_type: 'Anomaly', details: '{{\"name\": \"Glitch\", \"hook\": \"Vibrating intensely\"}}']"
            
    # Parse the commands using Regex from llm_gm
    cleaned_response, commands = parse_llm_commands(response_text)
    
    # Execute the commands
    execution_results = []
    for cmd in commands:
        try:
            # Override tile_id dynamically if missing or default to the player's cluster
            if 'tile_id' not in cmd:
                cmd['tile_id'] = cluster_id
            action_type = cmd.pop('type')
            res = command_parser.execute_action(player_id, action_type, **cmd)
            execution_results.append(res)
        except Exception as e:
            execution_results.append({"status": "error", "message": f"Failed to execute {action_type}: {str(e)}"})
        
    return {
        "narrative": cleaned_response,
        "execution_results": execution_results
    }
