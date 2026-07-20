import json

class AIDirector:
    """
    Translates raw natural language into strict JSON mechanical intents,
    and translates mechanical engine results back into immersive narrative.
    """
    def __init__(self):
        self.system_prompt = """
        You are the BRUTAL Engine Facilitator. 
        Your function is to translate mechanical game data into grim, high-stakes narrative.
        
        STRICT RULES:
        1. DO NOT invent mechanical outcomes (e.g. do not say an enemy died unless the mechanical data says 'Damage: 11+').
        2. DO NOT spew lore unprompted. Use the provided Setting Context to ground the scene (e.g. mention the red sky or the architecture), but never dump historical facts unless explicitly asked.
        3. All entities are 'Biological Chassis'. Frame injuries in visceral, anatomical terms.
        4. Be brief, punchy, and atmospheric.
        """
        
    def parse_intent(self, user_input: str) -> dict:
        """
        Parses raw text into actionable JSON for the Rules Engine.
        (Mocked Ollama response for now)
        """
        user_input = user_input.lower()
        if "attack" in user_input or "hit" in user_input or "strike" in user_input:
            # Attempt to extract target
            words = user_input.split()
            target = "Unknown Entity"
            if "bandit" in user_input: target = "Bandit"
            elif "guard" in user_input: target = "Town Guard"
            elif "blacksmith" in user_input: target = "Blacksmith"
            
            return {"action": "attack", "target": target}
            
        return {"action": "investigate", "target": "Environment"}

    def generate_llm_prompt(self, mechanical_result: dict, context_data: str) -> str:
        """
        Constructs the strict prompt sent to the LLM for generation.
        """
        prompt = f"{self.system_prompt}\n\n"
        prompt += f"--- SETTING & CONTEXT ---\n{context_data}\n\n"
        prompt += f"--- MECHANICAL REALITY ---\n"
        prompt += f"Action Taken: {mechanical_result.get('action')}\n"
        
        if "success" in mechanical_result:
            prompt += f"Success: {mechanical_result['success']}\n"
            prompt += f"Damage Dealt: {mechanical_result.get('damage', 0)}\n"
            prompt += f"System Note: {mechanical_result.get('narrative_hint', '')}\n"
            
        prompt += "\nNARRATE THIS SCENE STRICTLY ADHERING TO THE MECHANICAL REALITY."
        
        # (MOCKING OLLAMA GENERATION FOR LOCAL TESTING)
        return self._mock_ollama_generate(prompt, mechanical_result)
        
    def _mock_ollama_generate(self, prompt: str, mechanical_result: dict) -> str:
        if "narrative_hint" in mechanical_result:
            return f"*** [NARRATIVE AI RESPONSE] ***\n{mechanical_result['narrative_hint']}\n(The AI utilizes the local lore to describe the visceral impact.)"
        return "*** [NARRATIVE AI RESPONSE] ***\nYou survey the grim surroundings. The air is thick with tension."
