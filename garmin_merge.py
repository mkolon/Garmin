
import pandas as pd
import sqlite3
import sys

def convert_time_to_seconds(t):
    if pd.isna(t):
        return None
    try:
        parts = [int(float(p)) for p in str(t).split(':')]
        if len(parts) == 3:
            return parts[0]*3600 + parts[1]*60 + parts[2]
        elif len(parts) == 2:
            return parts[0]*60 + parts[1]
        elif len(parts) == 1:
            return parts[0]
    except Exception:
        return None

def merge_to_database(df, db_file):
    # Convert 'Time' to 'duration' in seconds
    df['duration'] = df['Time'].apply(convert_time_to_seconds)

    # Keep only relevant columns and make a copy to avoid chained-assignment warnings
    columns_to_keep = [
        'Activity Type', 'Date', 'Title', 'Distance', 'Calories',
        'duration', 'Avg HR', 'Max HR', 'Total Ascent'
    ]
    df = df[columns_to_keep].copy()

    # Rename to match DB schema
    df.columns = [
        'activity_type', 'date', 'title', 'distance', 'calories',
        'duration', 'avg_hr', 'max_hr', 'total_ascent'
    ]

    # Normalize activity_type to lowercase
    df['activity_type'] = df['activity_type'].str.lower()

    # Connect to DB and fetch existing keys for deduplication
    conn = sqlite3.connect(db_file)
    existing = pd.read_sql_query(
        "SELECT activity_type, date FROM activities", conn
    )

    # Drop any rows in df that already exist in the DB based on (activity_type, date)
    df = df.merge(
        existing, on=['activity_type', 'date'], how='left', indicator=True
    )
    df = df[df['_merge'] == 'left_only'].drop(columns=['_merge'])

    # Append only new rows
    if not df.empty:
        df.to_sql("activities", conn, if_exists="append", index=False)
    conn.close()

if __name__ == "__main__":
    csv_file = sys.argv[1]
    db_file = sys.argv[2]
    print(f"Loading CSV: {csv_file}")
    print(f"Merging into database: {db_file}")
    df = pd.read_csv(csv_file)
    merge_to_database(df, db_file)
