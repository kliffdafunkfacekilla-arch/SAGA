import sqlite3
import random
import csv

def seed_resources(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Make sure we have some region cells to work with.
    cursor.execute("SELECT COUNT(*) FROM region_cells")
    if cursor.fetchone()[0] == 0:
        print("region_cells is empty. Seeding some basic cells from Okasha Burgs for testing...")
        try:
            with open('Okasha - Copy/Okasha Burgs 2026-06-26-06-56.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = []
                biomes = ['Hot desert', 'Cold desert', 'Savanna', 'Grassland', 'Tropical seasonal forest', 'Temperate deciduous forest', 'Tropical rainforest', 'Temperate rainforest', 'Taiga', 'Tundra', 'Glacier', 'Wetland', 'Shallow Reef', 'Kelp Forest', 'Pelagic Zone', 'Abyssal Plain', 'Oceanic Trench', 'Chaos Land', 'Chaos Water']
                for i, row in enumerate(reader):
                    if i > 500: # Seed more for better distribution
                        break
                    terrain = random.choice(biomes)
                    occupant = row.get('Burg', '')
                    rows.append((row['Id'], float(row['X']), float(row['Y']), terrain, occupant))
                
                cursor.executemany("INSERT INTO region_cells (cell_id, x_coord, y_coord, terrain_type, occupant) VALUES (?,?,?,?,?)", rows)
                conn.commit()
        except Exception as e:
            print(f"Failed to seed region_cells: {e}")

    # Map each biome to a UNIQUE resource as requested
    biome_resources = {
        'hot desert': 'Sunfire Geode',
        'cold desert': 'Frost-Rimmed Salt',
        'savanna': 'Lion-Mane Amber',
        'grassland': 'Wind-Whisper Fiber',
        'tropical seasonal forest': 'Monsoon Resin',
        'temperate deciduous forest': 'Heartwood Sap',
        'tropical rainforest': 'Emerald Canopy Orchid',
        'temperate rainforest': 'Mist-Shrouded Truffle',
        'taiga': 'Pine-Barrens Iron',
        'tundra': 'Permafrost Lichen',
        'glacier': 'Deep Ice Core',
        'wetland': 'Witch-bloom',
        'shallow reef': 'Coral Crystalline',
        'kelp forest': 'Abyssal Pearl',
        'pelagic zone': 'Leviathan Scale',
        'abyssal plain': 'Trench-Glow Phosphorus',
        'oceanic trench': 'Void-Pressure Diamond',
        'chaos land': 'Chaos Shard',
        'chaos water': 'Aether-Bleed Droplets'
    }

    # Clear existing resources before re-seeding
    cursor.execute("DELETE FROM cell_resources")
    cursor.execute("DELETE FROM rare_deposits")

    cursor.execute("SELECT cell_id, terrain_type, occupant FROM region_cells")
    cells = cursor.fetchall()
    
    resource_rows = []
    rare_rows = []
    
    for cell_id, terrain_type, occupant in cells:
        # Determine populations based on biome
        terrain = terrain_type.lower() if terrain_type else ""
        
        # Base populations based on hostility
        if 'desert' in terrain or 'tundra' in terrain or 'glacier' in terrain or 'trench' in terrain or 'abyssal' in terrain:
            plant_pop = random.uniform(10, 50)
            prey_pop = random.uniform(5, 20)
            pred_pop = random.uniform(1, 5)
        elif 'forest' in terrain or 'grassland' in terrain or 'savanna' in terrain:
            plant_pop = random.uniform(500, 1000)
            prey_pop = random.uniform(200, 500)
            pred_pop = random.uniform(20, 50)
        elif 'wetland' in terrain or 'kelp' in terrain or 'reef' in terrain or 'pelagic' in terrain:
            plant_pop = random.uniform(300, 600)
            prey_pop = random.uniform(400, 800)
            pred_pop = random.uniform(50, 100)
        elif 'chaos' in terrain:
            plant_pop = random.uniform(10, 2000)
            prey_pop = random.uniform(10, 2000)
            pred_pop = random.uniform(100, 500)
        else:
            plant_pop = 100.0
            prey_pop = 50.0
            pred_pop = 10.0
            
        stock_basic = 'Wood/Stone/Food'
        stock_qty = 1000 if occupant else 0
        harvest_pressure = 0.5 if occupant else 0.0
        
        resource_rows.append((cell_id, plant_pop, prey_pop, pred_pop, stock_basic, stock_qty, harvest_pressure))
        
        # 10% chance to have a rare deposit
        if random.random() < 0.1:
            rare_name = biome_resources.get(terrain, 'Common Ore')
            remaining_yield = random.randint(10, 100)
            difficulty = random.randint(1, 5)
            rare_rows.append((cell_id, rare_name, remaining_yield, difficulty))
            
    cursor.executemany("INSERT INTO cell_resources VALUES (?,?,?,?,?,?,?)", resource_rows)
    cursor.executemany("INSERT INTO rare_deposits VALUES (?,?,?,?)", rare_rows)
    
    conn.commit()
    conn.close()
    print(f"Successfully seeded resources for {len(resource_rows)} cells and {len(rare_rows)} unique rare deposits.")

if __name__ == "__main__":
    seed_resources('okasha_world.db')
