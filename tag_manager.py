from interaction_matrix import INTERACTION_MATRIX
import json

class TagManager:
    @staticmethod
    def get_object_tags(obj_id, table, db_cursor):
        # Fetches tags from map_tiles, map_deltas, or player_characters
        # We need to know which table to query
        db_cursor.execute(f"SELECT tags FROM {table} WHERE id = ?", (obj_id,))
        result = db_cursor.fetchone()
        if not result or not result[0]:
            return []
            
        try:
            return json.loads(result[0])
        except:
            return [t.strip() for t in result[0].strip('[]').replace('"', '').replace("'", "").split(',') if t.strip()]

    @staticmethod
    def resolve(power_tag, target_id, table, db_cursor):
        target_tags = TagManager.get_object_tags(target_id, table, db_cursor)
        
        # Check interaction matrix for each tag on the object
        for tag in target_tags:
            outcome = INTERACTION_MATRIX.get((power_tag, tag))
            if outcome:
                return outcome
        return "NO_EFFECT"

    @staticmethod
    def add_state(target_id, table, new_state, db_cursor):
        # Appends a state like 'Burning' or 'Barricaded' to the object's tags
        current_tags = TagManager.get_object_tags(target_id, table, db_cursor)
        if new_state not in current_tags:
            current_tags.append(new_state)
            db_cursor.execute(f"UPDATE {table} SET tags = ? WHERE id = ?", 
                              (json.dumps(current_tags), target_id))
