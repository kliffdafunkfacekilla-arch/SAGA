import threading

class SagaEventBus:
    """
    Centralized Event Bus (Pub/Sub) for S.A.G.A.
    All modules should broadcast here instead of talking directly to each other.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SagaEventBus, cls).__new__(cls)
                cls._instance.subscribers = {}
                cls._instance._publish_depth = 0
                cls._instance._publish_lock = threading.RLock()
        return cls._instance

    def subscribe(self, event_type: str, callback):
        with self._publish_lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            if callback not in self.subscribers[event_type]:
                self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, payload=None):
        with self._publish_lock:
            if self._publish_depth > 50:
                print(f"[ERROR] SagaEventBus infinite loop detected on {event_type}! Blocking publish.")
                self._publish_depth = 0
                return
                
            self._publish_depth += 1
            
            # Suppress massive payloads in the console to prevent freezing
            if event_type == "MAP_RENDER":
                print(f"EVENT DISPATCHED - Type: {event_type}, Payload: [OMITTED - TOO LARGE]")
            else:
                payload_str = str(payload)
                if len(payload_str) > 200:
                    print(f"EVENT DISPATCHED - Type: {event_type}, Payload: {payload_str[:200]}...")
                else:
                    print(f"EVENT DISPATCHED - Type: {event_type}, Payload: {payload_str}")
            
            if event_type in self.subscribers:
                for callback in self.subscribers[event_type]:
                    try:
                        callback(payload)
                    except Exception as e:
                        print(f"[ERROR] Subscriber callback failed for {event_type}: {e}")
                        
            self._publish_depth -= 1

# Global singleton instance for easy imports
event_bus = SagaEventBus()
