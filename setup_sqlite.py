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
        CREATE TABLE IF NOT EXISTS biomes (
            id INTEGER PRIMARY KEY,
            name TEXT,
            color TEXT,
            habitability TEXT,
            cells INTEGER,
            area_km2 REAL,
            population INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            cells INTEGER,
            x_coord REAL,
            y_coord REAL,
            lat REAL,
            lon REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS markers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            icon TEXT,
            x_coord REAL,
            y_coord REAL,
            lat REAL,
            lon REAL,
            note TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            length_km REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS region_cells (
            region_name TEXT,
            cell_id INTEGER,
            PRIMARY KEY (region_name, cell_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS story_hooks (
            id INTEGER PRIMARY KEY,
            location_type TEXT,
            location_id INTEGER,
            hook_category TEXT,
            description TEXT,
            status TEXT DEFAULT 'Active'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lore_crosslinks (
            hook_id INTEGER,
            lore_id INTEGER,
            PRIMARY KEY (hook_id, lore_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS map_tiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_type TEXT,
            location_id INTEGER,
            cluster_id INTEGER, -- 1 to 25
            base_biome TEXT,
            feature_archetype TEXT,
            seed INTEGER,
            discovered BOOLEAN DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS map_deltas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tile_id INTEGER,
            local_x INTEGER,
            local_y INTEGER,
            change_type TEXT,
            details TEXT,
            FOREIGN KEY(tile_id) REFERENCES map_tiles(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rivers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            length_km REAL
        )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS burgs (
        id INTEGER PRIMARY KEY,
        name TEXT,
        culture TEXT,
        population INTEGER,
        morale REAL DEFAULT 100.0,
        chaos_level REAL DEFAULT 0.0,
        x_coord REAL,
        y_coord REAL,
        lat REAL,
        lon REAL,
        current_weather TEXT DEFAULT 'Clear'
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
    
    # 8. PHYSICAL NETWORKS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS burg_routes (
        burg_a INTEGER,
        burg_b INTEGER,
        distance REAL,
        PRIMARY KEY (burg_a, burg_b),
        FOREIGN KEY(burg_a) REFERENCES burgs(id),
        FOREIGN KEY(burg_b) REFERENCES burgs(id)
    );
    ''')
    
    # 9. SHADOW FACTIONS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shadow_factions (
        id INTEGER PRIMARY KEY,
        name TEXT,
        type TEXT,
        treasury REAL DEFAULT 0.0,
        smuggled_goods REAL DEFAULT 0.0
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shadow_presence (
        faction_id INTEGER,
        burg_id INTEGER,
        influence_level REAL DEFAULT 1.0,
        hidden BOOLEAN DEFAULT 1,
        PRIMARY KEY (faction_id, burg_id),
        FOREIGN KEY(faction_id) REFERENCES shadow_factions(id),
        FOREIGN KEY(burg_id) REFERENCES burgs(id)
    );
    ''')
    
    # 10. THE CHAOS LAYER: Wardens vs Cults
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS world_prisons (
        prison_id INTEGER PRIMARY KEY,
        name TEXT,
        containment_strength REAL DEFAULT 10000.0,
        chaos_pressure REAL DEFAULT 0.0,
        cell_id INTEGER
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cult_forces (
        cult_id INTEGER,
        location_type TEXT, -- 'Burg' or 'Prison'
        location_id INTEGER,
        new_members REAL DEFAULT 0.0,
        priests REAL DEFAULT 0.0,
        PRIMARY KEY (cult_id, location_type, location_id)
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS warden_forces (
        location_type TEXT, -- 'Burg' or 'Prison'
        location_id INTEGER,
        patrols REAL DEFAULT 0.0,
        the_eyeless REAL DEFAULT 0.0,
        PRIMARY KEY (location_type, location_id)
    );
    ''')
    
    # 11. THE PARAGON SYSTEM    # Player Characters (BRUTAL PCs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            origin TEXT NOT NULL,
            loadout TEXT NOT NULL,
            health INTEGER, max_health INTEGER,
            composure INTEGER, max_composure INTEGER,
            stamina INTEGER, max_stamina INTEGER,
            focus INTEGER, max_focus INTEGER,
            level INTEGER DEFAULT 1, xp INTEGER DEFAULT 0, shards INTEGER DEFAULT 0,
            inventory TEXT DEFAULT '[]', skills TEXT DEFAULT '[]',
            might INTEGER, endurance INTEGER, finesse INTEGER, reflex INTEGER, vitality INTEGER, fortitude INTEGER,
            knowledge INTEGER, logic INTEGER, awareness INTEGER, intuition INTEGER, charm INTEGER, willpower INTEGER,
            trait_1 TEXT, flaw_1 TEXT,
            location_id INTEGER, cluster_id INTEGER, local_x INTEGER, local_y INTEGER
        )
    ''')

    # Paragons (Elite NPCs/Entities)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS paragons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        location_id INTEGER,
        cluster_id INTEGER DEFAULT 1,
        local_x INTEGER DEFAULT 50,
        local_y INTEGER DEFAULT 50,
        faction_name TEXT,
        health INTEGER DEFAULT 20,
        max_health INTEGER DEFAULT 20,
        composure INTEGER DEFAULT 10,
        max_composure INTEGER DEFAULT 10,
        stamina INTEGER DEFAULT 10,
        max_stamina INTEGER DEFAULT 10,
        focus INTEGER DEFAULT 10,
        max_focus INTEGER DEFAULT 10,
        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0,
        origin TEXT DEFAULT 'Core-born',
        class TEXT DEFAULT 'Wanderer',
        inventory TEXT DEFAULT '[]',
        skills TEXT DEFAULT '[]',
        might INTEGER DEFAULT 10,
        endurance INTEGER DEFAULT 10,
        finesse INTEGER DEFAULT 10,
        reflex INTEGER DEFAULT 10,
        vitality INTEGER DEFAULT 10,
        fortitude INTEGER DEFAULT 10,
        knowledge INTEGER DEFAULT 10,
        logic INTEGER DEFAULT 10,
        awareness INTEGER DEFAULT 10,
        intuition INTEGER DEFAULT 10,
        charm INTEGER DEFAULT 10,
        willpower INTEGER DEFAULT 10,
        trait_1 TEXT,
        trait_2 TEXT,
        flaw_1 TEXT,
        flaw_2 TEXT
    );
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO player_characters (
            id, name, origin, loadout, level, xp, shards,
            health, max_health, stamina, max_stamina, focus, max_focus,
            might, finesse, reflex, endurance, fortitude, vitality,
            knowledge, awareness, intuition, logic, charm, willpower,
            inventory, skills,
            location_id, cluster_id, local_x, local_y
        ) VALUES (
            1, 'Warden', 'The Drift', 'Light', 1, 0, 0,
            30, 30, 20, 20, 20, 20,
            10, 10, 10, 10, 10, 10,
            10, 10, 10, 10, 10, 10,
            '[]', '[]',
            1, 13, 50, 50
        )
    ''')

    conn.commit()
    conn.close()
    print("Database schema updated with world_lore and new region_cells.")

if __name__ == "__main__":
    setup_database()
