"""Template Option model"""
from mongoengine import Document, StringField, DateTimeField, ListField
from datetime import datetime


class TemplateOption(Document):
    """Email template with list of questions for a specific animal case"""
    meta = {
        'collection': 'template_options',
        'indexes': ['animal_type', 'case_name']
    }
    
    animal_type = StringField(required=True, max_length=50)  # e.g., "dog", "cat"
    case_name = StringField(required=True, max_length=100)  # e.g., "aggressive", "injured"
    case_label = StringField(required=True, max_length=200)  # e.g., "Pies agresywny" - for UI display
    questions = ListField(StringField(required=True), required=True)  # List of questions to include in email
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        """Convert template to dictionary"""
        return {
            'id': str(self.id),
            'animal_type': self.animal_type,
            'case_name': self.case_name,
            'case_label': self.case_label,
            'questions': self.questions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TemplateOption {self.animal_type} - {self.case_name}>'
