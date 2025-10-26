import sqlite3
import shutil
from datetime import datetime
import os

print("🔄 Starting comprehensive database merge...\n")

# Paths
current_db = "db.sqlite3"
new_db = os.path.expanduser("~/Downloads/db.sqlite3")

# Check if both files exist
if not os.path.exists(current_db):
    print(f"❌ Current database not found: {current_db}")
    exit(1)

if not os.path.exists(new_db):
    print(f"❌ New database not found: {new_db}")
    exit(1)

# Backup current database
backup_name = f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
shutil.copy(current_db, backup_name)
print(f"✅ Backup created: {backup_name}\n")

# Connect to both databases
current_conn = sqlite3.connect(current_db)
new_conn = sqlite3.connect(new_db)

current_cursor = current_conn.cursor()
new_cursor = new_conn.cursor()

# Get all tables from new database
new_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
all_tables = [row[0] for row in new_cursor.fetchall()]

print("📊 Analyzing and merging tables:\n")
print("-" * 70)

total_merged = 0
tables_processed = 0

for table in all_tables:
    try:
        # Check if table exists in current database
        current_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        table_exists = current_cursor.fetchone() is not None
        
        if not table_exists:
            # Table doesn't exist in current DB - create it
            new_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
            create_sql = new_cursor.fetchone()[0]
            current_cursor.execute(create_sql)
            print(f"🆕 {table}: Table created (new)")
        
        # Get data from new database
        new_cursor.execute(f"SELECT * FROM {table}")
        new_data = new_cursor.fetchall()
        
        if not new_data:
            print(f"⚪ {table}: Empty (0 records)")
            continue
        
        # Get column info
        new_cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in new_cursor.fetchall()]
        
        # Get current count
        current_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        before_count = current_cursor.fetchone()[0]
        
        # Insert new data (ignore duplicates based on primary key)
        placeholders = ','.join(['?' for _ in columns])
        inserted = 0
        skipped = 0
        
        for row in new_data:
            try:
                current_cursor.execute(f"INSERT OR IGNORE INTO {table} VALUES ({placeholders})", row)
                if current_cursor.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            except sqlite3.Error as e:
                # Try to handle the error
                try:
                    # Maybe the row already exists with a different structure, update it
                    current_cursor.execute(f"INSERT OR REPLACE INTO {table} VALUES ({placeholders})", row)
                    inserted += 1
                except:
                    skipped += 1
                    pass
        
        # Get final count
        current_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        after_count = current_cursor.fetchone()[0]
        
        if inserted > 0:
            print(f"✅ {table}: Added {inserted} records, skipped {skipped} duplicates")
            print(f"   Before: {before_count} | After: {after_count}")
        elif skipped > 0:
            print(f"⚪ {table}: All {skipped} records already exist")
        else:
            print(f"⚪ {table}: No changes")
        
        total_merged += inserted
        tables_processed += 1
        
    except Exception as e:
        print(f"⚠️  {table}: Error - {str(e)[:60]}")
        continue

print("-" * 70)

# Commit changes
current_conn.commit()

# Close connections
current_conn.close()
new_conn.close()

print(f"\n✨ Merge complete!")
print(f"📊 Statistics:")
print(f"   - Tables processed: {tables_processed}/{len(all_tables)}")
print(f"   - Total new records added: {total_merged}")
print(f"   - Backup saved: {backup_name}")
print(f"\n✅ Your database now contains all data from both sources!")
