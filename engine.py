import sqlite3
import os

TICK_FILE = 'current_tick.txt'

def get_current_tick():
    if not os.path.exists(TICK_FILE):
        return 0
    with open(TICK_FILE, 'r') as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def save_current_tick(tick):
    with open(TICK_FILE, 'w') as f:
        f.write(str(tick))

def run_world_tick(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Fetching Cosmos State...")
    cursor.execute("SELECT aether_intensity FROM celestial_calendar LIMIT 1") 
    row = cursor.fetchone()
    aether = row[0] if row else 'Low'
    
    # 2. Simulate Ecology
    print("Simulating Ecology...")
    modifier = 1.5 if aether == 'High' else 0.5
    cursor.execute("UPDATE cell_resources SET plant_pop = plant_pop * ?", (modifier,))
    
    # 3. Process Economy
    print("Processing Economy...")
    cursor.execute("UPDATE burg_stocks SET stock = stock - consumption WHERE food_type IN ('Grain', 'Wood')")
    
    cursor.execute("""
        UPDATE burg_stocks
        SET stock = stock + (
            SELECT production_rate FROM burg_production 
            WHERE burg_production.burg_id = burg_stocks.burg_id AND burg_production.good_id = burg_stocks.good_id
        )
        WHERE EXISTS (
            SELECT 1 FROM burg_production 
            WHERE burg_production.burg_id = burg_stocks.burg_id AND burg_production.good_id = burg_stocks.good_id
        )
    """)
    
    # 4. Faction AI: Trade
    print("Faction AI: Trade Phase...")
    # Find burgs with excess grain and those with deficit, within friendly factions
    # This is a simplified logic where friendly factions instantly share a bit of excess stock
    cursor.execute("""
        SELECT b1.culture, b2.culture, bs1.burg_id, bs2.burg_id, bs1.good_id
        FROM burg_stocks bs1
        JOIN burgs b1 ON bs1.burg_id = b1.id
        JOIN burg_stocks bs2 ON bs1.good_id = bs2.good_id
        JOIN burgs b2 ON bs2.burg_id = b2.id
        JOIN faction_relations fr ON b1.culture = fr.faction_a AND b2.culture = fr.faction_b
        WHERE bs1.food_type = 'Grain' 
          AND bs1.stock > 1000 
          AND bs2.stock < 100
          AND fr.status IN ('Friendly', 'Ally')
        LIMIT 10
    """)
    trade_opportunities = cursor.fetchall()
    
    for opp in trade_opportunities:
        fac_a, fac_b, burg_source, burg_dest, good_id = opp
        transfer_amount = 100.0
        # Transfer stock
        cursor.execute("UPDATE burg_stocks SET stock = stock - ? WHERE burg_id = ? AND good_id = ?", (transfer_amount, burg_source, good_id))
        cursor.execute("UPDATE burg_stocks SET stock = stock + ? WHERE burg_id = ? AND good_id = ?", (transfer_amount, burg_dest, good_id))
        # Log agreement
        cursor.execute("INSERT INTO trade_agreements (faction_a, faction_b, good_type, volume) VALUES (?, ?, ?, ?)", (fac_a, fac_b, 'Grain', transfer_amount))
        # Improve relations
        cursor.execute("UPDATE faction_relations SET status = 'Ally' WHERE faction_a = ? AND faction_b = ? AND status = 'Friendly'", (fac_a, fac_b))
        print(f"Trade executed: {fac_a} (Burg {burg_source}) -> {fac_b} (Burg {burg_dest})")

    # 5. Faction AI: Conflict
    print("Faction AI: Conflict Phase...")
    # If a burg is starving (stock < 0) and borders a rival with food, trigger skirmish
    cursor.execute("""
        SELECT b1.culture, b2.culture
        FROM burg_stocks bs1
        JOIN burgs b1 ON bs1.burg_id = b1.id
        JOIN burg_stocks bs2 ON bs1.good_id = bs2.good_id
        JOIN burgs b2 ON bs2.burg_id = b2.id
        JOIN faction_relations fr ON b1.culture = fr.faction_a AND b2.culture = fr.faction_b
        WHERE bs1.food_type = 'Grain' 
          AND bs1.stock < 0 
          AND bs2.stock > 500
          AND fr.status IN ('Rival', 'Suspicion')
        LIMIT 5
    """)
    skirmishes = cursor.fetchall()
    
    for sk in skirmishes:
        attacker, defender = sk
        print(f"SKIRMISH ALERT: Starving {attacker} attacks {defender} for resources!")
        # Consume military strength
        cursor.execute("UPDATE faction_military SET military_strength = military_strength * 0.9 WHERE faction_name IN (?, ?)", (attacker, defender))
        # Degrade relations
        cursor.execute("UPDATE faction_relations SET status = 'Rival' WHERE faction_a = ? AND faction_b = ?", (attacker, defender))

    conn.commit()
    conn.close()
    print("Tick processed successfully.")

def run_simulation_tick(famine_faction=None):
    tick = get_current_tick()
    print(f"--- Running Simulation Tick {tick} ---")
    
    if famine_faction:
        print(f"Inducing Famine in {famine_faction} for testing...")
        conn = sqlite3.connect('okasha_world.db')
        c = conn.cursor()
        c.execute("""
            UPDATE burg_stocks 
            SET stock = -100 
            WHERE burg_id IN (SELECT id FROM burgs WHERE culture = ?) 
              AND food_type = 'Grain'
        """, (famine_faction,))
        conn.commit()
        conn.close()
    
    run_world_tick('okasha_world.db')
    
    save_current_tick(tick + 1)

if __name__ == "__main__":
    import sys
    # Pass a faction name as argument to induce famine. e.g. python engine.py "Iron Caladra"
    famine_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_simulation_tick(famine_arg)
