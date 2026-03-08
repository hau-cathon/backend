from mongoengine import Document, StringField, EmailField, DateTimeField
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(Document):
    meta = {
        'collection': 'users',
        'indexes': ['email', 'username']
    }
    
    email = EmailField(required=True, unique=True)
    username = StringField(required=True, unique=True, max_length=80)
    password_hash = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
