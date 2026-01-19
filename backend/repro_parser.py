from datetime import datetime
import re
from typing import Optional, Dict, Any

def parse_change_text(text: str):
    """Parse a change text string into a ScheduleChange object."""
    print(f"Parsing text: '{text}'")
    # Split by comma
    parts = [p.strip() for p in text.split(',')]
    print(f"Parts: {parts}")
    
    if len(parts) < 4:
        print("Not enough parts")
        return None
    
    # Extract date
    date = parts[0]
    
    # Extract lesson number
    lesson_match = re.search(r'שיעור\s+(\d+)', parts[1])
    if not lesson_match:
        print("No lesson match")
        return None
    lesson_number = int(lesson_match.group(1))
    
    # Teacher name
    teacher = parts[2]
    
    # Description and change type
    description = ', '.join(parts[3:])
    print(f"Description: '{description}'")
    
    change_type = 'cancellation'
    new_room = None
    
    if 'ביטול' in description:
        print("Found 'ביטול'")
        change_type = 'cancellation'
    elif 'החלפת חדר' in description:
        print("Found 'החלפת חדר'")
        change_type = 'room_change'
        # Extract new room number
        room_match = re.search(r'לחדר\s+(\S+)', description)
        if room_match:
            new_room = room_match.group(1)
            
    return {
        'date': date,
        'lesson_number': lesson_number,
        'teacher': teacher,
        'change_type': change_type,
        'description': description,
        'new_room': new_room
    }

# Test cases based on what we think the format is
test1 = "15.01.2026, שיעור 8, ששון נטע, החלפת חדר לקבוצה ששון נטע - שיעור 8"
print("\n--- Test 1 ---")
print(parse_change_text(test1))
