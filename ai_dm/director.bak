import os
from pathlib import Path

try:
    from llama_cpp import Llama
except ImportError:  # pragma: no cover
    Llama = None  # type: ignore

class AIDirector:
    """Wraps a local GGUF model using llama-cpp-python.

    Provides compatible ``parse_intent`` and ``generate_llm_prompt`` methods.
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

    def parse_intent(self, intent_raw: str) -> dict:
        parts = intent_raw.split()
        target = parts[0] if parts else ""
        return {"target": target}

    def generate_llm_prompt(self, mechanical_result: str, context: str) -> str:
        prompt = (
            f"You are the narrator of a tabletop RPG. Use the mechanical result and the given context to produce a short, vivid description.\n"
            f"Mechanics: {mechanical_result}\n"
            f"Context:{context}\n"
            "Response:"
        )
        output = self._llama(
            prompt,
            max_tokens=256,
            temperature=0.7,
            top_p=0.9,
            stop=["\n\n"],
        )
        return output.get("choices", [{}])[0].get("text", "").strip()
