import logging
import random
from typing import Dict, Any

logger = logging.getLogger("JourneyManager")

class JourneyManager:
    """
    Handles spatial transition logic, enforcing risk (ambushes) during travel based on player stats.
    """
    def __init__(self, bus):
        self.bus = bus
        self.bus.subscribe("TRAVEL_REQUESTED", self._on_travel_requested)
        
    def _on_travel_requested(self, payload: Dict[str, Any]):
        location = payload.get("location", "Unknown")
        stats = payload.get("stats", {})
        
        # Calculate mechanical ambush chance
        # Base is 25% for a dangerous world.
        base_chance = 25
        
        # Player stats offset the risk. Average stat is 5.
        awareness = stats.get("awareness", 5)
        intuition = stats.get("intuition", 5)
        
        # Every point above 10 (combined) reduces risk by 3%
        # Every point below 10 increases risk by 3%
        stat_delta = (awareness + intuition) - 10
        ambush_chance = max(5, min(90, base_chance - (stat_delta * 3)))
        
        roll = random.randint(1, 100)
        logger.info(f"Journey roll to {location}: Rolled {roll} vs {ambush_chance}% Ambush Chance.")
        
        if roll <= ambush_chance:
            # AMBUSH!
            logger.warning(f"Ambush triggered en route to {location}!")
            self.bus.publish("GENERATE_AMBUSH_MAP", {"location": location})
            
            # Ping the Narrator to describe the ambush
            ambush_prompt = f"The player attempted to travel to {location} but was ambushed on the road by hostile forces. Generate a short, brutal description of the ambush."
            self.bus.publish("EXECUTE_INTENT", {"intent": ambush_prompt})
        else:
            # SAFE TRAVEL
            logger.info(f"Safe travel to {location}.")
            self.bus.publish("GENERATE_SAFE_MAP", {"location": location})
