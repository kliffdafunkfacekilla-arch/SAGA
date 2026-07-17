import sys
import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the Character Sheet HTML
old_sheet = '''    <!-- Persistent Character Sheet -->
    <div id="charSheet" style="position: fixed; top: 20px; left: 20px; background: rgba(30,30,30,0.9); padding: 15px; border: 1px solid #555; border-radius: 5px; color: white; display: none; z-index: 9999; box-shadow: 2px 2px 10px rgba(0,0,0,0.5); width: 250px;">
        <h3 id="sheetName" style="margin: 0 0 5px 0;">Name</h3>
        <p style="margin: 0 0 10px 0; font-size: 12px; color: #aaa;"><span id="sheetOrigin">Origin</span> | <span id="sheetLoadout">Loadout</span></p>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <div><b>HP:</b> <span id="sheetHP">20</span></div>
            <div><b>STA:</b> <span id="sheetSTA">10</span></div>
            <div><b>FOC:</b> <span id="sheetFOC">10</span></div>
        </div>'''

new_sheet = '''    <!-- Persistent Character Sheet -->
    <div id="charSheet" style="position: fixed; top: 20px; left: 20px; background: rgba(30,30,30,0.9); padding: 15px; border: 1px solid #555; border-radius: 5px; color: white; display: none; z-index: 9999; box-shadow: 2px 2px 10px rgba(0,0,0,0.5); width: 250px;">
        <h3 id="sheetName" style="margin: 0 0 5px 0;">Name</h3>
        <p style="margin: 0 0 10px 0; font-size: 12px; color: #aaa;"><span id="sheetOrigin">Origin</span> | Loadout: <span id="sheetLoadout" style="color: #ff9800;">Light</span></p>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <div><b>HP:</b> <span id="sheetHP">20</span></div>
            <div><b>STA:</b> <span id="sheetSTA">10</span></div>
            <div><b>FOC:</b> <span id="sheetFOC">10</span></div>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 13px;">
            <div><b>Shards:</b> <span id="sheetShards" style="color: #00ffcc;">0</span></div>
            <div><b>Level:</b> <span id="sheetLevel">1</span> (<span id="sheetXP">0</span>/100)</div>
        </div>'''

content = content.replace(old_sheet, new_sheet)

# 2. Update refreshCharacterSheet JS
old_js = '''        async function refreshCharacterSheet() {
            const res = await fetch('/api/ttrpg/get_character?id=1');
            if(res.ok) {
                const data = await res.json();
                if(data.status === 'success') {
                    document.getElementById('sheetName').innerText = data.name;
                    document.getElementById('sheetOrigin').innerText = data.origin;
                    document.getElementById('sheetLoadout').innerText = data.loadout;
                    document.getElementById('sheetHP').innerText = data.health;
                    document.getElementById('sheetSTA').innerText = data.stamina;
                    document.getElementById('sheetFOC').innerText = data.focus;
                    document.getElementById('sheetStats').innerText = `MIG ${data.stats.might} | FIN ${data.stats.finesse} | END ${data.stats.endurance} | KAW ${data.stats.knowledge}`;
                    document.getElementById('sheetInv').innerText = data.inventory || 'None';
                    document.getElementById('sheetSkills').innerText = data.skills || 'None';
                }
            }
        }'''

new_js = '''        async function refreshCharacterSheet() {
            const res = await fetch('/api/ttrpg/get_character?id=1');
            if(res.ok) {
                const data = await res.json();
                if(data.status === 'success') {
                    document.getElementById('sheetName').innerText = data.name;
                    document.getElementById('sheetOrigin').innerText = data.origin;
                    document.getElementById('sheetLoadout').innerText = data.loadout;
                    document.getElementById('sheetHP').innerText = data.health;
                    document.getElementById('sheetSTA').innerText = data.stamina;
                    document.getElementById('sheetFOC').innerText = data.focus;
                    document.getElementById('sheetStats').innerText = `MIG ${data.stats.might} | FIN ${data.stats.finesse} | END ${data.stats.endurance} | KAW ${data.stats.knowledge}`;
                    
                    document.getElementById('sheetShards').innerText = data.shards;
                    document.getElementById('sheetLevel').innerText = data.level;
                    document.getElementById('sheetXP').innerText = data.xp;
                    
                    let invList = data.inventory;
                    try { invList = JSON.parse(invList); } catch(e){}
                    if(Array.isArray(invList)) {
                        document.getElementById('sheetInv').innerText = invList.map(i => typeof i === 'object' ? i.name : i).join(', ') || 'None';
                    } else {
                        document.getElementById('sheetInv').innerText = 'None';
                    }
                    
                    let skillList = data.skills;
                    try { skillList = JSON.parse(skillList); } catch(e){}
                    if(Array.isArray(skillList)) {
                        document.getElementById('sheetSkills').innerText = skillList.join(', ') || 'None';
                    } else {
                        document.getElementById('sheetSkills').innerText = 'None';
                    }
                }
            }
        }'''

content = content.replace(old_js, new_js)

# 3. Remove PULSE SCENE button (I will use regex just in case)
content = re.sub(r'<div style="display: flex; gap: 10px; margin-bottom: 10px;">\s*<button onclick="pulseScene\(\).*?</div>', '', content, flags=re.DOTALL)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
