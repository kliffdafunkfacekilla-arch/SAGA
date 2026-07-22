import os
from pathlib import Path

try:
    from llama_cpp import Llama
except ImportError:  # pragma: no cover
    Llama = None  # type: ignore

class AIDirector:
    """Wraps a local GGUF model using llama-cpp-python.

    Provides compatible ``parse_intent``, ``generate_llm_prompt``, and Reactive Seed generation.
    Expects a ``models`` folder with a ``*.gguf`` file.
    """

    def __init__(self, model_path: str | os.PathLike = None):
        default_dir = Path(__file__).resolve().parents[1] / "models"
        if model_path is None:
            candidates = list(default_dir.glob("*.gguf"))
            if not candidates:
                raise FileNotFoundError(
                    f"No GGUF model found in {default_dir}. Place a .gguf model file there."
                )
            model_path = candidates[0]
        self.model_path = Path(model_path)
        if not self.model_path.is_file():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        try:
            self._llama = Llama(
            model_path=str(self.model_path),
            n_ctx=512,
            n_threads=2,
            n_gpu_layers=0,
            verbose=True,
        )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            with open("llama_error_log.txt", "w") as f:
                f.write(f"FAILED TO INIT LLAMA:\n{error_details}")
            print(f"\n\n[CRITICAL ERROR IN LLAMA INIT]: {e}")
            
            # Fallback to a dummy no-op Llama implementation to prevent crash
            class _DummyLlama:
                def __call__(self, *args, **kwargs):
                    return {"choices": [{"text": "[Model failed to initialize]"}]}
            self._llama = _DummyLlama()
            
        self.system_prompt = (
            "You are a Voice Actor and Style Translator for a gritty tabletop RPG. "
            "You have ZERO agency. You cannot invent outcomes, characters, or consequences. "
            "Your ONLY job is to take the mechanical facts provided to you and rephrase them into a gritty narrative tone, or translate dialogue into a specific dialect. "
            "DO NOT ADD ANY NEW INFORMATION."
        )

    def _extract_json(self, raw_text: str, default: dict) -> dict:
        """Safely extracts JSON from hallucinated or malformed LLM outputs."""
        try:
            if not raw_text: return default
            match = re.search(r'\{.*\}', raw_text.replace("\n", ""), re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(raw_text)
        except Exception:
            return default

    def parse_intent(self, intent_raw: str) -> dict:
        parts = intent_raw.split()
        target = parts[0] if parts else ""
        return {"target": target}

    def extract_anomaly_equation(self, intent_raw: str) -> str:
        """
        Uses the LLM to parse a spoken spell into the BRUTAL Engine Anomaly Equation.
        Returns a JSON string.
        """
        prompt = (
            "You are a rule parser for the BRUTAL RPG Engine. The player is casting an Anomaly (magic spell).\n"
            "Extract the spell parameters into this exact JSON format:\n"
            "{\n"
            '  "shape": "[point, line, cone, burst, wall, or aura]",\n'
            '  "school": "[Mass, Ordo, Motus, Flux, Vita, Nexus, Anumis, Ratio, Lux, Omen, Aura, or Lex]",\n'
            '  "effect_rank": [1 to 10],\n'
            '  "power_scale": [1 to 10]\n'
            "}\n\n"
            f"Player spell: '{intent_raw}'\n"
            "Output ONLY the JSON:\n"
        )
        
        output = self._llama(
            prompt,
            max_tokens=64,
            temperature=0.1,
            top_p=0.9,
            stop=["}"],
        )
        
        raw_text = output.get("choices", [{}])[0].get("text", "").strip()
        # Add the closing brace since it was used as a stop token
        if "{" in raw_text and not raw_text.endswith("}"):
            raw_text += "\n}"
            
        # Instead of returning raw string, we will return the safely parsed dict serialized
        fallback = {"shape": "point", "school": "Lex", "effect_rank": 1, "power_scale": 1}
        parsed = self._extract_json(raw_text, fallback)
        return json.dumps(parsed)

    def generate_llm_prompt(self, mechanical_result: str, context: str, intent_raw: str = None, filters: str = "") -> str:
        if intent_raw and "talk to" in intent_raw.lower():
            return self.generate_dialogue_prompt(mechanical_result, context, intent_raw, filters)
            
        full_prompt = (
            f"<|system|>\n{self.system_prompt}\n"
            f"{'STRICT CONTENT FILTER: Do NOT include any themes of ' + filters + ' under any circumstances.' if filters else ''}\n<|end|>\n"
            f"<|user|>\n"
            f"Mechanical Result (FACTS to rephrase):\n{mechanical_result}\n\n"
            f"CRITICAL DIRECTIVE:\n"
            f"1. Rewrite the Mechanical Result as a gritty narrative sentence.\n"
            f"2. DO NOT add any new points of interest, NPCs, or outcomes.\n"
            f"3. Keep it brief. 1 to 2 sentences maximum.\n"
            f"<|end|>\n"
            f"<|assistant|>\n"
        )
        
        output = self._llama(
            full_prompt,
            max_tokens=128,
            temperature=0.3,
            top_p=0.9,
            stop=["\n\n"],
        )
        return output.get("choices", [{}])[0].get("text", "").strip()

    def generate_dialogue_prompt(self, mechanical_result: str, context: str, intent_raw: str, filters: str = "") -> str:
        full_prompt = (
            f"<|system|>\n{self.system_prompt}\n"
            f"{'STRICT CONTENT FILTER: Do NOT include any themes of ' + filters + ' under any circumstances.' if filters else ''}\n<|end|>\n"
            f"<|user|>\n"
            f"The player says: '{intent_raw}'\n"
            f"NPC State: {mechanical_result}\n\n"
            f"CRITICAL DIRECTIVE:\n"
            f"1. Generate the exact spoken dialogue response from the NPC.\n"
            f"2. Do NOT describe the room or the NPC's actions.\n"
            f"3. Use a gritty, distrustful tone.\n"
            f"<|end|>\n"
            f"<|assistant|>\n"
        )
        output = self._llama(
            full_prompt,
            max_tokens=256,
            temperature=0.7,
            top_p=0.9,
            stop=["\n\n"],
        )
        return output.get("choices", [{}])[0].get("text", "").strip()

    def build_director_prompt_with_spine(self, location_name: str, local_lore: str, subtle_seeds: list, campaign_weaver, filters: str = "") -> str:
        """Constructs a rigidly templated description of the room without allowing hallucinated additions."""
        seed_whispers = "\n".join([f"- {seed.subtle_description}" for seed in subtle_seeds])
        
        full_prompt = (
            f"<|system|>\n{self.system_prompt}\n"
            f"{'STRICT CONTENT FILTER: Do NOT include any themes of ' + filters + ' under any circumstances.' if filters else ''}\n<|end|>\n"
            f"<|user|>\n"
            f"LOCATION: {location_name}\n"
            f"LORE: {local_lore}\n"
            f"ACTIVE THREATS/SEEDS: {seed_whispers if seed_whispers else 'None'}\n\n"
            f"CRITICAL DIRECTIVE: \n"
            f"1. Read the Location, Lore, and Threats and combine them into a 2-sentence description of what the player sees.\n"
            f"2. DO NOT add any NPCs, items, or monsters that are not explicitly listed in the facts above.\n"
            f"3. End by asking 'What do you do?'\n"
            f"<|end|>\n"
            f"<|assistant|>\n"
        )
        
        output = self._llama(
            full_prompt,
            max_tokens=256,
            temperature=0.7,
            top_p=0.9,
            stop=["\n\n"],
        )
        return output.get("choices", [{}])[0].get("text", "").strip()

    def evaluate_action_for_seed(self, intent_raw: str, mechanical_result: str) -> str:
        """Analyzes an action to see if it generates a new Reactive Seed."""
        prompt = (
            "You are evaluating a player's action for consequences in a living RPG world.\n"
            f"Action: {intent_raw}\n"
            f"Result: {mechanical_result}\n\n"
            "If this action caused a localized consequence (e.g., leaving an NPC unconscious, breaking a door, stealing an item), output a JSON block for a Reactive Seed.\n"
            "If it was a mundane action with no lingering consequence, output exactly: NONE.\n\n"
            "JSON Format:\n"
            "{\n"
            '  "origin_action": "brief description of what they did",\n'
            '  "subtle_description": "A subtle environmental clue that something changed (e.g., blood on the floor, a nervous guard, a missing component).",\n'
            '  "target_entity": "The person or object affected"\n'
            "}\n"
            "Output ONLY the JSON or NONE:\n"
        )
        
        output = self._llama(
            prompt,
            max_tokens=128,
            temperature=0.1,
            top_p=0.9,
            stop=["}"],
        )
        
        raw_text = output.get("choices", [{}])[0].get("text", "").strip()
        if raw_text == "NONE":
            return None
            
        if "{" in raw_text and not raw_text.endswith("}"):
            raw_text += "\n}"
            
        return raw_text
