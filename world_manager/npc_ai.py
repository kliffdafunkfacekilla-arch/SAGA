import math
import random

class UtilityScorer:
    @staticmethod
    def score_melee_attack(npc, player):
        score = 0.0
        # High utility if in Melee zone
        if npc.get("task") == "Melee":
            score += 0.6
        # Bonus if the player has a vulnerable tag
        if player and "brittle" in player.get("tags", []):
            score += 0.3
        return min(score, 1.0)

    @staticmethod
    def score_extinguish_self(npc):
        # If the NPC is burning, putting it out becomes the absolute highest priority
        if "burning" in npc.get("tags", []):
            return 0.95 
        return 0.0

    @staticmethod
    def score_flee(npc, player):
        score = 0.0
        health = npc.get("health", 100)
        # Utility to flee rises as health drops
        if health < 30:
            score += 0.7
        # Fleeing makes more sense if already in the Far zone
        if npc.get("task") == "Far":
            score += 0.2
        return min(score, 1.0)
        
    @staticmethod
    def score_ranged_attack(npc, player):
        score = 0.0
        if npc.get("task") in ["Close", "Far"]:
            score += 0.5
        if "ranged_weapon" in npc.get("tags", []):
            score += 0.3
        return min(score, 1.0)

class NPCAI:
    """
    Utility AI System. Replaces the legacy A* behavior trees.
    Evaluates scoring logic and executes the highest intent.
    """
    def __init__(self, clash_calculator=None):
        self.clash = clash_calculator

    def set_clash_calculator(self, clash_calculator):
        self.clash = clash_calculator

    def tick(self, entities: list, grid: list, player_x: int, player_y: int):
        # Legacy fallback if used by map systems
        pass
        
    def process_turn(self, entities: list, player_state: dict):
        """
        Processes Utility AI for all active combat entities.
        """
        if not self.clash:
            print("Warning: NPCAI has no ClashCalculator assigned.")
            return

        for ent in entities:
            # We only process combat/encounter entities
            if ent.get("type") != "NPC" and ent.get("behavior") != "blueprint_spawn":
                continue
                
            # Basic health check
            if ent.get("health", 100) <= 0:
                continue
            
            # Action Economy check (Placeholder for Stamina/AP)
            # Assuming AI gets 1 action per turn for now
            active_stamina = ent.get("active_stamina", 3)
            if active_stamina >= 3:
                
                # Evaluate all possible intents
                options = {
                    "Strike": UtilityScorer.score_melee_attack(ent, player_state),
                    "Extinguish Flames": UtilityScorer.score_extinguish_self(ent),
                    "Retreat": UtilityScorer.score_flee(ent, player_state),
                    "Shoot": UtilityScorer.score_ranged_attack(ent, player_state)
                }

                # Find the highest scoring action
                best_intent = max(options, key=options.get)
                winning_score = options[best_intent]

                # Execute (Only if the score is high enough to bother)
                if winning_score > 0.1:
                    print(f"Utility AI: Entity '{ent.get('name', 'NPC')}' chose '{best_intent}' (score: {winning_score:.2f})")
                    
                    # Funnel the intent directly into the physics loop
                    # Note: We need a unique actor_id. We'll use the entity's name or a generated ID.
                    actor_id = ent.get("id", ent.get("name", "Unknown NPC"))
                    
                    # Deduct stamina
                    ent["active_stamina"] = active_stamina - 3
                    
                    # Call clash
                    self.clash.resolve_action(
                        actor_id=actor_id,
                        intent=best_intent,
                        target_id="Player",
                        actor_tags=ent.get("tags", []),
                        target_tags=player_state.get("tags", []),
                        global_tags=[] # Will be handled by the controller's wrapper
                    )
