# S.A.G.A. (Simulation & AI Game Architecture) - Beta

Welcome to the **S.A.G.A. Engine**, an AI-generated story engine that dynamically syncs with a simulated, hardcoded world, designed to be played by users as a Virtual Tabletop RPG (VTT). 

SAGA is built on a strict **Separation of Concerns**:
- **The Python Engine is the Physics:** It handles all the math, stats, grid coordinates, Line of Sight, and combat resolution. It calculates the irrefutable truth.
- **The AI Director is the Storyteller:** The Local LLM reads the Python engine's truth and narratively translates it. The AI *never* invents game mechanics or hallucinates combat outcomes.

## 1. Quick Start

To run the SAGA Beta Engine locally, execute the asynchronous entry point:
```powershell
$env:PYTHONPATH="."; python beta_build/ui/async_app.py
```
This spins up the PyQt6 `QApplication` and handles the asynchronous event loop so AI generation (Ollama) doesn't freeze the UI.

## 2. Core Architecture

The system is fully decoupled using an Event-Driven Architecture (`EventBus`). The engine is organized into specific domains:

### `beta_build/ui/` (The Frontend & Nervous System)
- **`async_app.py`**: The application bootstrapper.
- **`main_window.py`**: The orchestrator. It sets up the UI Stack (`QStackedWidget`) and subscribes to major events to route payloads between the UI and background workers.
- **`event_bus.py`**: The central nervous system. All cross-domain communication happens by publishing and subscribing to string-based events (e.g., `PLAYER_CREATED`, `MAP_PAYLOAD_READY`, `SCENE_STABILIZED`).
- **`char_creation.py`**: A strict wizard that enforces the B.R.U.T.A.L. character creation rules, including the "1 Offense, 1 Defense, 2 Utility/Power" skill track matrix.
- **`map_view.py`**: A highly optimized 2D VTT environment built on `QGraphicsScene` that physically renders tokens, handles Line of Sight (`fov_calculator.py`), and catches `SPAWN_ENTITY` events.

### `beta_build/core/` (The Physics & Math Engine)
- **`models.py`**: Strict Pydantic models acting as the definitive source of truth. Includes `CharacterSheet`, `Inventory`, `Item`, and the `TerrainTile` (containing coordinates, tile types, and environmental tags).
- **`skills_data.py`**: The **48-Track Matrix**. Contains a massive dictionary of all generic skills categorized perfectly into `Offense`, `Defense`, `Utility`, and `Magic` for all 12 Base Stats. The python engine plucks descriptions directly from this dictionary to feed the LLM contextually.
- **`action_resolver.py` & `combat_manager.py`**: The deterministic heart of the system. Resolves the 1d20 Margin of Success combat math, applies trauma, and outputs JSON for the AI to narrate.
- **`world_gen.py` & `world_gen_worker.py`**: Procedurally generates the zone matrix. It builds a 2D array of Pydantic `TerrainTile` objects, automatically injecting environmental tags (like `blocks_los` or `cover`) for the physics engine.

### `beta_build/ai_services/` (The Narrator)
- **`director.py`**: Translates the hard math from the `ActionResolver` into visceral prose. It takes the mechanical outcome, pairs it with the specific flavor text from `skills_data.py`, and sends the packaged prompt to the LLM.
- **`llm_worker.py`**: A dedicated background `QThread` running local inference (via Ollama or LLaMA cpp) without blocking the PyQt6 GUI.

## 3. The Event Chain Lifecycle (Example: Safe-Spawn)

SAGA's architecture shines in its event choreography. For example, when a player finishes character creation:
1. **The Handoff:** The UI publishes `PLAYER_CREATED` with the JSON payload. `main_window.py` catches it and immediately emits `GENERATE_SAFE_MAP`.
2. **The Procedural Generation:** The background `world_gen_worker` builds the Pydantic `TerrainTile` grid, applying "safe" and "lit" tags. Once built, it fires `MAP_PAYLOAD_READY`.
3. **The Token Drop:** `main_window.py` hears the map is ready and commands the physical board by publishing `SPAWN_ENTITY`.
4. **The Handshake:** `map_view.py` visually drops the token onto the 2D grid and fires `SCENE_STABILIZED`.
5. **The AI Kickoff:** Catching the stabilized scene, the system publishes `INITIATE_BOOT_SEQUENCE`, commanding the AI Director to write a rich, atmospheric opening paragraph based on the generated world state.

## 4. Expanding the Game

To add new functionality, respect the Separation of Concerns:
- **Math goes in `core/`**: If you add new statuses or environmental effects, handle them strictly using tags in Python.
- **Visuals go in `ui/`**: Subscribe to a bus event, parse the JSON payload, and draw it.
- **Flavor goes in `ai_services/`**: The AI should only be narrating the mechanical truths passed to it via prompt injection. It must never calculate damage or invent rules.
