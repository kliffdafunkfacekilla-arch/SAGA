import sqlite3
import csv
import json
import glob
import os
import logging
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorldDBBuilder")

class WorldDBBuilder:
    def __init__(self, data_dir: str = r'C:\Users\krazy\Desktop\Okasha', db_path: str = r'c:\Users\krazy\Desktop\SAGA\beta_build\data\okasha.sqlite'):
        self.data_dir = data_dir
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def _get_file(self, pattern):
        matches = glob.glob(os.path.join(self.data_dir, pattern))
        return matches[0] if matches else None

    def ingest_csv(self, file_pattern: str, table_name: str):
        filepath = self._get_file(file_pattern)
        if not filepath:
            logger.warning(f"No file found for pattern {file_pattern}")
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            # Sanitize headers for SQLite
            clean_headers = [h.strip().replace(' ', '_').replace('.', '_').lower() for h in headers]
            
            # Create table
            cols_def = ", ".join([f'"{h}" TEXT' for h in clean_headers])
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.cursor.execute(f"CREATE TABLE {table_name} ({cols_def})")
            
            # Insert rows
            placeholders = ", ".join(["?" for _ in headers])
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            
            rows = [row for row in reader]
            self.cursor.executemany(insert_sql, rows)
            
            logger.info(f"Ingested {len(rows)} rows into {table_name} from {os.path.basename(filepath)}")
            
        self.conn.commit()

    def ingest_geojson(self, file_pattern: str, feature_type: str):
        filepath = self._get_file(file_pattern)
        if not filepath:
            logger.warning(f"No file found for {file_pattern}")
            return
            
        # Create table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS spatial_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_type TEXT,
                min_x REAL,
                max_x REAL,
                min_y REAL,
                max_y REAL,
                properties_json TEXT,
                geometry_json TEXT
            )
        ''')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            features = data.get("features", [])
            
            for feat in features:
                geom = feat.get("geometry", {})
                props = feat.get("properties", {})
                
                # Calculate Bounding Box
                min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
                
                coords = geom.get("coordinates", [])
                
                # Recursively extract all numbers from coordinates array to find min/max
                def extract_points(arr):
                    nonlocal min_x, max_x, min_y, max_y
                    if not arr: return
                    if isinstance(arr[0], (int, float)):
                        x, y = arr[0], arr[1]
                        min_x = min(min_x, x)
                        max_x = max(max_x, x)
                        min_y = min(min_y, y)
                        max_y = max(max_y, y)
                    else:
                        for sub_arr in arr:
                            extract_points(sub_arr)
                            
                extract_points(coords)
                
                if min_x == float('inf'):
                    min_x, max_x, min_y, max_y = 0.0, 0.0, 0.0, 0.0
                    
                self.cursor.execute('''
                    INSERT INTO spatial_features (feature_type, min_x, max_x, min_y, max_y, properties_json, geometry_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (feature_type, min_x, max_x, min_y, max_y, json.dumps(props), json.dumps(geom)))
                
            logger.info(f"Ingested {len(features)} {feature_type} features from {os.path.basename(filepath)}")
            
        self.conn.commit()

    def add_simulation_columns(self):
        # Add unrest and wealth to burgs
        try:
            self.cursor.execute("ALTER TABLE burgs ADD COLUMN unrest REAL DEFAULT 0.0")
            self.cursor.execute("ALTER TABLE burgs ADD COLUMN wealth REAL DEFAULT 50.0")
            
            # Base wealth based on market
            self.cursor.execute("UPDATE burgs SET wealth = 50.0")
            self.cursor.execute("UPDATE burgs SET unrest = 0.0")
            self.conn.commit()
            logger.info("Added simulation columns to burgs table")
        except sqlite3.OperationalError:
            pass # Columns likely exist

    def build(self):
        logger.info("Starting Database Build...")
        self.ingest_csv("Okasha Burgs*.csv", "burgs")
        self.ingest_csv("Okasha States*.csv", "states")
        self.ingest_csv("Okasha Cultures*.csv", "cultures")
        self.ingest_csv("Okasha Religions*.csv", "religions")
        self.ingest_csv("Okasha Biomes*.csv", "biomes")
        self.ingest_csv("Okasha Military*.csv", "military")
        self.ingest_csv("Okasha Markets_Overview*.csv", "markets")
        self.ingest_csv("Okasha Relations*.csv", "relations")
        
        # Spatial
        self.cursor.execute("DROP TABLE IF EXISTS spatial_features")
        self.ingest_geojson("Okasha Cells*.geojson", "cell")
        self.ingest_geojson("Okasha Rivers*.geojson", "river")
        self.ingest_geojson("Okasha Routes*.geojson", "route")
        self.ingest_geojson("Okasha Zones*.geojson", "zone")
        
        self.add_simulation_columns()
        
        logger.info("Database Build Complete!")
        self.conn.close()

if __name__ == "__main__":
    builder = WorldDBBuilder()
    builder.build()
