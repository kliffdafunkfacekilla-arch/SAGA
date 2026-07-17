import re
import json
import urllib.request
import urllib.error
import command_parser

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3" # Default model, can be changed to mistral, etc.

BRUTAL_PROMPT = """
You are the B.R.U.T.A.L. Engine AI Facilitator.
Your primary function is to manage the mechanical architecture of the B.R.U.T.A.L. Engine while maintaining the grim, high-stakes atmosphere of the "Desperate Negotiation." 
Enforce Ludonarrative Grounding: All entities are "Biological Chassis." Statistics are "Source Code." Narrate outcomes as physiological failures or architectural glitches within the Drift.

The 3-Beat Pulse Action Economy:
- Move Beat (None)
- Stamina Action (Burn 1 Stamina)
- Focus Action (Burn 1 Focus)

When resolving actions, you MUST strictly enforce the rules and execute backend commands inside brackets.
Supported Backend Commands:
- [EXECUTE: TAKE_DAMAGE, target_id: <id>, amount: <int>]
- [EXECUTE: LOOT_ITEM, target_id: <id>, item: <json_string_with_name_and_weight>]
- [EXECUTE: GAIN_XP, target_id: <id>, amount: <int>]
- [EXECUTE: LEVEL_UP, target_id: <id>, stat_increase: <string>, new_skill: <string>]
- [EXECUTE: TRANSACT, target_id: <id>, amount: <int>]  # Use negative to buy, positive to sell/loot shards
- [EXECUTE: SPAWN_ENTITY, sector_id: <id>, x: <int>, y: <int>, entity_type: <string>, details: <json_string>]
- [EXECUTE: TICK_WORLD]

Respond with immersive narrative text, telegraph danger clearly, and append any [EXECUTE] tags at the end of your response to push changes to the Engine. Do not explain your commands, just output them in brackets.
"""

def parse_llm_commands(response_text):
    """
    Scans the raw LLM output for [EXECUTE: ...] blocks, parses them, 
    and returns a list of command dictionaries and the cleaned narrative text.
    """
    commands = []
    # Regex to find [EXECUTE: CMD_NAME, key: val, key: val]
    pattern = r'\[EXECUTE:\s*([A-Z_]+)(?:,\s*(.*?))?\]'
    matches = re.finditer(pattern, response_text)
    
    for match in matches:
        cmd_type = match.group(1)
        cmd_args_str = match.group(2)
        cmd_dict = {"type": cmd_type}
        
        if cmd_args_str:
            # Simple split by comma, then split by colon
            parts = cmd_args_str.split(',')
            for part in parts:
                if ':' in part:
                    k, v = part.split(':', 1)
                    k = k.strip()
                    v = v.strip()
                    # Type conversion attempts
                    if v.isdigit():
                        v = int(v)
                    elif v.startswith("'") and v.endswith("'"):
                        v = v[1:-1]
                    elif v.startswith('"') and v.endswith('"'):
                        v = v[1:-1]
                    # Note: We aren't doing deep JSON parsing for 'details' here yet, keeping it as string 
                    # unless it specifically requires dict conversion. command_parser expects dict for details.
                    if k == 'details' and isinstance(v, str) and (v.startswith('{') and v.endswith('}')):
                        try:
                            v = json.loads(v.replace("'", '"'))
                        except json.JSONDecodeError:
                            pass
                            
                    cmd_dict[k] = v
                    
        commands.append(cmd_dict)
        
    # Clean the narrative text by stripping out the execute blocks
    cleaned_text = re.sub(pattern, '', response_text).strip()
    return cleaned_text, commands

def chat_with_gm(player_id, message, state):
    """
    Sends the player message to the local Ollama LLM to extract intent.
    If Ollama is down, falls back to a mock response.
    """
    # Construct the full prompt
    full_prompt = f"{BRUTAL_PROMPT}\n\nPLAYER ACTION:\n{message}\n\nFACILITATOR RESPONSE:"
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False
    }
    
    response_text = ""
    try:
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            response_text = result.get('response', '')
            
    except (urllib.error.URLError, TimeoutError) as e:
        # Graceful Fallback if Ollama is offline
        print(f"Ollama Connection Error: {e}. Falling back to mock logic.")
        msg_lower = message.lower()
        if "attack" in msg_lower or "press" in msg_lower:
            response_text = "The biological chassis strains under the kinetic impact. Blood spatters. [EXECUTE: TAKE_DAMAGE, target_id: " + str(player_id) + ", amount: 2]"
        elif "tick" in msg_lower or "wait" in msg_lower:
            response_text = "Time passes. The global clock ticks forward. [EXECUTE: TICK_WORLD]"
        else:
            response_text = "[OLLAMA OFFLINE] The environment pulses with tension. Unseen source code rewrites the shadows around you. What is your next Beat?"
            
    # Parse the commands using Regex
    cleaned_response, commands = parse_llm_commands(response_text)
    
    # Execute the commands
    execution_results = []
    for cmd in commands:
        try:
            res = command_parser.execute_action(cmd['type'], **cmd)
            execution_results.append(res)
        except Exception as e:
            execution_results.append({"status": "error", "message": f"Failed to execute {cmd['type']}: {str(e)}"})
        
    return {
        "response": cleaned_response,
        "execution_results": execution_results
    }
