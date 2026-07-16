import sqlite3

def ingest_calendar(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Seed the Months/Quadrants
    calendar_data = [
        ('Nexar', 1, 'Shadowburn', 'High'), ('Massis', 1, 'Shadowburn', 'High'), ('Motom', 1, 'Dryspell', 'High'),
        ('Fluxen', 2, 'Frostin', 'Low'), ('Vitan', 2, 'Frostin', 'Low'), ('Lexis', 2, 'GreenSpan', 'Low'),
        ('Ration', 3, 'Highreach', 'High'), ('Ordis', 3, 'Highreach', 'High'), ('Luxen', 3, 'Spurium', 'High'),
        ('Omin', 4, 'Dimfreeze', 'Low'), ('Aurum', 4, 'Dimfreeze', 'Low'), ('Anum', 4, 'Dimfreeze', 'Low')
    ]
    
    cursor.executemany("INSERT OR REPLACE INTO celestial_calendar VALUES (?,?,?,?)", calendar_data)
    conn.commit()
    conn.close()
    print("Calendar data successfully ingested.")

if __name__ == "__main__":
    ingest_calendar('okasha_world.db')
