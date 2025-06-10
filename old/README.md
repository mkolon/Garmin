# Garmin Activity Merge Tool

This script merges new Garmin activity data from a CSV export (`Activities.csv`) into a local SQLite database (`garmin_activities.sqlite`).

## Features

- Loads and cleans the Garmin CSV file
- Normalizes column names to lowercase with underscores
- Converts `date` and `time` fields to ISO 8601 format for consistency
- Prevents duplicate entries by comparing on `title` and `date`
- Only inserts new records not already in the database

## Usage

```bash
python garmin_merge.py Activities.csv garmin_activities.sqlite
```

## Deployment Details

- This script doesn't handle backups, so a process or wrapper that will back up the database either before or after the mege is required to guard against corruption.
- The current deployment requires a manual backup to cloud storage.



