import logging
import random
from typing import Dict, Any

logger = logging.getLogger("ActionResolver")

class ActionResolver:
    """
    The BRUTAL Combat Engine.
    Collapses Hit & Damage into a single opposed d20 calculation.
    """
    def __init__(self, bus):
        self.bus = bus
        self.bus.subscribe("COMBAT_ACTION_DECLARED", self._on_combat_action)
        
    def _on_combat_action(self, payload: Dict[str, Any]):
        attacker = payload.get("attacker", "Attacker")
        defender = payload.get("defender", "Defender")
        
        offense_stat = payload.get("offense_stat", 5)
        weapon_mod = payload.get("weapon_mod", 0)
        
        defense_stat = payload.get("defense_stat", 5)
        armor_mod = payload.get("armor_mod", 0)
        
        is_physical = payload.get("is_physical", True)
        
        attacker_tags = payload.get("attacker_tags", [])
        defender_tags = payload.get("defender_tags", [])
        cover_bonus = payload.get("cover_bonus", 0)
        
        # Apply terrain/tag logic
        if "cover" in defender_tags and is_physical:
            armor_mod += cover_bonus
            
        # Roll the dice
        att_roll = random.randint(1, 20)
        def_roll = random.randint(1, 20)
        
        att_total = att_roll + offense_stat + weapon_mod
        def_total = def_roll + defense_stat + armor_mod
        
        margin = att_total - def_total
        
        # Formatting narrative string
        damage_type = "Physical Damage" if is_physical else "Mental Damage"
        
        log_string = f"{attacker} rolled {att_total} (d20:{att_roll} + Stat:{offense_stat} + Mod:{weapon_mod}). "
        if "cover" in defender_tags and is_physical:
            log_string += f"{defender} rolled {def_total} (d20:{def_roll} + Stat:{defense_stat} + Mod:{armor_mod} [includes +{cover_bonus} Cover]). "
        else:
            log_string += f"{defender} rolled {def_total} (d20:{def_roll} + Stat:{defense_stat} + Mod:{armor_mod}). "
        
        if margin <= 0:
            log_string += f"The attack missed or was completely absorbed!"
            self._notify_hud_and_narrator(payload, 0, False, log_string)
        elif 1 <= margin <= 4:
            log_string += f"{attacker} hits {defender} for {margin} {damage_type}!"
            self._notify_hud_and_narrator(payload, margin, False, log_string)
        else:
            log_string += f"CRITICAL STRIKE! {attacker} hits {defender} for {margin} {damage_type}, inflicting a Trauma Token!"
            self._notify_hud_and_narrator(payload, margin, True, log_string)
            
    def _notify_hud_and_narrator(self, payload, damage, trauma, log_string):
        logger.info(log_string)
        
        target = payload.get("defender")
        
        # We bounce this event to the UI so it can apply damage if the target is the player
        self.bus.publish("COMBAT_RESOLVED", {
            "target": target,
            "damage": damage,
            "trauma": trauma,
            "is_physical": payload.get("is_physical", True),
            "log": log_string
        })
        
        # Visual Map Events
        if damage > 0:
            self.bus.publish("ENTITY_DAMAGED", {"uuid": target})
            
        # For the demo: Critical strikes (trauma=True) on NPCs kill them outright
        if trauma and target != payload.get("attacker"): 
            self.bus.publish("ENTITY_DIED", {"uuid": target})
        
        # Finally, pass the mathematical truth and the tags to the AI Director
        intent_prompt = f"COMBAT RESOLUTION: {log_string} Attacker Tags: {payload.get('attacker_tags', [])}. Defender Tags: {payload.get('defender_tags', [])}. Generate a 1-2 sentence brutal, visceral narrative description of this outcome."
        self.bus.publish("EXECUTE_INTENT", {"intent": intent_prompt})
