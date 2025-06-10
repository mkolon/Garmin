# Garmin Activity Merge & Display Tools

This repository provides tools to manage and inspect a personal activity database exported from Garmin Connect. The database is stored in SQLite and updated via a custom merge script. A separate script is available to view the latest activity records from the terminal.

## Files

- `garmin_activities_normalized_updated.sqlite`  
  SQLite database containing normalized activity data (canonical types, clean fields, no duplicates).

- `garmin_merge.py`  
  Script to merge new Garmin Connect exports into the database. It performs deduplication, normalization, and basic validation.

- `show_recent_activities.py`  
  Script to display the last 10 activities in a readable, multi-line format from the terminal.

---

## Canonical Activity Types

The system normalizes Garmin activity types to a fixed set:

```
running, hiking, walking, cycling, mountain biking, backcountry skiing,
resort skiing, nordic skiing, indoor rowing, outdoor rowing, other
```

Unrecognized types default to `other`. Some types (e.g. “skiing”) are inferred from activity titles if needed.

---

## Usage

### 1. Merge New Activities

To merge a new CSV export from Garmin Connect:

1. Place the exported file (e.g., `Activities.csv`) in the same directory.
2. Run the merge script:

```bash
python garmin_merge.py
```

This will:
- Normalize activity types
- Convert time to duration (in seconds)
- Reject invalid records (e.g., distance = 0, heart rate > 240)
- Skip duplicates based on `activity_type` and `date`

The script is safe to run multiple times with overlapping or identical data.

---

### 2. View Recent Activities

To view the last 10 activities in the terminal:

```bash
python show_recent_activities.py
```

Each activity is printed using a multi-line layout showing:

- Activity type
- Timestamp
- Title
- Distance (miles)
- Duration (seconds)
- Calories
- Average and max heart rate
- Total ascent

---

## Schema

The SQLite `activities` table contains the following fields:

| Field          | Type     | Description                       |
|----------------|----------|-----------------------------------|
| activity_type  | TEXT     | Canonical activity type           |
| date           | TEXT     | Timestamp (ISO 8601)              |
| title          | TEXT     | Garmin-exported title             |
| distance       | REAL     | Distance in miles                 |
| calories       | INTEGER  | Calories burned                   |
| duration       | INTEGER  | Duration in seconds               |
| avg_hr         | INTEGER  | Average heart rate (if available) |
| max_hr         | INTEGER  | Max heart rate (if available)     |
| total_ascent   | INTEGER  | Elevation gain (units vary)       |

---

## Requirements

- Python 3.6+
- Standard library only (no external packages required)

---

## Notes

- The database assumes Garmin Connect exports in their default CSV format.
- If Garmin changes field names or formatting, minor updates to `garmin_merge.py` may be required.
- No raw activity types or extra metadata are stored — this is an intentionally compact schema.
