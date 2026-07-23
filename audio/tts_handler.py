import os
import threading
import asyncio
import edge_tts
import pygame

class TTSHandler:
    def __init__(self):
        self.voice = "en-GB-RyanNeural"
        pygame.mixer.init()
        self._lock = threading.Lock()
        
    def speak(self, text: str):
        print(f"\n[AI NARRATOR]: {text}\n")
        asyncio.run(self._async_speak(text))

    async def _async_speak(self, text: str):
        if not text or not text.strip():
            return

        with self._lock:
            try:
                communicate = edge_tts.Communicate(text, self.voice)
                audio_file = f"temp_speech_{threading.get_ident()}.mp3"
                await communicate.save(audio_file)
                
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
                pygame.mixer.music.unload()
                try:
                    os.remove(audio_file)
                except OSError:
                    pass
            except Exception as e:
                print(f"[SYSTEM ERROR]: TTS failed: {e}")

    def speak_async(self, text: str):
        t = threading.Thread(target=self.speak, args=(text,), daemon=True)
        t.start()
        return t
