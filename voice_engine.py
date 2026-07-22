import time
import json
import random

from ai_dm.director import AIDirector
from rules_engine.character_sheet import CharacterSheet
from rules_engine.anomaly_parser import AnomalyParser
from audio.tts_handler import TTSHandler
from audio.stt_handler import STTHandler
from story_manager.world_db import WorldDB
from story_manager.campaign_weaver import CampaignWeaver
from story_manager.reactive_seeds import SeedManager

class VoiceEngine:
    def __init__(self, ui_callback=None):
        print("Initializing SAGA Voice Engine & The Nervous System...")
        self.ui_callback = ui_callback
        self.ai = AIDirector()
        self.tts = TTSHandler()
        self.stt = STTHandler()
        self.player = None
        
        # Phase 3 & 6 Integrations
        self.db = WorldDB("okasha_world.db")
        self.campaign_weaver = CampaignWeaver(self.db)
        self.seed_manager = SeedManager(self.db)
        
        # Phase 7 Integrations: Load Campaign Settings
        self.settings = self._load_settings()
        self.filters_string = ", ".join(self.settings.get("filters", []))
        
        # Start location and plot override from Launcher
        custom_plot = self.settings.get("starting_plot", "").strip()
        cell_data = None
        
        # If the user provided a starting plot, check if it matches a cell ID
        if custom_plot and custom_plot.isdigit():
            cell_data = self.db.get_cell_data(int(custom_plot))
            
        if not cell_data:
            # Select a random cell from the Omnis simulation
            cell_data = self.db.get_random_cell()
            
        if cell_data:
            self.current_cell_data = cell_data
            self.current_location_id = str(cell_data["id"])
            self.current_location_name = cell_data["name"]
            
            # Construct dynamic lore from the Omnis simulation data
            self.current_location_lore = (
                f"You are in {self.current_location_name} (Cell {cell_data['id']}), a {cell_data['biome']} region. "
                f"The weather is currently {cell_data.get('weather', 'mild')}. "
                f"It is controlled by the {cell_data['faction']}."
            )
            if cell_data["population"] > 0:
                self.current_location_lore += f" There are {cell_data['population']} residents here."
            if cell_data["chaos"] > 1.0:
                self.current_location_lore += f" The area is saturated with chaotic energy (Chaos: {cell_data['chaos']:.2f})."
        else:
            self.current_cell_data = {}
            self.current_location_id = "loc_custom"
            self.current_location_name = "The Wildlands"
            self.current_location_lore = "An uncharted region of Okasha."
            
        custom_plot = self.settings.get("starting_plot", "").strip()
        if custom_plot:
            self.current_quest = custom_plot
        else:
            self.current_quest = "Explore the world and survive."
            
        self.last_intent = ""
        self.last_prompt = ""
            
        self.update_ui_state()

    def _load_settings(self):
        import os
        if os.path.exists("campaign_settings.json"):
            with open("campaign_settings.json", "r") as f:
                return json.load(f)
        return {}

    def update_ui_state(self, narration_text: str = "Waiting for AI Director..."):
        """Sends current state to the UI via callback, completely eliminating JSON locks."""
        
        # Grab active seeds for DM Dashboard
        active_seeds = []
        try:
            raw_seeds = self.seed_manager.get_active_seeds(self.current_location_id)
            for s in raw_seeds:
                active_seeds.append({"seed_id": s.seed_id, "subtle_description": s.subtle_description})
        except Exception:
            pass
            
        tags = {
            "biome": "Underground Vault",
            "structural": ["barricade_steel"],
            "props": ["Console"],
            "entities": [],
            "stamina": self.player.active_stamina if self.player else 10,
            "max_stamina": self.player.max_stamina if self.player else 10,
            "focus": self.player.active_focus if self.player else 10,
            "max_focus": self.player.max_focus if self.player else 10,
            "location": self.current_location_name,
            "narration_text": narration_text,
            "character": self.player.to_dict() if self.player else None,
            "dm_data": {
                "cell_data": getattr(self, "current_cell_data", {}),
                "last_intent": getattr(self, "last_intent", ""),
                "last_prompt": getattr(self, "last_prompt", ""),
                "active_seeds": active_seeds,
                "current_quest": self.current_quest,
                "character": self.player.to_dict() if self.player else None
            }
        }
        if self.ui_callback:
            self.ui_callback(tags)

    def create_character(self):
        import os
        if os.path.exists("player_save.json"):
            with open("player_save.json", "r") as f:
                data = json.load(f)
            self.player = CharacterSheet.from_dict(data)
            self.tts.speak(f"Character loaded. Welcome back, {self.player.name}.")
        else:
            name = self.settings.get("character_name", "Ael Thorne")
            if not name:
                name = "Ael Thorne"
                
            self.player = CharacterSheet(name)
            self.player.stats = {
                "might": 5, "endurance": 5, "finesse": 5, "reflexes": 5,
                "vitality": 5, "fortitude": 5, "knowledge": 5, "logic": 5,
                "awareness": 5, "intuition": 5, "charm": 5, "willpower": 5
            }
            self.player._derive_pools()
            self.tts.speak(f"Character created. Welcome, {self.player.name}.")

    def run_loop(self):
        self.create_character()
        
        # Initial Scene narration using Campaign Spine and Burg Intro
        self._narrate_intro()
        
        while True:
            # Start turn to regenerate action battery
            self.player.start_turn()
            self.update_ui_state(narration_text="What would you like to do?")
            
            intent = self.stt.listen()
            
            if not intent:
                continue
                
            if "quit" in intent.lower() or "exit" in intent.lower():
                self.tts.speak("Ending session. Goodbye.")
                break
                
            print(f"\n[PLAYER INTENT]: {intent}")
            
            i_lower = intent.lower()
            
            # --- PHASE 1.5: INVENTORY HOOK ---
            if "inventory" in i_lower or "what do i have" in i_lower:
                inv_text = "You are currently carrying: "
                items = [item.name for item in self.player.inventory.bag]
                for slot, item in self.player.inventory.slots.items():
                    if item:
                        items.append(f"{item.name} equipped on {slot}")
                if items:
                    inv_text += ", ".join(items)
                else:
                    inv_text = "Your inventory is completely empty."
                
                self.tts.speak(inv_text)
                self.update_ui_state(narration_text=inv_text)
                continue
                
            if "equip" in i_lower:
                target_item = intent.replace("equip", "").strip().lower()
                success = False
                for item in self.player.inventory.bag:
                    if target_item in item.name.lower():
                        self.player.inventory.equip(item, item.item_type)
                        msg = f"You equipped the {item.name}."
                        self.tts.speak(msg)
                        self.update_ui_state(narration_text=msg)
                        success = True
                        break
                if not success:
                    msg = f"You do not have a {target_item} in your backpack."
                    self.tts.speak(msg)
                    self.update_ui_state(narration_text=msg)
                continue
            
            # --- PHASE 2: MAGIC HOOK ---
            if "cast" in intent.lower() or "spell" in intent.lower() or "anomaly" in intent.lower():
                print(">>> Magic Intent Detected. Parsing Anomaly...")
                eq_json = self.ai.extract_anomaly_equation(intent)
                result = AnomalyParser.parse_spell(self.player, eq_json)
                if result.get("success"):
                    mech_result = result["narrative_hint"]
                    print(f">>> {mech_result}")
                else:
                    self.tts.speak(result.get("error", "Spell failed."))
                    continue
            else:
                i_lower = intent.lower()
                
                # --- INQUIRY DETECTION ---
                inquiry_prefixes = ["who", "what", "where", "when", "why", "how", "can i", "is there", "are there", "do i"]
                is_inquiry = any(i_lower.startswith(q) for q in inquiry_prefixes) or "?" in intent
                
                if is_inquiry:
                    mech_result = f"[OBSERVATION]: {self.player.name} takes a moment to observe and consider: '{intent}'."
                    print(">>> Inquiry Detected. Bypassing Skill Check.")
                else:
                    # Basic Skill Check mapping with HARDCODED CONSEQUENCES
                    action_stat = "might"
                    if "climb" in i_lower or "jump" in i_lower or "push" in i_lower or "break" in i_lower:
                        action_stat = "might"
                    elif "sneak" in i_lower or "hide" in i_lower or "pick" in i_lower or "dodge" in i_lower:
                        action_stat = "finesse"
                    elif "look" in i_lower or "search" in i_lower or "listen" in i_lower:
                        action_stat = "awareness"
                    elif "talk" in i_lower or "persuade" in i_lower or "lie" in i_lower or "fuck" in i_lower:
                        action_stat = "charm"
                    elif "think" in i_lower or "remember" in i_lower or "read" in i_lower:
                        action_stat = "knowledge"
                    elif "attack" in i_lower or "strike" in i_lower or "kill" in i_lower or "shoot" in i_lower:
                        action_stat = "might"
                    
                    stat_val = self.player.stats.get(action_stat, 5)
                    roll = random.randint(1, 20)
                    total = roll + stat_val
                    
                    # Hardcoded Templates - NO WIGGLE ROOM
                    if roll == 20:
                        mech_result = f"{self.player.name} critically succeeds! The action is performed flawlessly and deals massive impact."
                    elif roll == 1:
                        mech_result = f"{self.player.name} critically fails. The action goes disastrously wrong, causing immediate danger."
                    elif total >= 15:
                        if action_stat == "might":
                            mech_result = f"{self.player.name} strikes with overwhelming force. The target is destroyed or heavily damaged."
                        elif action_stat == "finesse":
                            mech_result = f"{self.player.name} slips by unnoticed or performs the delicate task perfectly."
                        elif action_stat == "awareness":
                            mech_result = f"{self.player.name} spots a hidden detail or senses an approaching threat before it arrives."
                        elif action_stat == "charm":
                            mech_result = f"{self.player.name}'s words ring true. The NPC is convinced or pacified."
                        else:
                            mech_result = f"{self.player.name} succeeds completely without complication."
                    elif total >= 10:
                        mech_result = f"{self.player.name} succeeds, but at a cost. They take 1 damage or alert a nearby enemy."
                    else:
                        mech_result = f"{self.player.name} fails entirely. They take damage or the situation escalates immediately."
                        
                    print(f">>> Hardcoded Skill Check: {mech_result}")

            # --- PHASE 6: DIRECTOR NARRATION ---
            lore_with_quest = f"{self.current_location_lore}\nCURRENT MOTIVATION: {self.current_quest}"
            prompt = self.ai.generate_llm_prompt(mech_result, lore_with_quest, intent_raw=intent, filters=self.filters_string)
            
            self.last_intent = intent
            self.last_prompt = prompt
            
            self.update_ui_state(narration_text=prompt)
            self.tts.speak(prompt)
            
            # --- PHASE 3: CONSEQUENCE HOOK (Reactive Seeds) ---
            seed_json = self.ai.evaluate_action_for_seed(intent, prompt)
            if seed_json:
                try:
                    seed_data = json.loads(seed_json)
                    self.seed_manager.create_seed(
                        location_id=self.current_location_id,
                        origin_action=seed_data.get("origin_action", intent),
                        subtle_description=seed_data.get("subtle_description", "Something has changed here."),
                        target_entity=seed_data.get("target_entity", "Environment")
                    )
                    print(">>> Generated new Reactive Seed from player action.")
                except json.JSONDecodeError:
                    pass
            
            # --- CLOCK ADVANCE ---
            self.seed_manager.tick_simulation()

    def _narrate_intro(self):
        """Forces the LLM to generate a strong, contextual opening crawl."""
        lore_with_quest = f"LOCATION: {self.current_location_name}\nCULTURAL LORE: {self.current_location_lore}\nPLOT HOOK: {self.current_quest}"
        
        # Override the standard LLM prompt for the intro
        intro_directive = (
            "CRITICAL DIRECTIVE: This is the opening narration of the game. "
            f"Introduce the player character, {self.player.name}. Describe their arrival or presence in {self.current_location_name} "
            "based heavily on the Cultural Lore provided. Establish the atmosphere, sight, and sounds of the settlement. "
            "End by explicitly introducing the Plot Hook and asking 'What do you do?'"
        )
        
        prompt = self.ai.generate_llm_prompt(intro_directive, lore_with_quest, intent_raw="Start Game", filters=self.filters_string)
        self.last_intent = "Start Game"
        self.last_prompt = prompt
        
        self.update_ui_state(narration_text=prompt)
        self.tts.speak(prompt)

    def _narrate_scene(self):
        """Builds the deep lore prompt using the Campaign Weaver."""
        active_seeds = self.seed_manager.get_active_seeds(self.current_location_id)
        
        lore_with_quest = f"{self.current_location_lore}\nCURRENT MOTIVATION: {self.current_quest}"
        
        prompt = self.ai.build_director_prompt_with_spine(
            location_name=self.current_location_name,
            local_lore=lore_with_quest,
            subtle_seeds=active_seeds,
            campaign_weaver=self.campaign_weaver,
            filters=self.filters_string
        )
        self.update_ui_state(narration_text=prompt)
        self.tts.speak(prompt)


if __name__ == "__main__":
    engine = VoiceEngine()
    engine.run_loop()
