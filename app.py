from flask import Flask, render_template, jsonify, request
import sqlite3
import os
import subprocess

app = Flask(__name__)
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
    burgs = query_db("SELECT name, morale, chaos_level, x_coord, y_coord, current_weather FROM burgs")
    stats_data['map_burgs'] = [dict(b) for b in burgs] if burgs else []
    
    # Map Data: Zones
    zones = query_db("SELECT name, type, x_coord, y_coord FROM zones WHERE x_coord != 0 AND y_coord != 0")
    stats_data['map_zones'] = [dict(z) for z in zones] if zones else []
    
    # Map Data: Markers
    markers = query_db("SELECT name, icon, x_coord, y_coord FROM markers")
    stats_data['map_markers'] = [dict(m) for m in markers] if markers else []
    
    # Map Data: Prisons (Join with burgs to get coords since cell_id is burg_id)
    map_prisons = query_db('''
        SELECT p.name, p.containment_strength, b.x_coord, b.y_coord 
        FROM world_prisons p
        JOIN burgs b ON p.cell_id = b.id
    ''')
    stats_data['map_prisons'] = [dict(p) for p in map_prisons] if map_prisons else []
    
    return jsonify(stats_data)

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

if __name__ == '__main__':
    # Ensure templates dir exists
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, port=5000)
