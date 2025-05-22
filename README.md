# Garmin Activity Data Processor

A robust Python tool for importing and managing Garmin Connect activity data in SQLite databases. This script safely processes Garmin CSV exports, handles data cleaning, prevents duplicates, and provides comprehensive backup protection.

## Features

🚀 **Smart Data Processing**
- Automatically cleans and normalizes Garmin CSV exports
- Converts time formats (HH:MM:SS) to seconds for easy analysis
- Intelligently classifies activities based on title keywords
- Handles missing data and formatting inconsistencies

🛡️ **Backup & Safety**
- Automatic timestamped backups before any database operation
- Automatic rollback and restore if operations fail
- Transactional database operations for data integrity
- Configurable backup retention (default: keeps last 10 backups)

🔄 **Duplicate Prevention**
- Smart duplicate detection using title + date combinations
- Only adds truly new activities to prevent data duplication
- Safe for running multiple times with overlapping data

📊 **Database Management**
- Creates SQLite databases optimized for activity data analysis
- Supports both new database creation and existing database updates
- WAL mode enabled for better performance and crash recovery

## Requirements

- Python 3.6+ (tested on Python 3.11.3)
- pandas
- sqlite3 (included with Python)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/garmin-data-processor.git
cd garmin-data-processor
```

2. Install required dependencies:
```bash
pip install pandas
```

## Usage

### Basic Commands

#### Merge Garmin CSV data into database:
```bash
python garmin_merge.py merge Activities.csv garmin_activities.sqlite
```

#### Create manual backup:
```bash
python garmin_merge.py backup garmin_activities.sqlite
```

#### List available backups:
```bash
python garmin_merge.py list-backups garmin_activities.sqlite
```

#### Restore from backup:
```bash
python garmin_merge.py restore garmin_activities.sqlite backup_file.sqlite
```

### Getting Your Data from Garmin Connect

1. Log into [Garmin Connect](https://connect.garmin.com)
2. Go to Account Settings → Data Export
3. Request your data export
4. Download and extract the `Activities.csv` file
5. Use this CSV file with the script

## How It Works

### Data Processing Pipeline

1. **Load & Clean**: Reads Garmin CSV and handles formatting issues
   - Standardizes column names
   - Converts "--" placeholders to proper null values
   - Removes commas from numeric fields
   - Normalizes data types

2. **Time Conversion**: Converts time strings to seconds
   - `"1:23:45"` → `5025` seconds
   - `"23:45"` → `1425` seconds
   - Handles both HH:MM:SS and MM:SS formats

3. **Activity Classification**: Improves activity categorization
   - Detects cycling activities from title keywords
   - Identifies skiing activities
   - Preserves existing classifications

4. **Safe Database Merge**: Prevents duplicates and corruption
   - Creates automatic backup before any operation
   - Uses title + date combinations to detect duplicates
   - Atomic transactions with automatic rollback on failure

### Backup Strategy

The script implements a comprehensive backup strategy:

- **Automatic Backups**: Created before every database operation
- **Timestamped Files**: Format: `garmin_YYYYMMDD_HHMMSS_suffix.sqlite`
- **Backup Verification**: Each backup is tested for validity
- **Automatic Cleanup**: Removes old backups (configurable retention)
- **Emergency Restore**: Automatic rollback if operations fail

Backups are stored in a `{database_name}_backups/` directory next to your main database.

## Database Schema

The processed data includes these key fields:

| Field | Description | Type |
|-------|-------------|------|
| `title` | Activity name | Text |
| `date` | Activity date | Text |
| `activity_type` | Type of activity | Text |
| `distance` | Distance covered | Numeric |
| `calories` | Calories burned | Numeric |
| `duration_sec` | Total duration in seconds | Integer |
| `moving_time_sec` | Moving time in seconds | Integer |
| `elapsed_time_sec` | Elapsed time in seconds | Integer |

Plus all other fields from your Garmin CSV export.

## Examples

### First Time Setup
```bash
# Process your first Garmin export
python garmin_merge.py merge Activities.csv my_garmin_data.sqlite
# ✅ Database created with 1,250 records.
```

### Adding New Data
```bash
# Add new activities from recent export
python garmin_merge.py merge New_Activities.csv my_garmin_data.sqlite
# 💾 Creating backup: my_garmin_data_20241121_143022_auto.sqlite
# ✅ 47 truly new record(s) to be added.
# ✅ Database updated with 47 new records.
```

### Backup Management
```bash
# List available backups
python garmin_merge.py list-backups my_garmin_data.sqlite
# 📋 Available backups:
#   • my_garmin_data_20241121_143022_auto.sqlite (created: 2024-11-21 14:30:22)
#   • my_garmin_data_20241120_091505_manual.sqlite (created: 2024-11-20 09:15:05)

# Restore from backup if needed
python garmin_merge.py restore my_garmin_data.sqlite my_garmin_data_20241121_143022_auto.sqlite
```

## Safety Features

### What happens if something goes wrong?

1. **Script crashes during operation**: Database automatically restored from backup
2. **Corrupt CSV data**: Processing stops, database unchanged
3. **Power failure**: WAL mode ensures database consistency
4. **User error**: Manual restore available from timestamped backups

### Data Integrity Checks

- CSV data validation before processing
- Backup verification after creation
- Transaction-based database operations
- Duplicate detection and prevention

## Troubleshooting

### Common Issues

**"No module named 'pandas'"**
```bash
pip install pandas
```

**"Database is locked"**
- Close any database browser/editor applications
- Check if another instance of the script is running

**"Backup verification failed"**
- Check disk space availability
- Verify source database isn't corrupted
- Try creating manual backup first

**"No new records to add"**
- This is normal if you're re-processing the same CSV
- Check your CSV file has the expected date range

### Getting Help

If you encounter issues:

1. Check the backup directory for recent backups
2. Try the `list-backups` command to see available restore points
3. Use manual backup before trying risky operations
4. Check Python and pandas versions meet requirements

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for processing Garmin Connect activity exports
- Designed with data safety and integrity as top priorities
- Inspired by the need for reliable fitness data analysis tools

---

**⚠️ Important**: Always backup your data before processing. While this script includes comprehensive backup features, it's good practice to keep your own copies of important data files.
