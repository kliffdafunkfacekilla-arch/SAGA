// terminal.js
const input = document.getElementById('playerInput');
input.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
        const msg = input.value;
        input.value = '';
        
        const response = await fetch('/api/ttrpg/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({player_id: 1, message: msg})
        });
        const result = await response.json();
        
        // Narrate output
        document.getElementById('terminal').innerHTML += `<p>${result.response}</p>`;
        
        // Execute Mechanical Actions if the LLM triggers them
        if (result.execution_results && result.execution_results.length > 0) {
            renderBattlemap('Burg', 1, 13); // Refresh map after action
        }
    }
});
