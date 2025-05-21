# Garmin Merge Tool

This Python script imports activities from a Garmin Connect CSV export into a local SQLite database (`garmin_activities.sqlite`). It cleans, normalizes, and deduplicates data, ensuring that only new activity records are added.

---

## 🔧 Features

- Cleans Garmin-exported CSV data
- Normalizes field names and data formats
- Converts time strings (`HH:MM:SS`) to seconds
- Standardizes activity types (e.g., all cycling → `Cycling`)
- Skips duplicate entries (using `(title, date)` as keys)
- Updates the database in-place

---

## 🗂 Requirements

- Python 3.7+
- pandas
- sqlite3 (built-in with Python)

Install dependencies with:

```bash
pip install pandas

