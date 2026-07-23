from contextlib import closing
from story_manager.world_db import WorldDB
from story_manager.fsm import StoryFSM, StoryState

class CampaignWeaver:
    def __init__(self, db: WorldDB):
        self.db = db
        self.fsm = StoryFSM()

    def get_campaign_act(self) -> int:
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_act FROM campaign_state WHERE id = 1")
            return cursor.fetchone()[0]

    def set_campaign_act(self, act: int):
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE campaign_state SET current_act = ? WHERE id = 1", (act,))
            conn.commit()
            
    def generate_campaign_frame(self):
        """Generates the rigid 3-Act structural template in the database."""
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            # Wipe existing template
            cursor.execute("DELETE FROM campaign_slots")
            
            # Act 1 Major Beats
            act1_majors = ["Major: Inciting Incident", "Major: First Threshold"]
            # Act 2 Major Beats
            act2_majors = ["Major: Rising Action", "Major: The Midpoint Disaster", "Major: Point of No Return"]
            # Act 3 Major Beats
            act3_majors = ["Major: Final Preparation", "Major: The Climax", "Major: Resolution"]
            
            import random
            
            def build_act(act_num, major_beats):
                act_slots = []
                step = 1
                for major in major_beats:
                    # Randomly insert 0 to 2 minor slots before each major beat (except the first one if we want a fast start)
                    if step > 1 or act_num > 1:
                        num_minors = random.randint(1, 3)
                        for _ in range(num_minors):
                            minor_type = random.choice([
                                "Minor: Local Threat", "Minor: Faction Encounter", "Minor: Mysterious Rumor", 
                                "Minor: Gathering Resources", "Minor: Ambush", "Minor: Unexpected Ally"
                            ])
                            act_slots.append((act_num, step, minor_type, random.randint(1, 2)))
                            step += 1
                            
                    act_slots.append((act_num, step, major, random.randint(2, 3)))
                    step += 1
                return act_slots

            slots = build_act(1, act1_majors)
            slots.extend(build_act(2, act2_majors))
            slots.extend(build_act(3, act3_majors))
            
            for act, step, slot_type, max_scenes in slots:
                status = 'Active' if act == 1 and step == 1 else 'Pending'
                cursor.execute(
                    "INSERT INTO campaign_slots (act, step_number, slot_type, status, max_scenes) VALUES (?, ?, ?, ?, ?)",
                    (act, step, slot_type, status, max_scenes)
                )
            conn.commit()
            
    def trigger_background_script_generation(self, ai_director, location_name: str, local_lore: str, subtle_seeds: list):
        """Generates the pre-written scene script synchronously to prevent llama.cpp segfaults."""
        self.generate_scene_script(ai_director, location_name, local_lore, subtle_seeds)

    def get_current_slot(self) -> dict:
        """Retrieves the current active slot from the campaign frame."""
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT act, step_number, slot_type, scenes_passed, max_scenes, active_seed_id FROM campaign_slots WHERE status = 'Active' ORDER BY act ASC, step_number ASC LIMIT 1")
            row = cursor.fetchone()
            if row:
                return {
                    "act": row[0],
                    "step": row[1],
                    "type": row[2],
                    "scenes_passed": row[3],
                    "max_scenes": row[4],
                    "seed_id": row[5]
                }
            return None

    def slot_seed(self, seed_id: str, ai_director=None, location_name: str = "", local_lore: str = "", subtle_seeds: list = None):
        """Locks a specific seed into the current active slot."""
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            # Find the active slot that doesn't have a seed yet
            cursor.execute("SELECT id FROM campaign_slots WHERE status = 'Active' AND active_seed_id IS NULL ORDER BY act ASC, step_number ASC LIMIT 1")
            row = cursor.fetchone()
            if row:
                slot_id = row[0]
                cursor.execute("UPDATE campaign_slots SET active_seed_id = ? WHERE id = ?", (seed_id, slot_id))
                conn.commit()
                print(f"[CampaignWeaver] Locked seed {seed_id} into Slot ID {slot_id}.")
                if ai_director:
                    self.trigger_background_script_generation(ai_director, location_name, local_lore, subtle_seeds or [])
                
    def get_scene_script(self) -> str:
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT scene_script FROM campaign_slots WHERE status = 'Active' ORDER BY act ASC, step_number ASC LIMIT 1")
            row = cursor.fetchone()
            if row and row[0]:
                return row[0]
            return "You observe the area. (Scene script generating in background...)"
                
    def generate_scene_script(self, ai_director, location_name: str, local_lore: str, subtle_seeds: list):
        """Asynchronously calls the AI to pre-write the scene's narration based on the active slot."""
        current_slot = self.get_current_slot()
        if not current_slot:
            return
            
        slot_directive = f"Act {current_slot['act']}, Step {current_slot['step']}: {current_slot['type']}"
        
        seed_whispers = "\n".join([f"- [ENVIRONMENTAL DETAIL] {seed.subtle_description}" for seed in subtle_seeds])
        history_summary = "\n".join([f"- Past Action: {h['node']} resulted in '{h['action_taken']}'" for h in self.get_resolved_history(3)])
        
        prompt = (
            f"You are the pre-script generator for a tabletop RPG.\n"
            f"CURRENT CAMPAIGN SCRIPT: You are in {slot_directive}.\n"
            f"LOCATION: {location_name}\n"
            f"LORE: {local_lore}\n\n"
            f"RECENT HISTORY:\n{history_summary if history_summary else 'None.'}\n\n"
            f"LOCAL SEEDS:\n{seed_whispers if seed_whispers else 'None'}\n\n"
            f"CRITICAL DIRECTIVE:\n"
            f"Write a 2-3 sentence gritty, atmospheric scene description. Do not describe player actions. Describe 1 to 3 interactive points of interest or clues based on the current Campaign Script and Seeds. End by explicitly handing agency to the player with a hook."
        )
        
        # Use AI to generate script
        # Assuming the ai_director has a generic text completion wrapper we can use, or we just call _llama directly if exposed.
        # We will use evaluate_action_for_seed's internal llama call or add a generic completion method.
        # For safety, let's just use generate_llm_prompt with an empty mechanical result.
        script = ai_director.generate_llm_prompt(
            mechanical_result="Player enters the scene.",
            context=prompt,
            intent_raw="Look around."
        )
        
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE campaign_slots SET scene_script = ? WHERE status = 'Active'", (script,))
            conn.commit()

    def get_resolved_history(self, limit: int = 5) -> list[dict]:
        history = []
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT node_title, action_taken, impact_vector FROM resolved_seeds_history ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            for r in rows:
                history.append({
                    "node": r[0],
                    "action_taken": r[1],
                    "impact_vector": r[2]
                })
        return history[::-1] # Return in chronological order

    def get_escalated_threads(self) -> list[str]:
        threads = []
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT threat_description FROM escalated_threads")
            rows = cursor.fetchall()
            for r in rows:
                threads.append(r[0])
        return threads

    def ingest_seed_resolution(self, seed_data: dict, player_choice_outcome: str):
        """Takes a resolved seed and weaves it into the grand framework."""
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO resolved_seeds_history (node_title, action_taken, impact_vector) VALUES (?, ?, ?)",
                (seed_data.get("title", "Unknown Event"), player_choice_outcome, seed_data.get("category", "General"))
            )
            conn.commit()
            
        self._evaluate_campaign_shift()

    def escalate_ignored_seed(self, threat_description: str):
        """Promotes a localized seed that went unaddressed into a macro threat."""
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO escalated_threads (threat_description) VALUES (?)",
                (threat_description,)
            )
            conn.commit()

    def _evaluate_campaign_shift(self):
        """Shifts the logical shape of the campaign based on accumulated choices, gated by FSM."""
        with closing(self.db._get_local_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM resolved_seeds_history")
            count = cursor.fetchone()[0]
            
        current_fsm_state = self.fsm.get_current_state()
        
        # Example FSM progression logic based on resolved seed counts
        if count >= 2 and current_fsm_state == StoryState.INIT:
            self.fsm.attempt_transition(StoryState.ACT_1_MIDPOINT)
        elif count >= 5 and current_fsm_state == StoryState.ACT_1_MIDPOINT:
            if self.fsm.attempt_transition(StoryState.ACT_1_CLIMAX):
                print(">>> CAMPAIGN SHIFT: Act 1 Climax Reached! <<<")
        elif count >= 7 and current_fsm_state == StoryState.ACT_1_CLIMAX:
            if self.fsm.attempt_transition(StoryState.ACT_2_INIT):
                self.set_campaign_act(2)
                print(">>> CAMPAIGN SHIFT: Act II Begins! <<<")
