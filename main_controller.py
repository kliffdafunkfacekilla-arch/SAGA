import sys
import json
from PyQt6.QtWidgets import QApplication
from frontend.app import SagaDesktopApp

# Clean Modules
from world_manager.simulation import WorldSimulator
from world_manager.map_generator import ClusterManager
from rules_engine.clash_calculator import ClashCalculator
from rules_engine.character_sheet import CharacterSheet
from rules_engine.inventory import Item
from world_manager.npc_ai import NPCAI

from story_manager.quest_weaver import QuestWeaver

class SagaMessageBus:
    def __init__(self):
        self.subscribers = {}
    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    def publish(self, event_type, payload=None):
        # Debug: print every event payload for schema validation
        print(f"EVENT DISPATCHED - Type: {event_type}, Payload: {payload}")
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(payload)

class SagaController:
    def __init__(self):
        self.bus = SagaMessageBus()
        self.app = QApplication(sys.argv)
        
        self.world = WorldSimulator()
        self.rules = ClashCalculator()
        self.story = QuestWeaver()
        self.npc_ai = NPCAI()
        
        self.map_engine = ClusterManager()
        
        self.map_engine = ClusterManager()
        
        # We no longer statically initialize the party here. 
        # It waits for the Character Creation Screen.
        self.party = []
        self.active_party_member_idx = 0
        self.player = None
        
        self.ui = SagaDesktopApp(self.bus)
        self._wire_events()
        
        # Player coordinates
        self.player_cx = 12
        self.player_cy = 12
        self.player_px = 50
        self.player_py = 50
        
    def _init_world(self, payload=None):
        hook = self.story.generate_hook_for_cell(14, 22)
        poi_coords = [[14, 22]]
        
        self.map_engine.generate_cluster(region_id=1, base_biome="Forest", poi_coords=poi_coords, poi_context=hook['objective'])
        
        self.current_hook = hook
        self._update_map_render()
        self._update_hud()
        
    def _update_map_render(self):
        # We need to preserve the reference to current map so AI can tick it
        if not hasattr(self, 'current_battlemap') or self.current_battlemap is None:
            self.current_battlemap = self.map_engine.get_battlemap(self.player_cx, self.player_cy)
            
            # Register physically spawned entities with the Rules Engine
            for ent in self.current_battlemap.get("entities", []):
                if ent["name"] not in self.rules.entities:
                    stats = {"might": 5, "reflexes": 5, "endurance": 5}
                    if "Bandit" in ent["name"]: stats = {"might": 4, "reflexes": 6, "endurance": 4}
                    elif "Guard" in ent["name"]: stats = {"might": 7, "reflexes": 4, "endurance": 7}
                    new_sheet = CharacterSheet(ent["name"], stats)
                    self.rules.register_entity(new_sheet)
                
        self.bus.publish("MAP_RENDER", {
            "battlemap": self.current_battlemap,
            "px": self.player_px,
            "py": self.player_py,
            "cx": self.player_cx,
            "cy": self.player_cy
        })

    def _update_hud(self):
        """Pushes current player stats to the new Character HUD"""
        self.bus.publish("HUD_UPDATE", {
            "name": self.player.name,
            "hp": self.player.current_hp,
            "max_hp": self.player.max_hp,
            "stamina": self.player.active_stamina,
            "max_stamina": self.player.max_stamina,
            "focus": self.player.active_focus,
            "max_focus": self.player.max_focus,
            "trauma": self.player.trauma_tokens
        })

    def _wire_events(self):
        self.bus.subscribe("PLAYER_ACTION", self.handle_player_action)
        self.bus.subscribe("UI_FINALIZE_PARTY", self._finalize_party_and_start)
        self.bus.subscribe("UI_LOAD_GAME", lambda p: self.load_state())
        
    def _finalize_party_and_start(self, payload):
        sheet = CharacterSheet(payload["name"], payload["stats"], payload["origin"])
        sheet.inventory.equip(Item("Rusty Broadsword", "weapon", "might", 2, 1))
        
        self.party = [sheet]
        self.active_party_member_idx = 0
        self.player = sheet
        self.rules.register_entity(sheet)
        
        self._init_world()
        
    def handle_player_action(self, payload):
        intent_raw = payload.get("intent", "").lower()
        
        if intent_raw == "/save":
            self.save_state()
            return
        elif intent_raw == "/load":
            self.load_state()
            return
        elif intent_raw == "/swap":
            self.active_party_member_idx = (self.active_party_member_idx + 1) % len(self.party)
            self.player = self.party[self.active_party_member_idx]
            self._update_hud()
            self.bus.publish("SYSTEM_LOG", f"Swapped active character to {self.player.name}.")
            return
            
        moved = False
        if "walk north" in intent_raw or "move north" in intent_raw:
            self.player_py -= 1; moved = True
        elif "walk south" in intent_raw or "move south" in intent_raw:
            self.player_py += 1; moved = True
        elif "walk east" in intent_raw or "move east" in intent_raw:
            self.player_px += 1; moved = True
        elif "walk west" in intent_raw or "move west" in intent_raw:
            self.player_px -= 1; moved = True
            
        if self.player_px < 0:
            self.player_px = 99; self.player_cx -= 1; self.current_battlemap = None
        elif self.player_px > 99:
            self.player_px = 0; self.player_cx += 1; self.current_battlemap = None
        if self.player_py < 0:
            self.player_py = 99; self.player_cy -= 1; self.current_battlemap = None
        elif self.player_py > 99:
            self.player_py = 0; self.player_cy += 1; self.current_battlemap = None
            
        if moved:
            if not self.current_battlemap:
                self._update_map_render()
                
            # Tick the NPC AI every time the player moves
            entities = self.current_battlemap.get("entities", [])
            grid = self.current_battlemap.get("grid", [])
            self.npc_ai.tick(entities, grid, self.player_px, self.player_py)
            
            self._update_map_render()
            self.world.advance_time()
            
            sim_messages = self.map_engine.tick_simulation(hours=1)
            for msg in sim_messages:
                self.bus.publish("SYSTEM_LOG", msg)
                
            return
        
        intent_json = self.ai.parse_intent(intent_raw)
        target = intent_json.get("target", "Goblin")
        
        # Tick the NPC AI for combat/action beats too
        entities = self.current_battlemap.get("entities", [])
        grid = self.current_battlemap.get("grid", [])
        self.npc_ai.tick(entities, grid, self.player_px, self.player_py)
        # Update render to show movement immediately
        self._update_map_render()
        
        self.world.advance_time()
        
        sim_messages = self.map_engine.tick_simulation(hours=1)
        for msg in sim_messages:
            self.bus.publish("SYSTEM_LOG", msg)
            
        lore = self.lore.get_context_for_location(target)
        
        # Pull personality data if interacting with an entity
        personality_context = ""
        for ent in entities:
            if ent["name"].lower() in target.lower() or target.lower() in ent["name"].lower():
                p = ent.get("personality", "neutral")
                t = ent.get("task", "standing around")
                personality_context = f"\nNPC DATA: The target is {ent['name']}. They are currently {t}. Their personality is: {p}."
        
        explicit_hook_directive = ""
        if "search" in intent_raw or "investigate" in intent_raw:
             explicit_hook_directive = f"\nSYSTEM DIRECTIVE: Narrate the following objective: '{self.current_hook['objective']}'"
        
        # If target isn't explicitly defined by intent parser, try to match a local entity
        if target not in self.rules.entities:
            target = "Unknown Entity"
            
        mechanical_result = self.rules.resolve_action(intent_raw, "Player", target)
        
        self._update_hud()
        
        prompt = self.ai.generate_llm_prompt(mechanical_result, lore + explicit_hook_directive + personality_context)
        self.bus.publish("NARRATIVE_OUTPUT", {"response": prompt})

    def save_state(self, filepath: str = "saves/quicksave.json"):
        import os
        os.makedirs("saves", exist_ok=True)
        
        entities_data = {name: sheet.to_dict() for name, sheet in self.rules.entities.items()}
        
        state = {
            "player_coords": {
                "cx": self.player_cx, "cy": self.player_cy,
                "px": self.player_px, "py": self.player_py
            },
            "rules_registry": entities_data,
            "map_engine": self.map_engine.to_dict(),
            "story": self.story.to_dict()
        }
        
        with open(filepath, "w") as f:
            json.dump(state, f, indent=4)
            
        self.bus.publish("SYSTEM_LOG", f"Game saved to {filepath}.")
        
    def load_state(self, filepath: str = "saves/quicksave.json"):
        import os
        if not os.path.exists(filepath):
            self.bus.publish("SYSTEM_LOG", "Save file not found.")
            return
            
        with open(filepath, "r") as f:
            state = json.load(f)
            
        coords = state.get("player_coords", {})
        self.player_cx = coords.get("cx", 12)
        self.player_cy = coords.get("cy", 12)
        self.player_px = coords.get("px", 50)
        self.player_py = coords.get("py", 50)
        
        self.rules.entities.clear()
        for name, sheet_data in state.get("rules_registry", {}).items():
            sheet = CharacterSheet.from_dict(sheet_data)
            self.rules.register_entity(sheet)
            if name.startswith("Player"):
                self.party.append(sheet)
                
        if self.party:
            self.player = self.party[0]
                
        if "map_engine" in state:
            self.map_engine = ClusterManager.from_dict(state["map_engine"])
            
        if "story" in state:
            self.story = QuestWeaver.from_dict(state["story"])
            
        self.current_battlemap = None
        self._update_map_render()
        self._update_hud()
        self.bus.publish("SYSTEM_LOG", "Game loaded.")

    def run(self):
        self.ui.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = SagaController()
    controller.run()
