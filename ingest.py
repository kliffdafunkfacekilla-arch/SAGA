import pandas as pd
from sqlalchemy import create_engine
import os

# Connect to your DB (Using SQLite)
engine = create_engine('sqlite:///okasha_world.db')

# Load your CSV
# Ensure the CSV exists in the same directory, or provide the full path
csv_path = 'Okasha Burgs.csv'
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    # Push data to your table
    df.to_sql('region_cells', engine, if_exists='append', index=False)
    print("Data ingested successfully!")
else:
    print(f"Error: Could not find {csv_path}. Please make sure the file is in the same directory.")
