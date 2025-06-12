import sqlite3

DB_PATH = "garmin_activities.sqlite"

def format_duration(seconds):
    """Round seconds to the nearest minute and return HH:MM."""
    if seconds is None:
        return "00:00"
    total_minutes = int((seconds + 30) // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"

def show_last_10_activities():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT activity_type, date, title, distance, calories,
               duration, avg_hr, max_hr, total_ascent
        FROM activities
        ORDER BY date DESC
        LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()

    for i, row in enumerate(rows, start=1):
        formatted_duration = format_duration(row[5])
        print(f"=== Activity #{i} ===")
        print(f"Type:          {row[0]}")
        print(f"Date:          {row[1]}")
        print(f"Title:         {row[2]}")
        print(f"Distance:      {row[3]}")
        print(f"Calories:      {row[4]}")
        print(f"Duration:      {formatted_duration}")
        print(f"Avg HR:        {row[6]}")
        print(f"Max HR:        {row[7]}")
        print(f"Total Ascent:  {row[8]}")

if __name__ == "__main__":
    show_last_10_activities()
