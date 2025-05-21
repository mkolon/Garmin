
def main():
    import sys
    import os
    import pandas as pd
    import sqlite3
    import shutil
    import datetime
    import numpy as np

    # Handle optional --no-backup flag
    args = sys.argv[1:]
    skip_backup = '--no-backup' in args
    args = [arg for arg in args if arg != '--no-backup']

    if len(args) != 2:
        print("Usage: python garmin_merge.py input.csv output.sqlite [--no-backup]")
        sys.exit(1)

    csv_file, db_file = args
    table_name = "activities"

    if not skip_backup and os.path.exists(db_file):
        backup_path = db_file + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(db_file, backup_path)
        print(f"🗂️  Backup created: {backup_path}")

    df = pd.read_csv(csv_file)
    df.columns = [col.strip().lower() for col in df.columns]
    df.replace("--", pd.NA, inplace=True)
    df = df.applymap(lambda x: x.replace(",", "").strip() if isinstance(x, str) else x)

    # Normalize activity_type
    df['distance'] = pd.to_numeric(df['distance'], errors='coerce')
    df.loc[(df['distance'] > 0) & (df['title'].str.lower().str.contains('bike|ride|cycling', na=False)), 'activity type'] = 'Cycling'
    df.loc[(df['distance'] > 0) & (df['title'].str.lower().str.contains('ski', na=False)), 'activity type'] = 'Skiing'

    non_numeric = ['activity type', 'date', 'favorite', 'title', 'time', 'moving time', 'elapsed time', 'best lap time']
    numeric_columns = [col for col in df.columns if col not in non_numeric]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for time_col, target in [('time', 'duration_sec'), ('moving time', 'moving_time_sec'), ('elapsed time', 'elapsed_time_sec')]:
        def parse_time(val):
            if isinstance(val, str) and ":" in val:
                parts = [int(x) for x in val.strip().split(":")]
                return sum(x * 60 ** i for i, x in enumerate(reversed(parts)))
            return None
        df[target] = df[time_col].apply(parse_time)

    if os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        existing_df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.drop_duplicates(subset=['title', 'date'], keep='last', inplace=True)
    else:
        conn = sqlite3.connect(db_file)
        combined_df = df

    combined_df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"✅ {len(df)} record(s) processed. Database updated: {db_file}")

if __name__ == "__main__":
    main()
