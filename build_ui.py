html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B.R.U.T.A.L. Engine Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
        .card { background-color: #1e1e1e; border: 1px solid #444; margin-bottom: 20px; }
        .card-header { background-color: #2c2c2c; border-bottom: 1px solid #555; font-weight: bold; color: #fff; }
        .text-neon { color: #00ffcc; }
        #chatOutput { background-color: #0d0d0d; color: #b3b3b3; font-family: monospace; height: 300px; overflow-y: auto; padding: 10px; border: 1px solid #333; }
        .llm-narrative { color: #d4af37; font-style: italic; }
        .system-math { color: #00ffcc; font-size: 0.9em; }
        .player-msg { color: #ffffff; font-weight: bold; }
        #mapContainer { height: 400px; width: 100%; background-color: #000; border: 1px solid #444; }
    </style>
</head>
<body>
<div class="container-fluid mt-3">
    <h2 class="mb-3 text-center" style="font-family: Georgia, serif; color: #d4af37;">B.R.U.T.A.L. Engine</h2>
    <div class="row">
        
        <!-- Left: Map & Chat -->
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">World Map (Click to Move/Target)</div>
                <div class="card-body p-0"><div id="mapContainer"></div></div>
            </div>
            
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span>Terminal / Facilitator Log</span>
                    <span id="loadingSpinner" style="display:none;" class="spinner-border spinner-border-sm text-warning" role="status"></span>
                </div>
                <div class="card-body p-0">
                    <div id="chatOutput">
                        <div class="llm-narrative">System Initialized. The Drift awaits.</div>
                    </div>
                    <div class="p-2 bg-dark border-top border-secondary d-flex">
                        <input type="text" id="chatInput" class="form-control bg-dark text-light border-secondary" placeholder="State your intent... (e.g. 'I attack the bandit')">
                        <button class="btn btn-warning ms-2" onclick="sendChat()">Send</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right: Character Sheet & Actions -->
        <div class="col-md-4">
            <div class="card border-warning">
                <div class="card-header bg-warning text-dark">Character Sheet</div>
                <div class="card-body" style="font-size: 14px;">
                    <h4 id="charName" class="text-warning">Loading...</h4>
                    <p class="mb-1 text-secondary"><span id="charOrigin">Origin</span> | Lvl <span id="charLevel">1</span> (<span id="charXP">0</span> XP)</p>
                    <p class="mb-3">Shards: <span id="charShards" class="text-neon">0</span> | Loadout: <span id="charLoadout" class="text-danger">Light</span></p>
                    
                    <div class="row text-center mb-3">
                        <div class="col"><b>HP</b><br><span id="charHP" class="fs-5">0</span></div>
                        <div class="col"><b>STA</b><br><span id="charSTA" class="fs-5">0</span></div>
                        <div class="col"><b>FOC</b><br><span id="charFOC" class="fs-5">0</span></div>
                    </div>
                    
                    <h6 class="border-bottom border-secondary pb-1">Stats</h6>
                    <div class="row mb-3">
                        <div class="col-6">MIG: <span id="statMIG">0</span></div>
                        <div class="col-6">KNO: <span id="statKNO">0</span></div>
                        <div class="col-6">FIN: <span id="statFIN">0</span></div>
                        <div class="col-6">AWA: <span id="statAWA">0</span></div>
                        <div class="col-6">REF: <span id="statREF">0</span></div>
                        <div class="col-6">INT: <span id="statINT">0</span></div>
                        <div class="col-6">END: <span id="statEND">0</span></div>
                        <div class="col-6">LOG: <span id="statLOG">0</span></div>
                        <div class="col-6">FOR: <span id="statFOR">0</span></div>
                        <div class="col-6">CHA: <span id="statCHA">0</span></div>
                        <div class="col-6">VIT: <span id="statVIT">0</span></div>
                        <div class="col-6">WIL: <span id="statWIL">0</span></div>
                    </div>
                    
                    <h6 class="border-bottom border-secondary pb-1">Inventory & Skills</h6>
                    <p class="mb-1"><b>Inv:</b> <span id="charInv">None</span></p>
                    <p class="mb-3"><b>Skills:</b> <span id="charSkills">None</span></p>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">Visual Actions</div>
                <div class="card-body">
                    <button class="btn btn-outline-danger w-100 mb-2" onclick="visualAction('COMBAT_TACTIC', 'PRESS')">⚔️ Press (Might/Kno) [-1 STA]</button>
                    <button class="btn btn-outline-danger w-100 mb-2" onclick="visualAction('COMBAT_TACTIC', 'FEINT')">⚔️ Feint (For/Wil) [-1 STA]</button>
                    <button class="btn btn-outline-info w-100 mb-2" onclick="visualAction('WAIT', 'WAIT')">⏳ Wait / Tick World</button>
                    <button class="btn btn-outline-secondary w-100" onclick="refreshData()">🔄 Refresh Sheet</button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    async function refreshData() {
        // Refresh Character
        try {
            const res = await fetch('/api/ttrpg/get_character?id=1');
            const data = await res.json();
            if(data.status === 'success') {
                document.getElementById('charName').innerText = data.name;
                document.getElementById('charOrigin').innerText = data.origin;
                document.getElementById('charLevel').innerText = data.level;
                document.getElementById('charXP').innerText = data.xp;
                document.getElementById('charShards').innerText = data.shards;
                document.getElementById('charLoadout').innerText = data.loadout;
                document.getElementById('charHP').innerText = data.health;
                document.getElementById('charSTA').innerText = data.stamina;
                document.getElementById('charFOC').innerText = data.focus;
                
                document.getElementById('statMIG').innerText = data.stats.might;
                document.getElementById('statFIN').innerText = data.stats.finesse;
                document.getElementById('statREF').innerText = data.stats.reflex;
                document.getElementById('statEND').innerText = data.stats.endurance;
                document.getElementById('statFOR').innerText = data.stats.fortitude;
                document.getElementById('statVIT').innerText = data.stats.vitality;
                document.getElementById('statKNO').innerText = data.stats.knowledge;
                document.getElementById('statAWA').innerText = data.stats.awareness;
                document.getElementById('statINT').innerText = data.stats.intuition;
                document.getElementById('statLOG').innerText = data.stats.logic;
                document.getElementById('statCHA').innerText = data.stats.charm;
                document.getElementById('statWIL').innerText = data.stats.willpower;
                
                let inv = data.inventory;
                try { inv = JSON.parse(inv); } catch(e){}
                document.getElementById('charInv').innerText = Array.isArray(inv) ? inv.map(i => i.name || i).join(', ') : 'None';
                
                let skills = data.skills;
                try { skills = JSON.parse(skills); } catch(e){}
                document.getElementById('charSkills').innerText = Array.isArray(skills) ? skills.join(', ') : 'None';
            }
        } catch(e) { console.error("Sheet error", e); }
        
        // Refresh Map
        try {
            const res = await fetch('/api/stats');
            const mapData = await res.json();
            renderMap(mapData.prisons); // Quick hack to show something on map
        } catch(e) {}
    }
    
    function renderMap(prisons) {
        if(!prisons) return;
        var trace = {
            x: prisons.map((p, i) => i*10),
            y: prisons.map((p, i) => i*10),
            mode: 'markers',
            marker: { size: 15, color: 'purple' },
            text: prisons.map(p => p.name),
            hoverinfo: 'text'
        };
        var layout = { plot_bgcolor: '#000', paper_bgcolor: '#000', margin: { t: 0, b: 0, l: 0, r: 0 }, xaxis:{visible:false}, yaxis:{visible:false} };
        Plotly.newPlot('mapContainer', [trace], layout, {displayModeBar: false});
    }

    async function sendChat(messageOverride=null) {
        const input = document.getElementById('chatInput');
        const msg = messageOverride || input.value;
        if(!msg) return;
        
        const out = document.getElementById('chatOutput');
        out.innerHTML += `<div class="player-msg">> ${msg}</div>`;
        input.value = '';
        out.scrollTop = out.scrollHeight;
        
        document.getElementById('loadingSpinner').style.display = 'block';
        
        const fd = new FormData();
        fd.append('message', msg);
        fd.append('player_id', 1);
        
        try {
            const res = await fetch('/api/ttrpg/chat', { method: 'POST', body: fd });
            const data = await res.json();
            
            // Format response
            let html = `<div class="mt-2 mb-3">`;
            if(data.execution_results && data.execution_results.length > 0) {
                data.execution_results.forEach(r => {
                    html += `<div class="system-math">[SYS] ${r.message || r.status}</div>`;
                });
            }
            html += `<div class="llm-narrative">${data.response}</div></div>`;
            out.innerHTML += html;
            out.scrollTop = out.scrollHeight;
            refreshData();
        } catch(e) {
            out.innerHTML += `<div class="text-danger">Error: ${e}</div>`;
        }
        document.getElementById('loadingSpinner').style.display = 'none';
    }
    
    function visualAction(intentType, tactic) {
        // Build a simulated chat message that the LLM Phase 1 will parse easily
        let msg = "";
        if(intentType === 'COMBAT_TACTIC') msg = `I use the ${tactic} combat tactic against the enemy.`;
        if(intentType === 'WAIT') msg = `I wait and pass the time.`;
        sendChat(msg);
    }

    // Init
    refreshData();
    document.getElementById('chatInput').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') sendChat();
    });
</script>
</body>
</html>"""

with open(r'C:\Users\krazy\Desktop\SAGA\templates\index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("UI Rebuilt")
