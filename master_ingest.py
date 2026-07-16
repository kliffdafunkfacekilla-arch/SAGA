import sqlite3
import csv
import os
import random

def master_ingest(db_path, burgs_csv, goods_csv, states_csv, relations_csv):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear previously ingested basic data
    cursor.execute("DELETE FROM burgs")
    cursor.execute("DELETE FROM goods_catalog")
    cursor.execute("DELETE FROM burg_stocks")
    cursor.execute("DELETE FROM burg_production")
    cursor.execute("DELETE FROM ecology_output")
    cursor.execute("DELETE FROM faction_relations")
    cursor.execute("DELETE FROM faction_military")

    # 1. Ingest Goods
    if os.path.exists(goods_csv):
        with open(goods_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            goods_rows = []
            for row in reader:
                goods_rows.append((row['Id'], row['Good'], row['Type']))
            cursor.executemany("INSERT OR REPLACE INTO goods_catalog (item_id, name, type) VALUES (?, ?, ?)", goods_rows)
        print("Ingested Goods Catalog.")

    # 2. Ingest Burgs and Seed Initial Stocks
    if os.path.exists(burgs_csv):
        with open(burgs_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            burg_rows = []
            stock_rows = []
            prod_rows = []
            
            # Fetch all goods to randomly assign production
            cursor.execute("SELECT item_id, name FROM goods_catalog")
            all_goods = cursor.fetchall()
            grain_id = next((g[0] for g in all_goods if g[1] == 'Grain'), None)
            wood_id = next((g[0] for g in all_goods if g[1] == 'Wood'), None)
            
            for i, row in enumerate(reader):
                if i > 100: # Limit for testing
                    break
                
                b_id = row['Id']
                name = row['Burg']
                state_val = row.get('State', '').strip()
                culture = state_val if state_val and state_val != 'undefined' else row['Culture']
                pop = row.get('Population', 1000)
                
                burg_rows.append((b_id, name, culture, pop))
                
                # Seed Stocks
                if grain_id:
                    stock_rows.append((b_id, grain_id, 'Grain', 5000.0, float(pop) * 0.1))
                if wood_id:
                    stock_rows.append((b_id, wood_id, 'Wood', 1000.0, float(pop) * 0.05))
                    
                # Seed Production
                if all_goods:
                    for _ in range(3): # Each burg produces 3 random goods
                        g_id = random.choice(all_goods)[0]
                        prod_rate = random.uniform(10.0, 100.0)
                        prod_rows.append((b_id, g_id, prod_rate))
                        
            cursor.executemany("INSERT OR REPLACE INTO burgs (id, name, culture, population) VALUES (?, ?, ?, ?)", burg_rows)
            cursor.executemany("INSERT INTO burg_stocks (burg_id, good_id, food_type, stock, consumption) VALUES (?, ?, ?, ?, ?)", stock_rows)
            cursor.executemany("INSERT INTO burg_production (burg_id, good_id, production_rate) VALUES (?, ?, ?)", prod_rows)
        print("Ingested Burgs, Stocks, and Production.")

    # 3. Ingest States (Military)
    if os.path.exists(states_csv):
        with open(states_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            military_rows = []
            for row in reader:
                faction_name = row['State']
                # Mock military strength based on population
                pop_str = row.get('Total Population', '100000')
                strength = float(pop_str) * 0.05
                treasury = float(pop_str) * 0.1
                military_rows.append((faction_name, strength, treasury))
            cursor.executemany("INSERT OR REPLACE INTO faction_military (faction_name, military_strength, treasury) VALUES (?, ?, ?)", military_rows)
        print("Ingested Faction Military States.")

    # 4. Ingest Relations
    if os.path.exists(relations_csv):
        with open(relations_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            relations_rows = []
            for row in reader:
                faction_a = row[0]
                if not faction_a: continue
                for idx, status in enumerate(row[1:], start=1):
                    faction_b = header[idx]
                    if faction_a != faction_b and status != 'x':
                        relations_rows.append((faction_a, faction_b, status))
            cursor.executemany("INSERT OR REPLACE INTO faction_relations (faction_a, faction_b, status) VALUES (?, ?, ?)", relations_rows)
        print("Ingested Faction Relations.")

    conn.commit()
    conn.close()
    print("Master Ingestion complete: Diplomacy & Trade linked.")

if __name__ == "__main__":
    master_ingest(
        'okasha_world.db', 
        'Okasha - Copy/Okasha Burgs 2026-06-26-06-56.csv', 
        'Okasha - Copy/Okasha Goods 2026-06-26-06-59.csv',
        'Okasha - Copy/Okasha States 2026-06-26-06-57.csv',
        'Okasha - Copy/Okasha Relations 2026-06-26-06-58.csv'
    )
