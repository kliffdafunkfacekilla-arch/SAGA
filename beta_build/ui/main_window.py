"""
Provides the main application window that orchestrates all UI screens and background workers.
"""
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import pyqtSlot

# --- Beta Architecture ---
from beta_build.ui.event_bus import EventBus
from beta_build.ai_services.llm_worker import LLMWorker
from beta_build.audio.audio_manager import TTSWorker, STTWorker
from beta_build.core.models import CharacterSheet
from beta_build.ai_services.director import AIDirector
from beta_build.data.memory_store import MemoryStore
from beta_build.core.world_gen_worker import WorldGenWorker
from beta_build.core.journey_manager import JourneyManager
from beta_build.core.action_resolver import ActionResolver
from beta_build.core.combat_manager import CombatManager
from beta_build.core.campaign_manager import CampaignManager

# --- Frontend Components ---
from beta_build.ui.char_creation import CharacterCreationScreen
from beta_build.ui.character_management import CharacterManagementScreen
from beta_build.ui.map_view import MapCanvas
from beta_build.ui.screens import StartMenu, VendorScreen

class SagaDesktopApp(QMainWindow):
    """
    The main window for the S.A.G.A Engine.
    Handles the initialization of background workers (LLM, Audio), the central EventBus,
    and the StackedWidget to navigate between UI views.
    """
    def __init__(self):
        super().__init__()
        self.bus = EventBus()
        self.setWindowTitle("S.A.G.A. Engine Beta")
        self.setGeometry(100, 100, 1200, 800)
        
        premium_css = """
        QMainWindow { background-color: #0f1115; }
        QWidget { color: #d8d8d8; font-family: 'Segoe UI', Arial, sans-serif; }
        QPushButton {
            background-color: #1c2026;
            border: 1px solid #3a414c;
            border-radius: 4px;
            color: #4CAF50;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover { background-color: #2b323b; border: 1px solid #4CAF50; }
        QPushButton:pressed { background-color: #4CAF50; color: #0f1115; }
        QLabel { font-size: 14px; }
        QTextEdit, QLineEdit, QComboBox, QSpinBox {
            background-color: #14171c;
            border: 1px solid #2b323b;
            border-radius: 3px;
            color: #e0e0e0;
            padding: 6px;
        }
        QTextEdit:focus, QLineEdit:focus { border: 1px solid #4CAF50; }
        """
        self.setStyleSheet(premium_css)
        
        # UI Stack
        self.stack = QStackedWidget()
        
        # Initialize UI Screens
        self.start_menu = StartMenu(self.bus)
        self.char_creation = CharacterCreationScreen(self.bus)
        self.map_canvas = MapCanvas(self.bus)
        self.char_management = CharacterManagementScreen(self.bus)
        self.vendor_screen = VendorScreen(self.bus)
        
        self.stack.addWidget(self.start_menu)      # 0
        self.stack.addWidget(self.char_creation)   # 1
        self.stack.addWidget(self.map_canvas)      # 2
        self.stack.addWidget(self.char_management) # 3
        self.stack.addWidget(self.vendor_screen)   # 4
        
        self.setCentralWidget(self.stack)
        
        # Navigation Subs
        self.bus.subscribe("UI_START_NEW_GAME", lambda p: self.stack.setCurrentIndex(1))
        self.bus.subscribe("UI_LOAD_GAME", self._show_game)
        self.bus.subscribe("UI_FINALIZE_PARTY", self._show_game)
        self.bus.subscribe("PLAYER_CREATED", self._on_player_created)
        
        self.bus.subscribe("UI_OPEN_CHAR_MANAGEMENT", lambda p: self.stack.setCurrentIndex(3))
        self.bus.subscribe("UI_CLOSE_CHAR_MANAGEMENT", lambda p: self.stack.setCurrentIndex(2))
        
        self.bus.subscribe("UI_OPEN_VENDOR", lambda p: self.stack.setCurrentIndex(4))
        self.bus.subscribe("UI_CLOSE_VENDOR", lambda p: self.stack.setCurrentIndex(2))

        # Intent Execution Sub
        self.bus.subscribe("EXECUTE_INTENT", self._handle_intent)
        self.bus.subscribe("EXECUTE_AI_INTENT", self._handle_ai_intent)
        self.bus.subscribe("UI_TOGGLE_MIC", self._handle_mic_toggle)
        
        self.bus.subscribe("GENERATE_SAFE_MAP", lambda p: self.world_gen_worker.request_generation(p.get("location"), False))
        self.bus.subscribe("GENERATE_AMBUSH_MAP", lambda p: self.world_gen_worker.request_generation(p.get("location"), True))
        
        self.bus.subscribe("MAP_PAYLOAD_READY", self._on_map_payload_ready)
        self.bus.subscribe("COMBAT_RESOLVED", self._on_combat_resolved)
        
        self.bus.subscribe("AI_NARRATED", self._handle_ai_narrated)
        self.bus.subscribe("MECHANICS_TRIGGERED", self._handle_mechanics_triggered)
        self.bus.subscribe("LOOT_ACQUIRED", self._on_loot_acquired)

        # Background Workers Initialization
        self.init_workers()
        
        # Core State
        self.player_character = CharacterSheet(name="Wanderer")
        self.ai_director = AIDirector(load_model=False)
        self.memory = MemoryStore()
        self.journey_manager = JourneyManager(self.bus)
        self.action_resolver = ActionResolver(self.bus)
        self.combat_manager = CombatManager(self.bus)
        self.campaign_manager = CampaignManager(self.bus)

    def init_workers(self):
        """Initializes and connects QThreads for background AI and audio tasks."""
        # 1. LLM Worker
        self.llm_worker = LLMWorker(self.bus, parent=self)
        self.llm_worker.generation_complete.connect(self._on_llm_complete)
        self.llm_worker.error_occurred.connect(self.map_canvas.on_error)
        self.llm_worker.start()

        # 2. TTS Worker
        self.tts_worker = TTSWorker(parent=self)
        self.tts_worker.error_occurred.connect(self.map_canvas.on_error)
        self.tts_worker.start()

        # 3. STT Worker
        self.stt_worker = STTWorker(parent=self)
        self.stt_worker.speech_recognized.connect(self.map_canvas.on_speech_recognized)
        self.stt_worker.error_occurred.connect(self.map_canvas.on_error)

        # 4. World Gen Worker
        self.world_gen_worker = WorldGenWorker(parent=self)
        self.world_gen_worker.map_ready.connect(lambda payload: self.bus.publish("MAP_PAYLOAD_READY", payload))
        self.world_gen_worker.error_occurred.connect(self.map_canvas.on_error)
        self.world_gen_worker.start()
        
    def _show_game(self, payload=None):
        self.stack.setCurrentIndex(2)
        # Hook up the Pydantic character state to the UI HUD
        self.bus.publish("HUD_UPDATE", {"character": self.player_character.model_dump()})
        self.bus.publish("LOAD_CAMPAIGN", {})

    def _on_map_payload_ready(self, payload):
        """Called when WorldGen finishes. If entities are present, it's combat."""
        entities = payload.get("entities", [])
        if entities:
            # Short delay so UI can render them first
            self.bus.publish("COMBAT_START", {
                "entities": entities, 
                "player_stats": self.player_character.stats
            })

    def _on_loot_acquired(self, payload):
        from beta_build.core.models import Item
        item_data = payload.get("item_data", {})
        item = Item(**item_data)
        self.player_character.inventory.bag.append(item)
        self.bus.publish("HUD_UPDATE", {"character": self.player_character.model_dump()})
        self.bus.publish("SYSTEM_LOG", {"message": f"<font color='#FFD700'><b>Loot Acquired:</b> {item.name}</font>"})
        
        intent_prompt = f"LOOT ACQUIRED: The player picked up {item.name}. Generate a brief narrative about them finding it."
        self.bus.publish("EXECUTE_INTENT", {"intent": intent_prompt})

    def _on_player_created(self, payload):
        """Handoff from Character Creation to the active Game Screen."""
        self.player_character = CharacterSheet(**payload)
        self.bus.publish("HUD_UPDATE", {"character": self.player_character.model_dump()})
        self.stack.setCurrentIndex(2)

    def _on_combat_resolved(self, payload):
        target = payload.get("target")
        if target == self.player_character.name:
            self.player_character.take_damage(payload.get("damage", 0), payload.get("is_physical", True))
            if payload.get("trauma"):
                self.player_character.trauma_tokens += 1
            self.bus.publish("HUD_UPDATE", {"character": self.player_character.model_dump()})
        else:
            # In a full game, we'd update the specific NPC token on the map here
            pass
            
    def _handle_intent(self, payload):
        intent = payload.get("intent", "").strip()
        if not intent: return
        
        # We don't want to show raw backend prompts in the UI
        if not intent.startswith("COMBAT RESOLUTION:") and not intent.startswith("The player attempted to travel"):
            self.map_canvas.log_view.append(f"<b>You:</b> {intent}")
        
        import re
        
        match_travel = re.search(r"(?:travel to|head to|go to)\s+([a-zA-Z\s]+)", intent, re.IGNORECASE)
        if match_travel:
            location = match_travel.group(1).strip()
            self.map_canvas.log_view.append(f"\n<i>Traveling to {location}...</i>\n")
            self.bus.publish("TRAVEL_REQUESTED", {"location": location, "stats": self.player_character.stats})
            return
            
        match_combat = re.search(r"(?:attack|strike|hit|intimidate|fear)\s+([a-zA-Z\s]+)", intent, re.IGNORECASE)
        if match_combat and not intent.startswith("COMBAT RESOLUTION:"):
            target = match_combat.group(1).strip()
            
            # Very basic parsing for demo: check if it's a mental attack
            is_mental = "intimidate" in intent.lower() or "fear" in intent.lower()
            
            weapon_mod = 0
            if self.player_character.inventory.slots.get("weapon"):
                weapon_mod += self.player_character.inventory.slots["weapon"].modifier
                
            armor_mod = 0
            if is_mental:
                for slot in self.player_character.inventory.mental_slots:
                    item = self.player_character.inventory.slots.get(slot)
                    if item: armor_mod += item.armor_mod
            else:
                for slot in self.player_character.inventory.physical_slots:
                    item = self.player_character.inventory.slots.get(slot)
                    if item: armor_mod += item.armor_mod
            
            # Extract defender's terrain tags and cover from Map Canvas
            defender_tags = []
            defender_cover = 0
            for uid, ent in self.map_canvas.battle_map.entities.items():
                if target.lower() in ent.name.lower():
                    tx = int(ent.pos().x() // self.map_canvas.battle_map.tile_size)
                    ty = int(ent.pos().y() // self.map_canvas.battle_map.tile_size)
                    try:
                        node = self.map_canvas.battle_map.grid_data[ty][tx]
                        if isinstance(node, dict):
                            defender_tags.extend(node.get("tags", []))
                            defender_cover = node.get("cover_bonus", 0)
                        
                        # Add entity's own tags too
                        if hasattr(ent, 'tags'):
                            defender_tags.extend(ent.tags)
                    except (IndexError, AttributeError):
                        pass
                    break
                    
            combat_payload = {
                "attacker": self.player_character.name,
                "attacker_tags": self.player_character.tags,
                "defender": target,
                "defender_tags": defender_tags,
                "offense_stat": self.player_character.stats.get("might", 5) if not is_mental else self.player_character.stats.get("willpower", 5),
                "weapon_mod": weapon_mod,
                "defense_stat": 4, # Example enemy stat
                "armor_mod": 1, # Example enemy armor
                "cover_bonus": defender_cover,
                "is_physical": not is_mental
            }
            self.bus.publish("COMBAT_ACTION_DECLARED", combat_payload)
            return
            
        self.map_canvas.log_view.append("\n<i>Narrator is thinking...</i>\n")
        self.map_canvas.log_view.append("<font color='#a0a0ff'>[NARRATOR]:</font> ")
        
        # 1. Recall past memories related to the player's intent
        past_memories = self.memory.recall_context(intent)
        
        # 2. Inject memories into the current context
        current_context = "The player is standing in a dusty, ruined town square.\n"
        if past_memories:
            current_context += f"\n{past_memories}"
            
        # 3. Generate context-aware prompt
        prompt = self.ai_director.generate_llm_prompt(
            mechanical_result="The action resolves successfully.",
            context=current_context,
            intent_raw=intent
        )
        self.llm_worker.request_generation(prompt=prompt, tag="narrative")

    def _handle_ai_intent(self, payload):
        intent = payload.get("intent", "")
        
        self.map_canvas.log_view.append("\n<i>AI Director is generating...</i>\n")
        self.map_canvas.log_view.append("<font color='#ff5555'>[AI]:</font> ")
        
        self.llm_worker.request_generation(prompt=intent, tag="narrative")

    def _handle_mic_toggle(self, payload):
        if payload.get("active", False):
            if not self.stt_worker.isRunning():
                self.stt_worker.start()
        else:
            self.stt_worker.stop_listening()

    def _handle_ai_narrated(self, payload):
        prose = payload.get("prose", "")
        # Implement a basic typewriter effect by appending characters over time
        # For a robust implementation, this would use a QTimer, but appending at once is safe for beta.
        # We simulate it by just printing it nicely formatted.
        self.map_canvas.log_view.append(f"<font color='#e0e0e0'>{prose}</font>")
        
    def _handle_mechanics_triggered(self, payload):
        actions = payload.get("actions", [])
        for action in actions:
            if action.get("type") == "attack":
                # Convert AI intent to ActionResolver payload
                combat_payload = {
                    "attacker": action.get("actor_uuid"),
                    "defender": action.get("target_uuid"),
                    "offense_stat": 5, # We'd pull real stats here
                    "weapon_mod": 0,
                    "defense_stat": 5, 
                    "armor_mod": 0,
                    "is_physical": True
                }
                self.bus.publish("COMBAT_ACTION_DECLARED", combat_payload)

    @pyqtSlot(str, str)
    def _on_llm_complete(self, tag: str, full_text: str):
        # Feed the fully generated text to the TTS worker
        if full_text:
            self.tts_worker.speak(full_text)
            # Store the final generated narrative into long-term memory
            self.memory.store_event(text=full_text, metadata={"type": tag})
            
        self.bus.publish("END_TURN")

    def closeEvent(self, event):
        """Ensure threads are properly closed when shutting down."""
        self.llm_worker.requestInterruption()
        self.tts_worker.requestInterruption()
        self.stt_worker.requestInterruption()
        self.world_gen_worker.requestInterruption()
        super().closeEvent(event)
