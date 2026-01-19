"""
Flask REST API for the schedule notifier.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from scraper import BeginHSScraper
from database import Database
from notifier import NotificationService
from scheduler import ScheduleMonitor


# Load environment variables
load_dotenv()

# Initialize database first
DB_PATH = os.getenv('DATABASE_PATH', 'schedule_notifier.db')
db = Database(DB_PATH)

# Clear schedule-related tables on startup (keep user tokens)
try:
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM changes_history')
        cursor.execute('DELETE FROM schedule_cache')
        print(f"🗑️  Cleared schedule data from database (kept user tokens)")
except Exception as e:
    print(f"Note: Could not clear schedule tables: {e}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for web app

# Initialize services (db already created above)
notifier = NotificationService(os.getenv('FIREBASE_CREDENTIALS_PATH'))
scraper = BeginHSScraper()
monitor = ScheduleMonitor(db, notifier)

# Start scheduler immediately (gunicorn will load this once per worker)
# We use 1 worker in production, so this is safe
interval_minutes = int(os.getenv('CHECK_INTERVAL_MINUTES', '20'))
monitor.start(interval_minutes=interval_minutes)
print(f"Scheduler started (interval: {interval_minutes}m)")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Schedule Notifier API is running'})


@app.route('/api/classes', methods=['GET'])
def get_classes():
    """Get list of all available classes."""
    try:
        classes = scraper.get_class_list()
        
        # Convert to list of objects for easier frontend handling
        class_list = [
            {'id': class_id, 'name': name}
            for name, class_id in classes.items()
        ]
        
        return jsonify({
            'success': True,
            'classes': class_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/schedule/<class_id>', methods=['GET'])
def get_schedule(class_id):
    """Get schedule for a specific class with unique subjects and teachers."""
    try:
        # Get unique subjects and teachers
        subjects = scraper.get_unique_subjects(class_id)
        
        # Convert to list format
        subject_list = [
            {
                'subject': subject,
                'teachers': teachers
            }
            for subject, teachers in subjects.items()
        ]
        
        return jsonify({
            'success': True,
            'subjects': subject_list
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/register', methods=['POST'])
def register_user():
    """Register a new user with their class and teacher preferences."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['device_token', 'class_id', 'class_name', 'preferences']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Register user
        user_id = db.register_user(
            device_token=data['device_token'],
            class_id=data['class_id'],
            class_name=data['class_name'],
            language=data.get('language', 'he')
        )
        
        # Set teacher preferences
        db.set_teacher_preferences(user_id, data['preferences'])
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'User registered successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/preferences', methods=['PUT'])
def update_preferences():
    """Update user's teacher preferences."""
    try:
        data = request.json
        
        # Validate required fields
        if 'device_token' not in data or 'preferences' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: device_token, preferences'
            }), 400
        
        # Get user
        user = db.get_user_by_token(data['device_token'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Update preferences
        db.set_teacher_preferences(user['id'], data['preferences'])
        
        # Update language if provided
        if 'language' in data:
            db.register_user(
                device_token=data['device_token'],
                class_id=user['class_id'],
                class_name=user['class_name'],
                language=data['language']
            )
        
        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/<device_token>', methods=['GET'])
def get_user(device_token):
    """Get user information and preferences."""
    try:
        user = db.get_user_by_token(device_token)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        preferences = db.get_teacher_preferences(user['id'])
        
        return jsonify({
            'success': True,
            'user': {
                'class_id': user['class_id'],
                'class_name': user['class_name'],
                'language': user['language'],
                'preferences': preferences
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/changes/<class_id>', methods=['GET'])
def get_changes(class_id):
    """Get current schedule changes for a class."""
    try:
        # Get from database (recent changes)
        changes = db.get_recent_changes(class_id, limit=50)
        
        return jsonify({
            'success': True,
            'changes': changes
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/changes/live/<class_id>', methods=['GET'])
def get_live_changes(class_id):
    """Get live schedule changes directly from the website."""
    try:
        changes = scraper.get_changes(class_id)
        
        # Convert dataclasses to dicts
        change_list = [
            {
                'date': change.date,
                'lesson_number': change.lesson_number,
                'teacher': change.teacher,
                'subject': change.subject,
                'change_type': change.change_type,
                'description': change.description,
                'new_room': change.new_room
            }
            for change in changes
        ]
        
        return jsonify({
            'success': True,
            'changes': change_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test-notification', methods=['POST'])
def test_notification():
    """Send a test notification (for debugging)."""
    try:
        data = request.json
        
        if 'device_token' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing device_token'
            }), 400
        
        success = notifier.send_notification(
            device_token=data['device_token'],
            title=data.get('title', 'Test Notification'),
            body=data.get('body', 'This is a test notification from Schedule Notifier'),
            data={'test': 'true'}
        )
        
        return jsonify({
            'success': success,
            'message': 'Test notification sent' if success else 'Failed to send notification'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def start_server(host='0.0.0.0', port=5000, debug=False):
    """Start the Flask server."""
    print(f"Starting Schedule Notifier API on {host}:{port}")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    # Convert string 'True'/'False' to boolean
    debug_str = os.getenv('DEBUG', 'True')
    debug = debug_str.lower() in ('true', '1', 't')
    
    start_server(host=host, port=port, debug=debug)
