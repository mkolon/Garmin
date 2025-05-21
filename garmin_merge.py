
import pandas as pd
import sqlite3
import sys
import os

def parse_time_to_seconds(value):
    if isinstance(value, str) and ':' in value:
        try:
            parts = [float(p) for p in value.strip().split(":")]
            if len(parts) == 3:
                h, m, s = parts
            elif len(parts) == 2:
                h, m, s = 0, *parts
            else:
                return None
            return int(h * 3600 + m * 60 + s)
        except ValueError:
            return None
    return None

def clean_column_names(df):
    df.columns = [col.strip().lower() for col in df.columns]
    return df

def load_and_clean_csv(csv_path):
    df = pd.read_csv(csv_path)
    df = clean_column_names(df)
    df.replace("--", pd.NA, inplace=True)
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].map(lambda x: x.replace(",", "").strip() if isinstance(x, str) else x)

    # Normalize fields
    df['distance'] = pd.to_numeric(df.get('distance'), errors='coerce')
    df['calories'] = pd.to_numeric(df.get('calories'), errors='coerce')
    df.loc[(df['distance'] > 0) & (df['title'].str.lower().str.contains('bike|ride|cycling', na=False)), 'activity type'] = 'Cycling'
    df.loc[(df['distance'] > 0) & (df['title'].str.lower().str.contains('ski', na=False)), 'activity type'] = 'Skiing'

    df['duration_sec'] = df['time'].apply(parse_time_to_seconds)
    df['moving_time_sec'] = df['moving time'].apply(parse_time_to_seconds)
    df['elapsed_time_sec'] = df['elapsed time'].apply(parse_time_to_seconds)

    return df

def merge_to_sqlite(df_new, db_path, table_name='activities'):
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        df_existing = pd.read_sql_query(f"SELECT title, date FROM {table_name}", conn)
        key_existing = set(tuple(x) for x in df_existing[['title', 'date']].dropna().values)
        df_filtered = df_new[~df_new[['title', 'date']].apply(tuple, axis=1).isin(key_existing)]
        print(f"✅ {len(df_filtered)} truly new record(s) to be added.")
        if not df_filtered.empty:
            df_full = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            df_merged = pd.concat([df_full, df_filtered], ignore_index=True)
            df_merged.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
    else:
        conn = sqlite3.connect(db_path)
        df_new.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"✅ Database created with {len(df_new)} records.")
        conn.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: python garmin_merge_clean.py Activities.csv garmin_activities.sqlite")
        sys.exit(1)

    csv_path = sys.argv[1]
    db_path = sys.argv[2]

    df = load_and_clean_csv(csv_path)
    merge_to_sqlite(df, db_path)

if __name__ == "__main__":
    main()
