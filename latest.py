import sqlite3
import pandas as pd
import sys
import os

# Default database filename
default_db = "garmin_activities.sqlite"
db_path = sys.argv[1] if len(sys.argv) > 1 else default_db

# Validate existence
if not os.path.isfile(db_path):
    print(f"Database file not found: {db_path}")
    sys.exit(1)

# Connect and query
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("""
    SELECT title, date, distance, calories
    FROM activities
    ORDER BY date DESC
    LIMIT 10;
""", conn)

print(df.to_string(index=False))
