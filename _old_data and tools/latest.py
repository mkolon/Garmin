import sqlite3
import pandas as pd

# Path to your local SQLite database file
db_path = "garmin_activities.sqlite"  # Adjust path if necessary

# Connect to the database
conn = sqlite3.connect(db_path)

# Query the latest 5 activities
query = """
SELECT title, date, calories
FROM activities
ORDER BY date DESC
LIMIT 5;
"""

# Execute and display results
df = pd.read_sql_query(query, conn)
print(df)

conn.close()

