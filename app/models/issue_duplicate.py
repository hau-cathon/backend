"""Issue Duplicate model for tracking merged issues"""
from mongoengine import DateTimeField, Document, ListField, ReferenceField, StringField
from datetime import datetime
from app.models.user import User


class IssueDuplicate(Document):
    """Tracks relationship between original and duplicate issues"""
    meta = {
        'collection': 'issue_duplicates',
        'indexes': ['original_issue', 'duplicate_issue', 'status', 'created_at']
    }

    original_issue = ReferenceField('Issue', required=True)
    duplicate_issue = ReferenceField('Issue', required=True)
    status = StringField(
        required=True,
        choices=['pending', 'merged', 'rejected'],
        default='pending'
    )
    # Fields that were merged from duplicate to original
    merged_fields = ListField(
        StringField(choices=['description', 'contact_phone', 'media', 'options', 'animal_count']),
        default=[]
    )
    merged_by = ReferenceField(User, null=True)  # Operator who approved the merge
    rejection_reason = StringField(max_length=500, null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    merged_at = DateTimeField(null=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'original_issue_id': str(self.original_issue.id) if self.original_issue else None,
            'duplicate_issue_id': str(self.duplicate_issue.id) if self.duplicate_issue else None,
            'status': self.status,
            'merged_fields': self.merged_fields,
            'merged_by_id': str(self.merged_by.id) if self.merged_by else None,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'merged_at': self.merged_at.isoformat() if self.merged_at else None
        }

    def __repr__(self):
        return f'<IssueDuplicate {self.original_issue.id} <- {self.duplicate_issue.id} ({self.status})>'
