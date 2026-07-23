from core.event_bus import event_bus
from world_manager.map_generator import ZoneMapGenerator
from rules_engine.tag_engine import TagEngine

class WorldSimulator:
    """
    Manages the physical simulation of the world, integrating the map, entities, and time.
    """
    def __init__(self, rules_engine=None):
        self.tick_count = 0
        self.current_season = "Spring"
        self.weather = "Clear"
        
        self.map_generator = ZoneMapGenerator()
        self.current_map = None
        self.active_entities = []
        self.rules = rules_engine
        
        event_bus.subscribe("SIMULATION_TICK", self._on_tick)
        event_bus.subscribe("FSM_TRANSITION", self._on_fsm_transition)
        
    def _on_fsm_transition(self, payload):
        new_state = payload.get("new_state", "")
        # Shift weather and season based on story beats
        if "ACT_2" in new_state:
            self.current_season = "Autumn"
            self.weather = "Stormy"
            print(f"[WorldSimulator] FSM Transition: Weather shifted to {self.weather}, Season to {self.current_season}.")
        elif "ACT_3" in new_state:
            self.current_season = "Winter"
            self.weather = "Blizzard"
            print(f"[WorldSimulator] FSM Transition: Weather shifted to {self.weather}, Season to {self.current_season}.")
        
    def build_local_scene(self, biome_type: str, active_seed: dict = None):
        """Generates the local map zones and registers all entities with the rules engine."""
        self.current_map = self.map_generator.generate(biome_type, active_seed)
        
        # Flatten entities from zones
        self.active_entities = []
        for zone, entities in self.current_map["zones"].items():
            for entity in entities:
                entity["zone"] = zone
                self.active_entities.append(entity)
                
                # If we had full character sheets for NPCs, we'd register them here.
                # For now, we mock basic sheets for them so the rules engine can process them.
                if self.rules:
                    from rules_engine.character_sheet import CharacterSheet
                    npc_sheet = CharacterSheet(name=entity["name"])
                    npc_sheet.tags = set(entity.get("tags", []))
                    self.rules.register_entity(npc_sheet)
                    
        return self.current_map
        
    def move_entity(self, entity_name: str, target_zone: str) -> bool:
        """Moves an entity to a specific zone if it exists."""
        if not self.current_map or target_zone not in self.current_map["zones"]:
            return False
            
        for current_zone, entities in self.current_map["zones"].items():
            for i, entity in enumerate(entities):
                if entity["name"].lower() == entity_name.lower():
                    # Move to new zone
                    moved_entity = entities.pop(i)
                    moved_entity["zone"] = target_zone
                    self.current_map["zones"][target_zone].append(moved_entity)
                    return True
        return False
        
    def get_entity_zone(self, entity_name: str) -> str:
        """Returns the current zone of an entity."""
        if not self.current_map:
            return "Unknown"
        for current_zone, entities in self.current_map["zones"].items():
            for entity in entities:
                if entity["name"].lower() == entity_name.lower():
                    return current_zone
        return "Unknown"
        
    def advance_time(self, ticks: int = 1):
        self.tick_count += ticks
        if self.tick_count % 100 == 0:
            self.weather = "Raining" if self.weather == "Clear" else "Clear"
            
        # Apply end-of-turn Tag effects (like DoT Burn)
        if self.rules:
            for entity_name, entity in self.rules.entities.items():
                log = TagEngine.apply_dot(entity)
                if log:
                    print(f">>> [ENVIRONMENT] {log}")
                    
        return {"tick": self.tick_count, "weather": self.weather, "season": self.current_season}

    def _on_tick(self, payload):
        self.advance_time(1)
