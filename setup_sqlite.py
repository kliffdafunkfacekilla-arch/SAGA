import sqlite3

def setup_database():
    conn = sqlite3.connect('okasha_world.db')
    cursor = conn.cursor()
    
    # Drop the old table to replace it with the new structured one
    cursor.execute('DROP TABLE IF EXISTS region_cells;')
    
    # New region_cells schema as requested
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS region_cells (
        cell_id INTEGER PRIMARY KEY,
        x_coord INTEGER,
        y_coord INTEGER,
        terrain_type TEXT,
        occupant TEXT
    );
    ''')
    
    # Add a table for world lore
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS world_lore (
        lore_id INTEGER PRIMARY KEY,
        subject TEXT,
        content TEXT,
        source_file TEXT
    );
    ''')
    
    # Add tables for the celestial calendar
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS celestial_calendar (
        month_name TEXT PRIMARY KEY,
        quadrant INTEGER,
        season_name TEXT,
        aether_intensity TEXT
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS days_of_week (
        day_order INTEGER PRIMARY KEY,
        day_name TEXT
    );
    ''')
    
    # 1. CLIMATE & COSMOLOGY: Link cells to the current Aether state
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS world_state (
        current_quadrant INTEGER,
        current_month TEXT,
        global_aether_modifier REAL
    );
    ''')
    
    # Initialize world state if empty
    cursor.execute("SELECT COUNT(*) FROM world_state")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO world_state VALUES (1, 'Nexar', 1.0)")
        
    # 2. ECOLOGY: Resources based on region
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ecology (
        cell_id INTEGER REFERENCES region_cells(cell_id),
        resource_type TEXT,
        growth_rate REAL,
        is_volatile BOOLEAN
    );
    ''')
    
    # 3. ECONOMY & CIVILIZATION: Faction influence
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS factions (
        faction_id INTEGER PRIMARY KEY,
        name TEXT,
        strength INTEGER,
        territory_center_id INTEGER REFERENCES region_cells(cell_id)
    );
    ''')
    
    # 4. ECOLOGY & BIOLOGY: Dynamic Resource State
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cell_resources (
        cell_id INTEGER PRIMARY KEY,
        plant_pop REAL,
        prey_pop REAL,
        predator_pop REAL,
        stock_basic TEXT,
        stock_quantity INTEGER,
        harvest_pressure REAL DEFAULT 0.0,
        FOREIGN KEY(cell_id) REFERENCES region_cells(cell_id)
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rare_deposits (
        cell_id INTEGER,
        resource_name TEXT,
        remaining_yield INTEGER,
        extraction_difficulty INTEGER,
        FOREIGN KEY(cell_id) REFERENCES region_cells(cell_id)
    );
    ''')
    
    # 5. INTEGRATED REALITY: Foundations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS burgs (
        id INTEGER PRIMARY KEY,
        name TEXT,
        culture TEXT,
        population INTEGER
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goods_catalog (
        item_id INTEGER PRIMARY KEY,
        name TEXT,
        type TEXT
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS burg_stocks (
        burg_id INTEGER,
        good_id INTEGER,
        food_type TEXT,
        stock REAL,
        consumption REAL,
        FOREIGN KEY(burg_id) REFERENCES burgs(id),
        FOREIGN KEY(good_id) REFERENCES goods_catalog(item_id)
    );
    ''')
    
    # 6. INTEGRATED REALITY: Linking
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS burg_production (
        burg_id INTEGER,
        good_id INTEGER,
        production_rate REAL,
        FOREIGN KEY(burg_id) REFERENCES burgs(id),
        FOREIGN KEY(good_id) REFERENCES goods_catalog(item_id)
    );
    ''')
    
    # 7. FACTION AI & DIPLOMACY
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faction_relations (
        faction_a TEXT,
        faction_b TEXT,
        status TEXT,
        PRIMARY KEY (faction_a, faction_b)
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faction_military (
        faction_name TEXT PRIMARY KEY,
        military_strength REAL,
        treasury REAL
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trade_agreements (
        faction_a TEXT,
        faction_b TEXT,
        good_type TEXT,
        volume REAL
    );
    ''')
    
    conn.commit()
    conn.close()
    print("Database schema updated with world_lore and new region_cells.")

if __name__ == "__main__":
    setup_database()
