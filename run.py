from app import create_app
from mongoengine import get_connection
import sys

app, socketio = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
