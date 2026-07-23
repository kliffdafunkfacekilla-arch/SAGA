import random
from rules_engine.character_sheet import CharacterSheet
from rules_engine.tag_engine import TagEngine

class ClashCalculator:
    """
    The Master Rules Engine.
    Handles Action Economy, Opposed Rolls, and Tag Physics.
    """
    def __init__(self):
        self.entities = {}
        
    def register_entity(self, sheet: CharacterSheet):
        self.entities[sheet.name] = sheet
        
    def resolve_action(self, intent: str, actor_name: str, target_name: str, incoming_tags: list = None, actor_zone: str = "Melee", target_zone: str = "Melee") -> dict:
        """
        Resolves a turn-based action.
        """
        if incoming_tags is None:
            incoming_tags = []
            
        actor = self.entities.get(actor_name)
        target = self.entities.get(target_name)
        
        if not actor:
            return {"action": intent, "error": "Actor not found.", "narrative_hint": "Glitch: Actor missing."}
        if not target:
            # If no specific target, assume it's an environmental action.
            # We'll need environmental target handling later, for now we fail gracefully.
            return {"action": intent, "error": "Target not found.", "narrative_hint": f"{actor.name} acts into the void."}
            
        # Parse intent for tags (primitive NLP for tags)
        i_lower = intent.lower()
        if "fire" in i_lower or "flame" in i_lower or "burn" in i_lower:
            incoming_tags.append("flame")
        if "smash" in i_lower or "hit" in i_lower or "strike" in i_lower:
            incoming_tags.append("impact")
        if "push" in i_lower or "shove" in i_lower or "force" in i_lower:
            incoming_tags.append("force")
            
        # Opposed Roll based on Equipment Loadout
        actor_stat = "might"
        weapon_range = "Melee"
        if hasattr(actor, "inventory") and actor.inventory.slots.get("weapon"):
            weapon = actor.inventory.slots["weapon"]
            actor_stat = weapon.stat_type
            if weapon.tags:
                incoming_tags.extend(weapon.tags)
                if "ranged" in weapon.tags or "bow" in weapon.tags:
                    weapon_range = "Ranged"
                    
        # Action Economy Check (3-Beat Pulse)
        ap_cost = 1 # 1 Stamina Action for a base attack
        focus_cost = 0
        weapon_range = "Melee"
        
        # Skill Parsing
        from rules_engine.skills_data import PASSIVE_HARDWARE, SUBCONSCIOUS_MAGIC, ANOMALIES
        matched_skill = None
        for category in [PASSIVE_HARDWARE, SUBCONSCIOUS_MAGIC, ANOMALIES]:
            for group in category.values():
                for tier, skill in group.items():
                    if skill["name"].lower() in intent.lower():
                        matched_skill = skill
                        break
                if matched_skill: break
            if matched_skill: break
            
        if matched_skill:
            ap_cost = matched_skill.get("cost", {}).get("stamina", 1)
            focus_cost = matched_skill.get("cost", {}).get("focus", 0)
            incoming_tags.extend(matched_skill.get("tags", []))
            if "range" in matched_skill:
                weapon_range = matched_skill["range"]
            if "zone_shift" in matched_skill:
                actor_zone = matched_skill["zone_shift"]
                narrative_hint = f"[SKILL] {actor.name} shifts to the {actor_zone} zone! "
            
        if hasattr(actor, "active_stamina") and hasattr(actor, "active_focus"):
            if actor.active_stamina < ap_cost or actor.active_focus < focus_cost:
                return {
                    "action": intent, "success": False,
                    "narrative_hint": f"[EXHAUSTED] {actor.name} lacks the Stamina/Focus required."
                }
            
        # Zone Validation (Atomic check before AP deduction)
        if weapon_range == "Melee" and actor_zone != target_zone:
            return {
                "action": intent, "success": False,
                "narrative_hint": f"[OUT OF RANGE] {target.name} is in the {target_zone} zone. You must move closer."
            }
        if weapon_range == "Close" and actor_zone == "Far" and target_zone == "Far":
            # Rough distance validation: Melee/Close/Far
            pass # Keep it simple for now, require strict Melee match, others are flexible
            
        # Deduct Resources
        if hasattr(actor, "active_stamina"):
            actor.active_stamina -= ap_cost
            actor.active_focus -= focus_cost
                
        target_stat = "reflexes"
        target_armor_bonus = 0
        if hasattr(target, "inventory") and target.inventory.slots.get("body"):
            armor = target.inventory.slots["body"]
            target_stat = armor.stat_type
            target_armor_bonus = armor.armor_mod
            
        actor_roll = random.randint(1, 20) + actor.get_stat(actor_stat)
        target_roll = random.randint(1, 20) + target.get_stat(target_stat) + target_armor_bonus
        
        if 'narrative_hint' not in locals():
            narrative_hint = ""
        narrative_hint += f"[{actor.name} Action: {actor_roll} vs {target.name} Defense: {target_roll}] "
        
        if actor_roll > target_roll:
            damage = max(1, actor_roll - target_roll)
            narrative_hint += f"SUCCESS. {actor.name} strikes for {damage} damage! "
            
            if hasattr(target, "take_damage"):
                target.take_damage(damage)
                
            # Process Tags
            if incoming_tags:
                tag_logs = TagEngine.process_reaction(incoming_tags, target)
                for log in tag_logs:
                    narrative_hint += log + " "
        else:
            narrative_hint += f"FAILURE. {target.name} deflects or dodges the attack."
            
        return {
            "action": intent,
            "success": actor_roll > target_roll,
            "damage": max(1, actor_roll - target_roll) if actor_roll > target_roll else 0,
            "narrative_hint": narrative_hint
        }
