import sqlite3
import shutil
from datetime import datetime

print("🔄 Starting database merge...\n")

# Backup your current database
backup_name = f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
shutil.copy("db.sqlite3", backup_name)
print(f"✅ Backup created: {backup_name}\n")

# Connect to both databases
your_db = sqlite3.connect("db.sqlite3")
friend_db = sqlite3.connect(r"C:\Users\dhiab\Downloads\db.sqlite3")

your_cursor = your_db.cursor()
friend_cursor = friend_db.cursor()

# Get all tables
friend_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'django_%'")
tables = [row[0] for row in friend_cursor.fetchall()]

print("📊 Merging tables:\n")

merged_count = 0

for table in tables:
    try:
        # Get data from friend's database
        friend_cursor.execute(f"SELECT * FROM {table}")
        friend_data = friend_cursor.fetchall()
        
        if not friend_data:
            continue
            
        # Get column info
        friend_cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in friend_cursor.fetchall()]
        placeholders = ','.join(['?' for _ in columns])
        
        # Insert into your database (ignore duplicates)
        inserted = 0
        for row in friend_data:
            try:
                your_cursor.execute(f"INSERT OR IGNORE INTO {table} VALUES ({placeholders})", row)
                if your_cursor.rowcount > 0:
                    inserted += 1
            except:
                pass
        
        if inserted > 0:
            print(f"✅ {table}: Added {inserted} new records")
            merged_count += inserted
        
    except Exception as e:
        print(f"⚠️  {table}: Skipped ({str(e)[:50]})")

# Commit and close
your_db.commit()
your_db.close()
friend_db.close()

print(f"\n✨ Merge complete! Added {merged_count} total records")
print(f"📁 Your original database is backed up as: {backup_name}")
