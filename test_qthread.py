import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread
from llama_cpp import Llama

class TestWorker(QThread):
    def run(self):
        print("Worker thread started...")
        try:
            llama = Llama(
                model_path=r"C:\Users\krazy\Desktop\SAGA\models\phi-3-mini-4k-instruct-q4.gguf",
                n_ctx=4096,
                n_threads=2,
                n_gpu_layers=0,
                verbose=True
            )
            print("Loaded in QThread successfully.")
        except Exception as e:
            print(f"Crash in QThread: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    worker = TestWorker()
    worker.start()
    worker.wait()
