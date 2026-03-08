from mongoengine import BooleanField, DateTimeField, Document, IntField, ListField, ReferenceField, StringField
from datetime import datetime, timedelta
from datetime import timedelta
from app.models.user import User


class Issue(Document):
    meta = {
        'collection': 'issues',
        'indexes': ['event_type', 'species', 'urgency', 'status', 'created_at', 'user']
    }

    event_type = StringField(
        required=True,
        choices=['bezdomne_zwierze', 'zdarzenie_drogowe', 'znecanie_sie', 'inne']
    )
    species = StringField(required=True, max_length=100)
    animal_count = IntField(required=True, min_value=1, default=1)
    options = ListField(StringField(max_length=100))
    urgency = BooleanField(
        default=False
    )
    media = ListField(StringField(max_length=500))
    incident_address = StringField(required=True, max_length=300)
    contact_phone = StringField(max_length=20)

    description = StringField(max_length=2000)

    status = StringField(
        required=True,
        choices=['open', 'in_progress', 'resolved', 'closed', 'duplicate'],
        default='open'
    )
    user = ReferenceField(User, null=True)
    assigned_to = ReferenceField(User, null=True)
    duplicate_of = ReferenceField('self', null=True)  # Referencja do oryginalnego zgłoszenia jeśli jest duplikatem
    duplicates = ListField(ReferenceField('self'))  # Lista zduplikowanych zgłoszeń
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    resolved_at = DateTimeField(null=True)
    reminder_time = DateTimeField(default=lambda: datetime.utcnow() + timedelta(seconds=30))

    def to_dict(self):
        return {
            'id': str(self.id),
            'event_type': self.event_type,
            'species': self.species,
            'animal_count': self.animal_count,
            'options': self.options,
            'urgency': self.urgency,
            'media': self.media,
            'incident_address': self.incident_address,
            'contact_phone': self.contact_phone,
            'description': self.description,
            'reporter_email': self.reporter_email,
            'ticket_number': self.ticket_number,
            'status': self.status,
            'user_id': str(self.user.id) if self.user else None,
            'assigned_to_id': str(self.assigned_to.id) if self.assigned_to else None,
            'duplicate_of_id': str(self.duplicate_of.id) if self.duplicate_of else None,
            'duplicates_ids': [str(dup.id) for dup in self.duplicates] if self.duplicates else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'reminder_time': self.reminder_time.isoformat() if self.reminder_time else None
        }

    def __repr__(self):
        return f'<Issue {self.event_type} - {self.species}>'
