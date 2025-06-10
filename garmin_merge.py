import csv
import sqlite3
import os

# Canonical mapping dictionary
ACTIVITY_TYPE_MAP = {
    'running': 'running',
    'treadmill running': 'running',
    'trail running': 'running',
    'cycling': 'cycling',
    'road cycling': 'cycling',
    'mountain biking': 'mountain biking',
    'biking': 'cycling',
    'walking': 'walking',
    'hiking': 'hiking',
    'backcountry skiing': 'backcountry skiing',
    'downhill skiing': 'resort skiing',
    'alpine skiing': 'resort skiing',
    'cross country skiing': 'backcountry skiing',
    'indoor rowing': 'indoor rowing',
    'rowing': 'outdoor rowing',
}

def normalize_activity_type(raw_type, title):
    t = (raw_type or "").strip().lower()
    title_lower = (title or "").lower()

    if t == "skiing":
        if "backcountry" in title_lower or "xc" in title_lower or "cross country" in title_lower or "skin" in title_lower:
            return "backcountry skiing"
        elif "resort" in title_lower or "alpine" in title_lower or "smugglers'" in title_lower or "stowe" in title_lower or "cambridge" in title_lower:
            return "resort skiing"
        else:
            return "resort skiing"
    elif t in ACTIVITY_TYPE_MAP:
        return ACTIVITY_TYPE_MAP[t]
    else:
        return ACTIVITY_TYPE_MAP.get(t, 'other')

def parse_time_to_seconds(time_str):
    if not time_str:
        return 0
    parts = list(map(int, time_str.strip().split(":")))
    if len(parts) == 3:
        h, m, s = parts
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = parts
        return m * 60 + s
    return int(parts[0]) if parts else 0

def merge_csv_to_db(csv_path, db_path):
    if not os.path.exists(csv_path) or not os.path.exists(db_path):
        print("CSV or DB path not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            raw_type = row.get("Activity Type")
            title = row.get("Title", "")
            date = row.get("Date")
            distance = float(row.get("Distance", 0) or 0)
            calories = int(row.get("Calories", 0) or 0)
            duration = parse_time_to_seconds(row.get("Time", "0:00"))
            avg_hr = int(row.get("Average Heart Rate", 0) or 0)
            max_hr = int(row.get("Max Heart Rate", 0) or 0)
            ascent = int(row.get("Total Ascent", 0) or 0)

            activity_type = normalize_activity_type(raw_type, title)

            cursor.execute("""
                SELECT COUNT(*) FROM activities
                WHERE activity_type = ? AND date = ?
            """, (activity_type, date))
            exists = cursor.fetchone()[0]

            if not exists:
                cursor.execute("""
                    INSERT INTO activities (
                        activity_type, date, title, distance, calories, duration, avg_hr, max_hr, total_ascent
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (activity_type, date, title, distance, calories, duration, avg_hr, max_hr, ascent))

    conn.commit()
    conn.close()
    print("Merge complete.")