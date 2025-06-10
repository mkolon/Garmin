import sqlite3
from textwrap import indent

DB_PATH = "garmin_activities.sqlite"

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
        print(f"\n=== Activity #{i} ===")
        print(f"Type:          {row[0]}")
        print(f"Date:          {row[1]}")
        print(f"Title:         {row[2]}")
        print(f"Distance (mi): {row[3]}")
        print(f"Calories:      {row[4]}")
        print(f"Duration (s):  {row[5]}")
        print(f"Avg HR:        {row[6]}")
        print(f"Max HR:        {row[7]}")
        print(f"Total Ascent:  {row[8]}")

if __name__ == "__main__":
    show_last_10_activities()


