import random
from rules_engine.character_sheet import CharacterSheet

class ClashCalculator:
    """
    The Ultimate Rules Engine.
    Maintains all character state, inventories, and resolves actions deterministically.
    """
    def __init__(self):
        self.entities = {}
        
    def register_entity(self, sheet: CharacterSheet):
        self.entities[sheet.name] = sheet
        
    def resolve_action(self, intent: str, actor_name: str, target_name: str) -> dict:
        """
        Calculates damage and applies the strict BRUTAL Engine Trauma Pipeline.
        Also parses functional skills and applies them via the Effects Engine.
        """
        from rules_engine.skills_data import PASSIVE_HARDWARE, SUBCONSCIOUS_MAGIC, ANOMALIES
        from rules_engine.effects import execute_effects
        
        actor = self.entities.get(actor_name)
        target = self.entities.get(target_name)
        
        if not actor or not target:
            return {"action": intent, "error": "Entities not found in Rules Engine state.", "narrative_hint": "A glitch in the simulation prevents this action."}
            
        # Check Stabilization State (Cannot act if bleeding out)
        if hasattr(actor, "is_stabilized") and not actor.is_stabilized:
            return {
                "action": intent,
                "success": False,
                "damage": 0,
                "narrative_hint": f"[CRITICAL FAILURE] {actor.name} is bleeding out and requires Stabilization to act!"
            }
            
        # Search for skill in intent
        matched_skill = None
        for category in [PASSIVE_HARDWARE.values(), SUBCONSCIOUS_MAGIC.values(), ANOMALIES.values()]:
            for group in category:
                if type(group) == dict:
                    for tier, skill in group.items():
                        if type(skill) == dict and skill.get("name", "").lower() in intent.lower():
                            matched_skill = skill
                            break
                if matched_skill: break
            if matched_skill: break
            
        if matched_skill:
            # Execute Functional Skill
            cost = matched_skill.get("cost", {})
            if cost:
                actor.apply_action_cost(cost)
            
            logs = execute_effects(actor, target, matched_skill, self)
            
            return {
                "action": intent,
                "success": True,
                "is_clash": False,
                "damage": 0, # Simplified, actual damage done in effects
                "narrative_hint": " | ".join(logs)
            }
            
        # Check Disadvantage State (Adrenaline Shock)
        disadvantage = False
        if hasattr(actor, "has_disadvantage") and actor.has_disadvantage:
            disadvantage = True
            actor.has_disadvantage = False # Clears after one roll
            
        # Check Narrative Tags (Brutal vs Brittle)
        # Check intent string for keywords OR actual tags on the actor/target
        if ("brutal" in intent.lower() or "brutal" in actor.tags) and "brittle" in target.tags:
            return {
                "action": intent,
                "success": True,
                "damage": 5,
                "narrative_hint": f"[NARRATIVE BYPASS] The Brutal force instantly shatters the Brittle target without a roll."
            }
            
        roll_1 = random.randint(1, 20)
        roll_2 = random.randint(1, 20)
        base_roll = min(roll_1, roll_2) if disadvantage else roll_1
        
        # Skill Checks & Magic
        is_magic = "cast" in intent.lower() or "channel" in intent.lower()
        is_skill = "pick" in intent.lower() or "sneak" in intent.lower()
        
        if is_magic:
            actor.apply_action_cost({"focus": 2})
            actor_roll = base_roll + actor.get_stat("logic")
            target_defense = 10 + target.get_stat("willpower")
        elif is_skill:
            actor_roll = base_roll + actor.get_stat("finesse")
            target_defense = 12 # Static DC for simple skills
        else:
            actor.apply_action_cost({"stamina": 1})
            actor_roll = base_roll + actor.get_stat("might")
            target_defense = 10 + target.get_stat("reflexes")
            if "prone" in target.tags: target_defense -= 2
            if "exposed" in target.tags: target_defense -= 4
        
        is_clash = (actor_roll == target_defense) and not is_skill
        success = actor_roll > target_defense
        
        result = {
            "action": intent,
            "success": success,
            "is_clash": is_clash,
            "damage": 0,
            "narrative_hint": ""
        }
        
        if is_clash:
            # 3-Beat Pulse Clash Drain
            actor.apply_action_cost({"stamina": 1, "focus": 1})
            target.apply_action_cost({"stamina": 1, "focus": 1})
            result["narrative_hint"] = f"[CLASH] Both {actor.name} and {target.name} burn 1 Focus and 1 Stamina in a deadlock."
        elif success:
            damage = max(1, actor_roll - target_defense)
            result["damage"] = damage
            target.take_damage(damage)
            
            # The Trauma Pipeline
            if damage >= 11:
                target.is_stabilized = False
                result["narrative_hint"] = f"[CRITICAL INJURY] {damage} Damage! {target.name}'s anatomy fails. They take a Trauma token and begin bleeding out. (Requires Stabilization)."
            elif damage >= 7:
                result["narrative_hint"] = f"[MAJOR INJURY] {damage} Damage! A brutal strike. {target.name} takes a permanent Trauma token."
            elif damage >= 3:
                target.has_disadvantage = True
                result["narrative_hint"] = f"[ADRENALINE SHOCK] {damage} Damage. The impact staggers {target.name}, forcing Disadvantage on their next action."
            else:
                result["narrative_hint"] = f"A solid hit on {target.name} for {damage} damage, but their biological chassis absorbs the worst of it."
        else:
            reason = "through the lingering effects of Adrenaline Shock" if disadvantage else "completely"
            result["narrative_hint"] = f"{actor.name}'s attack misses {reason}."
            
        return result
