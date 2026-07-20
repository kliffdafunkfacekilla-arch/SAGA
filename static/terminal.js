// UI Elements
const mainMenu = document.getElementById('mainMenu');
const charCreation = document.getElementById('characterCreation');
const gameplayView = document.getElementById('gameplayView');

// Buttons
const btnNewGame = document.getElementById('btnNewGame');
const btnContinue = document.getElementById('btnContinue');
const btnCreateCharacter = document.getElementById('btnCreateCharacter');
const btnBackToMenu = document.getElementById('btnBackToMenu');

// Views logic
function showView(viewId) {
    mainMenu.style.display = 'none';
    charCreation.style.display = 'none';
    gameplayView.style.display = 'none';
    
    document.getElementById(viewId).style.display = 'flex';
    // Small timeout for fade-in effect via CSS
    setTimeout(() => {
        document.getElementById(viewId).style.opacity = 1;
    }, 50);
}

// Event Listeners
btnNewGame.addEventListener('click', () => showView('characterCreation'));
btnBackToMenu.addEventListener('click', () => showView('mainMenu'));

btnContinue.addEventListener('click', async () => {
    // Assuming player ID 1 for now
    showView('gameplayView');
    await refreshCharData(1);
    renderBattlemap('Burg', 1, 13);
});

btnCreateCharacter.addEventListener('click', async () => {
    const name = document.getElementById('charName').value;
    const origin = document.getElementById('charOrigin').value;
    const charClass = document.getElementById('charClass').value;
    
    if(!name) {
        alert("Please enter a character name.");
        return;
    }
    
    btnCreateCharacter.innerText = "Manifesting...";
    btnCreateCharacter.disabled = true;
    
    try {
        const response = await fetch('/api/ttrpg/create_character', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: name,
                origin: origin,
                class: charClass
            })
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showView('gameplayView');
            await refreshCharData(1); // Assuming the backend creates char ID 1 or we manage session
            renderBattlemap('Burg', 1, 13);
            document.getElementById('narrativeOutput').innerHTML += `<p class="system-msg">Character created successfully.</p>`;
        } else {
            alert("Error creating character: " + JSON.stringify(result));
        }
    } catch(e) {
        console.error(e);
        alert("Failed to connect to the server.");
    } finally {
        btnCreateCharacter.innerText = "Manifest";
        btnCreateCharacter.disabled = false;
    }
});

// Terminal input logic
const input = document.getElementById('playerInput');
input.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
        const msg = input.value;
        if(!msg.trim()) return;
        
        // Echo input
        document.getElementById('narrativeOutput').innerHTML += `<p style="color:var(--accent-glow)">> ${msg}</p>`;
        
        input.value = '';
        input.disabled = true;
        
        try {
            const response = await fetch('/api/ttrpg/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({player_id: 1, message: msg})
            });
            const result = await response.json();
            
            // Narrate output
            if (result.response) {
                document.getElementById('narrativeOutput').innerHTML += `<p>${result.response}</p>`;
            }
            
            // Execute Mechanical Actions if the LLM triggers them
            if (result.execution_results && result.execution_results.length > 0) {
                renderBattlemap('Burg', 1, 13); // Refresh map after action
                refreshCharData(1); // Refresh stats in case HP/Stamina changed
            }
            
            // Auto scroll to bottom
            const narrativeOut = document.getElementById('narrativeOutput');
            narrativeOut.scrollTop = narrativeOut.scrollHeight;
        } catch(err) {
            document.getElementById('narrativeOutput').innerHTML += `<p class="system-msg" style="color:var(--health-color)">Error: Connection to engine lost.</p>`;
        } finally {
            input.disabled = false;
            input.focus();
        }
    }
});
