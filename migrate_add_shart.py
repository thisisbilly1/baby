"""
Migrate database to add 'shart' to the diapers type constraint
"""
import sqlite3
import os

DATABASE = 'baby_tracker.db'

def migrate():
    if not os.path.exists(DATABASE):
        print(f"Database {DATABASE} not found!")
        return
    
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    try:
        # Create new table with updated constraint
        cursor.execute('''
            CREATE TABLE diapers_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                type TEXT NOT NULL CHECK(type IN ('pee', 'poop', 'both', 'blowout', 'shart'))
            )
        ''')
        
        # Copy data from old table
        cursor.execute('INSERT INTO diapers_new SELECT * FROM diapers')
        
        # Drop old table
        cursor.execute('DROP TABLE diapers')
        
        # Rename new table
        cursor.execute('ALTER TABLE diapers_new RENAME TO diapers')
        
        db.commit()
        print("✅ Database migrated successfully! 'shart' option is now available.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        
    finally:
        db.close()

if __name__ == '__main__':
    migrate()
