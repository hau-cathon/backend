from datetime import datetime
from mongoengine import DateTimeField, DictField, Document, ReferenceField, StringField


class ActionHistoryEntry(Document):
    """Timeline event stored for a ticket/issue."""

    meta = {
        'collection': 'action_history',
        'indexes': ['ticket_id', 'created_at', 'action_type', 'timeline_type'],
    }

    ticket_id = StringField(required=True, max_length=120)
    issue = ReferenceField('Issue', null=True)
    action_type = StringField(required=True, max_length=80)
    timeline_type = StringField(
        required=True,
        choices=['info', 'warning', 'success', 'alert'],
        default='info',
    )
    label = StringField(required=True, max_length=200)
    detail = StringField(required=True, max_length=2000)
    source = StringField(default='system', max_length=80)
    actor_id = StringField(max_length=80)
    metadata = DictField(default=dict)
    created_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'ticket_id': self.ticket_id,
            'issue_id': str(self.issue.id) if self.issue else None,
            'action_type': self.action_type,
            'timeline_type': self.timeline_type,
            'label': self.label,
            'detail': self.detail,
            'source': self.source,
            'actor_id': self.actor_id,
            'metadata': self.metadata or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
