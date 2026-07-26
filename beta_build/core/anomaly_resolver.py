import logging
import random

logger = logging.getLogger("AnomalyResolver")

class AnomalyResolver:
    """
    Resolves the deterministic Anomaly Equation (Shape + Rank + Scale) 
    and handles the unpredictable 'Channeling Chaos' (13th Power) mechanic.
    """
    def __init__(self, bus):
        self.bus = bus
        self.bus.subscribe("CAST_ANOMALY", self._on_cast_anomaly)
        
    def _on_cast_anomaly(self, payload: Dict[str, Any]):
        caster = payload.get("caster", "Sparkborn")
        targets = payload.get("targets", [])
        school = payload.get("school", "Unknown")
        shape = payload.get("shape", "The Point")
        effect_rank = payload.get("effect_rank", 1)
        power_scale = payload.get("power_scale", 1)
        is_chaos = payload.get("is_chaos", False)
        
        # We assume the UI or Combat Manager validates the CharacterSheet has enough beats/focus/stamina 
        # before emitting this event, but we will deduct them logically here for the log string.
        # Costs:
        focus_cost = effect_rank
        stamina_cost = power_scale
        
        # Shape Beat Costs
        move_beats_cost = 0
        focus_beats_cost = 0
        stamina_beats_cost = 0
        
        if shape == "The Point":
            focus_beats_cost = 1
        elif shape == "The Line":
            focus_beats_cost = 1
            move_beats_cost = 1
        elif shape == "The Cone":
            focus_beats_cost = 2
        elif shape == "The Burst":
            focus_beats_cost = 1
            stamina_beats_cost = 1
        elif shape == "The Wall":
            focus_beats_cost = 2
            move_beats_cost = 1
        elif shape == "The Aura":
            focus_beats_cost = 1
            move_beats_cost = 1 # +1 every subsequent round
        
        if is_chaos:
            self._channel_chaos(caster, targets, school, payload)
        else:
            self._resolve_standard_anomaly(
                caster, targets, school, shape, effect_rank, power_scale, 
                focus_cost, stamina_cost, focus_beats_cost, move_beats_cost, stamina_beats_cost, payload
            )

    def _resolve_standard_anomaly(self, caster, targets, school, shape, rank, scale, f_cost, s_cost, f_beats, m_beats, s_beats, payload):
        log_string = f"{caster} casts a Rank {rank} {school} anomaly shaped as {shape} at Power Scale {scale}!\n"
        log_string += f"[Cost: {f_beats} Focus Beat(s), {m_beats} Move Beat(s), {s_beats} Stamina Beat(s) | {f_cost} Focus, {s_cost} Stamina]\n"
        
        target_names = [t.get("name", "Unknown") for t in targets] if targets else ["nobody"]
        
        if rank == 10:
            log_string += f"GOD-TIER EFFECT! {caster} unleashes apocalyptic power. {', '.join(target_names)} are instantly obliterated or permanently staggered!"
            for t in targets:
                t["is_dead"] = True
                self.bus.publish("ENTITY_DIED", {"uuid": t.get("uuid")})
        else:
            log_string += f"The anomaly deterministically strikes {', '.join(target_names)} for {scale} effect!"
        
        self.bus.publish("ANOMALY_RESOLVED", {
            "caster": caster,
            "targets": targets,
            "school": school,
            "rank": rank,
            "scale": scale,
            "log": log_string
        })
        
        # Tell the AI Director to narrate
        intent_prompt = f"ANOMALY RESOLUTION: {log_string} Generate a brutal, visceral 1-2 sentence narrative description of this reality-hack. Do not hallucinate extra targets."
        self.bus.publish("EXECUTE_INTENT", {"intent": intent_prompt})

    def _channel_chaos(self, caster, targets, school, payload):
        log_string = f"{caster} is Channeling Chaos! (Requires NO Focus, consumes ALL remaining Stamina).\n"
        
        roll = random.randint(1, 12)
        log_string += f"Chaos Die Roll: {roll}\n"
        
        power_scale = payload.get("power_scale", 10) # Massive effect usually
        target_names = [t.get("name", "Unknown") for t in targets] if targets else ["the void"]
        
        if roll >= 9:
            log_string += f"[ASCENSION] Reality bends perfectly. The miracle strikes {', '.join(target_names)} for {power_scale} effect!"
        elif roll >= 5:
            log_string += f"[FRICTION] The miracle strikes {', '.join(target_names)} for {power_scale} effect, BUT there is a horrific complication! (Permanent Stamina Burn / Destroyed Gear)."
        elif roll >= 2:
            log_string += f"[MUTAGENIC BACKFIRE] The spell FAILS. {caster} is mutated by raw Chaos!"
        else:
            log_string += "[THE TEAR] Natural 1. A hole is torn in Ostraka! A hostile Void Entity spills out!"
            self.bus.publish("SPAWN_ENTITY", {"type": "void_entity"})
            
        self.bus.publish("ANOMALY_RESOLVED", {
            "caster": caster,
            "targets": targets,
            "school": "Chaos",
            "log": log_string
        })
        
        intent_prompt = f"CHAOS RESOLUTION: {log_string} Generate a terrifying, visceral narrative of this catastrophic magical event."
        self.bus.publish("EXECUTE_INTENT", {"intent": intent_prompt})
