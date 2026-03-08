from mongoengine import BooleanField, DateTimeField, Document, ReferenceField, StringField
from datetime import datetime


class EmailTemplate(Document):
    """
    Email template for a specific case type.
    Contains placeholders like {animal_type}, {case_description}, etc.
    that can be filled with values selected from TemplateOptions.
    
    Example body:
    "Szacowny Panie Burmistrzu,
     Zgłaszam przypadek {animal_type} ({case_description}) 
     w lokalizacji {location}."
    """
    meta = {
        'collection': 'email_templates',
        'indexes': ['name', 'case_type', 'is_active']
    }
    
    name = StringField(required=True, max_length=100)
    case_type = ReferenceField('EmailCaseType', required=True)
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=500)
    body = StringField(required=True)
    # List of placeholder names used in body, e.g. ['animal_type', 'case_description', 'location']
    placeholders = StringField(default="")  # comma-separated list of placeholder names
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'case_type_id': str(self.case_type.id) if self.case_type else None,
            'title': self.title,
            'description': self.description,
            'body': self.body,
            'placeholders': self.placeholders.split(',') if self.placeholders else [],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'
