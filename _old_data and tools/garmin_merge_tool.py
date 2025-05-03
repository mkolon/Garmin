
import pandas as pd
import numpy as np
import sqlite3
import argparse
import os

def clean_data(df):
    # Standardize column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace("®", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(" ", "_")
    )

    if "activity_type" in df.columns:
        df["activity_type"] = df["activity_type"].str.strip().str.title()

    # Convert date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Replace '--' with NaN and remove commas
    df.replace("--", np.nan, inplace=True)
    df = df.applymap(lambda x: x.replace(",", "") if isinstance(x, str) else x)

    # Convert likely numeric columns
    non_numeric = ["activity_type", "date", "favorite", "title"]
    numeric_columns = [col for col in df.columns if col not in non_numeric]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def merge_to_sqlite(new_data, db_path, table_name="activities", key_columns=None):
    # Connect to or create database
    conn = sqlite3.connect(db_path)

    if not key_columns:
        key_columns = ["date", "activity_type", "title"]

    # Check if table exists
    existing_df = pd.DataFrame()
    if os.path.exists(db_path):
        try:
            existing_df = pd.read_sql(f"SELECT * FROM {table_name}", conn, parse_dates=["date"])
        except Exception:
            pass

    if not existing_df.empty:
        # Merge without duplicates
        combined_df = pd.concat([existing_df, new_data], ignore_index=True)
        combined_df.drop_duplicates(subset=key_columns, inplace=True)
        new_count = len(combined_df) - len(existing_df)
    else:
        combined_df = new_data.copy()
        new_count = len(new_data)

    # Write to SQLite
    combined_df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ {new_count} new record(s) added. Database updated: {db_path}")

def main():
    parser = argparse.ArgumentParser(description="Clean and merge Garmin data into SQLite DB")
    parser.add_argument("input_csv", help="Path to the new Garmin CSV file")
    parser.add_argument("output_sqlite", help="Path to the output SQLite database")
    parser.add_argument("--table", default="activities", help="Table name")
    args = parser.parse_args()

    raw_df = pd.read_csv(args.input_csv)
    clean_df = clean_data(raw_df)
    merge_to_sqlite(clean_df, args.output_sqlite, table_name=args.table)

if __name__ == "__main__":
    main()
