import sqlite3
import json

class StoryState:
    INIT = "ACT_1_INIT"
    ACT_1_MIDPOINT = "ACT_1_MIDPOINT"
    ACT_1_CLIMAX = "ACT_1_CLIMAX"
    ACT_2_INIT = "ACT_2_INIT"
    ACT_2_MIDPOINT = "ACT_2_MIDPOINT"
    ACT_2_CLIMAX = "ACT_2_CLIMAX"
    ACT_3_INIT = "ACT_3_INIT"
    ACT_3_CLIMAX = "ACT_3_CLIMAX"
    EPILOGUE = "EPILOGUE"

class StoryFSM:
    """
    Finite State Machine to strictly gate Act transitions.
    Prevents background engines from mutating the world state wildly.
    """
    def __init__(self, db_path="okasha_world.db"):
        self.db_path = db_path

    def get_current_state(self) -> str:
        """Fetch the current global state from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT state_data FROM campaign_state WHERE key = 'current_fsm_state'")
            row = c.fetchone()
            conn.close()
            if row:
                return row[0]
            return StoryState.INIT
        except Exception:
            return StoryState.INIT

    def set_state(self, new_state: str):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                "INSERT OR REPLACE INTO campaign_state (key, state_data) VALUES (?, ?)", 
                ("current_fsm_state", new_state)
            )
            conn.commit()
            conn.close()
            print(f"[StoryFSM] Transitioned to {new_state}")
        except Exception as e:
            print(f"[StoryFSM] Error setting state: {e}")

    def can_transition(self, target_state: str) -> bool:
        """
        Validates whether the transition to `target_state` is legal
        based on the current state and world conditions (e.g., filled slots).
        """
        current_state = self.get_current_state()
        
        # Linear progression logic
        progression = [
            StoryState.INIT, StoryState.ACT_1_MIDPOINT, StoryState.ACT_1_CLIMAX,
            StoryState.ACT_2_INIT, StoryState.ACT_2_MIDPOINT, StoryState.ACT_2_CLIMAX,
            StoryState.ACT_3_INIT, StoryState.ACT_3_CLIMAX, StoryState.EPILOGUE
        ]
        
        try:
            current_idx = progression.index(current_state)
            target_idx = progression.index(target_state)
            if target_idx != current_idx + 1:
                return False # Must transition exactly to the next state
        except ValueError:
            return False

        # Additional DB preconditions could go here (e.g. checking 'slots_filled')
        return True

    def attempt_transition(self, target_state: str) -> bool:
        if self.can_transition(target_state):
            self.set_state(target_state)
            from core.event_bus import event_bus
            event_bus.publish("FSM_TRANSITION", {"new_state": target_state})
            return True
        return False
