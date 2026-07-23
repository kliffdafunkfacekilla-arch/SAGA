import sqlite3
import os
import csv
import glob
import re

DB_PATH = "okasha_world.db"
OKASHA_DIR = r"C:\Users\krazy\Desktop\Okasha"

def get_latest_csv(pattern):
    files = glob.glob(os.path.join(OKASHA_DIR, pattern))
    if not files:
        return None
    # Sort by modification time to get the newest, or just alphabetical if timestamps are in name
    return sorted(files)[-1]

def setup_tables(conn):
    cursor = conn.cursor()
    # Cultures Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cultures (
            id INTEGER PRIMARY KEY,
            name TEXT,
            color TEXT,
            expansionism REAL,
            type TEXT,
            area_km2 INTEGER,
            population INTEGER,
            namesbase TEXT,
            emblems_shape TEXT
        )
    ''')
    cursor.execute('DELETE FROM cultures')
    
    # Update Factions (States) Table
    # The existing table is: (id TEXT, name TEXT, ideology TEXT, current_status TEXT)
    # We will expand or replace it
    cursor.execute('DROP TABLE IF EXISTS factions')
    cursor.execute('''
        CREATE TABLE factions (
            id TEXT PRIMARY KEY,
            name TEXT,
            form TEXT,
            culture TEXT,
            type TEXT,
            expansionism REAL,
            cells INTEGER,
            burgs INTEGER,
            area_km2 INTEGER,
            total_population INTEGER
        )
    ''')
    
    # Detailed Lore Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detailed_lore (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter TEXT,
            title TEXT,
            content TEXT
        )
    ''')
    cursor.execute('DELETE FROM detailed_lore')
    conn.commit()

def parse_cultures(conn):
    csv_file = get_latest_csv("Okasha Cultures*.csv")
    if not csv_file:
        print("No cultures CSV found.")
        return
        
    cursor = conn.cursor()
    print(f"Parsing {csv_file}...")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Id'): continue
            cursor.execute('''
                INSERT INTO cultures (id, name, color, expansionism, type, area_km2, population, namesbase, emblems_shape)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                int(row['Id']),
                row.get('Name', ''),
                row.get('Color', ''),
                float(row.get('Expansionism', 0) or 0),
                row.get('Type', ''),
                int(row.get('Area km2', 0) or 0),
                int(row.get('Population', 0) or 0),
                row.get('Namesbase', ''),
                row.get('Emblems Shape', '')
            ))
    conn.commit()

def parse_factions(conn):
    csv_file = get_latest_csv("Okasha States*.csv")
    if not csv_file:
        print("No states CSV found.")
        return
        
    cursor = conn.cursor()
    print(f"Parsing {csv_file}...")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Id'): continue
            cursor.execute('''
                INSERT INTO factions (id, name, form, culture, type, expansionism, cells, burgs, area_km2, total_population)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['Id'],
                row.get('Full Name', row.get('State', '')),
                row.get('Form', ''),
                row.get('Culture', ''),
                row.get('Type', ''),
                float(row.get('Expansionism', 0) or 0),
                int(row.get('Cells', 0) or 0),
                int(row.get('Burgs', 0) or 0),
                int(row.get('Area km2', 0) or 0),
                int(row.get('Total Population', 0) or 0)
            ))
    conn.commit()

def parse_markdown_lore(conn):
    md_files = glob.glob(os.path.join(OKASHA_DIR, "Chapter_*.md"))
    cursor = conn.cursor()
    
    # Regex to find ## Master Lore: <Title> and capture the title and the content following it
    for md_file in md_files:
        chapter_name = os.path.basename(md_file).replace('_v1.6.md', '').replace('_', ' ')
        print(f"Parsing {chapter_name}...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        sections = content.split("## Master Lore:")
        
        for i, section in enumerate(sections):
            if i == 0:
                intro_text = section.strip()
                if len(intro_text) > 100:
                    cursor.execute(
                        "INSERT INTO detailed_lore (chapter, title, content) VALUES (?, ?, ?)",
                        (chapter_name, "Chapter Intro", intro_text)
                    )
                continue
                
            lines = section.split('\n', 1)
            if len(lines) < 2: continue
            
            title = lines[0].strip()
            body = lines[1].strip()
            
            # Clean up frontmatter tags that might immediately follow the title
            body = re.sub(r'---[\s\S]*?---', '', body, count=1).strip()
            
            cursor.execute(
                "INSERT INTO detailed_lore (chapter, title, content) VALUES (?, ?, ?)",
                (chapter_name, title, body)
            )
            
    conn.commit()

def main():
    print("Starting Lore Parser...")
    conn = sqlite3.connect(DB_PATH)
    setup_tables(conn)
    parse_cultures(conn)
    parse_factions(conn)
    parse_markdown_lore(conn)
    conn.close()
    print("Lore parsing complete!")

if __name__ == "__main__":
    main()
