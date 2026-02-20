import sqlite3
from datetime import datetime
import pytz
import re

DATABASE = 'baby_tracker.db'

def parse_time(date_str, time_str):
    """Parse date and time string into UTC ISO format"""
    # date_str format: "2/15"
    # time_str format: "3:30am" or "11:48am"
    
    month, day = date_str.split('/')
    
    # Parse time
    time_match = re.match(r'(\d+):(\d+)(am|pm)', time_str.lower())
    if not time_match:
        raise ValueError(f"Invalid time format: {time_str}")
    
    hour = int(time_match.group(1))
    minute = int(time_match.group(2))
    period = time_match.group(3)
    
    # Convert to 24-hour format
    if period == 'pm' and hour != 12:
        hour += 12
    elif period == 'am' and hour == 12:
        hour = 0
    
    # Create datetime object in America/Chicago timezone
    chicago_tz = pytz.timezone('America/Chicago')
    dt_local = chicago_tz.localize(datetime(2026, int(month), int(day), hour, minute))
    
    # Convert to UTC
    dt_utc = dt_local.astimezone(pytz.UTC)
    
    return dt_utc.isoformat()

def parse_diaper_file(filename):
    """Parse the diapers.txt file and return list of diapers"""
    diapers = []
    current_date = None
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if it's a date header (e.g., "2/15")
            if re.match(r'^\d+/\d+$', line):
                current_date = line
                continue
            
            # Remove bullet point if present
            line = line.replace('⁃', '').strip()
            
            # Check if it's a diaper entry (e.g., "poop 3:15am" or "Pee 9:00am")
            diaper_match = re.match(r'(poop|pee|both|dry|blowout)\s+(\d+:\d+\s*[ap]m)', line, re.IGNORECASE)
            if diaper_match and current_date:
                diaper_type = diaper_match.group(1).lower()
                time_str = diaper_match.group(2).replace(' ', '')
                
                # Skip "dry" entries as they're not in the valid types
                if diaper_type == 'dry':
                    print(f"Skipping 'dry' entry: {line}")
                    continue
                
                try:
                    timestamp = parse_time(current_date, time_str)
                    
                    diapers.append({
                        'type': diaper_type,
                        'timestamp': timestamp
                    })
                except ValueError as e:
                    print(f"Error parsing line: {line} - {e}")
    
    return diapers

def insert_diapers(diapers):
    """Insert diapers into the database"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    for diaper in diapers:
        try:
            cursor.execute(
                'INSERT INTO diapers (type, timestamp) VALUES (?, ?)',
                (diaper['type'], diaper['timestamp'])
            )
            print(f"Inserted: {diaper['type']} at {diaper['timestamp']}")
        except Exception as e:
            print(f"Error inserting diaper: {e}")
    
    db.commit()
    db.close()
    print(f"\n✅ Successfully inserted {len(diapers)} diapers")

if __name__ == '__main__':
    print("🚼 Parsing diaper backfill data...")
    diapers = parse_diaper_file('diapers.txt')
    print(f"Found {len(diapers)} diapers\n")
    
    print("💾 Inserting into database...")
    insert_diapers(diapers)
    print("\n✨ Diaper backfill complete!")
