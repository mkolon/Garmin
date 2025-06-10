#!/usr/bin/env zsh
set -euo pipefail

# Paths
CSV="$HOME/Downloads/Activities.csv"
DB="$HOME/git/Garmin/garmin_activities.sqlite"
BACKUP_DIR="$HOME/Google Drive/My Drive/Matt/Backups/Garmin Data/garmin_activities_backups"

# Timestamp in YYYYMMDD
DATE="$(date +%Y%m%d)"
BACKUP_NAME="activities_database_${DATE}.sqlite"

# 1) Run the merge script
python3 ~/git/Garmin/garmin_merge.py "$CSV" "$DB"

# 2) Delete the CSV
rm -f -- "$CSV"

# 3) Ensure backup directory exists
mkdir -p -- "$BACKUP_DIR"

# 4) Copy the updated DB to backups with date suffix
cp -- "$DB" "${BACKUP_DIR}/${BACKUP_NAME}"

python3 latest.py

