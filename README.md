# Garmin Activity Tools – Quick Guide

These tools help you clean, merge, inspect, and manage Garmin CSV exports in a local SQLite database.  
Place all files in the same folder for easy operation.

---

## 📂 Files

- `Activities.csv` – Your Garmin-exported activity log
- `garmin_activities.sqlite` – Your SQLite database
- `garmin_merge.py` – Script to merge new activities into the database
- `check_latest.py` – Script to view the 10 most recent activities

---

## 🛠 Merge Script: `garmin_merge.py`

### Usage

```bash
python3 garmin_merge.py Activities.csv garmin_activities.sqlite
```

### Optional

```bash
--no-backup    # Skip automatic .bak_YYYYMMDD_HHMMSS backup of the database
```

### What It Does

- Cleans the Garmin CSV (removes commas, blanks, misformatted data)
- Converts times like `02:30:45` into seconds
- Preserves key fields like distance, calories, heart rate, ascent, etc.
- Safely adds new records without duplicating existing ones
- Creates a backup copy of the database unless `--no-backup` is used

---

## 🔍 Check Script: `check_latest.py`

### Usage

```bash
python3 check_latest.py                # Uses garmin_activities.sqlite by default
python3 check_latest.py other.sqlite  # Use a different database file
```

### What It Shows

- The 10 most recent activities
- Including title, date, distance, and calories

---

## ✅ Best Practices

- Always verify `Activities.csv` is freshly downloaded from Garmin Connect.
- Use the same filename (`garmin_activities.sqlite`) unless you intend to version it.
- Run the merge script each time you download new activities.
- Use the check script to confirm the import worked correctly.
