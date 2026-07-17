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
    
    // Render Deltas (NPCs, loot, hazards)
    if(data.deltas) {
        data.deltas.forEach(d => {
            ctx.fillStyle = d.type === 'NPC' ? '#ff4d4d' : '#00cc66';
            ctx.fillRect(d.x * 5, d.y * 5, 10, 10);
        });
    }
}

document.addEventListener("DOMContentLoaded", function() {
    renderBattlemap('Burg', 1, 13);
});
