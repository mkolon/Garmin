
import sys
import sqlite3
import pandas as pd
import os

def load_and_clean_csv(csv_path):
    print(f"📋 Loading and cleaning CSV data from: {csv_path}")
    df = pd.read_csv(csv_path)
    df.columns = [col.strip().lower() for col in df.columns]
    print(f"✅ Successfully processed {len(df)} activities from CSV")
    return df

def merge_to_sqlite(df_new, db_path, table_name='activities'):
    print(f"💾 Merging data into: {db_path}")
    conn = sqlite3.connect(db_path)

    try:
        if os.path.exists(db_path):
            print(f"📁 Database exists, checking for duplicates...")
            df_existing = pd.read_sql_query(f"SELECT title, date FROM {table_name}", conn)
            key_existing = set(tuple(x) for x in df_existing[['title', 'date']].dropna().values)

            df_filtered = df_new[~df_new[['title', 'date']].apply(tuple, axis=1).isin(key_existing)]
            print(f"✅ {len(df_filtered)} new record(s) to be added.")

            if not df_filtered.empty:
                # Align columns with table schema
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                table_columns = [row[1].lower() for row in cursor.fetchall()]
                df_filtered.columns = [col.lower() for col in df_filtered.columns]
                df_filtered = df_filtered[[col for col in df_filtered.columns if col in table_columns]]

                df_filtered.to_sql(table_name, conn, if_exists='append', index=False)
                print(f"📊 Successfully added {len(df_filtered)} new records.")
            else:
                print("ℹ️ No new records to add.")
        else:
            print(f"🆕 Creating new database and table: {table_name}")
            df_new.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"📊 Created new table and added {len(df_new)} records.")

    finally:
        conn.close()

def main():
    if len(sys.argv) != 4 or sys.argv[1] != "merge":
        print("Usage: python garmin_merge_simple.py merge Activities.csv garmin_activities.sqlite")
        sys.exit(1)

    _, _, csv_path, db_path = sys.argv
    df_new = load_and_clean_csv(csv_path)
    merge_to_sqlite(df_new, db_path)

if __name__ == "__main__":
    main()
