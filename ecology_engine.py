import config
import sqlite3

def update_cell_ecology(cursor, cell_id, aether_mod, is_burg=False):
    # Fetch current values
    cursor.execute("SELECT plant_pop, prey_pop, predator_pop, harvest_pressure FROM cell_resources WHERE cell_id = ?", (cell_id,))
    row = cursor.fetchone()
    if not row:
        return
    plant, prey, pred, harvest_pressure = row

    if not is_burg:
        # Wild Cells: Natural Growth
        # 1. Plants grow based on Aether (Surge = faster growth, but maybe higher mutation risk)
        new_plant = plant + (plant * 0.1 * aether_mod) 
        
        # 2. Prey population depends on plant availability
        new_prey = prey + (prey * 0.05 * (plant / 100))
        
        # 3. Apply Harvesting Penalty
        # If harvest_pressure > 0.8, the population cannot recover
        if harvest_pressure > 0.8:
            new_plant *= 0.5
            new_prey *= 0.5
            
        cursor.execute("""
            UPDATE cell_resources 
            SET plant_pop = ?, prey_pop = ? 
            WHERE cell_id = ?
        """, (new_plant, new_prey, cell_id))
    else:
        # Burg Cells: Consume resources, drive up harvest pressure
        # For simplicity in this iteration, Burgs just increase harvest pressure
        new_harvest_pressure = min(harvest_pressure + 0.1, 1.0)
        cursor.execute("""
            UPDATE cell_resources
            SET harvest_pressure = ?
            WHERE cell_id = ?
        """, (new_harvest_pressure, cell_id))

def run_ecology_simulation(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get global aether modifier
    cursor.execute("SELECT global_aether_modifier FROM world_state LIMIT 1")
    row = cursor.fetchone()
    aether_mod = row[0] if row else 1.0
    
    # Get all cells with resources
    cursor.execute("""
        SELECT cr.cell_id, rc.occupant 
        FROM cell_resources cr
        JOIN region_cells rc ON cr.cell_id = rc.cell_id
    """)
    cells = cursor.fetchall()
    
    for cell_id, occupant in cells:
        # If occupant is populated, treat as Burg, else Wild
        is_burg = bool(occupant and occupant.strip())
        update_cell_ecology(cursor, cell_id, aether_mod, is_burg)
        
    conn.commit()
    conn.close()
    print("Ecology simulation tick complete.")

if __name__ == "__main__":
    run_ecology_simulation(config.ACTIVE_DB_PATH)
