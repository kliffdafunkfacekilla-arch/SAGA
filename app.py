from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import subprocess
import command_parser
import llm_gm
import engine
import ai_director
import narrative_engine

app = Flask(__name__)
CORS(app)
DB_PATH = 'okasha_world.db'

def query_db(query, args=(), one=False):
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    if not os.path.exists(DB_PATH):
        return jsonify({"error": "Database not found."}), 404
        
    stats_data = {}
    
    # Tick
    try:
        with open('current_tick.txt', 'r') as f:
            stats_data['tick'] = int(f.read().strip())
    except:
        stats_data['tick'] = 0
        
    # Global Morale & Chaos
    burg_stats = query_db("SELECT AVG(morale) as avg_morale, SUM(chaos_level) as total_chaos FROM burgs", one=True)
    if burg_stats:
        stats_data['avg_morale'] = round(burg_stats['avg_morale'] or 0.0, 1)
        stats_data['total_chaos'] = round(burg_stats['total_chaos'] or 0.0, 1)
        
    # Prisons
    prisons = query_db("SELECT name, containment_strength FROM world_prisons")
    stats_data['prisons'] = [{"name": p["name"], "strength": round(p["containment_strength"], 1)} for p in prisons] if prisons else []
    
    # Shadows
    shadows = query_db("SELECT name, type, treasury FROM shadow_factions WHERE type IN ('Guild', 'Cartel')")
    stats_data['shadows'] = [{"name": s["name"], "type": s["type"], "treasury": round(s["treasury"], 1)} for s in shadows] if shadows else []
    
    # Map Data: Burgs
    burgs = query_db("SELECT id, name, morale, chaos_level, lat, lon, current_weather FROM burgs")
    stats_data['map_burgs'] = [dict(b) for b in burgs] if burgs else []
    
    # Map Data: Zones
    zones = query_db("SELECT id, name, type, lat, lon FROM zones")
    stats_data['map_zones'] = [dict(z) for z in zones] if zones else []
    
    # Map Data: Markers
    markers = query_db("SELECT id, name, icon, lat, lon FROM markers")
    stats_data['map_markers'] = [dict(m) for m in markers] if markers else []
    
    # Map Data: Prisons (Join with burgs to get coords since cell_id is burg_id)
    map_prisons = query_db('''
        SELECT p.prison_id as id, p.name, p.containment_strength, b.lat, b.lon 
        FROM world_prisons p
        JOIN burgs b ON p.cell_id = b.id
    ''')
    stats_data['map_prisons'] = [dict(p) for p in map_prisons] if map_prisons else []
    
    return jsonify(stats_data)

@app.route('/api/hooks/<location_type>/<int:location_id>')
def get_hooks(location_type, location_id):
    # Fetch story hooks
    hooks = query_db('''
        SELECT id, hook_category, description, status 
        FROM story_hooks 
        WHERE location_type = ? AND location_id = ?
    ''', [location_type, location_id])
    
    if not hooks:
        return jsonify([])
        
    result = []
    for h in hooks:
        hook_dict = dict(h)
        # Fetch crosslinked lore
        lore = query_db('''
            SELECT l.lore_id, l.subject, l.content 
            FROM world_lore l
            JOIN lore_crosslinks c ON c.lore_id = l.lore_id
            WHERE c.hook_id = ?
        ''', [h['id']])
        hook_dict['lore'] = [dict(l) for l in lore] if lore else []
        result.append(hook_dict)
        
    return jsonify(result)

# --- TTRPG API ---
@app.route('/api/ttrpg/query', methods=['GET'])
def ttrpg_query():
    loc_type = request.args.get('location_type', 'Burg')
    loc_id = request.args.get('location_id', 1, type=int)
    cluster_idx = request.args.get('cluster_id', 13, type=int)
    
    # Generate map dynamically if it doesn't exist
    command_parser.generate_local_map(loc_type, loc_id, cluster_idx)
    
    # Get state
    state = command_parser.query_local_state(loc_type, loc_id, cluster_idx)
    return jsonify(state)

@app.route('/api/ttrpg/create_character', methods=['POST'])
def ttrpg_create_character():
    data = request.json
    name = data.get('name', 'Unknown')
    origin = data.get('origin', 'Core-born')
    char_class = data.get('class', 'Wanderer')
    
    result = command_parser.create_character(name, origin, char_class)
    return jsonify(result)

@app.route('/api/ttrpg/roll', methods=['POST'])
def ttrpg_roll():
    data = request.json
    paragon_id = data.get('paragon_id')
    stat = data.get('stat', 'might')
    difficulty = data.get('difficulty', 10)
    
    result = command_parser.roll_dice(paragon_id, stat, difficulty)
    return jsonify(result)

@app.route('/api/ttrpg/action', methods=['POST'])
def ttrpg_action():
    data = request.json
    actor_id = data.get('actor_id')
    action_type = data.get('action_type')
    target_id = data.get('target_id')
    kwargs = data.get('kwargs', {})
    
    result = command_parser.execute_action(actor_id, action_type, target_id, **kwargs)
    return jsonify(result)

@app.route('/static/geojson/<path:filename>')
def serve_geojson(filename):
    # Serve GeoJSON from the data directory
    return send_from_directory('data', filename)

@app.route('/api/db_query', methods=['POST'])
def db_query():
    query = request.form.get('query', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        if query.strip().upper().startswith('SELECT'):
            rows = cur.fetchall()
            conn.close()
            return jsonify({"results": [dict(r) for r in rows]})
        else:
            conn.commit()
            conn.close()
            return jsonify({"message": "Query executed successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/run_tick', methods=['POST'])
def run_tick():
    famine_faction = request.form.get('famine_faction', '')
    
    cmd = ['python', 'engine.py']
    if famine_faction:
        cmd.append(famine_faction)
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return jsonify({"status": "success", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "output": e.stdout + "\n" + e.stderr}), 500

@app.route('/api/ttrpg/chat', methods=['POST'])
def ttrpg_chat():
    data = request.json
    player_id = data.get('player_id', 1)
    message = data.get('message', '')
    
    # LLM acts purely as an intent parser; state validation happens in the rules engine.
    state = {}
    
    result = llm_gm.chat_with_gm(player_id, message, state)
    return jsonify(result)

@app.route('/api/ttrpg/director_pulse', methods=['POST'])
def director_pulse():
    data = request.json
    player_id = data.get('player_id', 1)
    
    result = ai_director.pulse_scene(player_id, DB_PATH)
    return jsonify(result)

@app.route('/api/ttrpg/tick', methods=['POST'])
def ttrpg_tick():
    engine.run_world_tick(DB_PATH)
    return jsonify({"status": "success", "message": "World Engine ticked forward 1 interval."})

if __name__ == '__main__':
    # Ensure templates dir exists
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, port=5000)
