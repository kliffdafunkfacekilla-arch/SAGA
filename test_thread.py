import threading
from llama_cpp import Llama

def run_worker():
    print("Worker thread started...")
    try:
        llama = Llama(
            model_path=r"C:\Users\krazy\Desktop\SAGA\models\phi-3-mini-4k-instruct-q4.gguf",
            n_ctx=4096,
            n_threads=2,
            n_gpu_layers=0,
            verbose=True
        )
        print("Loaded in standard threading.Thread successfully.")
    except Exception as e:
        print(f"Crash in thread: {e}")

if __name__ == "__main__":
    t = threading.Thread(target=run_worker)
    t.start()
    t.join()
