import os
import sys
import requests

def main():
    # Correct download URL for Phi-3 mini 4k instruct (q4) model
    url = "https://huggingface.co/microsoft/phi-3-mini-4k-instruct-gguf/resolve/main/phi-3-mini-4k-instruct-q4.gguf"
    out_dir = r"C:\Users\krazy\Desktop\SAGA\models"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "phi-3-mini-4k-instruct-q4.gguf")
    print(f"Downloading model to {out_path} ...")
    try:
        with requests.get(url, stream=True, timeout=180) as r:
            r.raise_for_status()
            total = 0
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total += len(chunk)
            print(f"Download complete. Size: {total} bytes")
    except Exception as e:
        print("Error during download:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
