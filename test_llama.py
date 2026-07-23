from llama_cpp import Llama

model_path = r"C:\Users\krazy\Desktop\SAGA\models\phi-3-mini-4k-instruct-q4.gguf"

print(f"Loading {model_path}...")
try:
    llama = Llama(
        model_path=model_path,
        n_ctx=4096,
        n_threads=2,
        n_gpu_layers=0,
        verbose=True
    )
    print("Successfully loaded.")
except Exception as e:
    print(f"Failed: {e}")
