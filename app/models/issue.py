from mongoengine import BooleanField, DateTimeField, Document, IntField, ListField, ReferenceField, StringField
from datetime import datetime, timedelta, UTC
from app.models.user import User


class Issue(Document):
    meta = {
        'collection': 'issues',
        'indexes': ['event_type', 'species', 'urgency', 'status', 'created_at', 'user', 'title']
    }

    event_type = StringField(
        required=True,
        choices=['bezdomne_zwierze', 'zdarzenie_drogowe', 'znecanie_sie', 'inne']
    )
    title = StringField(max_length=250)
    species = StringField(required=True, max_length=100)
    animal_count = IntField(required=True, min_value=1, default=1)
    options = ListField(StringField(max_length=100))
    urgency = BooleanField(
        default=False
    )
    media = ListField(StringField(max_length=500))
    incident_address = StringField(required=True, max_length=300)
    contact_phone = StringField(max_length=20)
    reporter_email = StringField(max_length=200)
    ticket_number = StringField(max_length=50)

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
    created_at = DateTimeField(default=lambda: datetime.now(UTC))
    updated_at = DateTimeField(default=lambda: datetime.now(UTC))
    resolved_at = DateTimeField(null=True)
    reminder_time = DateTimeField(default=lambda: datetime.now(UTC) + timedelta(seconds=30))

    def build_title(self):
        timestamp = self.created_at or datetime.now(UTC)
        created_part = timestamp.strftime('%Y%m%d-%H%M%S')
        issue_id = str(self.id) if self.id else 'noid'
        short_id = issue_id[-6:]
        species_part = (self.species or 'unknown').strip().replace(' ', '_')
        return f"{short_id}-{species_part}-{created_part}"

    def to_dict(self):
        computed_title = self.title or self.build_title()
        return {
            'id': str(self.id),
            'title': computed_title,
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
