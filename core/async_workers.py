import threading
import queue
from core.event_bus import event_bus

class AsyncWorkerPool:
    """
    Manages background thread queues for heavy operations (AI, TTS, STT).
    Listens for REQUEST events on the Event Bus and publishes RESPONSE events.
    """
    def __init__(self, ai_director=None):
        self.ai_director = ai_director
        
        # Queues
        self.ai_queue = queue.Queue()
        self.tts_queue = queue.Queue()
        
        # Threads
        self.ai_thread = threading.Thread(target=self._ai_worker_loop, daemon=True)
        self.tts_thread = threading.Thread(target=self._tts_worker_loop, daemon=True)
        
        self.ai_thread.start()
        self.tts_thread.start()
        
        # Subscriptions
        event_bus.subscribe("REQUEST_AI_PROMPT", self._handle_ai_request)
        event_bus.subscribe("REQUEST_TTS", self._handle_tts_request)
        
    def _handle_ai_request(self, payload: dict):
        """payload expects: {'mechanical_result': str, 'context': str, 'intent_raw': str}"""
        self.ai_queue.put(payload)
        
    def _handle_tts_request(self, payload: dict):
        """payload expects: {'text': str}"""
        self.tts_queue.put(payload)
        
    def _ai_worker_loop(self):
        while True:
            try:
                task = self.ai_queue.get()
                if self.ai_director:
                    # Generate the prompt
                    response = self.ai_director.generate_llm_prompt(
                        mechanical_result=task.get('mechanical_result', ''),
                        context=task.get('context', ''),
                        intent_raw=task.get('intent_raw', '')
                    )
                    event_bus.publish("RESPONSE_AI_READY", {"response": response, "original_task": task})
                self.ai_queue.task_done()
            except Exception as e:
                print(f"[AsyncWorkerPool] AI Worker Error: {e}")

    def _tts_worker_loop(self):
        # We need a local TTS instance since COM objects (like pyttsx3 on Windows) 
        # often require being initialized in the thread they are used in.
        try:
            import pyttsx3
            tts_engine = pyttsx3.init()
            # Basic config
            tts_engine.setProperty('rate', 200)
            tts_engine.setProperty('volume', 0.9)
        except ImportError:
            tts_engine = None
            
        while True:
            try:
                task = self.tts_queue.get()
                text = task.get('text', '')
                if text and tts_engine:
                    tts_engine.say(text)
                    tts_engine.runAndWait()
                event_bus.publish("RESPONSE_TTS_COMPLETE", {"text": text})
                self.tts_queue.task_done()
            except Exception as e:
                print(f"[AsyncWorkerPool] TTS Worker Error: {e}")
