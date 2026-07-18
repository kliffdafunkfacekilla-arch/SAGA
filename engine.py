import config
"""
engine.py

The SAGA Engine core tick loop.
This module processes chronological intervals in the simulation, executing 
Meteorology, Ecology, Faction AI, and Metaphysical Conflicts across the world state.
It directly interacts with `okasha_world.db` as the source of truth.
"""
import sqlite3
import os
import random
import narrative_engine

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
    
    # 1.5 METEOROLOGY (Weather Phase)
    print("Simulating Weather...")
    cursor.execute("SELECT id, name, chaos_level FROM burgs")
    burgs_for_weather = cursor.fetchall()
    weather_states = ['Clear', 'Rain', 'Drought', 'Storm', 'Blizzard']
    weather_weights = [0.60, 0.15, 0.10, 0.12, 0.03]
    
    for b in burgs_for_weather:
        b_id, b_name, b_chaos = b
        new_weather = random.choices(weather_states, weights=weather_weights, k=1)[0]
        
        # Chaos Infusion Logic: Storms in chaos zones have a chance to become Aether Storms
        if new_weather in ['Storm', 'Blizzard'] and b_chaos > 10.0:
            if random.random() < 0.2: # 20% chance
                new_weather = 'Aether Storm'
                
        cursor.execute("UPDATE burgs SET current_weather = ? WHERE id = ?", (new_weather, b_id))
        
        # Immediate extreme effects
        if new_weather == 'Aether Storm':
            print(f"  *** AETHER STORM hits {b_name} (Chaos Zone)! Chaos spikes!")
            cursor.execute("UPDATE burgs SET chaos_level = min(100.0, chaos_level + 10.0), morale = max(0.0, morale - 10.0) WHERE id = ?", (b_id,))
            
    # 2. Simulate Ecology
    print("Simulating Ecology...")
    modifier = 1.5 if aether == 'High' else 0.5
    cursor.execute("UPDATE cell_resources SET plant_pop = plant_pop * ?", (modifier,))
    
    # 3. Process Economy
    print("Processing Economy...")
    cursor.execute("UPDATE burg_stocks SET stock = stock - consumption WHERE food_type IN ('Grain', 'Wood')")
    
    # Get Mayor Traits for Morale
    cursor.execute("SELECT location_id, trait_1, trait_2, flaw_1, flaw_2 FROM paragons WHERE role = 'Mayor'")
    mayor_traits = {}
    for row in cursor.fetchall():
        b_id, t1, t2, f1, f2 = row
        mayor_traits[b_id] = [t1, t2, f1, f2]
        
    cursor.execute("SELECT id, morale, chaos_level FROM burgs")
    burgs = cursor.fetchall()
    for b in burgs:
        b_id, morale, chaos_level = b
        traits = mayor_traits.get(b_id, [])
        morale_drop = 10.0
        morale_recover = 2.0
        
        if "Cruel" in traits or "Corrupt" in traits:
            morale_drop += 5.0
        if "Charitable" in traits:
            morale_drop -= 5.0
            morale_recover += 3.0
            
        # Check starvation
        cursor.execute("SELECT stock FROM burg_stocks WHERE burg_id = ? AND food_type = 'Grain'", (b_id,))
        stock_row = cursor.fetchone()
        if stock_row and stock_row[0] < 0:
            cursor.execute("UPDATE burgs SET morale = morale - ? WHERE id = ?", (morale_drop, b_id))
        elif stock_row and stock_row[0] > 100 and chaos_level < 20.0:
            cursor.execute("UPDATE burgs SET morale = min(100.0, morale + ?) WHERE id = ?", (morale_recover, b_id))
            
    # Modify Morale based on Chaos Level
    cursor.execute("""
        UPDATE burgs 
        SET morale = max(0.0, morale - (chaos_level * 0.2)) 
        WHERE chaos_level > 10.0
    """)
    
    # Get Mayors to buff production (Logic instead of Stewardship) and mitigate weather (Knowledge)
    cursor.execute("SELECT location_id, logic, knowledge, intuition, flaw_1, flaw_2 FROM paragons WHERE role = 'Mayor'")
    mayors = {row[0]: (row[1], row[2], row[3], row[4], row[5]) for row in cursor.fetchall()}
    
    # Get current weather for all burgs
    cursor.execute("SELECT id, current_weather FROM burgs")
    burg_weather = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Calculate production buffs
    cursor.execute("SELECT burg_id, good_id, production_rate FROM burg_production")
    prod_rows = cursor.fetchall()
    for prow in prod_rows:
        b_id, g_id, base_rate = prow
        m_data = mayors.get(b_id, (10, 10, 10, "", ""))
        logic = m_data[0]
        knowledge = m_data[1]
        intuition = m_data[2]
        flaws = [m_data[3], m_data[4]]
        weather = burg_weather.get(b_id, 'Clear')
        
        modifier = 1.0 + ((logic - 10) * 0.05) # +/- 5% per point from 10
        if "Corrupt" in flaws:
            modifier -= 0.1 # Corrupt mayors skim 10% off the top
            
        # Apply weather modifiers
        weather_penalty = 0.0
        if weather == 'Rain' and g_id == 1: # Assuming 1 is Grain
            modifier += 0.2
        elif weather == 'Drought' and g_id == 1:
            weather_penalty = 0.5
        elif weather in ['Storm', 'Blizzard']:
            weather_penalty = 0.3
        elif weather == 'Aether Storm':
            weather_penalty = 0.5
            
        # Mayor mitigates weather penalties with Knowledge and Intuition
        if weather_penalty > 0:
            mitigation = ((knowledge - 10) * 0.02) + ((intuition - 10) * 0.02)
            actual_penalty = max(0.0, weather_penalty - max(0.0, mitigation))
            modifier -= actual_penalty
            
        actual_rate = max(0.0, base_rate * modifier)
        cursor.execute("UPDATE burg_stocks SET stock = stock + ? WHERE burg_id = ? AND good_id = ?", (actual_rate, b_id, g_id))
    
    # [Skip printing old Trade/Conflict/Shadow loops for brevity, but they'd run here]

    # 9. METAPHYSICAL WAR: Wardens vs Cults
    print("Metaphysical Phase: Wardens vs Cults...")
    
    # A. Recruitment
    # Wardens passively recruit 5.0 patrols per burg (Buffed for equilibrium)
    cursor.execute("UPDATE warden_forces SET patrols = patrols + 5.0 WHERE location_type = 'Burg'")
    
    # Cults recruit dynamically based on low morale and High Priest Charm
    cursor.execute("SELECT faction_name, charm, trait_1, trait_2 FROM paragons WHERE role = 'High Priest'")
    priests = {row[0]: (row[1], row[2], row[3]) for row in cursor.fetchall()}
    
    cursor.execute("""
        SELECT cf.cult_id, cf.location_id, b.morale, sf.name, b.name
        FROM cult_forces cf
        JOIN burgs b ON cf.location_id = b.id
        JOIN shadow_factions sf ON cf.cult_id = sf.id
        WHERE cf.location_type = 'Burg'
    """)
    cult_burgs = cursor.fetchall()
    for cb in cult_burgs:
        c_id, b_id, morale, c_name, b_name = cb
        p_data = priests.get(c_name, (10, "", ""))
        charm = p_data[0]
        traits = [p_data[1], p_data[2]]
        
        charm_mod = 1.0 + ((charm - 10) * 0.1)
        if "Inspiring" in traits:
            charm_mod *= 1.2
        
        # If morale is 100, recruit 0. If morale is 0, recruit 50 * charm_mod.
        recruit_amount = max(0.0, ((100.0 - morale) * 0.5) * charm_mod)
        if recruit_amount > 0:
            cursor.execute("UPDATE cult_forces SET new_members = new_members + ? WHERE cult_id = ? AND location_type = 'Burg' AND location_id = ?", (recruit_amount, c_id, b_id))
            print(f"  -> {c_name} recruited {recruit_amount:.1f} members in starving {b_name}!")
            
    # B. The Settlement War (Burg Phase)
    # Mayors resist chaos via Willpower
    cursor.execute("SELECT location_id, willpower, trait_1, trait_2, flaw_1, flaw_2 FROM paragons WHERE role = 'Mayor'")
    mayor_wills = {row[0]: (row[1], row[2], row[3], row[4], row[5]) for row in cursor.fetchall()}
    
    cursor.execute("SELECT id, name FROM burgs")
    all_burgs = cursor.fetchall()
    for b in all_burgs:
        b_id = b[0]
        # Cults raise chaos
        cursor.execute("SELECT SUM(new_members) FROM cult_forces WHERE location_type = 'Burg' AND location_id = ?", (b_id,))
        total_cultists = cursor.fetchone()[0] or 0.0
        
        # Wardens fight chaos
        cursor.execute("SELECT patrols FROM warden_forces WHERE location_type = 'Burg' AND location_id = ?", (b_id,))
        wardens_row = cursor.fetchone()
        patrols = wardens_row[0] if wardens_row else 0.0
        
        chaos_increase = total_cultists * 0.1
        
        # Mayor's Willpower reduces chaos increase
        m_data = mayor_wills.get(b_id, (10, "", "", "", ""))
        willpower = m_data[0]
        traits_flaws = [m_data[1], m_data[2], m_data[3], m_data[4]]
        
        will_resist = ((willpower - 10) * 0.05) # Up to 50% resistance
        if "Vigilant" in traits_flaws:
            will_resist += 0.10
        if "Corrupt" in traits_flaws:
            will_resist -= 0.10
            
        chaos_increase = max(0.0, chaos_increase * (1.0 - will_resist))
        
        chaos_decrease = patrols * 0.2
        
        net_chaos = chaos_increase - chaos_decrease
        cursor.execute("UPDATE burgs SET chaos_level = max(0.0, min(100.0, chaos_level + ?)) WHERE id = ?", (net_chaos, b_id))
        
        # Wardens kill cultists
        if patrols > 0 and total_cultists > 0:
            kills = min(total_cultists, patrols * 0.5)
            # Distribute kills across cults evenly for simplicity
            cursor.execute("UPDATE cult_forces SET new_members = max(0.0, new_members - (? / (SELECT COUNT(*) FROM cult_forces WHERE location_type='Burg' AND location_id=?))) WHERE location_type='Burg' AND location_id=?", (kills, b_id, b_id))
            
    # C. Pilgrimage Phase
    cursor.execute("SELECT prison_id FROM world_prisons")
    prison_ids = [row[0] for row in cursor.fetchall()]
    
    if prison_ids:
        # Cultists to Priests (10% of new members mutate and travel)
        cursor.execute("SELECT cult_id, location_id, new_members FROM cult_forces WHERE location_type = 'Burg' AND new_members > 10.0")
        migrants = cursor.fetchall()
        for m in migrants:
            c_id, b_id, count = m
            migrating_count = count * 0.1
            target_prison = random.choice(prison_ids)
            
            cursor.execute("UPDATE cult_forces SET new_members = new_members - ? WHERE cult_id = ? AND location_type = 'Burg' AND location_id = ?", (migrating_count, c_id, b_id))
            # Add to prison
            cursor.execute("""
                INSERT INTO cult_forces (cult_id, location_type, location_id, priests)
                VALUES (?, 'Prison', ?, ?)
                ON CONFLICT(cult_id, location_type, location_id) DO UPDATE SET priests = priests + ?
            """, (c_id, target_prison, migrating_count, migrating_count))
            
        # Wardens to Eyeless (5% of veteran patrols)
        cursor.execute("SELECT location_id, patrols FROM warden_forces WHERE location_type = 'Burg' AND patrols > 20.0")
        w_migrants = cursor.fetchall()
        for wm in w_migrants:
            b_id, p_count = wm
            promotions = p_count * 0.05
            target_prison = random.choice(prison_ids)
            
            cursor.execute("UPDATE warden_forces SET patrols = patrols - ? WHERE location_type = 'Burg' AND location_id = ?", (promotions, b_id))
            cursor.execute("""
                INSERT INTO warden_forces (location_type, location_id, the_eyeless)
                VALUES ('Prison', ?, ?)
                ON CONFLICT(location_type, location_id) DO UPDATE SET the_eyeless = the_eyeless + ?
            """, (target_prison, promotions, promotions))
            
    # D. The Prison War (Metaphysical Phase)
    cursor.execute("SELECT prison_id, name, containment_strength FROM world_prisons")
    prisons = cursor.fetchall()
    for p in prisons:
        p_id, p_name, strength = p
        
        # Priests absorb chaos (weaken seal)
        cursor.execute("SELECT SUM(priests) FROM cult_forces WHERE location_type = 'Prison' AND location_id = ?", (p_id,))
        priests = cursor.fetchone()[0] or 0.0
        
        damage = priests * 5.0
        
        # Eyeless sacrifice to restore
        cursor.execute("SELECT the_eyeless FROM warden_forces WHERE location_type = 'Prison' AND location_id = ?", (p_id,))
        eyeless_row = cursor.fetchone()
        eyeless = eyeless_row[0] if eyeless_row else 0.0
        
        restore = eyeless * 50.0 # Buffed from 10.0 to 50.0 for equilibrium
        
        new_strength = max(0.0, strength - damage + restore)
        cursor.execute("UPDATE world_prisons SET containment_strength = ? WHERE prison_id = ?", (new_strength, p_id))
        
        if damage > 0 or restore > 0:
            print(f"  -> PRISON WAR at {p_name}: {priests:.0f} Priests attacked (-{damage:.0f}), {eyeless:.0f} Eyeless defended (+{restore:.0f}). Strength: {new_strength:.0f}/10000")
            
        if new_strength <= 0:
            print(f"  *** CATACLYSM! The {p_name} has been broken! Chaos Dragon unleashed! ***")
            print("  *** CHAIN REACTION: The world is engulfed in Chaos! ***")
            
            # Global Destruction Event
            cursor.execute("UPDATE burgs SET population = 0, morale = 0.0, chaos_level = 100.0")
            cursor.execute("UPDATE world_prisons SET containment_strength = 0.0")
            cursor.execute("UPDATE cell_resources SET plant_pop = 0.0, prey_pop = 0.0, predator_pop = 0.0")
            
            print("  *** THE WORLD OF OSTRAKA HAS ENDED. ***")
            break # Halt further prison processing, world is dead.

    conn.commit()
    conn.close()
    
    # Generate Narrative Matrix
    print("Generating Narrative Hooks...")
    narrative_engine.generate_initial_hooks(db_path)

def run_simulation_tick(famine_faction=None):
    tick = get_current_tick()
    print(f"--- Running Simulation Tick {tick} ---")
    
    if famine_faction:
        print(f"Inducing Famine in {famine_faction} for testing...")
        conn = sqlite3.connect(config.ACTIVE_DB_PATH)
        c = conn.cursor()
        c.execute("""
            UPDATE burg_stocks 
            SET stock = -100 
            WHERE burg_id IN (SELECT id FROM burgs WHERE culture = ?) 
              AND food_type = 'Grain'
        """, (famine_faction,))
        conn.commit()
        conn.close()
    
    run_world_tick(config.ACTIVE_DB_PATH)
    
    save_current_tick(tick + 1)

if __name__ == "__main__":
    import sys
    famine_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_simulation_tick(famine_arg)
