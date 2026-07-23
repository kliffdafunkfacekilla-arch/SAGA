import random
import time

class GruntPack:
    def __init__(self, name: str, pack_type: str, count: int, level: int):
        self.name = name
        self.pack_type = pack_type 
        self.count = count
        self.level = level
        
    def to_dict(self):
        return {
            "name": self.name,
            "pack_type": self.pack_type,
            "count": self.count,
            "level": self.level
        }

class QuestJournal:
    def __init__(self):
        self.active_quests = []
        self.completed_quests = []
        
    def add_quest(self, objective: str, source: str, stage: int = 1, target_cx: int = 0, target_cy: int = 0):
        self.active_quests.append({
            "objective": objective,
            "source": source,
            "timestamp": time.time(),
            "status": "active",
            "stage": stage,
            "target_cx": target_cx,
            "target_cy": target_cy
        })
        
    def complete_quest(self, index: int = -1):
        if self.active_quests:
            quest = self.active_quests.pop(index)
            quest["status"] = "completed"
            self.completed_quests.append(quest)
            return quest
        return None
            
    def get_journal_summary(self, current_cx: int = None, current_cy: int = None) -> str:
        if not self.active_quests: return "No active quests."
        
        summary = []
        for q in self.active_quests:
            tcx = q.get('target_cx')
            tcy = q.get('target_cy')
            
            direction = "Unknown"
            if current_cx is not None and current_cy is not None and tcx is not None and tcy is not None:
                if tcx == current_cx and tcy == current_cy:
                    direction = "You are at the location!"
                else:
                    dx = tcx - current_cx
                    dy = tcy - current_cy
                    ns = "South" if dy > 0 else "North" if dy < 0 else ""
                    ew = "East" if dx > 0 else "West" if dx < 0 else ""
                    dist = abs(dx) + abs(dy)
                    direction = f"{dist} regions {ns}{ew}"
                    
            summary.append(f"- [Stage {q.get('stage', 1)} | Direction: {direction}] {q['objective']}")
        return "\n".join(summary)
        
    def to_dict(self):
        return {
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests
        }
        
    @classmethod
    def from_dict(cls, data):
        journal = cls()
        journal.active_quests = data.get("active_quests", [])
        journal.completed_quests = data.get("completed_quests", [])
        return journal

class QuestWeaver:
    def __init__(self):
        self.journal = QuestJournal()
        self.beat_history = []
        
        self.current_act = 0 # 0 = Tutorial/Prologue, 1 = Act 1
        self.current_slot = 0
        self.active_hook = "Escape the burning carriage."
        
        self.act_blueprints = {
            1: {"max_slots": 3, "finale_type": "boss_ambush"},
            2: {"max_slots": 5, "finale_type": "siege"},
            3: {"max_slots": 4, "finale_type": "grand_finale"}
        }
        
        self.campaign_themes = [
            {"type": "The Warlord", "base_objective": "Dismantle the local Warlord's grip on the region."},
            {"type": "The Artifact", "base_objective": "Track down rumors of a pre-Sundering artifact."},
            {"type": "The Infestation", "base_objective": "Investigate the spread of aggressive beasts."}
        ]
        
        self.lore_templates = [
            {"type": "Ancient Ruin", "objective": "You uncover the crumbled foundation of a pre-Sundering structure. Strange runes pulse faintly."},
            {"type": "Abandoned Camp", "objective": "You find a smoldering campfire. Whoever was here left in a hurry, leaving behind scattered supplies."},
            {"type": "Ominous Tracks", "objective": "Massive, inhuman footprints cross the path ahead, heading deeper into the wilderness."}
        ]
        
        self.npc_templates = [
            {"type": "Wandering Merchant", "objective": "A heavily burdened traveler offers to trade goods and rumors.", "personality": "Friendly", "entity_name": "Merchant"},
            {"type": "Wounded Survivor", "objective": "You stumble upon someone clinging to life, babbling about what attacked them.", "personality": "Desperate", "entity_name": "Survivor"},
            {"type": "Rival Adventurer", "objective": "A cocky mercenary blocks the path, demanding a toll or a duel.", "personality": "Hostile (Social)", "entity_name": "Mercenary"}
        ]
        
        self.trap_templates = [
            {"type": "Tripwire Trap", "objective": "A hidden tripwire snaps underfoot!", "entity_name": "Poison Dart Trap"},
            {"type": "Runic Puzzle", "objective": "A glowing runic barrier blocks the path forward, requiring a logical bypass.", "entity_name": "Runic Barrier"},
            {"type": "Pitfall", "objective": "The ground gives way underneath you!", "entity_name": "Spiked Pit"}
        ]
        
    def log_beat(self, action: str, outcome: str):
        self.beat_history.append({"action": action, "outcome": outcome})
        if len(self.beat_history) > 10:
            self.beat_history.pop(0)

    def trigger_act_one(self, starting_cell_id: str, db):
        print("QuestWeaver: Prologue complete. Initializing Act 1...")
        
        # 1. Update internal state
        self.current_act = 1
        self.current_slot = 1
        
        # 2. Pull the new region's lore to ground the hook
        cell_data = db.get_cell_data(starting_cell_id) if db else {}
        region_lore = cell_data.get("lore_snippet", "a barren wilderness.")
        faction_control = cell_data.get("faction", "unknown forces")
        
        # 3. Generate the overarching Act 1 goal, flavored by the local database
        self.active_hook = (
            f"You survived the carriage fire. You are now hunted by the Baron. "
            f"You have stumbled into territory controlled by {faction_control}. "
            f"Local rumors say {region_lore}. Find a safe haven and investigate the Baron's motives."
        )
        return self.active_hook
        
    def advance_story(self, cleared_cell_id, db, seed_resolved=True):
        if self.current_act == 0:
            return

        act_data = self.act_blueprints.get(self.current_act)
        if not act_data:
            return
            
        if seed_resolved:
            self.current_slot += 1
            print(f"Story Progressed: Act {self.current_act} - Slot {self.current_slot}/{act_data['max_slots']}")

        if self.current_slot >= act_data['max_slots']:
            self._trigger_act_finale(act_data['finale_type'])
        else:
            self._evolve_hook(cleared_cell_id, db)

    def _evolve_hook(self, last_cell_id, db):
        if not db:
            return
            
        # Example dynamic progression
        if self.current_slot == 1:
            self.active_hook = f"You found clues about the Baron's hunt in this region. The trail leads deeper. Find the informant."
        elif self.current_slot == 2:
            self.active_hook = f"The informant is dead, but they pointed you to the Baron's outpost. Infiltrate it."

    def _trigger_act_finale(self, finale_type):
        print(f"CRITICAL: Act {self.current_act} Finale Triggered!")
        self.active_hook = "ACT FINALE: The Baron's forces have cornered you. Survive the ambush to escape."
        
    def get_act_status(self):
        if self.current_act > 0:
            max_slots = self.act_blueprints[self.current_act]['max_slots']
        else:
            max_slots = 1
            
        return {
            "act": self.current_act,
            "current_slot": self.current_slot,
            "max_slots": max_slots,
            "objective": self.active_hook
        }

    def initialize_campaign(self, current_cx: int, current_cy: int):
        if not self.journal.active_quests:
            theme = random.choice(self.campaign_themes)
            target_cx = current_cx + random.randint(-2, 2)
            target_cy = current_cy + random.randint(-2, 2)
            self.journal.add_quest(theme["base_objective"], "World Generator", stage=1, target_cx=target_cx, target_cy=target_cy)

    def check_for_story_node(self, cx: int, cy: int, party_level: int = 1) -> dict:
        if not self.journal.active_quests:
            return None
            
        current_quest = self.journal.active_quests[-1]
        
        if current_quest.get("target_cx") != cx or current_quest.get("target_cy") != cy:
            return None
            
        hook = {"id": f"story_{cx}_{cy}_{int(time.time())}"}
        stage = current_quest.get("stage", 1)
        base_objective = current_quest["objective"]
        
        if stage == 1:
            if random.random() > 0.5:
                template = random.choice(self.npc_templates)
                hook["type"] = template["type"]
                hook["objective"] = f"{base_objective} -> {template['objective']}"
                hook["social_pack"] = {"name": template["entity_name"], "personality": template["personality"]}
            else:
                template = random.choice(self.lore_templates)
                hook["type"] = template["type"]
                hook["objective"] = f"{base_objective} -> {template['objective']}"
            
            self.journal.complete_quest(-1)
            new_cx = cx + random.randint(-1, 1)
            new_cy = cy + random.randint(-1, 1)
            self.journal.add_quest(base_objective, "Campaign Progression", stage=2, target_cx=new_cx, target_cy=new_cy)
            return hook
            
        elif stage == 2:
            if random.random() > 0.5:
                template = random.choice(self.trap_templates)
                hook["type"] = template["type"]
                hook["objective"] = f"{base_objective} -> {template['objective']}"
                hook["hazard_pack"] = {"name": template["entity_name"]}
            else:
                hook["type"] = "Ambush"
                hook["objective"] = f"{base_objective} -> An ambush party strikes!"
                hook["grunt_pack"] = GruntPack("Scout", "Predators", 2, party_level).to_dict()
                
            self.journal.complete_quest(-1)
            new_cx = cx + random.randint(-2, 2)
            new_cy = cy + random.randint(-2, 2)
            self.journal.add_quest(base_objective, "Campaign Progression", stage=3, target_cx=new_cx, target_cy=new_cy)
            return hook
            
        else:
            hook["type"] = "Final Showdown"
            hook["objective"] = f"{base_objective} -> You have cornered the target. A brutal fight ensues!"
            hook["grunt_pack"] = GruntPack("Elite Guard", "Heavies", random.randint(3, 5), party_level).to_dict()
            self.journal.complete_quest(-1)
            return hook
        
    def to_dict(self):
        return {
            "journal": self.journal.to_dict(),
            "beat_history": self.beat_history
        }
        
    @classmethod
    def from_dict(cls, data):
        weaver = cls()
        weaver.beat_history = data.get("beat_history", [])
        if "journal" in data:
            weaver.journal = QuestJournal.from_dict(data["journal"])
        return weaver
