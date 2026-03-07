"""Issue/Report model"""
from mongoengine import Document, StringField, EmailField, DateTimeField, ReferenceField, ListField
from datetime import datetime
from app.models.user import User


class Issue(Document):
    """Issue/Report document"""
    meta = {
        'collection': 'issues',
        'indexes': ['status', 'created_at', 'user']
    }
    
    title = StringField(required=True, max_length=200)
    description = StringField(required=True)
    status = StringField(
        required=True, 
        choices=['open', 'in_progress', 'resolved', 'closed'],
        default='open'
    )
    priority = StringField(
        choices=['low', 'medium', 'high', 'critical'],
        default='medium'
    )
    user = ReferenceField(User, required=True)
    assigned_to = ReferenceField(User, null=True)
    tags = ListField(StringField(max_length=50))
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    resolved_at = DateTimeField(null=True)
    
    def to_dict(self):
        """Convert issue to dictionary"""
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': str(self.user.id) if self.user else None,
            'assigned_to_id': str(self.assigned_to.id) if self.assigned_to else None,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
    
    def __repr__(self):
        return f'<Issue {self.title}>'
