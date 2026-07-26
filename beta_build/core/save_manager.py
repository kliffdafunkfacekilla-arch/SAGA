import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger("SaveManager")

class SaveManager:
    """Handles serialization and deserialization of the entire game state."""
    
    def __init__(self, save_dir: str = "data/saves"):
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)
            
    def save_game(self, slot: int, data: Dict[str, Any]) -> bool:
        """Serializes the game state dict to a JSON file."""
        filepath = os.path.join(self.save_dir, f"save_{slot:02d}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logger.info(f"Game saved successfully to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save game to {filepath}: {e}")
            return False
            
    def load_game(self, slot: int) -> Dict[str, Any]:
        """Deserializes a save file back into a game state dict."""
        filepath = os.path.join(self.save_dir, f"save_{slot:02d}.json")
        if not os.path.exists(filepath):
            logger.error(f"Save file {filepath} does not exist.")
            return {}
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Game loaded successfully from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Failed to load game from {filepath}: {e}")
            return {}

