import json
import re

class DialogueSystem:
    def __init__(self, ecs_manager, clash_calculator, ai_director):
        self.ecs = ecs_manager
        self.clash = clash_calculator
        self.ai = ai_director
        self.conversation_memory = {}

    def speak_to_npc(self, npc_name, player_speech, current_battlemap, plot_hook):
        if not current_battlemap:
            return "There is no one here to speak to."
            
        entities = current_battlemap.get("entities", [])
        npc_entity = next((e for e in entities if npc_name.lower() in e.get("name", "").lower()), None)
        
        if not npc_entity:
            return f"{npc_name} is not here."
            
        npc_tags = npc_entity.get("tags", ["generic"])
        health = npc_entity.get("health", 100)
        weather = current_battlemap.get("weather_tags", ["clear"])
        
        if npc_name not in self.conversation_memory:
            self.conversation_memory[npc_name] = []
            
        history = "\n".join(self.conversation_memory[npc_name][-3:])
        
        system_prompt = f"""
        You are an NPC in a dark fantasy game. Respond directly to the player.
        
        YOUR CURRENT STATE:
        - Identity Tags: {', '.join(npc_tags)}
        - Health: {health}/100
        
        SCENE CONTEXT:
        - Weather/Environment: {', '.join(weather)}
        - Current Plot Hook: {plot_hook}
        
        RULES:
        1. Keep responses under 3 sentences. Be concise.
        2. You MUST output your response in valid JSON format.
        3. Do NOT offer items, weapons, or money.
        4. Do NOT make up names for cities or factions not mentioned in the Plot Hook.
        
        OUTPUT SCHEMA:
        {{
            "dialogue": "What the NPC actually says.",
            "intent": "continue|attack|flee"
        }}
        
        INTENT RULES:
        - 'continue': The conversation is proceeding normally.
        - 'attack': The player insulted you, threatened you, or you are hostile.
        - 'flee': The player terrified you or your health is too low to fight.
        """
        
        full_prompt = f"{system_prompt}\n\nRecent History:\n{history}\n\nPlayer: {player_speech}\nNPC:"
        
        if hasattr(self.ai, "_llama"):
            raw_response = self.ai._llama(
                full_prompt,
                max_tokens=200,
                stop=["Player:", "\n\n"],
                echo=False,
                temperature=0.6
            )["choices"][0]["text"].strip()
        else:
            raw_response = '{"dialogue": "I have nothing to say.", "intent": "continue"}'
            
        try:
            match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            parsed_data = json.loads(match.group(0))
            dialogue = parsed_data.get("dialogue", "...")
            intent = parsed_data.get("intent", "continue")
        except (json.JSONDecodeError, AttributeError):
            print("Dialogue Parse Error. Defaulting to safe response.")
            dialogue = "I... I don't know what you're talking about."
            intent = "continue"

        print(f"NPC [{npc_name}] says: {dialogue}")
        
        if intent == "attack":
            print(f"--> SYSTEM: NPC {npc_name} was provoked!")
            # Convert to ClashCalculator call
            # In a true ECS this might use entity ID, but here we pass the name
            if self.clash:
                # The Clash Calculator expects resolve_action(actor_name, intent, target_name)
                # But since the dialogue system triggers it, we need to pass a mock string or let the engine handle it.
                # For now, we will add an "attacking" tag so the NPC AI picks it up, or directly resolve.
                if "hostile" not in npc_tags:
                    npc_entity["tags"].append("hostile")
                    
        elif intent == "flee":
            print(f"--> SYSTEM: NPC {npc_name} is fleeing!")
            if "fleeing" not in npc_tags:
                npc_entity["tags"].append("fleeing")
                
        self.conversation_memory[npc_name].append(f"Player: {player_speech}")
        self.conversation_memory[npc_name].append(f"NPC: {dialogue}")
        
        return dialogue
