"""
Background scheduler for checking schedule changes periodically.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
from typing import Dict, List

from scraper import BeginHSScraper
from database import Database
from notifier import NotificationService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScheduleMonitor:
    """Monitors schedule changes and sends notifications."""
    
    def __init__(self, db: Database, notifier: NotificationService):
        self.db = db
        self.notifier = notifier
        self.scraper = BeginHSScraper()
        self.scheduler = BackgroundScheduler()
    
    def check_changes_for_class(self, class_id: str):
        """Check for changes in a specific class and notify affected users."""
        try:
            logger.info(f"Checking changes for class {class_id}")
            
            # Scrape current changes
            changes = self.scraper.get_changes(class_id)
            
            if not changes:
                logger.info(f"No changes found for class {class_id}")
                return
            
            # Process each change
            for change in changes:
                # Convert dataclass to dict
                change_dict = {
                    'date': change.date,
                    'lesson_number': change.lesson_number,
                    'teacher': change.teacher,
                    'change_type': change.change_type,
                    'description': change.description,
                    'new_room': change.new_room
                }
                
                # Add to database (returns True if new)
                is_new_change = self.db.add_change(class_id, change_dict)
                
                if is_new_change:
                    logger.info(f"New change detected: {change.teacher} - {change.change_type}")
                    
                    # Get users who have this teacher
                    affected_users = self.db.get_users_for_teacher(class_id, change.teacher)
                    
                    # Send notifications
                    for user in affected_users:
                        success = self.notifier.send_change_notification(
                            device_token=user['device_token'],
                            change=change_dict,
                            language=user.get('language', 'he')
                        )
                        
                        if success:
                            logger.info(f"Notification sent to user {user['id']}")
                        else:
                            logger.error(f"Failed to send notification to user {user['id']}")
                    
                    # Mark as notified
                    # Get the change ID
                    recent_changes = self.db.get_recent_changes(class_id, limit=1)
                    if recent_changes:
                        self.db.mark_change_notified(recent_changes[0]['id'])
        
        except Exception as e:
            logger.error(f"Error checking changes for class {class_id}: {e}", exc_info=True)
    
    def check_all_classes(self):
        """Check changes for all registered classes."""
        logger.info("Starting scheduled check for all classes")
        
        try:
            # Get all classes that have registered users
            classes = self.db.get_all_classes()
            
            logger.info(f"Checking {len(classes)} classes")
            
            for class_id in classes:
                self.check_changes_for_class(class_id)
        
        except Exception as e:
            logger.error(f"Error in scheduled check: {e}", exc_info=True)
    
    def start(self, interval_minutes: int = 20):
        """
        Start the background scheduler.
        
        Args:
            interval_minutes: How often to check for changes (default: 20 minutes)
        """
        # Add job to check every interval_minutes
        self.scheduler.add_job(
            func=self.check_all_classes,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='check_schedule_changes',
            name='Check schedule changes',
            replace_existing=True
        )
        
        # Run once immediately on startup
        self.scheduler.add_job(
            func=self.check_all_classes,
            trigger='date',
            id='initial_check',
            name='Initial check on startup'
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started - checking every {interval_minutes} minutes")
    
    def stop(self):
        """Stop the background scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")


# Example usage
if __name__ == "__main__":
    import time
    
    db = Database("test.db")
    notifier = NotificationService()
    
    monitor = ScheduleMonitor(db, notifier)
    
    # Start monitoring (check every 1 minute for testing)
    monitor.start(interval_minutes=1)
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        print("Stopped monitoring")
