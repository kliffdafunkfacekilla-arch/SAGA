import random

class BattlemapGenerator:
    """Generates a 100x100 grid for a specific biome."""
    def __init__(self):
        self.width = 100
        self.height = 100

    def generate(self, biome_type: str, has_poi: bool = False, poi_context: str = "") -> dict:
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        entities = []
        
        if biome_type == "Forest" or biome_type == "Wilderness":
            self._generate_organic(grid, biome_type)
        elif biome_type == "Town":
            self._generate_town(grid, entities)
            
        if has_poi:
            self._inject_poi(grid, entities, poi_context)
            
        return {
            "grid": grid,
            "width": self.width,
            "height": self.height,
            "biome": biome_type,
            "entities": entities
        }

    def _generate_organic(self, grid, biome_type):
        """Cellular-automata style organic clumping."""
        # Initial noise
        density = 0.2 if biome_type == "Forest" else 0.1
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < density:
                    grid[y][x] = 1 # Tree/Rock
                    
        # Smooth for organic clumping
        for _ in range(2):
            new_grid = [row[:] for row in grid]
            for y in range(1, self.height-1):
                for x in range(1, self.width-1):
                    neighbors = sum([
                        grid[y-1][x-1], grid[y-1][x], grid[y-1][x+1],
                        grid[y][x-1],                 grid[y][x+1],
                        grid[y+1][x-1], grid[y+1][x], grid[y+1][x+1]
                    ])
                    if neighbors > 4: new_grid[y][x] = 1
                    elif neighbors < 3: new_grid[y][x] = 0
            grid[:] = new_grid

    def _generate_town(self, grid, entities):
        """Structured grid with roads, buildings, and logical entities."""
        # 1. Carve main roads
        for x in range(self.width):
            grid[50][x] = 4 # Horizontal Road
            grid[51][x] = 4
        for y in range(self.height):
            grid[y][50] = 4 # Vertical Road
            grid[y][51] = 4
            
        # 2. Spawn Buildings (clusters of 3s)
        building_centers = [(30, 30), (70, 30), (30, 70), (70, 70)]
        for (cx, cy) in building_centers:
            for y in range(cy-4, cy+4):
                for x in range(cx-4, cx+4):
                    grid[y][x] = 3
                    
        # 3. Spawn Logical Entities (Blacksmith, Guards)
        entities.append({"name": "Blacksmith", "type": "NPC", "x": 35, "y": 35, 
                         "behavior": "task", "task": "forging a steel broadsword", "personality": "gruff, overworked, dismissive"})
        entities.append({"name": "Town Guard", "type": "NPC", "x": 52, "y": 48,
                         "behavior": "patrol", "task": "watching for thieves", "personality": "stoic, suspicious"})
        entities.append({"name": "Town Guard", "type": "NPC", "x": 48, "y": 52,
                         "behavior": "patrol", "task": "enforcing curfew", "personality": "lazy, easily bribed"})

    def _inject_poi(self, grid, entities, poi_context):
        """Builds a specific structure and spawns entities for the Story Hook."""
        cx, cy = 20, 20
        # Carve clearing
        for y in range(cy-6, cy+6):
            for x in range(cx-6, cx+6):
                grid[y][x] = 0
                
        # Build camp/structure
        for y in range(cy-2, cy+3):
            for x in range(cx-2, cx+3):
                grid[y][x] = 3
                
        # Spawn context-aware entities
        if "bandit" in poi_context.lower() or "splinter" in poi_context.lower():
            entities.append({"name": "Bandit Leader", "type": "Enemy", "x": cx, "y": cy,
                             "behavior": "hunt", "task": "guarding the loot stash", "personality": "ruthless, arrogant"})
            entities.append({"name": "Bandit Scum", "type": "Enemy", "x": cx-3, "y": cy-3,
                             "behavior": "hunt", "task": "patrolling the perimeter", "personality": "jittery, greedy"})
            entities.append({"name": "Bandit Scum", "type": "Enemy", "x": cx+3, "y": cy+3,
                             "behavior": "hunt", "task": "sharpening weapons", "personality": "cruel, dull-witted"})
        else:
            entities.append({"name": "Mysterious Figure", "type": "NPC", "x": cx, "y": cy,
                             "behavior": "task", "task": "reading an ancient tome", "personality": "cryptic, whispery"})


class WeatherSystem:
    def __init__(self):
        self.states = ["Clear", "Rain", "Fog", "Ash-Storm"]
        self.current_state = "Clear"
        self.hours_until_change = random.randint(12, 48)
        
    def tick_hour(self) -> str:
        self.hours_until_change -= 1
        message = None
        if self.hours_until_change <= 0:
            old_state = self.current_state
            self.current_state = random.choice(self.states)
            self.hours_until_change = random.randint(12, 48)
            if self.current_state != old_state:
                message = f"The weather has shifted to {self.current_state}."
        return message
        
    def get_global_tags(self):
        if self.current_state == "Rain":
            return ["Conductive", "Slippery"]
        elif self.current_state == "Fog":
            return ["Obscured"]
        elif self.current_state == "Ash-Storm":
            return ["Suffocating", "Obscured"]
        return []

class ClusterManager:
    """
    Maintains the 25x25 logical array of local maps.
    Generates the overarching contents before the player renders them.
    """
    def __init__(self):
        self.cluster_width = 25
        self.cluster_height = 25
        self.cluster_grid = []
        self.current_region_id = -1
        self.battlemap_gen = BattlemapGenerator()
        
        # Phase 3: World Simulation
        self.weather = WeatherSystem()
        self.global_time_hours = 0
        self.global_time_days = 0
        
    def generate_cluster(self, region_id: int, base_biome: str, poi_coords: list, poi_context: str = "", blueprint: dict = None):
        self.current_region_id = region_id
        self.cluster_grid = [[{"biome": base_biome, "has_poi": False, "poi_context": ""} 
                              for _ in range(self.cluster_width)] 
                             for _ in range(self.cluster_height)]
                             
        # Force a town into the cluster for logic testing
        self.cluster_grid[12][12]["biome"] = "Town"
        
        # Apply Blueprint Constraints
        self.current_blueprint = blueprint
        if blueprint and "visual_state" in blueprint:
            v_state = blueprint["visual_state"]
            if "weather_tags" in v_state and len(v_state["weather_tags"]) > 0:
                self.weather.current_state = v_state["weather_tags"][0].capitalize()
                
        # Inject POIs (Story Hooks)
        for coord in poi_coords:
            cx, cy = coord
            if 0 <= cx < self.cluster_width and 0 <= cy < self.cluster_height:
                self.cluster_grid[cy][cx]["has_poi"] = True
                self.cluster_grid[cy][cx]["poi_context"] = poi_context
                
    def get_battlemap(self, cx: int, cy: int) -> dict:
        if 0 <= cx < self.cluster_width and 0 <= cy < self.cluster_height:
            cell_logic = self.cluster_grid[cy][cx]
            bmap = self.battlemap_gen.generate(cell_logic["biome"], cell_logic["has_poi"], cell_logic["poi_context"])
            bmap["weather"] = self.weather.current_state
            bmap["global_tags"] = self.weather.get_global_tags()
            
            # Inject Blueprint Encounters
            if hasattr(self, "current_blueprint") and self.current_blueprint:
                encounters = self.current_blueprint.get("planned_encounters", [])
                import random
                for enc in encounters:
                    bmap["entities"].append({
                        "name": enc.get("name", "Unknown Figure"),
                        "type": enc.get("type", "NPC"),
                        "x": random.randint(45, 55),
                        "y": random.randint(45, 55),
                        "behavior": "blueprint_spawn",
                        "task": enc.get("location_zone", "Melee"),
                        "personality": ""
                    })
                    
            return bmap
        return None
        
    def tick_simulation(self, hours: int = 1) -> list:
        """Advances the world clock and returns any system messages."""
        messages = []
        for _ in range(hours):
            self.global_time_hours += 1
            if self.global_time_hours >= 24:
                self.global_time_hours = 0
                self.global_time_days += 1
                messages.append(f"Day {self.global_time_days} begins.")
                
            w_msg = self.weather.tick_hour()
            if w_msg:
                messages.append(w_msg)
        return messages
        
    def to_dict(self):
        return {
            "current_region_id": self.current_region_id,
            "cluster_grid": self.cluster_grid,
            "global_time_hours": self.global_time_hours,
            "global_time_days": self.global_time_days,
            "weather_state": self.weather.current_state,
            "weather_timer": self.weather.hours_until_change
        }
        
    @classmethod
    def from_dict(cls, data):
        mgr = cls()
        mgr.current_region_id = data.get("current_region_id", -1)
        mgr.cluster_grid = data.get("cluster_grid", [])
        mgr.global_time_hours = data.get("global_time_hours", 0)
        mgr.global_time_days = data.get("global_time_days", 0)
        mgr.weather.current_state = data.get("weather_state", "Clear")
        mgr.weather.hours_until_change = data.get("weather_timer", 24)
        return mgr

class ZoneMapGenerator:
    """
    Abstract map generator that organizes entities into abstract distance bands 
    (Melee, Close, Far) for narrative combat resolution without a strict 2D grid.
    """
    def __init__(self):
        self.zones = {
            "Melee": [],
            "Close": [],
            "Far": []
        }
        self.environment_tags = []
        
    def generate(self, biome_type: str, active_seed: dict = None) -> dict:
        self.zones = {"Melee": [], "Close": [], "Far": []}
        self.environment_tags = []
        
        if biome_type == "Forest":
            self.environment_tags = ["wooded", "difficult terrain", "flammable"]
            self._scatter_cover(5, ["tree", "brush", "log"])
        elif biome_type == "Town":
            self.environment_tags = ["urban", "populated", "cover"]
            self._scatter_cover(3, ["cart", "barrel", "wall"])
            
        if active_seed:
            self._inject_seed(active_seed)
            
        return {
            "zones": self.zones,
            "environment_tags": self.environment_tags
        }
        
    def _scatter_cover(self, count, object_types):
        for _ in range(count):
            obj_name = random.choice(object_types)
            entity = {
                "name": obj_name,
                "tags": self._derive_tags(obj_name)
            }
            # 50% chance in Melee or Close
            zone = random.choice(["Melee", "Close", "Far"])
            self.zones[zone].append(entity)
            
    def _inject_seed(self, seed: dict):
        """
        Interprets a story seed and injects hostile or key entities.
        If urgency is low (escalated), they start in Melee/Close.
        """
        desc = seed.get("subtle_description", "").lower()
        urgency = seed.get("urgency_ticks", 5)
        
        if urgency <= 0 or "ambush" in desc or "attack" in desc:
            spawn_zone = "Melee"
        elif urgency <= 2 or "approach" in desc or "patrol" in desc:
            spawn_zone = "Close"
        else:
            spawn_zone = "Far"
            
        entity_name = seed.get("target_entity", "Unknown Threat")
        entity = {
            "name": entity_name,
            "tags": self._derive_tags(entity_name) + ["hostile", "seed_spawn"]
        }
        self.zones[spawn_zone].append(entity)
        
    def _derive_tags(self, entity_name: str) -> list:
        name = entity_name.lower()
        tags = []
        if "wood" in name or "log" in name or "tree" in name or "brush" in name:
            tags.extend(["flammable", "fragile"])
        if "stone" in name or "rock" in name or "pillar" in name:
            tags.extend(["heavy", "cover"])
        if "water" in name or "river" in name:
            tags.extend(["wet", "liquid"])
        if "guard" in name or "bandit" in name or "threat" in name:
            tags.extend(["flesh", "movable"])
        return list(set(tags))
