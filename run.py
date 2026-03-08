from app import create_app
from mongoengine import get_connection
import sys
import threading
import time
from app.models.issue import Issue
from app.utils.websocket_handler import socketio
from datetime import datetime, timedelta, UTC

app, socketio = create_app()

# Create a test Issue at startup if none exists
def create_test_issue():
    if Issue.objects.count() == 0:
        test_issue = Issue(
            event_type='bezdomne_zwierze',
            species='pies',
            incident_address='ul. Testowa 1',
            animal_count=1,
            options=[],
            urgency=False,
            media=[],
            contact_phone='123456789',
            description='Testowe zgłoszenie',
            status='open',
            reminder_time=datetime.now(UTC) + timedelta(seconds=30)  # 30s na test
        )
        test_issue.save()
        print('Created test Issue:', test_issue.to_dict())

create_test_issue()

def reminder_notifier():
    while True:
        try:
            now = datetime.now(UTC)
            issues = Issue.objects(reminder_time__lte=now)
            for issue in issues:
                print(f"[Reminder] Issue {issue.id} deadline reached! Broadcasting to all clients...")
                socketio.emit('reminder', {
                    'issue_id': str(issue.id),
                    'message': f'Reminder for issue {issue.event_type} ({issue.species})',
                    'reminder_time': issue.reminder_time.isoformat()
                }, broadcast=True, skip_sid=None)
                print(f"[Reminder] Broadcasted event for issue {issue.id}")
                # Optionally, update reminder_time or mark as notified
                # issue.reminder_time = None
                # issue.save()
        except Exception as e:
            print(f"[Reminder Error] {str(e)}")
        time.sleep(10)  # Check every 10 seconds for faster testing

# Start reminder thread
threading.Thread(target=reminder_notifier, daemon=True).start()

if __name__ == "__main__":
    # Test MongoDB connection (already connected in init_db)
    try:
        print("\n" + "=" * 60)
        print("Testing MongoDB connection...")
        print("=" * 60)
        print(f"URI: {app.config['MONGODB_URI']}")
        print(f"Database: {app.config['MONGODB_DB']}")
        
        # Get existing connection to test it
        db = get_connection()
        collections = db[app.config['MONGODB_DB']].list_collection_names()
        
        print(f"\n✅ Connected successfully!")
        print(f"Collections in database: {len(collections)}")
        if collections:
            print(f"Existing: {', '.join(collections)}")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ MongoDB connection failed: {e}")
        print("\nMake sure MongoDB is running on port 27017")
        print("=" * 60 + "\n")
        sys.exit(1)
    
    # Start Flask server with Socket.IO support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
