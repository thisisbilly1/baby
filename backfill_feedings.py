import sqlite3
from datetime import datetime
import pytz
import re

DATABASE = 'baby_tracker.db'

def parse_time(date_str, time_str):
    """Parse date and time string into UTC ISO format"""
    # Assume year 2026 based on context
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

def parse_backfill_file(filename):
    """Parse the backfill.txt file and return list of feedings"""
    feedings = []
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
            
            # Check if it's a time range (e.g., "3:30am to 5:30am")
            # Remove bullet point if present
            line = line.replace('⁃', '').strip()
            
            time_match = re.match(r'(\d+:\d+\s*[ap]m)\s+to\s+(\d+:\d+\s*[ap]m)', line, re.IGNORECASE)
            if time_match and current_date:
                start_time_str = time_match.group(1).replace(' ', '')
                end_time_str = time_match.group(2).replace(' ', '')
                
                try:
                    start_time = parse_time(current_date, start_time_str)
                    end_time = parse_time(current_date, end_time_str)
                    
                    feedings.append({
                        'start_time': start_time,
                        'end_time': end_time
                    })
                except ValueError as e:
                    print(f"Error parsing line: {line} - {e}")
    
    return feedings

def insert_feedings(feedings):
    """Insert feedings into the database"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    for feeding in feedings:
        try:
            cursor.execute(
                'INSERT INTO feedings (start_time, end_time) VALUES (?, ?)',
                (feeding['start_time'], feeding['end_time'])
            )
            print(f"Inserted: {feeding['start_time']} to {feeding['end_time']}")
        except Exception as e:
            print(f"Error inserting feeding: {e}")
    
    db.commit()
    db.close()
    print(f"\n✅ Successfully inserted {len(feedings)} feedings")

if __name__ == '__main__':
    print("🍼 Parsing backfill data...")
    feedings = parse_backfill_file('feedings.txt')
    print(f"Found {len(feedings)} feedings\n")
    
    print("💾 Inserting into database...")
    insert_feedings(feedings)
    print("\n✨ Backfill complete!")
