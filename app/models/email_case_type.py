from mongoengine import BooleanField, DateTimeField, Document, StringField
from datetime import datetime


class EmailCaseType(Document):
    meta = {
        'collection': 'email_case_types',
        'indexes': ['code', 'label']
    }

    code = StringField(required=True, unique=True, max_length=80)
    label = StringField(required=True, max_length=200)
    description = StringField(max_length=500)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'code': self.code,
            'label': self.label,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<EmailCaseType {self.code}>'
