from mongoengine import Document, StringField, DateTimeField
from datetime import datetime


class Role(Document):
    meta = {
        'collection': 'roles',
        'indexes': ['name']
    }
    
    name = StringField(required=True, unique=True, max_length=50)
    description = StringField(max_length=500)
    #permissions = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'
