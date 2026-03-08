"""Email Message model for ticket communication history"""
from mongoengine import (
    Document, StringField, EmailField, DateTimeField, 
    ReferenceField, BooleanField, DictField
)
from datetime import datetime
from app.models.user import User


class EmailMessage(Document):
    """Email message associated with a ticket"""
    meta = {
        'collection': 'email_messages',
        'indexes': [
            'ticket_id',
            'created_at',
            'direction',
            ('ticket_id', '-created_at'),
        ]
    }
    
    # Ticket reference (as string ID)
    ticket_id = StringField(required=True, max_length=100)
    
    # Direction: 'inbound' (received) or 'outbound' (sent)
    direction = StringField(
        required=True,
        choices=['inbound', 'outbound'],
        default='outbound'
    )
    
    # Email addresses
    from_email = EmailField(required=True)
    to_email = EmailField(required=True)
    cc_emails = StringField()  # Comma-separated
    
    # Content
    subject = StringField(required=True, max_length=500)
    body = StringField(required=True)
    html_body = StringField()  # Optional HTML version
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    sent_by = ReferenceField(User, null=True)  # Staff member who sent (for outbound)
    
    # IMAP/SMTP metadata
    external_id = StringField()  # IMAP message ID for inbound
    read_at = DateTimeField(null=True)  # When processed
    is_automated = BooleanField(default=False)  # Auto-reply or notification
    
    # Additional data
    metadata = DictField()  # For storing extra info
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'ticket_id': self.ticket_id,
            'direction': self.direction,
            'from_email': self.from_email,
            'to_email': self.to_email,
            'cc_emails': self.cc_emails,
            'subject': self.subject,
            'body': self.body,
            'html_body': self.html_body,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_by_id': str(self.sent_by.id) if self.sent_by else None,
            'external_id': self.external_id,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'is_automated': self.is_automated,
            'metadata': self.metadata or {}
        }
    
    def __repr__(self):
        return f'<EmailMessage {self.direction} "{self.subject[:30]}">'
