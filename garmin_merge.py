import pandas as pd
import sqlite3
import sys
import os
import shutil
import datetime
import contextlib
from pathlib import Path

def parse_time_to_seconds(value):
    """
    Converts time strings in various formats (HH:MM:SS or MM:SS) to total seconds.
    """
    if isinstance(value, str) and ':' in value:
        try:
            parts = [float(p) for p in value.strip().split(":")]
            if len(parts) == 3:
                h, m, s = parts
            elif len(parts) == 2:
                h, m, s = 0, *parts
            else:
                return None
            return int(h * 3600 + m * 60 + s)
        except ValueError:
            return None
    return None

def clean_column_names(df):
    """
    Standardizes column names by converting to lowercase and removing whitespace.
    """
    df.columns = [col.strip().lower() for col in df.columns]
    return df

def load_and_clean_csv(csv_path):
    """
    Loads a Garmin CSV export and performs comprehensive data cleaning and normalization.
    """
    df = pd.read_csv(csv_path)
    df = clean_column_names(df)
    df.replace("--", pd.NA, inplace=True)
    
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].map(lambda x: x.replace(",", "").strip() if isinstance(x, str) else x)

    df['distance'] = pd.to_numeric(df.get('distance'), errors='coerce')
    df['calories'] = pd.to_numeric(df.get('calories'), errors='coerce')
    df.loc[(df['distance'] > 0) & (df['title'].str.lower().str.contains('bike|ride|cycling', na=False)), 'activity type'] = 'Cycling'
    df.loc[(df['distance'] > 0) & (df['title'].str.lower().str.contains('ski', na=False)), 'activity type'] = 'Skiing'

    df['duration_sec'] = df['time'].apply(parse_time_to_seconds)
    df['moving_time_sec'] = df['moving time'].apply(parse_time_to_seconds)
    df['elapsed_time_sec'] = df['elapsed time'].apply(parse_time_to_seconds)

    return df

class DatabaseBackupManager:
    """
    Handles database backup operations with multiple strategies for safety.
    
    This class provides:
    1. Automatic timestamped backups before any operation
    2. Rollback capability if operations fail
    3. Cleanup of old backups to prevent disk space issues
    4. Verification that backups are valid
    """
    
    def __init__(self, db_path, backup_dir=None, max_backups=10):
        """
        Initialize backup manager.
        
        Args:
            db_path: Path to the main database file
            backup_dir: Directory to store backups (default: same dir as db with '_backups' suffix)
            max_backups: Maximum number of backup files to keep
        """
        self.db_path = Path(db_path)
        self.max_backups = max_backups
        
        # Create backup directory next to database if not specified
        if backup_dir is None:
            self.backup_dir = self.db_path.parent / f"{self.db_path.stem}_backups"
        else:
            self.backup_dir = Path(backup_dir)
            
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🗂️  Backup directory: {self.backup_dir}")
    
    def create_backup(self, suffix="auto"):
        """
        Creates a timestamped backup of the database.
        
        Args:
            suffix: Optional suffix for the backup filename
            
        Returns:
            Path to the created backup file, or None if database doesn't exist
            
        Raises:
            Exception: If backup creation fails
        """
        if not self.db_path.exists():
            print("ℹ️  No existing database to backup")
            return None
            
        # Create timestamped backup filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{self.db_path.stem}_{timestamp}_{suffix}.sqlite"
        backup_path = self.backup_dir / backup_filename
        
        try:
            print(f"💾 Creating backup: {backup_filename}")
            
            # Copy the database file
            shutil.copy2(self.db_path, backup_path)
            
            # Verify the backup is valid by trying to open it
            self._verify_backup(backup_path)
            
            print(f"✅ Backup created successfully: {backup_path}")
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Backup creation failed: {str(e)}")
            # Remove partial backup file if it exists
            if backup_path.exists():
                backup_path.unlink()
            raise
    
    def _verify_backup(self, backup_path):
        """
        Verifies that a backup file is a valid SQLite database.
        
        Args:
            backup_path: Path to the backup file to verify
            
        Raises:
            Exception: If backup is not valid
        """
        try:
            conn = sqlite3.connect(backup_path)
            # Try to read the database schema
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            if not tables:
                raise Exception("Backup contains no tables")
                
        except Exception as e:
            raise Exception(f"Backup verification failed: {str(e)}")
    
    def _cleanup_old_backups(self):
        """
        Removes old backup files, keeping only the most recent max_backups files.
        """
        try:
            # Get all backup files sorted by modification time (newest first)
            backup_files = sorted(
                [f for f in self.backup_dir.glob("*.sqlite")],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Remove excess backups
            if len(backup_files) > self.max_backups:
                files_to_remove = backup_files[self.max_backups:]
                for old_backup in files_to_remove:
                    print(f"🗑️  Removing old backup: {old_backup.name}")
                    old_backup.unlink()
                    
        except Exception as e:
            print(f"⚠️  Warning: Cleanup of old backups failed: {str(e)}")
    
    def restore_backup(self, backup_path):
        """
        Restores database from a backup file.
        
        Args:
            backup_path: Path to the backup file to restore from
            
        Raises:
            Exception: If restore operation fails
        """
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise Exception(f"Backup file not found: {backup_path}")
        
        # Verify backup before restoring
        self._verify_backup(backup_path)
        
        print(f"🔄 Restoring database from: {backup_path.name}")
        
        # Create a backup of current state before restoring
        if self.db_path.exists():
            self.create_backup("pre_restore")
        
        # Copy backup to main database location
        shutil.copy2(backup_path, self.db_path)
        
        print("✅ Database restored successfully")
    
    def list_backups(self):
        """
        Lists all available backup files with their creation times.
        
        Returns:
            List of tuples: (backup_path, creation_time)
        """
        backup_files = []
        for backup_file in sorted(self.backup_dir.glob("*.sqlite"), key=lambda x: x.stat().st_mtime, reverse=True):
            creation_time = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
            backup_files.append((backup_file, creation_time))
        
        return backup_files

@contextlib.contextmanager
def safe_database_operation(db_path, backup_manager=None):
    """
    Context manager that provides automatic backup and rollback for database operations.
    
    Usage:
        with safe_database_operation(db_path) as (conn, backup_path):
            # Perform database operations
            # If an exception occurs, database will be automatically restored
    
    Args:
        db_path: Path to the database file
        backup_manager: Optional BackupManager instance
        
    Yields:
        tuple: (sqlite connection, backup_path)
    """
    if backup_manager is None:
        backup_manager = DatabaseBackupManager(db_path)
    
    # Create backup before operation
    backup_path = backup_manager.create_backup("operation")
    
    conn = None
    try:
        # Open database connection
        conn = sqlite3.connect(db_path)
        
        # Enable WAL mode for better concurrency and crash recovery
        conn.execute("PRAGMA journal_mode=WAL;")
        
        yield conn, backup_path
        
        # If we get here, operation was successful
        print("✅ Database operation completed successfully")
        
    except Exception as e:
        print(f"❌ Database operation failed: {str(e)}")
        
        # Close connection before restoring
        if conn:
            conn.close()
            conn = None
        
        # Restore from backup
        if backup_path:
            print("🔄 Restoring database from backup...")
            backup_manager.restore_backup(backup_path)
            
        # Re-raise the exception
        raise
        
    finally:
        # Ensure connection is closed
        if conn:
            conn.close()

def merge_to_sqlite_safe(df_new, db_path, table_name='activities'):
    """
    Safely merges new activity data with existing SQLite database using backup protection.
    
    This enhanced version:
    1. Creates automatic backups before any operation
    2. Uses transactions for atomicity
    3. Automatically restores from backup if anything goes wrong
    4. Provides detailed logging of the process
    
    Args:
        df_new: pandas DataFrame containing new activity data to add
        db_path: Path to the SQLite database file
        table_name: Name of the table in the database (default: 'activities')
    """
    backup_manager = DatabaseBackupManager(db_path)
    
    # Use the safe operation context manager
    with safe_database_operation(db_path, backup_manager) as (conn, backup_path):
        
        if os.path.exists(db_path):
            print(f"📁 Database exists, checking for duplicates...")
            
            # Begin transaction for atomicity
            conn.execute("BEGIN TRANSACTION;")
            
            try:
                # Read existing title and date combinations
                df_existing = pd.read_sql_query(f"SELECT title, date FROM {table_name}", conn)
                key_existing = set(tuple(x) for x in df_existing[['title', 'date']].dropna().values)
                
                # Filter out duplicates
                df_filtered = df_new[~df_new[['title', 'date']].apply(tuple, axis=1).isin(key_existing)]
                
                print(f"✅ {len(df_filtered)} new record(s) to be added.")
                
                if not df_filtered.empty:
                    # Instead of replacing entire table, append new records
                    df_filtered.to_sql(table_name, conn, if_exists='append', index=False)
                    print(f"📊 Successfully added {len(df_filtered)} new records.")
                else:
                    print("ℹ️  No new records to add.")
                
                # Commit transaction
                conn.execute("COMMIT;")
                
            except Exception as e:
                # Rollback transaction on any error
                conn.execute("ROLLBACK;")
                raise e
                
        else:
            print(f"🆕 Creating new database...")
            df_new.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"✅ Database created with {len(df_new)} records.")

def main():
    """
    Enhanced main function with backup management options.
    """
    if len(sys.argv) < 3:
        print("❌ Error: Incorrect number of arguments")
        print("Usage: python garmin_merge.py <command> [options]")
        print("")
        print("Commands:")
        print("  merge <csv_file> <db_file>     - Merge CSV data into database")
        print("  backup <db_file>               - Create manual backup")
        print("  restore <db_file> <backup_file> - Restore from backup")
        print("  list-backups <db_file>         - List available backups")
        print("")
        print("Examples:")
        print("  python garmin_merge.py merge Activities.csv garmin.sqlite")
        print("  python garmin_merge.py backup garmin.sqlite")
        print("  python garmin_merge.py restore garmin.sqlite garmin_20240315_backup.sqlite")
        sys.exit(1)

    command = sys.argv[1].lower()
    
    if command == "merge":
        if len(sys.argv) != 4:
            print("❌ Usage: python garmin_merge.py merge <csv_file> <db_file>")
            sys.exit(1)
            
        csv_path = sys.argv[2]
        db_path = sys.argv[3]
        
        print(f"🏃 Processing Garmin data from: {csv_path}")
        print(f"💾 Target database: {db_path}")
        print("")

        try:
            # Load and clean CSV data
            print("📋 Loading and cleaning CSV data...")
            df = load_and_clean_csv(csv_path)
            print(f"✅ Successfully processed {len(df)} activities from CSV")
            
            # Safely merge with database
            print("🔄 Safely merging with database...")
            merge_to_sqlite_safe(df, db_path)
            
            print("🎉 Process completed successfully!")
            
        except Exception as e:
            print(f"❌ Process failed: {str(e)}")
            print("💡 Database has been automatically restored from backup if it was modified.")
            sys.exit(1)
    
    elif command == "backup":
        if len(sys.argv) != 3:
            print("❌ Usage: python garmin_merge.py backup <db_file>")
            sys.exit(1)
            
        db_path = sys.argv[2]
        backup_manager = DatabaseBackupManager(db_path)
        backup_manager.create_backup("manual")
    
    elif command == "restore":
        if len(sys.argv) != 4:
            print("❌ Usage: python garmin_merge.py restore <db_file> <backup_file>")
            sys.exit(1)
            
        db_path = sys.argv[2]
        backup_file = sys.argv[3]
        
        backup_manager = DatabaseBackupManager(db_path)
        backup_manager.restore_backup(backup_file)
    
    elif command == "list-backups":
        if len(sys.argv) != 3:
            print("❌ Usage: python garmin_merge.py list-backups <db_file>")
            sys.exit(1)
            
        db_path = sys.argv[2]
        backup_manager = DatabaseBackupManager(db_path)
        backups = backup_manager.list_backups()
        
        if backups:
            print(f"📋 Available backups for {db_path}:")
            for backup_path, creation_time in backups:
                print(f"  • {backup_path.name} (created: {creation_time.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            print("ℹ️  No backups found.")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()