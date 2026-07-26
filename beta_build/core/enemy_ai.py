import logging
import math
from typing import Dict, Any

logger = logging.getLogger("EnemyAIEngine")

class EnemyAIEngine:
    """
    Lightweight tactical AI that runs during the enemy phase.
    """
    def __init__(self, bus, zone_manager, turn_manager):
        self.bus = bus
        self.zone_manager = zone_manager
        self.turn_manager = turn_manager
        
        self.bus.subscribe("TURN_STARTED", self._on_turn_started)

    def _on_turn_started(self, payload: Dict[str, Any]):
        active_uuid = payload.get("uuid")
        if not active_uuid or active_uuid == "player_1":
            return
            
        entity_data = self.zone_manager.entities.get(active_uuid)
        if not entity_data:
            self.turn_manager.end_turn(active_uuid)
            return
            
        tags = entity_data.get("tags", [])
        if "hostile" not in tags:
            # Passive entity, just pass turn
            self.turn_manager.end_turn(active_uuid)
            return
            
        # Hostile Entity Logic Loop
        self._take_turn(active_uuid, entity_data)
        
    def _take_turn(self, active_uuid: str, entity_data: Dict[str, Any]):
        name = entity_data.get("name", "Enemy")
        px, py = self.zone_manager.get_entity_pos("player_1")
        ex, ey = self.zone_manager.get_entity_pos(active_uuid)
        
        if px == -1 or ex == -1:
            self.turn_manager.end_turn(active_uuid)
            return
            
        dist = math.hypot(px - ex, py - ey)
        
        actions_taken = []
        
        # 1. Move if out of range
        if dist > 1.5 and self.turn_manager.can_act(active_uuid, "move"):
            # Simple vector movement
            dx = 1 if px > ex else (-1 if px < ex else 0)
            dy = 1 if py > ey else (-1 if py < ey else 0)
            
            new_x = ex + dx
            new_y = ey + dy
            
            # Check collision
            if new_y >= 0 and new_y < len(self.zone_manager.grid_data) and new_x >= 0 and new_x < len(self.zone_manager.grid_data[0]):
                node = self.zone_manager.grid_data[new_y][new_x]
                if node.get("tile_type") != "wall" and "obstacle" not in node.get("tags", []):
                    # Check entity collision
                    collision = False
                    for eid, edata in self.zone_manager.entities.items():
                        if edata["x"] == new_x and edata["y"] == new_y:
                            collision = True
                            break
                            
                    if not collision:
                        self.turn_manager.consume_beat(active_uuid, "move")
                        self.bus.publish("MOVE_ENTITY", {
                            "uuid": active_uuid,
                            "dx": dx, "dy": dy
                        })
                        ex, ey = new_x, new_y
                        dist = math.hypot(px - ex, py - ey)
                        actions_taken.append(f"{name} moved closer.")

        # 2. Attack if in range
        if dist <= 1.5 and self.turn_manager.can_act(active_uuid, "stamina"):
            self.turn_manager.consume_beat(active_uuid, "stamina")
            actions_taken.append(f"{name} attacked the Player!")
            
            payload = {
                "attacker": active_uuid,
                "defender": "player_1",
                "offense_stat": 6, 
                "defense_stat": 5,
                "is_physical": True,
                "attacker_tags": entity_data.get("tags", []),
                "defender_tags": [],
                "technique": "Savage Strike",
                "effort": 1
            }
            
            self.bus.publish("COMBAT_ACTION_DECLARED", payload)
            
        # 3. Narrate AI turn
        if actions_taken:
            combined_action = " ".join(actions_taken)
            self.bus.publish("EXECUTE_AI_INTENT", {
                "intent": f"System: Enemy Turn ({name}). {combined_action} Narrate their actions from the player's perspective in 1-2 brutal sentences.",
                "system_prompt": True
            })
            
        # End Turn
        self.turn_manager.end_turn(active_uuid)
