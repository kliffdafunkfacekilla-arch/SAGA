import os
from pathlib import Path
from llama_cpp import Llama

def test():
    model_path = Path(__file__).resolve().parent / "models" / "phi-3-mini-4k-instruct-q4.gguf"
    print(f"Loading model from {model_path}...")
    try:
        llm = Llama(
            model_path=str(model_path),
            n_ctx=512,
            n_gpu_layers=0,
            verbose=True
        )
        print("SUCCESSFULLY INITIALIZED LLAMA!")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test()
