from mongoengine import Document, StringField, DateTimeField, ReferenceField
from datetime import datetime


class TemplateOption(Document):
    """
    Pre-filled template values for specific case scenarios.
    These values can be selected and inserted into EmailTemplate placeholders.
    
    Example:
    - animal_type: "pies"
    - case_type: "bezdomny"  
    - description: "Pies bez domu znaleziony na ulicy"
    
    This can then be used to fill template: 
    "Zgłaszam {animal_type} ({case_type}): {description}"
    """
    meta = {
        'collection': 'template_options',
        'indexes': ['animal_type', 'case_type', 'case_type_ref']
    }
    
    # Reference to EmailCaseType for organization
    case_type_ref = ReferenceField('EmailCaseType', null=True)
    
    animal_type = StringField(required=True, max_length=50)  # e.g., "pies", "kot"
    case_type = StringField(required=True, max_length=100)   # e.g., "bezdomny", "potrącony"
    case_label = StringField(required=True, max_length=200)  # e.g., "Pies bez domu"
    description = StringField(max_length=1000)               # detailed description
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'case_type_ref_id': str(self.case_type_ref.id) if self.case_type_ref else None,
            'animal_type': self.animal_type,
            'case_type': self.case_type,
            'case_label': self.case_label,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TemplateOption {self.animal_type} - {self.case_type}>'
