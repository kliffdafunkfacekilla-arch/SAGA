import json
import os
import re

class SceneInitializer:
    def __init__(self, database, story_framework, ai_director):
        self.db = database
        self.story = story_framework
        self.ai = ai_director
        
        # Ensure runtime_data directory exists
        self.runtime_dir = "runtime_data"
        if not os.path.exists(self.runtime_dir):
            os.makedirs(self.runtime_dir)
            
        self.blueprint_path = os.path.join(self.runtime_dir, "current_scene.json")

    def prep_scene(self, cell_id: str):
        print(f"Loading Screen: Generating Scene for Cell {cell_id}...")
        
        # --- THE INTERCEPT ---
        if cell_id == "cell_0_tutorial":
            print("System: Tutorial state detected. Bypassing AI generation...")
            return self._generate_madlibs_tutorial()
        # ---------------------
        
        # 1. Pull the hard facts from your 250k cell DB and Story Framework
        cell_data = self.db.get_cell_data(cell_id)
        if not cell_data:
            print(f"WARNING: Cell {cell_id} not found. Using generic data.")
            cell_data = {
                "biome": "Unknown Wilderness",
                "chaos": 0.5,
                "weather": "mild",
                "faction": "None",
                "population": 0
            }
            
        story_status = self.story.get_act_status() if self.story else {"act": 1, "current_slot": 1, "max_slots": 1, "objective": "Explore"}
        
        # 2. Extract the pacing data
        act = story_status.get("act", 1)
        slot = story_status.get("current_slot", 1)
        max_slots = story_status.get("max_slots", 1)
        objective = story_status.get("objective", "")
        
        # 3. Calculate narrative escalation (0.0 to 1.0)
        escalation = slot / max_slots if max_slots > 0 else 0
        
        # 4. Build the dynamic prompt
        system_prompt = f"""
        You are the game engine's Scene Architect. Generate a JSON blueprint for the upcoming zone.
        
        STORY PROGRESSION:
        - We are in Act {act}, Plot Slot {slot} of {max_slots}.
        - Tension Escalation Level: {escalation:.2f} (Scale of 0.0 to 1.0)
        - Current Player Objective: {objective}
        
        HARD CONSTRAINTS:
        - Biome: {cell_data.get('biome_type', 'Wilderness')}
        - Local Lore: {cell_data.get('lore_snippet', 'An unknown land.')}
        
        DIRECTIVES:
        1. If Tension Escalation is below 0.5, 'visual_state' should be relatively normal, and 'planned_encounters' should favor dialogue or exploration.
        2. If Tension Escalation is 0.8 or higher, 'visual_state' MUST reflect danger (e.g., storms, darkness, ruins), and 'planned_encounters' MUST include high-stakes combat.
        3. The 'plot_hook' must directly advance the Current Player Objective.
        
        You must output ONLY valid JSON using this exact schema:
        {{
            "visual_state": {{"lighting": "string", "weather_tags": ["string"]}},
            "planned_encounters": [
                {{"name": "string", "type": "combat|dialogue|exploration", "npc_tags": ["string"], "location_zone": "string"}}
            ],
            "narrative_constraints": {{"plot_hook": "string", "banned_elements": ["string"]}}
        }}
        """

        # 3. Request the generation from your local AI
        raw_response = self._generate_blueprint(system_prompt)

        # 4. Clean and Validate the AI's output
        blueprint = self._parse_and_validate_json(raw_response)
        
        if not blueprint:
            print("CRITICAL: AI failed to generate valid blueprint. Falling back to default.")
            blueprint = self._get_fallback_blueprint(cell_data)

        # 5. Lock it in place for the rest of the game loop to read
        with open(self.blueprint_path, "w") as f:
            json.dump(blueprint, f, indent=4)
            
        print("Scene Initialized. Passing control to Map Generator.")
        return blueprint
        
    def _generate_madlibs_tutorial(self):
        """Bypasses the LLM and randomly generates a constrained Mad Libs tutorial."""
        import random
        
        settings = [
            {"name": "Burning Carriage", "lighting": "dim", "weather": "smoke_filled"},
            {"name": "Ransacked Inn", "lighting": "flickering", "weather": "dusty"},
            {"name": "Collapsed Mine", "lighting": "dark", "weather": "damp"}
        ]
        
        obstacles = [
            {"name": "Wooden Door", "tags": ["wooden", "flammable", "tutorial_obstacle"]},
            {"name": "Barricaded Window", "tags": ["glass", "fragile", "tutorial_obstacle"]},
            {"name": "Cave-In", "tags": ["stone", "heavy", "tutorial_obstacle"]}
        ]
        
        enemies = [
            {"name": "Lone Guard", "tags": ["flesh", "weak", "unarmed", "tutorial_enemy"]},
            {"name": "Drunken Thug", "tags": ["flesh", "drunk", "unarmed", "tutorial_enemy"]},
            {"name": "Starving Wolf", "tags": ["beast", "feral", "tutorial_enemy"]}
        ]
        
        setting = random.choice(settings)
        obstacle = random.choice(obstacles)
        enemy = random.choice(enemies)
        
        plot_hook = (
            f"You wake up inside a {setting['name']}. "
            f"You must break through the {obstacle['name']} before the {enemy['name']} spots you."
        )
        
        tutorial_blueprint = {
            "scene_id": "cell_0_tutorial",
            "visual_state": {
                "lighting": setting["lighting"],
                "weather_tags": [setting["weather"]]
            },
            "planned_encounters": [
                {
                    "name": obstacle["name"],
                    "type": "environmental_puzzle", 
                    "npc_tags": obstacle["tags"], 
                    "location_zone": "Melee"
                },
                {
                    "name": enemy["name"],
                    "type": "combat", 
                    "npc_tags": enemy["tags"], 
                    "location_zone": "Close"
                }
            ],
            "narrative_constraints": {
                "plot_hook": plot_hook,
                "banned_elements": ["complex_lore", "magic_items", "multiple_enemies"]
            }
        }
        
        with open(self.blueprint_path, "w") as f:
            json.dump(tutorial_blueprint, f, indent=4)
            
        print(f"Cell Zero Initialized ({setting['name']}). Passing control to Map Generator.")
        return tutorial_blueprint

    def _generate_blueprint(self, prompt: str) -> str:
        if hasattr(self.ai, "_llama"):
            output = self.ai._llama(
                prompt,
                max_tokens=300,
                temperature=0.3, # Low temp for logic!
                top_p=0.9,
                stop=["```"]
            )
            return output.get("choices", [{}])[0].get("text", "").strip()
        else:
            print("AI Director does not have _llama instance available!")
            return ""

    def _parse_and_validate_json(self, raw_text: str):
        """Extracts JSON from the AI output, ignoring conversational filler."""
        try:
            # Clean up markdown if any
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "", 1)
            if raw_text.startswith("```"):
                raw_text = raw_text.replace("```", "", 1)
                
            # Use regex to find the first '{' and last '}'
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                clean_json = match.group(0)
                return json.loads(clean_json)
            return None
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            return None

    def _get_fallback_blueprint(self, cell_data: dict):
        """Prevents a crash if the local AI spits out total garbage."""
        return {
            "visual_state": {"lighting": "normal", "weather_tags": [cell_data.get('weather', 'clear')]},
            "planned_encounters": [],
            "narrative_constraints": {"plot_hook": "Explore the area.", "banned_elements": []}
        }
