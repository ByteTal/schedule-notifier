"""
Web scraper for Begin High School schedule website.
Handles ASP.NET postback mechanism to extract schedule and changes data.
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScheduleLesson:
    """Represents a single lesson in the schedule."""
    day: str
    lesson_number: int
    subject: str
    teacher: str
    room: str = ""
    group: str = ""


@dataclass
class ScheduleChange:
    """Represents a schedule change (cancellation or room change)."""
    date: str
    lesson_number: int
    teacher: str
    change_type: str  # 'cancellation' or 'room_change'
    description: str
    new_room: Optional[str] = None


class BeginHSScraper:
    """Scraper for Begin High School schedule website."""
    
    BASE_URL = "https://beginhs.iscool.co.il/Default.aspx?TabId=4645&language=he-IL"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.viewstate = None
        self.viewstate_generator = None
        self.event_validation = None
    
    def _get_initial_page(self) -> BeautifulSoup:
        """Load the initial page and extract ASP.NET state variables."""
        response = self.session.get(self.BASE_URL, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract ASP.NET state variables
        self.viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
        self.viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
        event_val = soup.find('input', {'name': '__EVENTVALIDATION'})
        if event_val:
            self.event_validation = event_val['value']
        
        return soup
    
    def _do_postback(self, event_target: str, event_argument: str = '') -> BeautifulSoup:
        """Perform an ASP.NET postback."""
        data = {
            '__EVENTTARGET': event_target,
            '__EVENTARGUMENT': event_argument,
            '__VIEWSTATE': self.viewstate,
            '__VIEWSTATEGENERATOR': self.viewstate_generator,
        }
        
        if self.event_validation:
            data['__EVENTVALIDATION'] = self.event_validation
        
        response = self.session.post(self.BASE_URL, data=data, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Update state variables
        viewstate_input = soup.find('input', {'name': '__VIEWSTATE'})
        if viewstate_input:
            self.viewstate = viewstate_input['value']
        
        viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
        if viewstate_gen:
            self.viewstate_generator = viewstate_gen['value']
        
        event_val = soup.find('input', {'name': '__EVENTVALIDATION'})
        if event_val:
            self.event_validation = event_val['value']
        
        return soup
    
    def get_class_list(self) -> Dict[str, str]:
        """
        Get list of all available classes.
        Returns: Dict mapping class names to their internal IDs.
        """
        soup = self._get_initial_page()
        
        # Find the class dropdown
        class_select = soup.find('select', {'name': re.compile(r'.*ClassesList.*')})
        
        if not class_select:
            return {}
        
        classes = {}
        for option in class_select.find_all('option'):
            if option.get('value'):
                classes[option.text.strip()] = option['value']
        
        return classes
    
    def _select_class(self, class_id: str) -> BeautifulSoup:
        """Select a specific class."""
        # First load the page
        soup = self._get_initial_page()
        
        # Do a postback with the selected class value
        data = {
            '__EVENTTARGET': 'dnn$ctr16506$TimeTableView$ClassesList',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': self.viewstate,
            '__VIEWSTATEGENERATOR': self.viewstate_generator,
            'dnn$ctr16506$TimeTableView$ClassesList': class_id,
        }
        
        if self.event_validation:
            data['__EVENTVALIDATION'] = self.event_validation
        
        response = self.session.post(self.BASE_URL, data=data, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Update state variables after class selection
        viewstate_input = soup.find('input', {'name': '__VIEWSTATE'})
        if viewstate_input:
            self.viewstate = viewstate_input['value']
        
        viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
        if viewstate_gen:
            self.viewstate_generator = viewstate_gen['value']
        
        event_val = soup.find('input', {'name': '__EVENTVALIDATION'})
        if event_val:
            self.event_validation = event_val['value']
        
        return soup
    
    def get_schedule(self, class_id: str) -> List[ScheduleLesson]:
        """
        Get the weekly schedule for a specific class.
        Returns: List of ScheduleLesson objects.
        """
        # Select the class first
        self._select_class(class_id)
        
        # Now click on the schedule tab (מערכת שעות)
        soup = self._do_postback('dnn$ctr16506$TimeTableView$btnTimeTable', '')
        
        # Parse the schedule table
        lessons = []
        
        # Find the schedule table (TTTable class)
        table = soup.find('table', class_='TTTable')
        if not table:
            return lessons
        
        # Days of the week (columns)
        days = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי']
        
        # Iterate through rows (lessons)
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for lesson_num, row in enumerate(rows, start=1):
            cells = row.find_all('td', class_='TTCell')
            
            for day_idx, cell in enumerate(cells):
                if day_idx >= len(days):
                    break
                
                # Find all lessons in this cell (can have multiple)
                lesson_divs = cell.find_all('div', class_='TTLesson')
                
                for lesson_div in lesson_divs:
                    # Extract subject (in <b> tag)
                    subject_tag = lesson_div.find('b')
                    if not subject_tag:
                        continue
                    
                    subject_text = subject_tag.text.strip()
                    
                    # Extract room/group info (in parentheses)
                    room = ""
                    group = ""
                    room_match = re.search(r'\(([^)]+)\)', subject_text)
                    if room_match:
                        room_info = room_match.group(1)
                        if 'קבוצה' in room_info:
                            group = room_info
                        else:
                            room = room_info
                        subject_text = subject_text[:room_match.start()].strip()
                    
                    # Extract teacher (after <br>)
                    teacher = ""
                    br_tag = lesson_div.find('br')
                    if br_tag and br_tag.next_sibling:
                        teacher = br_tag.next_sibling.strip()
                    
                    if subject_text and teacher:
                        lessons.append(ScheduleLesson(
                            day=days[day_idx],
                            lesson_number=lesson_num,
                            subject=subject_text,
                            teacher=teacher,
                            room=room,
                            group=group
                        ))
        
        return lessons
    
    def get_changes(self, class_id: str) -> List[ScheduleChange]:
        """
        Get current schedule changes for a specific class.
        Returns: List of ScheduleChange objects.
        """
        # Select the class
        self._select_class(class_id)
        
        # Click on the changes tab
        soup = self._do_postback('dnn$ctr16506$TimeTableView$btnChanges', '')
        
        # Parse the changes
        changes = []
        
        # Find all change cells (MsgCell class)
        change_cells = soup.find_all('td', class_='MsgCell')
        
        for cell in change_cells:
            text = cell.get_text(strip=True)
            if not text:
                continue
            
            # Parse the change text
            # Format: "DD.MM.YYYY, שיעור N, Teacher Name, Description"
            change = self._parse_change_text(text)
            if change:
                changes.append(change)
        
        return changes
    
    def _parse_change_text(self, text: str) -> Optional[ScheduleChange]:
        """Parse a change text string into a ScheduleChange object."""
        # Split by comma
        parts = [p.strip() for p in text.split(',')]
        
        if len(parts) < 4:
            return None
        
        # Extract date
        date = parts[0]
        
        # Extract lesson number
        lesson_match = re.search(r'שיעור\s+(\d+)', parts[1])
        if not lesson_match:
            return None
        lesson_number = int(lesson_match.group(1))
        
        # Teacher name
        teacher = parts[2]
        
        # Description and change type
        description = ', '.join(parts[3:])
        
        change_type = 'cancellation'
        new_room = None
        
        if 'ביטול' in description:
            change_type = 'cancellation'
        elif 'החלפת חדר' in description:
            change_type = 'room_change'
            # Extract new room number
            room_match = re.search(r'לחדר\s+(\S+)', description)
            if room_match:
                new_room = room_match.group(1)
        
        return ScheduleChange(
            date=date,
            lesson_number=lesson_number,
            teacher=teacher,
            change_type=change_type,
            description=description,
            new_room=new_room
        )
    
    def get_unique_subjects(self, class_id: str) -> Dict[str, List[str]]:
        """
        Get unique subjects and their teachers for a class.
        Groups subjects with same base name and teacher (e.g., ספרות 30, ספרות 70 → ספרות)
        Returns: Dict mapping subject names to list of teacher names.
        """
        lessons = self.get_schedule(class_id)
        
        # First, collect all subject-teacher pairs
        subject_teacher_pairs = {}
        for lesson in lessons:
            # Remove numbers and extra spaces from subject name
            base_subject = re.sub(r'\s*\d+\s*$', '', lesson.subject).strip()
            
            if base_subject not in subject_teacher_pairs:
                subject_teacher_pairs[base_subject] = set()
            
            if lesson.teacher:
                subject_teacher_pairs[base_subject].add(lesson.teacher)
        
        # Convert sets to lists
        subjects = {subject: list(teachers) for subject, teachers in subject_teacher_pairs.items()}
        
        return subjects


# Example usage
if __name__ == "__main__":
    scraper = BeginHSScraper()
    
    # Get class list
    print("Available classes:")
    classes = scraper.get_class_list()
    for name, id in classes.items():
        print(f"  {name}: {id}")
    
    # Get schedule for יב' 4 (class_id = 3895)
    if '3895' in classes.values():
        print("\nSchedule for יב' 4:")
        schedule = scraper.get_schedule('3895')
        for lesson in schedule[:5]:  # Show first 5
            print(f"  {lesson.day} - Lesson {lesson.lesson_number}: {lesson.subject} ({lesson.teacher})")
        
        print("\nChanges for יב' 4:")
        changes = scraper.get_changes('3895')
        for change in changes:
            print(f"  {change.date} - Lesson {change.lesson_number}: {change.teacher} - {change.change_type}")
        
        print("\nUnique subjects and teachers:")
        subjects = scraper.get_unique_subjects('3895')
        for subject, teachers in subjects.items():
            print(f"  {subject}: {', '.join(teachers)}")
