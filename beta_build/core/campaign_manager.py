"""
campaign_manager.py
Manages the overarching Campaign Spine using a Storylet-based Directed Acyclic Graph (DAG).
"""
import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger("CampaignManager")

class CampaignManager:
    def __init__(self, bus, macro_simulator=None):
        self.bus = bus
        self.macro_simulator = macro_simulator
        self.campaign_data = {}
        self.nodes = {}
        
        self.current_act = 1
        self.current_node_id = None
        self.remaining_dynamic_slots = 0
        
        self.bus.subscribe("LOAD_CAMPAIGN", self._on_load_campaign)
        self.bus.subscribe("INITIATE_BOOT_SEQUENCE", self._on_initiate_boot)
        self.bus.subscribe("RESOLVE_DYNAMIC_SLOT", self._on_resolve_dynamic_slot)
        self.bus.subscribe("REQUEST_SEEDS", self._on_request_seeds)
        
    def _on_load_campaign(self, payload: Dict[str, Any]):
        filepath = payload.get("filepath", "data/campaigns/core_campaign.json")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.campaign_data = json.load(f)
                
            self.nodes = {}
            for act in self.campaign_data.get("acts", []):
                for node in act.get("nodes", []):
                    self.nodes[node["node_id"]] = node
                    
            logger.info(f"Loaded campaign: {self.campaign_data.get('campaign_name')}")
            
            # Start the first node
            first_act = self.campaign_data.get("acts", [])[0]
            first_node = first_act.get("nodes", [])[0]["node_id"]
            self._transition_to_node(first_node)
            
        except Exception as e:
            logger.error(f"Failed to load campaign {filepath}: {e}")
            
    def _on_initiate_boot(self, payload: Dict[str, Any]):
        location = payload.get("location", "Aloa")
        prompt = (
            f"You are the Game Master starting a new campaign in {location}. "
            "Write a rich, immersive opening narrative for the players in 'narrative_prose'. "
            "Then, define the initial world state and entities to populate the map in 'world_updates'. "
            "You MUST return a raw JSON object with the following structure:\n"
            "{\n"
            '  "narrative_prose": "Welcome to the Wastes. The dusty wind howls...",\n'
            '  "world_updates": {\n'
            '    "environment": "dusty town square",\n'
            '    "entities": [\n'
            '      {"name": "Local Merchant", "sprite": "vendor", "tags": ["humanoid", "civilian"]}\n'
            '    ]\n'
            '  }\n'
            "}"
        )
        self.bus.publish("EXECUTE_AI_INTENT", {"intent": prompt, "system_prompt": True, "tag": "boot_sequence", "location": location})
            
    def _transition_to_node(self, node_id: str):
        if node_id not in self.nodes:
            logger.error(f"Node {node_id} not found in campaign DAG!")
            return
            
        self.current_node_id = node_id
        node = self.nodes[node_id]
        
        self.remaining_dynamic_slots = node.get("dynamic_slots", 0)
        
        title = node.get("title", "Unknown")
        desc = node.get("description", "")
        
        if node.get("is_major_plot_point"):
            log_str = f"<br><font color='#FFD700'><b>MAJOR PLOT POINT: {title}</b></font><br><i>{desc}</i><br>"
        else:
            log_str = f"<br><font color='#88CCFF'><b>JOURNEY: {title}</b></font><br><i>{desc}</i><br>Dynamic slots remaining: {self.remaining_dynamic_slots}<br>"
            
        self.bus.publish("SYSTEM_LOG", {"message": log_str})
        
        # Force the AI Director to narrate the new campaign node
        intent_prompt = (
            f"[NARRATIVE INTRO]: The campaign has entered a new phase: '{title}'. "
            f"Context: {desc}. "
            f"You are the Game Master. Write a rich, atmospheric opening paragraph setting the scene for the players. "
            f"Describe the environment, the weather, and what they see. Do not write their actions."
        )
        self.bus.publish("EXECUTE_AI_INTENT", {"intent": intent_prompt})
        
        # Broadcast HUD update
        self.bus.publish("HUD_UPDATE", {
            "dm_data": {
                "current_quest": f"{title}\n{desc}",
                "active_seeds": []
            }
        })
        
        # Autosave Game when reaching a new major node
        self.bus.publish("UI_SAVE_GAME", {})
        
    def append_and_transition(self, new_node: Dict[str, Any]):
        """Dynamically append a generated node to the DAG and transition to it."""
        node_id = new_node.get("node_id")
        if node_id:
            self.nodes[node_id] = new_node
            self._transition_to_node(node_id)
        
    def _on_resolve_dynamic_slot(self, payload: Dict[str, Any]):
        # Called when a player resolves a procedural local event
        if self.remaining_dynamic_slots > 0:
            self.remaining_dynamic_slots -= 1
            logger.info(f"Dynamic slot resolved. Remaining: {self.remaining_dynamic_slots}")
            self.bus.publish("SYSTEM_LOG", {"message": f"<font color='#88CCFF'><i>Dynamic event resolved. Slots remaining before next major plot point: {self.remaining_dynamic_slots}</i></font>"})
            
            # Write resolution to memory store
            resolution = payload.get("resolution", "")
            if resolution:
                self.bus.publish("STORE_MEMORY", {"text": resolution, "type": "plot_resolution"})
                self.bus.publish("EVALUATE_WORLD_MUTATION", {"resolution": resolution})
                
            if self.remaining_dynamic_slots <= 0:
                self._advance_campaign()
        else:
            logger.warning("Tried to resolve a dynamic slot, but 0 remaining.")
            
    def _advance_campaign(self):
        current = self.nodes.get(self.current_node_id)
        if not current: return
        
        self.bus.publish("SYSTEM_LOG", {"message": "<br><font color='#FF5555'><b>[SYSTEM] Analyzing past events to generate next plot phase...</b></font>"})
        self.bus.publish("GENERATE_NEXT_NODE", {"current_node": current})
            
    def _on_request_seeds(self, payload: Dict[str, Any]):
        if self.remaining_dynamic_slots > 0:
            env = payload.get("environment", "Unknown location")
            tags = payload.get("tags", [])
            
            macro_context = ""
            if self.macro_simulator:
                # Assuming location name is roughly the Burg name
                burg_name = payload.get("location", env)
                macro_context = self.macro_simulator.get_burg_context(burg_name)
                
            prompt = (
                f"The players are in {env}. Tags: {tags}. "
                f"Macro World Context: {macro_context}\n"
                f"They need {self.remaining_dynamic_slots} more resolved event(s) to advance the plot. "
                f"Generate 3 minor narrative hooks (Seeds) that fit this environment and the Macro World Context (e.g. Unrest, Wealth). "
                f"Return strictly as a JSON array of strings."
            )
            # Ask the AI director for hooks
            self.bus.publish("EXECUTE_AI_INTENT", {"intent": prompt, "system_prompt": True})
