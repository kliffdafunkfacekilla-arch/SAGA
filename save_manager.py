import sqlite3
import os
import shutil
import datetime
import config

# Create the saves directory if it doesn't exist
os.makedirs('saves', exist_ok=True)

def init_master_db():
    conn = sqlite3.connect(config.MASTER_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS meta_saves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_name TEXT,
            character_name TEXT,
            timestamp TEXT,
            file_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_new_save(save_name, character_name):
    init_master_db()
    
    # 1. Copy the template (base_world.db) to a new slot
    # For MVP, we'll just copy okasha_world.db to saves/
    base_db = 'okasha_world.db'
    if not os.path.exists(base_db):
        return {"status": "error", "message": "Base world DB not found."}
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = f"saves/slot_{timestamp}.db"
    
    shutil.copy2(base_db, file_path)
    
    # 2. Add to master tracking
    conn = sqlite3.connect(config.MASTER_DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO meta_saves (save_name, character_name, timestamp, file_path) VALUES (?, ?, ?, ?)",
              (save_name, character_name, timestamp, file_path))
    conn.commit()
    conn.close()
    
    # 3. Update active config
    config.ACTIVE_DB_PATH = file_path
    
    return {"status": "success", "file_path": file_path}

def load_save(save_id):
    init_master_db()
    conn = sqlite3.connect(config.MASTER_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT file_path FROM meta_saves WHERE id = ?", (save_id,))
    row = c.fetchone()
    conn.close()
    
    if row and os.path.exists(row[0]):
        config.ACTIVE_DB_PATH = row[0]
        return {"status": "success", "file_path": row[0]}
    
    return {"status": "error", "message": "Save file not found."}
