class TagEngine:
    """
    The Universal Tag System (Physics/Chemistry Engine).
    Replaces hardcoded skill effects with emergent tag combinations.
    """
    
    @staticmethod
    def process_reaction(incoming_tags: list[str], target, current_depth: int = 0, max_depth: int = 3) -> list[str]:
        """
        Takes incoming tags (e.g., from an attack or spell) and applies them
        to the target's current state tags. Returns a list of narrative events.
        Enforces a max_depth to prevent infinite propagation loops.
        """
        logs = []
        if current_depth > max_depth:
            return logs
            
        target_tags = getattr(target, 'tags', [])
        
        # 1. FIRE / FLAME Logic
        if "flame" in incoming_tags or "fire" in incoming_tags:
            if "flammable" in target_tags:
                if "burn" not in target_tags:
                    target_tags.append("burn")
                if "heat" not in target_tags:
                    target_tags.append("heat")
                logs.append(f"[TAG REACTION] The flame ignites {target.name}! They are now Burning.")
            elif "wet" in target_tags:
                target_tags.remove("wet")
                logs.append(f"[TAG REACTION] The flame evaporates the moisture on {target.name}, creating Steam.")
                
        # 2. FORCE / IMPACT Logic
        if "force" in incoming_tags or "impact" in incoming_tags:
            if "fragile" in target_tags or "brittle" in target_tags:
                target_tags.append("shattered")
                logs.append(f"[TAG REACTION] The heavy impact shatters the brittle {target.name} into pieces!")
            
            if "movable" in target_tags:
                if "heavy" in target_tags:
                    logs.append(f"[TAG REACTION] The force shoves the heavy {target.name} back slightly.")
                else:
                    logs.append(f"[TAG REACTION] The force throws the light {target.name} violently backwards!")
                    
        # 3. WATER / WET Logic
        if "water" in incoming_tags or "liquid" in incoming_tags:
            if "burn" in target_tags:
                target_tags.remove("burn")
                logs.append(f"[TAG REACTION] The water extinguishes the flames on {target.name}.")
            if "wet" not in target_tags:
                target_tags.append("wet")
                
        # 4. SHOCK / ELECTRICITY Logic
        if "shock" in incoming_tags or "electric" in incoming_tags:
            if "wet" in target_tags:
                logs.append(f"[TAG REACTION] The electricity arcs through the water, electrocuting {target.name} for MASSIVE damage!")
                target_tags.append("stunned")
            if "metal" in target_tags:
                logs.append(f"[TAG REACTION] The metal conducts the shock, bypassing {target.name}'s armor!")
                target_tags.append("stunned")
                
        # 5. FROST / COLD Logic
        if "frost" in incoming_tags or "cold" in incoming_tags:
            if "wet" in target_tags:
                target_tags.remove("wet")
                target_tags.append("frozen")
                logs.append(f"[TAG REACTION] The cold flash-freezes the water, freezing {target.name} solid!")
            elif "brittle" in target_tags:
                target_tags.append("shatter_risk")
                logs.append(f"[TAG REACTION] The cold makes the brittle {target.name} highly unstable (Shatter Risk)!")
                
        # 6. CHEMICAL / ACID Logic
        if "acid" in incoming_tags or "poison" in incoming_tags:
            if "metal" in target_tags and "acid" in incoming_tags:
                target_tags.append("corroded")
                logs.append(f"[TAG REACTION] The acid eats through the metal on {target.name}, corroding their armor!")
            if "flesh" in target_tags and "poison" in incoming_tags:
                target_tags.append("toxin")
                logs.append(f"[TAG REACTION] The poison enters {target.name}'s bloodstream (Toxin applied)!")
                
        # Update target tags
        target.tags = list(set(target_tags))
        return logs

    @staticmethod
    def apply_dot(target) -> str:
        """Processes end-of-turn tag effects (like burn damage)."""
        target_tags = getattr(target, 'tags', [])
        logs = []
        if "burn" in target_tags:
            damage = 2
            if hasattr(target, "take_damage"):
                target.take_damage(damage)
            logs.append(f"{target.name} takes {damage} Burn damage.")
        if "toxin" in target_tags:
            damage = 3
            if hasattr(target, "take_damage"):
                target.take_damage(damage)
            logs.append(f"{target.name} takes {damage} Toxin damage.")
        if "frozen" in target_tags:
            # Frozen entities lose their action economy next turn, but we'll clear it after one tick
            target_tags.remove("frozen")
            logs.append(f"{target.name} thaws out from being Frozen.")
            
        target.tags = target_tags
        return " | ".join(logs) if logs else ""
