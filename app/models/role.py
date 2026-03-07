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
            'permissions': self.permissions
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'
