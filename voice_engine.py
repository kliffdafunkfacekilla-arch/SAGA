import time
import json
import random
import sqlite3

from core.event_bus import event_bus
from ai_dm.director import AIDirector
from rules_engine.character_sheet import CharacterSheet
from rules_engine.anomaly_parser import AnomalyParser
from audio.tts_handler import TTSHandler
from audio.stt_handler import STTHandler
from story_manager.world_db import WorldDB
from story_manager.campaign_weaver import CampaignWeaver
from story_manager.reactive_seeds import SeedManager

class VoiceEngine:
    def __init__(self, ui_callback=None, rules_callback=None, player=None, ai_director=None):
        print("Initializing SAGA Voice Engine & The Nervous System...")
        self.ui_callback = ui_callback
        self.rules_callback = rules_callback
        self.ai = ai_director if ai_director else AIDirector()
        self.tts = TTSHandler()
        self.stt = STTHandler()
        self.player = player
        
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
            )
            
            faction_name = cell_data.get('faction', '')
            if faction_name:
                try:
                    conn = sqlite3.connect("okasha_world.db")
                    fac_row = conn.execute("SELECT form, culture FROM factions WHERE name LIKE ?", ('%' + faction_name + '%',)).fetchone()
                    if fac_row:
                        self.current_location_lore += f"It is controlled by {faction_name}, a {fac_row[0]} composed mostly of the {fac_row[1]} culture."
                    else:
                        self.current_location_lore += f"It is controlled by the {faction_name}."
                    conn.close()
                except Exception:
                    self.current_location_lore += f"It is controlled by the {faction_name}."

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
            self.player.biological_origin = "Drifter"
            self.player.stats = {
                "might": 5, "endurance": 5, "finesse": 5, "reflexes": 5,
                "vitality": 5, "fortitude": 5, "knowledge": 5, "logic": 5,
                "awareness": 5, "intuition": 5, "charm": 5, "willpower": 5
            }
            self.player._derive_pools()
            self.tts.speak(f"Character created. Welcome, {self.player.name}.")

    def run_loop(self):
        # Allow passing player from the MainController (via character creation UI)
        if self.player is None:
            self.create_character()
        else:
            self.tts.speak(f"Character initialized. Welcome, {self.player.name}.")
            
        self.update_ui_state("World initializing...")
        time.sleep(2.0)
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
                
                # --- INQUIRY & MOVEMENT DETECTION ---
                inquiry_prefixes = ["who", "what", "where", "when", "why", "how", "can i", "is there", "are there", "do i"]
                is_inquiry = any(i_lower.startswith(q) for q in inquiry_prefixes) or "?" in intent
                
                movement_prefixes = ["go", "walk", "move", "run", "head", "travel", "proceed", "continue"]
                is_movement = any(i_lower.startswith(m) for m in movement_prefixes)
                
                if is_inquiry:
                    mech_result = f"[OBSERVATION]: {self.player.name} takes a moment to observe and consider: '{intent}'."
                    print(">>> Inquiry Detected. Bypassing Skill Check.")
                elif is_movement:
                    # Determine target zone based on intent
                    target_zone = "Close"
                    if "melee" in i_lower or "engage" in i_lower or "towards" in i_lower:
                        target_zone = "Melee"
                    elif "far" in i_lower or "away" in i_lower or "back" in i_lower:
                        target_zone = "Far"
                        
                    # Movement is a free Move Beat, no Stamina cost
                    if hasattr(self, "seed_manager") and hasattr(self.seed_manager, "move_entity"):
                        self.seed_manager.move_entity(self.player.name if self.player else "Player", target_zone)
                        
                    mech_result = f"[MOVEMENT]: {self.player.name} uses their Move Beat to shift to the {target_zone} zone."
                    print(">>> Movement Detected.")
                    event_bus.publish("PLAYER_MOVE_VTT", {"direction": intent})
                else:
                    if self.rules_callback:
                        # Use proper unified rules engine for ALL actions
                        print(">>> Engaging Unified Rules Engine...")
                        # Extract target loosely
                        target_guess = "Environment"
                        words = i_lower.split()
                        for word in words:
                            if word not in ["i", "attack", "strike", "kill", "shoot", "the", "a", "jump", "push", "sneak", "hide"]:
                                target_guess = word.capitalize()
                                break
                        
                        # Fetch Zones if we have the simulator
                        actor_zone = "Melee"
                        target_z = "Melee"
                        if hasattr(self, "seed_manager") and hasattr(self.seed_manager, "get_entity_zone"):
                            actor_zone = self.seed_manager.get_entity_zone(self.player.name if self.player else "Player")
                            target_z = self.seed_manager.get_entity_zone(target_guess)
                            
                        # If the target isn't found in the map, default it to Melee for now to avoid breaking static combat
                        if target_z == "Unknown":
                            target_z = actor_zone
                        
                        combat_res = self.rules_callback(
                            intent, 
                            self.player.name if self.player else "Player", 
                            target_guess,
                            incoming_tags=[],
                            actor_zone=actor_zone,
                            target_zone=target_z
                        )
                        mech_result = combat_res.get("narrative_hint", "The action resolves.")
                    else:
                        mech_result = "No rules engine hooked up to resolve action."
                    
                    print(f">>> Rules Engine Result: {mech_result}")

            # --- PHASE 6: DIRECTOR NARRATION (SCRIPT READER) ---
            # The AI is reinstated in the real-time loop to handle dialogue/actions, 
            # but is strictly constrained to read the background-generated script.
            scene_script = self.campaign_weaver.get_scene_script()
            subtle_seeds = self.seed_manager.get_active_seeds(self.current_location_id)
            
            prompt = self.ai.build_director_prompt_with_spine(
                location_name=self.current_location_name,
                local_lore=self.current_location_lore,
                subtle_seeds=subtle_seeds,
                campaign_weaver=self.campaign_weaver,
                filters=self.filters_string,
                intent_raw=intent,
                mechanical_result=mech_result,
                scene_script=scene_script
            )
            
            self.last_intent = intent
            self.last_prompt = prompt
            
            self.update_ui_state(narration_text=prompt)
            event_bus.publish("REQUEST_TTS", {"text": prompt})
            
            # Extract hallucinated physical entities for the UI map
            print(">>> Extracting Interactive Entities for VTT...")
            entities_json_str = self.ai.extract_scene_entities(prompt)
            try:
                entities_list = json.loads(entities_json_str)
                if entities_list:
                    print(f">>> VTT Entities Spawned: {len(entities_list)}")
                    event_bus.publish("SPAWN_VTT_ENTITIES", {"entities": entities_list})
            except Exception as e:
                print(f"Failed to parse entities JSON: {e}")
            
            # --- PHASE 3: CONSEQUENCE HOOK (Reactive Seeds) ---
            seed_json = self.ai.evaluate_action_for_seed(intent, prompt)
            if seed_json:
                try:
                    seed_data = json.loads(seed_json)
                    seed_id = self.seed_manager.create_seed(
                        location_id=self.current_location_id,
                        origin_action=seed_data.get("origin_action", intent),
                        subtle_description=seed_data.get("subtle_description", "Something has changed here."),
                        target_entity=seed_data.get("target_entity", "Environment")
                    )
                    print(f"\n[SEED GENERATED] Origin: {seed_data.get('origin_action')}")
                    print(f"Subtle Description: {seed_data.get('subtle_description')}")
                    
                    # Interactive Slotting: Automatically slot this seed into the Campaign Framework
                    self.campaign_weaver.slot_seed(
                        seed_id,
                        ai_director=self.ai,
                        location_name=self.current_location_name,
                        local_lore=self.current_location_lore,
                        subtle_seeds=self.seed_manager.get_active_seeds(self.current_location_id)
                    )
                    
                except json.JSONDecodeError:
                    pass
            
            # --- CLOCK ADVANCE ---
            self.seed_manager.tick_simulation()

    def _narrate_intro(self):
        """Forces the LLM to generate a strong, contextual opening crawl."""
        lore_with_quest = f"LOCATION: {self.current_location_name}\nCULTURAL LORE: {self.current_location_lore}\nPLOT HOOK: {self.current_quest}"
        
        origin_str = getattr(self.player, "biological_origin", "Drifter")
        culture_details = ""
        world_lore = "Okasha is a brutal, chaotic world of warped species."
        
        try:
            import sqlite3
            conn = sqlite3.connect("okasha_world.db")
            
            # Fetch Origin details from cultures table
            culture_row = conn.execute("SELECT name, type, namesbase, population FROM cultures WHERE name LIKE ?", ('%' + origin_str + '%',)).fetchone()
            if culture_row:
                c_name, c_type, c_namesbase, c_pop = culture_row
                culture_details = f"Your species is {c_name} (Type: {c_type}). Your culture heavily features {c_namesbase} aesthetics. Your global population is around {c_pop}."
            else:
                culture_details = f"Your biological makeup is {origin_str}. You are a unique mutant survivor of the drift, possessing no ties to the major factions."
            
            # Fetch a random piece of introductory world lore from detailed_lore
            lore_row = conn.execute("SELECT title, content FROM detailed_lore WHERE chapter LIKE '%The First Age%' AND content != '' LIMIT 1").fetchone()
            if lore_row:
                world_lore = f"Lore context - {lore_row[0]}: {lore_row[1][:400]}"
            
            conn.close()
        except Exception as e:
            print(f"Error fetching lore DB: {e}")
        
        # Generate the rigid Campaign Spine Frame
        self.campaign_weaver.generate_campaign_frame()
        self.campaign_weaver.trigger_background_script_generation(
            self.ai, self.current_location_name, self.current_location_lore, self.seed_manager.get_active_seeds(self.current_location_id)
        )
        
        current_slot = self.campaign_weaver.get_current_slot()
        slot_directive = f"Act {current_slot['act']}, Step {current_slot['step']}: {current_slot['type']}" if current_slot else "Free Roam"

        # Override the standard LLM prompt for the intro
        intro_directive = (
            "CRITICAL DIRECTIVE (SMART NARRATION PROTOCOL): This is the opening narration of the game. "
            f"CURRENT CAMPAIGN SCRIPT: You are in {slot_directive}. You MUST establish this specific story beat.\n"
            f"Introduce the player character, {self.player.name}, who is a {origin_str}. "
            f"{culture_details} "
            "STRICT LORE RULE: This is the world of Okasha. There are NO humans, elves, dwarves, orcs, or standard fantasy races. "
            f"Background Lore snippet: {world_lore}... "
            f"1. TONE: Be direct, gritty, and concise. Describe their arrival in {self.current_location_name} without being overly poetic or flowery.\n"
            "2. BREVITY: Limit your narration to 3-4 punchy sentences (maximum 80 words). Be dramatic and conversational.\n"
            "3. AGENCY HANDOFF: End by explicitly introducing the Plot Hook and asking 'What do you do?'"
        )
        
        prompt = self.ai.generate_llm_prompt(intro_directive, lore_with_quest, intent_raw="Start Game", filters=self.filters_string)
        self.last_intent = "Start Game"
        self.last_prompt = prompt
        
        self._has_narrated_cell_lore = True
        
        self.update_ui_state(narration_text=prompt)
        self.tts.speak(prompt)

    def _narrate_scene(self):
        """Builds the deep lore prompt using the Campaign Weaver."""
        active_seeds = self.seed_manager.get_active_seeds(self.current_location_id)
        
        if not getattr(self, '_has_narrated_cell_lore', False):
            lore_with_quest = f"{self.current_location_lore}\nCURRENT MOTIVATION: {self.current_quest}"
            self._has_narrated_cell_lore = True
        else:
            lore_with_quest = f"You are still in {self.current_location_name}. CURRENT MOTIVATION: {self.current_quest}"
        
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
