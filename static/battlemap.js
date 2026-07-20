// battlemap.js
const canvas = document.getElementById('battleMap');
const ctx = canvas.getContext('2d');

async function renderBattlemap(locType, locId, clusterId) {
    const response = await fetch(`/api/ttrpg/query?location_type=${locType}&location_id=${locId}&cluster_id=${clusterId}`);
    const data = await response.json();
    
    // Clear and draw grid
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Render Tiles (Logic based on feature_archetype)
    // Use data.seed to procedurally style tiles
    
    // Render Delta-Layer (NPCs, loot, cultists)
    if(data.deltas) {
        data.deltas.forEach(d => {
            if (d.type === 'NPC') {
                ctx.fillStyle = '#ff4d4d'; // Red for NPCs
            } else if (d.type === 'CULT_FORCE') {
                ctx.fillStyle = '#9932CC'; // Purple for hidden cultists
                // Optional: add a glow effect or pulsing, but simple color is fine for now.
                ctx.shadowBlur = 10;
                ctx.shadowColor = '#9932CC';
            } else {
                ctx.fillStyle = '#00cc66'; // Green for others (loot, etc)
                ctx.shadowBlur = 0;
            }
            
            ctx.fillRect(d.x * 5, d.y * 5, 10, 10);
            ctx.shadowBlur = 0; // reset
        });
    }
}

async function refreshCharData(player_id = 1) {
    try {
        const response = await fetch(`/api/ttrpg/get_character?id=${player_id}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            document.getElementById('hp').innerText = data.health || 0;
            document.getElementById('stamina').innerText = data.stamina || 0;
            document.getElementById('focus').innerText = data.focus || 0;
            
            // Render inventory
            let invList = data.inventory ? (typeof data.inventory === 'string' ? JSON.parse(data.inventory) : data.inventory) : [];
            const invHtml = invList.map(item => `<li>${item.name || item}</li>`).join('');
            const invElem = document.getElementById('inventoryList');
            if(invElem) invElem.innerHTML = invHtml || '<li>Empty</li>';
            
            // Render skills
            let skillsList = data.skills ? (typeof data.skills === 'string' ? JSON.parse(data.skills) : data.skills) : [];
            const skillsHtml = skillsList.map(skill => `<li>${skill}</li>`).join('');
            const skillsElem = document.getElementById('skillsList');
            if(skillsElem) skillsElem.innerHTML = skillsHtml || '<li>None</li>';
        }
    } catch(e) {
        console.error("Failed to refresh char data", e);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // Show main menu on load
    if (typeof showView === 'function') {
        showView('mainMenu');
    }
});
