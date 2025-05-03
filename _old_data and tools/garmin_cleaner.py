
import pandas as pd
import numpy as np
import sqlite3
import argparse

def clean_and_export(input_csv, output_sqlite, table_name="activities", null_threshold=0.25):
    # Load the dataset
    df = pd.read_csv(input_csv)

    # Standardize column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace("®", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(" ", "_")
    )

    # Convert date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Replace '--' with NaN and remove commas
    df.replace("--", np.nan, inplace=True)
    df = df.applymap(lambda x: x.replace(",", "") if isinstance(x, str) else x)

    # Convert numeric columns
    non_numeric = ["activity_type", "date", "favorite", "title"]
    numeric_columns = [col for col in df.columns if col not in non_numeric]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop columns with too many missing values
    threshold = len(df) * null_threshold
    df_reduced = df.dropna(axis=1, thresh=threshold)

    # Write to SQLite
    conn = sqlite3.connect(output_sqlite)
    df_reduced.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

    print(f"Data cleaned and exported to {output_sqlite}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean Garmin CSV and export to SQLite")
    parser.add_argument("input_csv", help="Path to input CSV file")
    parser.add_argument("output_sqlite", help="Path to output SQLite file")
    parser.add_argument("--table", default="activities", help="Table name in SQLite DB")
    parser.add_argument("--threshold", type=float, default=0.25, help="Null threshold (0.0-1.0)")
    args = parser.parse_args()

    clean_and_export(args.input_csv, args.output_sqlite, args.table, args.threshold)
