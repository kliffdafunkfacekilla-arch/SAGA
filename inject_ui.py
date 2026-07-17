import re

with open(r'C:\Users\krazy\Desktop\SAGA\templates\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# The UI we want to inject into the sidebar
ttrpg_ui = """
        <!-- TTRPG UI Injected Here -->
        <hr style="border-color: #555;">
        <h5 style="color: #d4af37;">Character Status</h5>
        <div style="background: #111; padding: 10px; border: 1px solid #444; font-size: 13px; color: #ccc; margin-bottom: 10px;">
            <div><b>Shards:</b> <span id="charShards" style="color: #00ffcc;">0</span> | <b>Loadout:</b> <span id="charLoadout" style="color: #ff4d4d;">Light</span></div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <span><b>HP:</b> <span id="charHP">0</span></span>
                <span><b>STA:</b> <span id="charSTA">0</span></span>
                <span><b>FOC:</b> <span id="charFOC">0</span></span>
            </div>
        </div>

        <h5 style="color: #d4af37;">Terminal</h5>
        <div id="chatOutput" style="background-color: #000; color: #0f0; font-family: monospace; height: 150px; overflow-y: scroll; padding: 10px; border: 1px solid #333; margin-bottom: 5px; font-size: 12px;">
            <div style="color: #d4af37; font-style: italic;">System Initialized. Awaiting input.</div>
        </div>
        <div style="display: flex; margin-bottom: 10px;">
            <input type="text" id="chatInput" style="flex-grow: 1; background: #222; color: #fff; border: 1px solid #444; padding: 5px;" placeholder="I attack the guard...">
            <button onclick="sendChat()" style="background: #d4af37; color: #000; border: none; padding: 5px 10px; font-weight: bold;">Submit</button>
        </div>
        
        <div style="display: flex; gap: 5px;">
            <button onclick="visualAction('COMBAT_TACTIC', 'PRESS')" style="flex: 1; background: #5a0000; color: #fff; border: 1px solid #ff4d4d; padding: 5px; font-size: 11px;">⚔️ Press</button>
            <button onclick="visualAction('COMBAT_TACTIC', 'FEINT')" style="flex: 1; background: #5a0000; color: #fff; border: 1px solid #ff4d4d; padding: 5px; font-size: 11px;">⚔️ Feint</button>
            <button onclick="visualAction('WAIT', 'WAIT')" style="flex: 1; background: #004d40; color: #fff; border: 1px solid #00ffcc; padding: 5px; font-size: 11px;">⏳ Wait</button>
        </div>
"""

# The JS we want to inject
ttrpg_js = """
    // TTRPG JS
    async function sendChat(messageOverride=null) {
        const input = document.getElementById('chatInput');
        const msg = messageOverride || input.value;
        if(!msg) return;
        
        const out = document.getElementById('chatOutput');
        out.innerHTML += `<div style="color: white; font-weight: bold;">> ${msg}</div>`;
        input.value = '';
        out.scrollTop = out.scrollHeight;
        
        const fd = new FormData();
        fd.append('message', msg);
        fd.append('player_id', 1);
        
        try {
            const res = await fetch('/api/ttrpg/chat', { method: 'POST', body: fd });
            const data = await res.json();
            
            let appendHtml = `<div style="margin-top: 5px; margin-bottom: 10px;">`;
            if(data.execution_results && data.execution_results.length > 0) {
                data.execution_results.forEach(r => {
                    appendHtml += `<div style="color: #00ffcc;">[SYS] ${r.message || r.status}</div>`;
                });
            }
            appendHtml += `<div style="color: #d4af37; font-style: italic;">${data.response}</div></div>`;
            out.innerHTML += appendHtml;
            out.scrollTop = out.scrollHeight;
            refreshCharData();
        } catch(e) {
            out.innerHTML += `<div style="color: red;">Error: ${e}</div>`;
        }
    }
    
    function visualAction(intentType, tactic) {
        let msg = "";
        if(intentType === 'COMBAT_TACTIC') msg = `I use the ${tactic} combat tactic against the enemy.`;
        if(intentType === 'WAIT') msg = `I wait and pass the time.`;
        sendChat(msg);
    }
    
    async function refreshCharData() {
        try {
            const res = await fetch('/api/ttrpg/get_character?id=1');
            const data = await res.json();
            if(data.status === 'success') {
                document.getElementById('charShards').innerText = data.shards;
                document.getElementById('charLoadout').innerText = data.loadout;
                document.getElementById('charHP').innerText = data.health;
                document.getElementById('charSTA').innerText = data.stamina;
                document.getElementById('charFOC').innerText = data.focus;
            }
        } catch(e) {}
    }
    
    document.addEventListener("DOMContentLoaded", function() {
        const ci = document.getElementById('chatInput');
        if (ci) {
            ci.addEventListener('keypress', function (e) {
                if (e.key === 'Enter') sendChat();
            });
        }
        refreshCharData();
    });
"""

if "TTRPG UI Injected Here" not in html:
    # Inject UI right after narrativeContent
    html = html.replace('<div id="narrativeContent" style="color: #eee; font-size: 15px; line-height: 1.6;">\n            Click a map marker to see local story hooks and crosslinked lore.\n        </div>', 
                        '<div id="narrativeContent" style="color: #eee; font-size: 15px; line-height: 1.6; margin-bottom: 15px;">\n            Click a map marker to see local story hooks and crosslinked lore.\n        </div>\n' + ttrpg_ui)
    
    # Inject JS right before </body>
    html = html.replace('</body>', ttrpg_js + '\n</body>')

with open(r'C:\Users\krazy\Desktop\SAGA\templates\index.html', 'w', encoding='utf-8') as f:
    f.write(html)
