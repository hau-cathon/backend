from datetime import datetime
from mongoengine import BooleanField, DateTimeField, DictField, Document, ReferenceField, StringField


class EmailMessage(Document):
    """Stored email communication for a ticket."""

    meta = {
        'collection': 'email_messages',
        'indexes': ['ticket_id', 'created_at', 'direction', 'external_id'],
    }

    ticket_id = StringField(required=True, max_length=120)
    issue = ReferenceField('Issue', null=True)

    direction = StringField(required=True, choices=['inbound', 'outbound'])
    from_email = StringField(required=True, max_length=300)
    to_email = StringField(required=True, max_length=300)
    cc_emails = StringField(max_length=500)
    subject = StringField(required=True, max_length=500)
    body = StringField(required=True)
    html_body = StringField()

    sent_by_id = StringField(max_length=80)
    external_id = StringField(max_length=200)
    read_at = DateTimeField(null=True)
    is_automated = BooleanField(default=False)
    metadata = DictField(default=dict)

    created_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'ticket_id': self.ticket_id,
            'issue_id': str(self.issue.id) if self.issue else None,
            'direction': self.direction,
            'from_email': self.from_email,
            'to_email': self.to_email,
            'cc_emails': self.cc_emails,
            'subject': self.subject,
            'body': self.body,
            'html_body': self.html_body,
            'sent_by_id': self.sent_by_id,
            'external_id': self.external_id,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'is_automated': self.is_automated,
            'metadata': self.metadata or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
