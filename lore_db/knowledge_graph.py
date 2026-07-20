import sqlite3
import os

class KnowledgeGraphDB:
    """
    Retrieves deeply contextual lore chunks from the ingested Okasha database.
    """
    def __init__(self, db_path="c:/Users/krazy/Desktop/SAGA/okasha_world.db"):
        self.db_path = db_path
        
    def get_context_for_location(self, keywords: str) -> str:
        """
        Retrieves the first chunk of lore that matches the requested keyword.
        """
        if not os.path.exists(self.db_path):
            return "[Lore Missing: Okasha DB not found.]"
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Attempt to find the keyword in the world_lore table
            cursor.execute('''
                SELECT subject, content 
                FROM world_lore 
                WHERE content LIKE ? 
                LIMIT 1
            ''', (f'%{keywords}%',))
            row = cursor.fetchone()
            
            if row:
                subject, content = row
                # Extract a small ~300 character snippet around the keyword
                idx = content.lower().find(keywords.lower())
                start = max(0, idx - 100)
                end = min(len(content), idx + 200)
                snippet = content[start:end].replace('\n', ' ').strip()
                return f"[Lore Archive - {subject}]: '...{snippet}...'"
            else:
                return f"No direct historical records found regarding '{keywords}'."
                
        except sqlite3.OperationalError:
            return "[Lore Missing: world_lore table not properly ingested.]"
        finally:
            conn.close()
