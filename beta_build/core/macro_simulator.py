import logging
import sqlite3
import os
import json
from typing import Dict, Any

logger = logging.getLogger("MacroSimulator")

class MacroSimulator:
    def __init__(self, db_path: str = r'c:\Users\krazy\Desktop\SAGA\beta_build\data\okasha.sqlite'):
        self.db_path = db_path
        self.current_tick = 0
        
        # Open a read/write connection. We keep it open since this is local simulation.
        if not os.path.exists(self.db_path):
            logger.error(f"Database not found at {self.db_path}. Please run world_db_builder.py")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def simulate_tick(self):
        self.current_tick += 1
        logger.info(f"Simulating World Tick {self.current_tick}...")
        
        cursor = self.conn.cursor()
        
        # Base unrest accumulation
        cursor.execute("UPDATE burgs SET unrest = unrest + 1.0")
        
        # Base wealth accumulation (faster for markets)
        # We find which burgs are in the markets table
        cursor.execute('''
            UPDATE burgs 
            SET wealth = wealth + 2.5 
            WHERE burg IN (SELECT burg FROM markets)
        ''')
        
        cursor.execute('''
            UPDATE burgs 
            SET wealth = wealth + 0.5 
            WHERE burg NOT IN (SELECT burg FROM markets)
        ''')
        
        # Caps
        cursor.execute("UPDATE burgs SET unrest = MIN(100.0, unrest), wealth = MIN(100.0, wealth)")
        self.conn.commit()
            
    def get_burg_context(self, burg_name: str) -> str:
        if not burg_name:
            return "Wilderness."
            
        cursor = self.conn.cursor()
        
        # We do a case-insensitive lookup
        cursor.execute("SELECT * FROM burgs WHERE LOWER(burg) = LOWER(?)", (burg_name,))
        b_data = cursor.fetchone()
        
        if not b_data:
            return f"Unknown location: {burg_name}. It is wilderness or a small encampment."
            
        state_name = b_data["state"] if "state" in b_data.keys() else "Independent"
        culture_name = b_data["culture"] if "culture" in b_data.keys() else "Unknown Culture"
        unrest = b_data["unrest"]
        wealth = b_data["wealth"]
        
        context = (
            f"Burg: {burg_name}. Controlled by Faction: {state_name}. Culture: {culture_name}. "
            f"Macro Stats -> Unrest: {unrest:.1f}/100, Wealth: {wealth:.1f}/100. "
        )
        
        # Check military
        cursor.execute("SELECT total FROM military WHERE LOWER(state) = LOWER(?)", (state_name,))
        mil_data = cursor.fetchone()
        if mil_data:
            context += f"Faction Military: {mil_data['total']} troops. "
            
        # Check market
        cursor.execute("SELECT top_good FROM markets WHERE LOWER(burg) = LOWER(?)", (burg_name,))
        market_data = cursor.fetchone()
        if market_data:
            context += f"Market active, top goods: {market_data['top_good']}. "
            
        return context

    def get_spatial_features_near(self, x: float, y: float, radius: float = 1.0) -> list:
        """
        Instantly queries the SQLite database for GeoJSON features whose bounding box
        intersects the player's coordinate +/- radius.
        """
        logger.info(f"Performing spatial DB lookup near {x}, {y}...")
        cursor = self.conn.cursor()
        
        min_x = x - radius
        max_x = x + radius
        min_y = y - radius
        max_y = y + radius
        
        cursor.execute('''
            SELECT feature_type, properties_json 
            FROM spatial_features 
            WHERE NOT (max_x < ? OR min_x > ? OR max_y < ? OR min_y > ?)
        ''', (min_x, max_x, min_y, max_y))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "type": row["feature_type"],
                "properties": json.loads(row["properties_json"])
            })
            
        return results

    def get_burg_coords(self, burg_name: str) -> tuple[float, float]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT x, y FROM burgs WHERE LOWER(burg) = LOWER(?)", (burg_name,))
        row = cursor.fetchone()
        if row:
            return float(row["x"]), float(row["y"])
        return 0.0, 0.0
        
    def get_nearest_burg(self, x: float, y: float) -> str:
        cursor = self.conn.cursor()
        # Find the nearest burg by simple euclidean distance squared
        cursor.execute("SELECT burg, x, y FROM burgs")
        burgs = cursor.fetchall()
        
        nearest_burg = "Wilderness"
        min_dist = float('inf')
        for b in burgs:
            try:
                bx, by = float(b["x"]), float(b["y"])
                dist = (bx - x)**2 + (by - y)**2
                if dist < min_dist:
                    min_dist = dist
                    nearest_burg = b["burg"]
            except ValueError:
                continue # Skip if x/y aren't floats
                
        return nearest_burg

    def get_location_context(self, x: float, y: float) -> str:
        nearest_burg = self.get_nearest_burg(x, y)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT feature_type, properties_json 
            FROM spatial_features 
            WHERE ? BETWEEN min_x AND max_x AND ? BETWEEN min_y AND max_y
        ''', (x, y))
        
        features = cursor.fetchall()
        context = f"Near {nearest_burg}"
        
        found_features = []
        for f in features:
            try:
                props = json.loads(f["properties_json"])
                if "name" in props and props["name"]:
                    found_features.append(f"{props['name']} ({f['feature_type']})")
                elif "type" in props and props["type"]:
                    found_features.append(f"{props['type']} ({f['feature_type']})")
            except Exception:
                pass
                
        if found_features:
            context += f" [Features: {', '.join(found_features)}]"
            
        return context
        
    def get_all_burgs(self) -> list:
        cursor = self.conn.cursor()
        cursor.execute("SELECT burg, x, y, population, state FROM burgs")
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        return results

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
