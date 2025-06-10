#!/usr/bin/env python3

import sys
import pandas as pd
import sqlite3
from datetime import datetime

ESSENTIAL_FIELDS = {
    "Activity Type": "activity_type",
    "Date": "date",
    "Title": "title",
    "Distance": "distance",
    "Calories": "calories",
    "Time": "time",
    "Avg HR": "avg_hr",
    "Max HR": "max_hr",
    "Total Ascent": "total_ascent"
}

def time_to_seconds(time_str):
    try:
        parts = [int(p) for p in time_str.split(":")]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
    except:
        return None
    return None

def clean_value(value):
    if pd.isna(value) or value in ("--", ""):
        return None
    return str(value).replace(",", "").strip()

def process_csv(csv_path):
    df_raw = pd.read_csv(csv_path)
    df = df_raw[list(ESSENTIAL_FIELDS.keys())].rename(columns=ESSENTIAL_FIELDS)

    # Clean and convert
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["distance"] = pd.to_numeric(df["distance"].apply(clean_value), errors="coerce")
    df["calories"] = pd.to_numeric(df["calories"].apply(clean_value), errors="coerce").round().astype("Int64")
    df["time"] = df["time"].apply(lambda t: time_to_seconds(clean_value(t))).astype("Int64")
    df["avg_hr"] = pd.to_numeric(df["avg_hr"].apply(clean_value), errors="coerce").round().astype("Int64")
    df["max_hr"] = pd.to_numeric(df["max_hr"].apply(clean_value), errors="coerce").round().astype("Int64")
    df["total_ascent"] = pd.to_numeric(df["total_ascent"].apply(clean_value), errors="coerce").round().astype("Int64")
    df["title"] = df["title"].astype(str).str.strip()
    df["activity_type"] = df["activity_type"].astype(str).str.strip()

    return df

def merge_to_database(csv_df, db_path):
    conn = sqlite3.connect(db_path)
    existing = pd.read_sql_query("SELECT title, date, distance FROM activities", conn)
    existing["date"] = pd.to_datetime(existing["date"], errors="coerce")

    # Deduplication
    merge_keys = ["title", "date", "distance"]
    new_df = pd.merge(csv_df, existing, on=merge_keys, how="left", indicator=True)
    clean_df = new_df[new_df["_merge"] == "left_only"].drop(columns=["_merge"])

    if not clean_df.empty:
        clean_df[[
            "activity_type", "date", "title", "distance", "calories",
            "time", "avg_hr", "max_hr", "total_ascent"
        ]].to_sql("activities", conn, if_exists="append", index=False)

    conn.close()
    print(f"{len(clean_df)} new record(s) added.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:\n  python garmin_csv_merge.py Activities.csv garmin_activities.sqlite")
        sys.exit(1)

    csv_file = sys.argv[1]
    db_file = sys.argv[2]

    print(f"Loading CSV: {csv_file}")
    df = process_csv(csv_file)
    print(f"Merging into database: {db_file}")
    merge_to_database(df, db_file)
