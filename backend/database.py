"""
Database models and operations for the schedule notifier.
Uses SQLite for simplicity and portability.
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
from contextlib import contextmanager


class Database:
    """Database manager for the schedule notifier."""
    
    def __init__(self, db_path: str = "schedule_notifier.db"):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_token TEXT UNIQUE NOT NULL,
                    class_id TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    language TEXT DEFAULT 'he',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Teacher preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teacher_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    teacher_name TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, subject)
                )
            ''')
            
            # Schedule cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schedule_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id TEXT NOT NULL,
                    day TEXT NOT NULL,
                    lesson_number INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    teacher TEXT NOT NULL,
                    room TEXT DEFAULT '',
                    group_info TEXT DEFAULT '',
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(class_id, day, lesson_number, subject, teacher)
                )
            ''')
            
            # Changes history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS changes_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    lesson_number INTEGER NOT NULL,
                    teacher TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    new_room TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notified BOOLEAN DEFAULT 0,
                    UNIQUE(class_id, date, lesson_number, teacher, change_type)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_class ON users(class_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_changes_class ON changes_history(class_id, notified)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedule_class ON schedule_cache(class_id)')
    
    # User operations
    def register_user(self, device_token: str, class_id: str, class_name: str, 
                     language: str = 'he') -> int:
        """Register a new user or update existing one."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (device_token, class_id, class_name, language)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(device_token) DO UPDATE SET
                    class_id = excluded.class_id,
                    class_name = excluded.class_name,
                    language = excluded.language,
                    updated_at = CURRENT_TIMESTAMP
            ''', (device_token, class_id, class_name, language))
            
            # Get user ID
            cursor.execute('SELECT id FROM users WHERE device_token = ?', (device_token,))
            return cursor.fetchone()[0]
    
    def get_user_by_token(self, device_token: str) -> Optional[Dict]:
        """Get user by device token."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE device_token = ?', (device_token,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_users_by_class(self, class_id: str) -> List[Dict]:
        """Get all users in a specific class."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE class_id = ?', (class_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_classes(self) -> List[str]:
        """Get list of all classes that have registered users."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT class_id FROM users')
            return [row[0] for row in cursor.fetchall()]
    
    # Teacher preferences operations
    def set_teacher_preferences(self, user_id: int, preferences: Dict[str, str]):
        """
        Set teacher preferences for a user.
        preferences: Dict mapping subject to teacher name
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear existing preferences
            cursor.execute('DELETE FROM teacher_preferences WHERE user_id = ?', (user_id,))
            
            # Insert new preferences
            for subject, teacher in preferences.items():
                if teacher:  # Skip subjects with no teacher selected
                    cursor.execute('''
                        INSERT INTO teacher_preferences (user_id, subject, teacher_name)
                        VALUES (?, ?, ?)
                    ''', (user_id, subject, teacher))
    
    def get_teacher_preferences(self, user_id: int) -> Dict[str, str]:
        """Get teacher preferences for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT subject, teacher_name 
                FROM teacher_preferences 
                WHERE user_id = ?
            ''', (user_id,))
            return {row['subject']: row['teacher_name'] for row in cursor.fetchall()}
    
    def get_users_for_teacher(self, class_id: str, teacher_name: str) -> List[Dict]:
        """Get all users who have selected a specific teacher."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT u.* 
                FROM users u
                JOIN teacher_preferences tp ON u.id = tp.user_id
                WHERE u.class_id = ? AND tp.teacher_name = ?
            ''', (class_id, teacher_name))
            return [dict(row) for row in cursor.fetchall()]
    
    # Schedule cache operations
    def cache_schedule(self, class_id: str, lessons: List[Dict]):
        """Cache the schedule for a class."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear old cache for this class
            cursor.execute('DELETE FROM schedule_cache WHERE class_id = ?', (class_id,))
            
            # Insert new schedule
            for lesson in lessons:
                cursor.execute('''
                    INSERT INTO schedule_cache 
                    (class_id, day, lesson_number, subject, teacher, room, group_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    class_id,
                    lesson.get('day', ''),
                    lesson.get('lesson_number', 0),
                    lesson.get('subject', ''),
                    lesson.get('teacher', ''),
                    lesson.get('room', ''),
                    lesson.get('group', '')
                ))
    
    def get_cached_schedule(self, class_id: str) -> List[Dict]:
        """Get cached schedule for a class."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM schedule_cache 
                WHERE class_id = ?
                ORDER BY lesson_number, day
            ''', (class_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Changes history operations
    def add_change(self, class_id: str, change: Dict) -> bool:
        """
        Add a schedule change to history.
        Returns True if this is a new change, False if it already exists.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO changes_history 
                    (class_id, date, lesson_number, teacher, change_type, description, new_room)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    class_id,
                    change.get('date', ''),
                    change.get('lesson_number', 0),
                    change.get('teacher', ''),
                    change.get('change_type', ''),
                    change.get('description', ''),
                    change.get('new_room')
                ))
                return True
            except sqlite3.IntegrityError:
                # Change already exists
                return False
    
    def get_unnotified_changes(self, class_id: str) -> List[Dict]:
        """Get changes that haven't been notified yet."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM changes_history 
                WHERE class_id = ? AND notified = 0
                ORDER BY detected_at DESC
            ''', (class_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_change_notified(self, change_id: int):
        """Mark a change as notified."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE changes_history 
                SET notified = 1 
                WHERE id = ?
            ''', (change_id,))
    
    def get_recent_changes(self, class_id: str, limit: int = 50) -> List[Dict]:
        """Get recent changes for a class."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM changes_history 
                WHERE class_id = ?
                ORDER BY detected_at DESC
                LIMIT ?
            ''', (class_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_changes(self, days: int = 7):
        """Remove changes older than specified days."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM changes_history 
                WHERE detected_at < datetime('now', '-' || ? || ' days')
            ''', (days,))


# Example usage
if __name__ == "__main__":
    db = Database("test.db")
    
    # Register a user
    user_id = db.register_user(
        device_token="test_token_123",
        class_id="3895",
        class_name="יב' 4",
        language="he"
    )
    print(f"Registered user ID: {user_id}")
    
    # Set teacher preferences
    preferences = {
        "מתמטיקה": "כהן דוד",
        "אנגלית": "לוי שרה",
        "ספרות": "מזרחי יוסף"
    }
    db.set_teacher_preferences(user_id, preferences)
    print(f"Set preferences: {preferences}")
    
    # Get preferences
    prefs = db.get_teacher_preferences(user_id)
    print(f"Retrieved preferences: {prefs}")
    
    # Add a change
    change = {
        'date': '15.01.2026',
        'lesson_number': 1,
        'teacher': 'כהן דוד',
        'change_type': 'cancellation',
        'description': 'ביטול שעור'
    }
    is_new = db.add_change("3895", change)
    print(f"Added change (new: {is_new})")
    
    # Get unnotified changes
    changes = db.get_unnotified_changes("3895")
    print(f"Unnotified changes: {len(changes)}")
