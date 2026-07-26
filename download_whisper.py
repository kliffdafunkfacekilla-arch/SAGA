import os
from faster_whisper import WhisperModel

def download_model():
    print("Downloading tiny.en to local models folder...")
    os.makedirs("models/whisper", exist_ok=True)
    # By setting local_files_only=False and providing a download_root, it fetches and caches it here
    model = WhisperModel("tiny.en", device="cpu", compute_type="int8", download_root="models/whisper", local_files_only=False)
    print("Download complete.")

if __name__ == "__main__":
    download_model()
