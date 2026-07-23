class ObjectiveSystem:
    def __init__(self, ecs_manager, scene_initializer, map_generator, story_framework):
        self.ecs = ecs_manager
        self.scene_init = scene_initializer
        self.map_gen = map_generator
        self.story = story_framework

    def evaluate_scene(self, player):
        """Runs at the end of every game tick."""
        if not player:
            return
            
        if getattr(player, "current_cell_id", "") == "cell_0_tutorial":
            if self._check_tutorial_cleared():
                self.transition_to_next_cell(player, "cell_0001")
        else:
            self.evaluate_procedural_scene(player)
            
    def evaluate_procedural_scene(self, player):
        """Checks if the player has resolved the current cell's seed."""
        if not self.map_gen or not self.map_gen.current_battlemap:
            return
            
        entities = self.map_gen.current_battlemap.get("entities", [])
        
        # Example condition: If all hostile NPCs are dead
        combat_npcs = [ent for ent in entities if ent.get("type") == "combat"]
        
        # If there are combat NPCs, check if they're all dead
        if combat_npcs:
            all_enemies_dead = all(ent.get("health", 0) <= 0 for ent in combat_npcs)
            if all_enemies_dead:
                print("ObjectiveSystem: Procedural scene cleared (all enemies dead).")
                db = getattr(self.scene_init, "db", None)
                if self.story:
                    self.story.advance_story(player.current_cell_id, db, seed_resolved=True)
                
                # Mock adjacent cell progression
                import random
                next_cell = f"cell_{random.randint(100, 999)}"
                self.transition_to_next_cell(player, next_cell)

    def _check_tutorial_cleared(self):
        # We don't have a strict ECS, so we query the map generator's active battlemap entities
        if not self.map_gen or not self.map_gen.current_battlemap:
            return False
            
        entities = self.map_gen.current_battlemap.get("entities", [])
        
        door_intact = False
        guard_alive = False

        for ent in entities:
            tags = ent.get("tags", [])
            # Check if the obstacle still exists
            if "tutorial_obstacle" in tags:
                door_intact = True
            
            # Check if the enemy is still alive
            if "tutorial_enemy" in tags and ent.get("health", 0) > 0:
                guard_alive = True

        # If the obstacle is broken AND the enemy is dead, the player wins
        return not door_intact and not guard_alive

    def transition_to_next_cell(self, player, next_cell_id):
        print("\n--- SCENE COMPLETE ---")
        print(f"Transitioning to {next_cell_id}...")
        
        # 1. Wipe the current map clean (handled by map_gen overwrite)
        if self.map_gen and self.map_gen.current_battlemap:
            self.map_gen.current_battlemap["entities"] = []
        
        # 2. Update the player's location tracker
        player.current_cell_id = next_cell_id
        
        # 3. TRIGGER THE STORY ENGINE
        # If we are leaving the tutorial, start Act 1
        if self.story and self.story.current_act == 0:
            db = getattr(self.scene_init, "db", None)
            self.story.trigger_act_one(next_cell_id, db)
        
        # 4. Trigger the procedural generation pipeline
        if self.scene_init and self.map_gen:
            blueprint = self.scene_init.prep_scene(player.current_cell_id)
            # Use generate_cluster to apply the blueprint constraints and encounters
            self.map_gen.generate_cluster(region_id=1, base_biome="Forest", poi_coords=[], blueprint=blueprint)
            print("ObjectiveSystem: New procedural map generated.")
