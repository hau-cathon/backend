from app import create_app
from mongoengine import get_connection
import sys

app, socketio = create_app()

if __name__ == "__main__":
<<<<<<< HEAD
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
    
    # Start Flask server
    app.run(debug=True)
=======
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
>>>>>>> b2ad6a1a9392e297ff157f7a9889db05b8fb065d
