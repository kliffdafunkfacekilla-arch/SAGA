import sqlite3
import csv
import os
import random
import math

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def master_ingest(db_path, burgs_csv, goods_csv, states_csv, relations_csv, religions_csv):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear all data
    cursor.execute("DELETE FROM burgs")
    cursor.execute("DELETE FROM goods_catalog")
    cursor.execute("DELETE FROM burg_stocks")
    cursor.execute("DELETE FROM burg_production")
    cursor.execute("DELETE FROM ecology_output")
    cursor.execute("DELETE FROM faction_relations")
    cursor.execute("DELETE FROM faction_military")
    cursor.execute("DELETE FROM burg_routes")
    cursor.execute("DELETE FROM shadow_factions")
    cursor.execute("DELETE FROM shadow_presence")
    cursor.execute("DELETE FROM world_prisons")
    cursor.execute("DELETE FROM cult_forces")
    cursor.execute("DELETE FROM warden_forces")
    cursor.execute("DELETE FROM paragons")

    # 1. Ingest Goods
    if os.path.exists(goods_csv):
        with open(goods_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            goods_rows = []
            for row in reader:
                goods_rows.append((row['Id'], row['Good'], row['Type']))
            cursor.executemany("INSERT OR REPLACE INTO goods_catalog (item_id, name, type) VALUES (?, ?, ?)", goods_rows)

    # 2. Ingest Burgs and Seed Initial Stocks/Morale
    burg_locations = []
    if os.path.exists(burgs_csv):
        with open(burgs_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            burg_rows = []
            stock_rows = []
            prod_rows = []
            
            cursor.execute("SELECT item_id, name FROM goods_catalog")
            all_goods = cursor.fetchall()
            grain_id = next((g[0] for g in all_goods if g[1] == 'Grain'), None)
            wood_id = next((g[0] for g in all_goods if g[1] == 'Wood'), None)
            
            for i, row in enumerate(reader):
                if i > 100: 
                    break
                
                b_id = row['Id']
                name = row['Burg']
                state_val = row.get('State', '').strip()
                culture = state_val if state_val and state_val != 'undefined' else row['Culture']
                pop = row.get('Population', 1000)
                
                x = float(row.get('X', 0))
                y = float(row.get('Y', 0))
                
                # Burgs start with high morale, zero chaos
                burg_rows.append((b_id, name, culture, pop, 100.0, 0.0, x, y))
                burg_locations.append((b_id, x, y))
                
                if grain_id:
                    stock_rows.append((b_id, grain_id, 'Grain', 5000.0, float(pop) * 0.1))
                if wood_id:
                    stock_rows.append((b_id, wood_id, 'Wood', 1000.0, float(pop) * 0.05))
                    
                if all_goods:
                    for _ in range(3):
                        g_id = random.choice(all_goods)[0]
                        prod_rate = random.uniform(10.0, 100.0)
                        prod_rows.append((b_id, g_id, prod_rate))
                        
            cursor.executemany("INSERT OR REPLACE INTO burgs (id, name, culture, population, morale, chaos_level, x_coord, y_coord) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", burg_rows)
            cursor.executemany("INSERT INTO burg_stocks (burg_id, good_id, food_type, stock, consumption) VALUES (?, ?, ?, ?, ?)", stock_rows)
            cursor.executemany("INSERT INTO burg_production (burg_id, good_id, production_rate) VALUES (?, ?, ?)", prod_rows)

    # 3. Procedural Trade Network
    if burg_locations:
        route_rows = set()
        for b1 in burg_locations:
            distances = []
            for b2 in burg_locations:
                if b1[0] != b2[0]:
                    dist = calculate_distance(b1[1], b1[2], b2[1], b2[2])
                    distances.append((b2[0], dist))
            distances.sort(key=lambda x: x[1])
            for neighbor_id, dist in distances[:3]:
                pair = tuple(sorted([b1[0], neighbor_id]))
                route_rows.add((pair[0], pair[1], dist))
        cursor.executemany("INSERT OR REPLACE INTO burg_routes (burg_a, burg_b, distance) VALUES (?, ?, ?)", list(route_rows))

    # 4. Ingest States (Military)
    if os.path.exists(states_csv):
        with open(states_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            military_rows = []
            for row in reader:
                faction_name = row['State']
                pop_str = row.get('Total Population', '100000')
                strength = float(pop_str) * 0.05
                treasury = float(pop_str) * 0.1
                military_rows.append((faction_name, strength, treasury))
            cursor.executemany("INSERT OR REPLACE INTO faction_military (faction_name, military_strength, treasury) VALUES (?, ?, ?)", military_rows)

    # 5. Ingest Relations
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

    # 6. Ingest Shadow Factions (Only non-Worm Cults now since Worm Cults are in Chaos Layer)
    shadow_rows = []
    worm_cults = []
    if os.path.exists(religions_csv):
        with open(religions_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                f_type = row.get('Type', 'Cult')
                if 'Worm Cult' in row.get('Form', ''):
                    worm_cults.append((row['Id'], row['Name']))
                else:
                    shadow_rows.append((row['Id'], row['Name'], f_type, 0.0, 0.0))
                
    shadow_rows.append((901, "The Obsidian Cartel", "Cartel", 5000.0, 0.0))
    shadow_rows.append((902, "The Iron Coin Guild", "Guild", 25000.0, 0.0))
    cursor.executemany("INSERT OR REPLACE INTO shadow_factions (id, name, type, treasury, smuggled_goods) VALUES (?, ?, ?, ?, ?)", shadow_rows)
    
    presence_rows = []
    if burg_locations:
        burg_ids = [b[0] for b in burg_locations]
        for shadow_f in shadow_rows:
            f_id = shadow_f[0]
            infested = random.sample(burg_ids, min(5, len(burg_ids)))
            for b_id in infested:
                influence = random.uniform(10.0, 50.0)
                presence_rows.append((f_id, b_id, influence, 1))
    cursor.executemany("INSERT OR REPLACE INTO shadow_presence (faction_id, burg_id, influence_level, hidden) VALUES (?, ?, ?, ?)", presence_rows)

    # 7. INGEST CHAOS LAYER (Prisons, Wardens, Cults)
    prisons = [
        (1, "The First Prison", 10000.0, 0.0, 10),
        (2, "The Abyssal Seal", 10000.0, 0.0, 20),
        (3, "The Crimson Vault", 10000.0, 0.0, 30),
        (4, "The Iron Cage", 10000.0, 0.0, 40),
        (5, "The Weeping Stone", 10000.0, 0.0, 50),
        (6, "The Obsidian Tomb", 10000.0, 0.0, 60),
        (7, "The Frozen Lock", 10000.0, 0.0, 70),
        (8, "The Emerald Chain", 10000.0, 0.0, 80),
        (9, "The Silent Cage", 10000.0, 0.0, 90),
        (10, "The Shadow Bind", 10000.0, 0.0, 100),
        (11, "The Gilded Prison", 10000.0, 0.0, 110),
        (12, "The Final Lock", 10000.0, 0.0, 120),
    ]
    cursor.executemany("INSERT OR REPLACE INTO world_prisons (prison_id, name, containment_strength, chaos_pressure, cell_id) VALUES (?, ?, ?, ?, ?)", prisons)

    warden_rows = []
    cult_forces_rows = []
    
    if burg_locations:
        for b_id in burg_ids:
            # Small starting presence of wardens in each burg
            warden_rows.append(('Burg', b_id, random.uniform(5.0, 20.0), 0.0))
            
            # Seed worm cults explicitly in burgs
            for c_id, c_name in worm_cults:
                if random.random() < 0.1: # 10% chance to have a presence
                    cult_forces_rows.append((c_id, 'Burg', b_id, random.uniform(10.0, 50.0), 0.0))
                    
        # Wardens and Priests at prisons
        for p in prisons:
            warden_rows.append(('Prison', p[0], random.uniform(100.0, 300.0), random.uniform(5.0, 20.0))) # Lots of wardens and eyeless
            for c_id, c_name in worm_cults:
                 if random.random() < 0.3:
                     cult_forces_rows.append((c_id, 'Prison', p[0], 0.0, random.uniform(20.0, 100.0))) # Priests attacking prison
                     
    cursor.executemany("INSERT OR REPLACE INTO warden_forces (location_type, location_id, patrols, the_eyeless) VALUES (?, ?, ?, ?)", warden_rows)
    cursor.executemany("INSERT OR REPLACE INTO cult_forces (cult_id, location_type, location_id, new_members, priests) VALUES (?, ?, ?, ?, ?)", cult_forces_rows)
    print(f"Ingested Chaos Layer: 12 Prisons, {len(warden_rows)} Warden deployments, {len(cult_forces_rows)} Cult presences.")

    # 8. THE PARAGON SYSTEM
    paragon_rows = []
    first_names = ["Kael", "Lyra", "Vane", "Seraph", "Thorne", "Elara", "Draken", "Sylas", "Rowan", "Mira", "Orin", "Nyla"]
    last_names = ["Ironhand", "Stormrider", "Shadowcloak", "Voidwalker", "Starborn", "Bloodmoon", "Ashbringer", "Frostweaver"]
    traits = ["Charitable", "Vigilant", "Inspiring", "Brave", "Diligent", "Just", "Patient", "Zealous"]
    flaws = ["Corrupt", "Cruel", "Paranoid", "Craven", "Greedy", "Slothful", "Arbitrary", "Wroth"]
    
    def gen_stats(focus):
        # 12 stats: might, endurance, finesse, reflex, vitality, fortitude, knowledge, logic, awareness, intuition, charm, willpower
        base = [random.randint(5, 15) for _ in range(12)]
        if focus == 'martial': base[0] += 5; base[5] += 3 # Might & Fortitude
        elif focus == 'stewardship': base[7] += 5; base[6] += 3 # Logic & Knowledge
        elif focus == 'intrigue': base[2] += 5; base[8] += 5 # Finesse & Awareness
        elif focus == 'zeal': base[10] += 8; base[11] += 5 # Charm & Willpower
        # Cap at 20
        return [min(20, max(1, s)) for s in base]
        
    def gen_paragon(role, loc_id, faction_name, focus):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        t1, t2 = random.sample(traits, 2)
        f1, f2 = random.sample(flaws, 2)
        stats = gen_stats(focus)
        return (name, role, loc_id, faction_name, *stats, t1, t2, f1, f2)
        
    # Mayors (Top 25 Burgs by population)
    cursor.execute("SELECT id, name FROM burgs ORDER BY population DESC LIMIT 25")
    for b in cursor.fetchall():
        paragon_rows.append(gen_paragon('Mayor', b[0], None, 'stewardship'))
        
    # State Leaders
    cursor.execute("SELECT faction_name FROM faction_military")
    for f in cursor.fetchall():
        paragon_rows.append(gen_paragon('State Leader', None, f[0], 'martial'))
        
    # Shadow Bosses
    cursor.execute("SELECT id, name FROM shadow_factions WHERE type IN ('Cartel', 'Guild')")
    for s in cursor.fetchall():
        paragon_rows.append(gen_paragon('Shadow Boss', None, s[1], 'intrigue'))
        
    # High Priests
    for c_id, c_name in worm_cults:
        paragon_rows.append(gen_paragon('High Priest', None, c_name, 'zeal'))
        
    cursor.executemany('''
    INSERT INTO paragons 
    (name, role, location_id, faction_name, might, endurance, finesse, reflex, vitality, fortitude, knowledge, logic, awareness, intuition, charm, willpower, trait_1, trait_2, flaw_1, flaw_2) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', paragon_rows)
    print(f"Ingested Paragon System: Generated {len(paragon_rows)} Paragons.")

    conn.commit()
    conn.close()
    print("Master Ingestion complete: Chaos Layer linked.")

if __name__ == "__main__":
    master_ingest(
        'okasha_world.db', 
        'Okasha - Copy/Okasha Burgs 2026-06-26-06-56.csv', 
        'Okasha - Copy/Okasha Goods 2026-06-26-06-59.csv',
        'Okasha - Copy/Okasha States 2026-06-26-06-57.csv',
        'Okasha - Copy/Okasha Relations 2026-06-26-06-58.csv',
        'Okasha - Copy/Okasha Religions 2026-06-26-06-57.csv'
    )
