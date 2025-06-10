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


