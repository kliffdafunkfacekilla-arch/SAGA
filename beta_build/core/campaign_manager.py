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
    def __init__(self, bus):
        self.bus = bus
        self.campaign_data = {}
        self.nodes = {}
        
        self.current_act = 1
        self.current_node_id = None
        self.remaining_dynamic_slots = 0
        
        self.bus.subscribe("LOAD_CAMPAIGN", self._on_load_campaign)
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
            
            # Start at intro_01
            self._transition_to_node("intro_01")
            
        except Exception as e:
            logger.error(f"Failed to load campaign {filepath}: {e}")
            
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
                
            if self.remaining_dynamic_slots <= 0:
                self._advance_campaign()
        else:
            logger.warning("Tried to resolve a dynamic slot, but 0 remaining.")
            
    def _advance_campaign(self):
        current = self.nodes.get(self.current_node_id)
        if not current: return
        
        next_nodes = current.get("next_nodes", [])
        if next_nodes:
            # For a true DAG with branches, we might ask the player or check state. 
            # For linear, just take the first.
            self._transition_to_node(next_nodes[0])
        else:
            self.bus.publish("SYSTEM_LOG", {"message": "<br><font color='#FFD700'><b>CAMPAIGN COMPLETE.</b></font>"})
            
    def _on_request_seeds(self, payload: Dict[str, Any]):
        if self.remaining_dynamic_slots > 0:
            env = payload.get("environment", "Unknown location")
            tags = payload.get("tags", [])
            prompt = (
                f"The players are in {env}. Tags: {tags}. "
                f"They need {self.remaining_dynamic_slots} more resolved event(s) to advance the plot. "
                f"Generate 3 minor narrative hooks (Seeds) that fit this environment and the players' current stats. "
                f"Return strictly as a JSON array of strings."
            )
            # Ask the AI director for hooks
            self.bus.publish("EXECUTE_AI_INTENT", {"intent": prompt, "system_prompt": True})
