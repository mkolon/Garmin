#!/usr/bin/env zsh
set -euo pipefail

# -----------------------------
# Config — adjust if needed
# -----------------------------
CSV="$HOME/Downloads/Activities.csv"
DB="$HOME/git/Garmin/garmin_activities.sqlite"
BACKUP_DIR="$HOME/Google Drive/My Drive/Matt/Backups/Garmin Data/garmin_activities_backups"

# Where to keep the dedicated Python environment for this job
VENV_DIR="$HOME/garmin_venv"

# -----------------------------
# Helper: choose a Python to seed the venv
# -----------------------------
choose_bootstrap_python() {
  if [[ -x /opt/homebrew/bin/python3 ]]; then
    echo "/opt/homebrew/bin/python3"  # Homebrew Python (preferred)
  elif command -v python3 >/dev/null 2>&1; then
    command -v python3               # Fallback to whatever python3 is available
  else
    echo "ERROR: No python3 found on PATH." >&2
    exit 1
  fi
}

# -----------------------------
# Ensure venv exists and has pandas
# -----------------------------
ensure_venv() {
  local BOOTSTRAP
  BOOTSTRAP="$(choose_bootstrap_python)"

  if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    echo "Creating virtualenv at $VENV_DIR using $BOOTSTRAP"
    "$BOOTSTRAP" -m venv "$VENV_DIR"
  fi

  # Upgrade pip and ensure pandas is present
  echo "Upgrading pip in venv…"
  "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel

  if ! "$VENV_DIR/bin/python" -c 'import pandas' >/dev/null 2>&1; then
    echo "Installing pandas in venv…"
    "$VENV_DIR/bin/python" -m pip install pandas
  fi
}

# -----------------------------
# Main
# -----------------------------
main() {
  # Check inputs early
  if [[ ! -f "$CSV" ]]; then
    echo "ERROR: CSV not found: $CSV" >&2
    exit 1
  fi

  ensure_venv

  # Activate venv so any subprocess that calls "python" or "python3" uses this venv.
  # Also disable user site to avoid system/user mixups.
  source "$VENV_DIR/bin/activate"
  export PYTHONNOUSERSITE=1

  echo "Using Python: $(command -v python)"
  python -c 'import sys; print("Python version:", sys.version.split()[0])'
  python -c 'import pandas, sys; print("pandas:", pandas.__version__, "from", pandas.__file__)'

  # Timestamp and backup name
  DATE="$(date +%Y%m%d)"
  BACKUP_NAME="activities_database_${DATE}.sqlite"

  echo "Loading CSV: $CSV"
  echo "Merging into database: $DB"

  # Run your merge script with the venv python
  python "$HOME/git/Garmin/garmin_merge.py" "$CSV" "$DB"

  # Remove CSV after successful merge
  rm -f -- "$CSV"

  # Ensure backup dir and make a dated copy
  mkdir -p -- "$BACKUP_DIR"
  cp -p -- "$DB" "$BACKUP_DIR/$BACKUP_NAME"

  echo "Backup written to: $BACKUP_DIR/$BACKUP_NAME"
  echo "Done."
}

main "$@"

