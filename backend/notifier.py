"""
Firebase Cloud Messaging integration for sending push notifications.
"""

import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Dict, Optional
import os


class NotificationService:
    """Service for sending push notifications via Firebase Cloud Messaging."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Firebase Admin SDK.
        
        Args:
            credentials_path: Path to Firebase service account JSON file.
                            If None, will look for GOOGLE_APPLICATION_CREDENTIALS env var.
        """
        if not firebase_admin._apps:
            if credentials_path and os.path.exists(credentials_path):
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
            else:
                # Try to use default credentials from environment
                firebase_admin.initialize_app()
    
    def send_notification(self, device_token: str, title: str, body: str, 
                         data: Optional[Dict] = None) -> bool:
        """
        Send a push notification to a single device.
        
        Args:
            device_token: FCM device token
            title: Notification title
            body: Notification body
            data: Optional data payload
        
        Returns:
            True if successful, False otherwise
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=device_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='schedule_changes',
                    ),
                ),
                webpush=messaging.WebpushConfig(
                    notification=messaging.WebpushNotification(
                        icon='/icon-192.png',
                        badge='/badge-72.png',
                    ),
                ),
            )
            
            response = messaging.send(message)
            print(f"Successfully sent notification: {response}")
            return True
            
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
    
    def send_multicast(self, device_tokens: List[str], title: str, body: str,
                      data: Optional[Dict] = None) -> Dict[str, int]:
        """
        Send a push notification to multiple devices.
        
        Args:
            device_tokens: List of FCM device tokens
            title: Notification title
            body: Notification body
            data: Optional data payload
        
        Returns:
            Dict with 'success' and 'failure' counts
        """
        if not device_tokens:
            return {'success': 0, 'failure': 0}
        
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=device_tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='schedule_changes',
                    ),
                ),
                webpush=messaging.WebpushConfig(
                    notification=messaging.WebpushNotification(
                        icon='/icon-192.png',
                        badge='/badge-72.png',
                    ),
                ),
            )
            
            response = messaging.send_multicast(message)
            print(f"Successfully sent {response.success_count} notifications")
            print(f"Failed to send {response.failure_count} notifications")
            
            return {
                'success': response.success_count,
                'failure': response.failure_count
            }
            
        except Exception as e:
            print(f"Error sending multicast notification: {e}")
            return {'success': 0, 'failure': len(device_tokens)}
    
    def format_cancellation_notification(self, change: Dict, language: str = 'he') -> tuple:
        """
        Format a cancellation notification.
        
        Returns:
            Tuple of (title, body)
        """
        if language == 'he':
            title = "ביטול שיעור"
            body = f"שיעור {change['lesson_number']} - {change['teacher']} בוטל ב-{change['date']}"
        else:  # English
            title = "Class Cancelled"
            body = f"Lesson {change['lesson_number']} - {change['teacher']} cancelled on {change['date']}"
        
        return title, body
    
    def format_room_change_notification(self, change: Dict, language: str = 'he') -> tuple:
        """
        Format a room change notification.
        
        Returns:
            Tuple of (title, body)
        """
        new_room = change.get('new_room', 'לא ידוע' if language == 'he' else 'Unknown')
        
        if language == 'he':
            title = "שינוי חדר"
            body = f"שיעור {change['lesson_number']} - {change['teacher']} עבר לחדר {new_room} ב-{change['date']}"
        else:  # English
            title = "Room Change"
            body = f"Lesson {change['lesson_number']} - {change['teacher']} moved to room {new_room} on {change['date']}"
        
        return title, body
    
    def send_change_notification(self, device_token: str, change: Dict, 
                                language: str = 'he') -> bool:
        """
        Send a notification for a schedule change.
        
        Args:
            device_token: FCM device token
            change: Change dict with date, lesson_number, teacher, change_type, etc.
            language: 'he' or 'en'
        
        Returns:
            True if successful, False otherwise
        """
        if change['change_type'] == 'cancellation':
            title, body = self.format_cancellation_notification(change, language)
        elif change['change_type'] == 'room_change':
            title, body = self.format_room_change_notification(change, language)
        else:
            # Generic change notification
            if language == 'he':
                title = "שינוי במערכת"
                body = f"שיעור {change['lesson_number']} - {change['teacher']}: {change['description']}"
            else:
                title = "Schedule Change"
                body = f"Lesson {change['lesson_number']} - {change['teacher']}: {change['description']}"
        
        data = {
            'change_type': change['change_type'],
            'lesson_number': str(change['lesson_number']),
            'teacher': change['teacher'],
            'date': change['date'],
        }
        
        return self.send_notification(device_token, title, body, data)


# Example usage
if __name__ == "__main__":
    # Note: This requires Firebase credentials to be set up
    # export GOOGLE_APPLICATION_CREDENTIALS="path/to/serviceAccountKey.json"
    
    notifier = NotificationService()
    
    # Example change
    change = {
        'date': '15.01.2026',
        'lesson_number': 1,
        'teacher': 'כהן דוד',
        'change_type': 'cancellation',
        'description': 'ביטול שעור'
    }
    
    # Send notification (requires valid device token)
    # success = notifier.send_change_notification("device_token_here", change, language='he')
    # print(f"Notification sent: {success}")
