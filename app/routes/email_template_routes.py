"""Email Template routes - CRUD and email generation"""
from flask import Blueprint, jsonify, request
from app.models.email_template import EmailTemplate
from app.models.email_case_type import EmailCaseType
from app.models.template_option import TemplateOption
from datetime import datetime
from mongoengine.errors import ValidationError, DoesNotExist

email_template_bp = Blueprint('email_templates', __name__)


@email_template_bp.route('/', methods=['GET'])
def get_email_templates():
    """Get all email templates with optional filtering"""
    try:
        case_type_id = request.args.get('case_type_id')
        is_active = request.args.get('is_active')
        
        query = {}
        if case_type_id:
            query['case_type'] = case_type_id
        if is_active is not None:
            query['is_active'] = is_active.lower() == 'true'
        
        templates = EmailTemplate.objects(**query).order_by('name')
        
        return jsonify({
            'status': 'success',
            'count': len(templates),
            'templates': [template.to_dict() for template in templates]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_template_bp.route('/<template_id>', methods=['GET'])
def get_email_template(template_id):
    """Get single email template by ID"""
    try:
        template = EmailTemplate.objects.get(id=template_id)
        return jsonify({
            'status': 'success',
            'template': template.to_dict()
        }), 200
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Email template not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_template_bp.route('/', methods=['POST'])
def create_email_template():
    """Create new email template"""
    try:
        data = request.get_json()
        
        # Required fields validation
        required_fields = ['name', 'case_type_id', 'title', 'body']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate case type exists
        try:
            case_type = EmailCaseType.objects.get(id=data['case_type_id'])
        except DoesNotExist:
            return jsonify({
                'status': 'error',
                'error': 'Email case type not found'
            }), 404
        
        template = EmailTemplate(
            name=data['name'],
            case_type=case_type,
            title=data['title'],
            body=data['body'],
            description=data.get('description', ''),
            placeholders=data.get('placeholders', ''),
            is_active=data.get('is_active', True)
        )
        
        template.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Email template created successfully',
            'template': template.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'error': f'Validation error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_template_bp.route('/<template_id>', methods=['PUT'])
def update_email_template(template_id):
    """Update email template"""
    try:
        template = EmailTemplate.objects.get(id=template_id)
        data = request.get_json()
        
        if 'name' in data:
            template.name = data['name']
        if 'title' in data:
            template.title = data['title']
        if 'body' in data:
            template.body = data['body']
        if 'description' in data:
            template.description = data['description']
        if 'placeholders' in data:
            template.placeholders = data['placeholders']
        if 'is_active' in data:
            template.is_active = data['is_active']
        if 'case_type_id' in data:
            try:
                case_type = EmailCaseType.objects.get(id=data['case_type_id'])
                template.case_type = case_type
            except DoesNotExist:
                return jsonify({
                    'status': 'error',
                    'error': 'Email case type not found'
                }), 404
        
        template.updated_at = datetime.utcnow()
        template.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Email template updated successfully',
            'template': template.to_dict()
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Email template not found'
        }), 404
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'error': f'Validation error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_template_bp.route('/<template_id>', methods=['DELETE'])
def delete_email_template(template_id):
    """Delete email template"""
    try:
        template = EmailTemplate.objects.get(id=template_id)
        template.delete()
        
        return jsonify({
            'status': 'success',
            'message': 'Email template deleted successfully'
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Email template not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_template_bp.route('/<template_id>/generate', methods=['POST'])
def generate_email(template_id):
    """
    Generate ready-to-copy email by filling template placeholders.
    
    Request body:
    {
        "option_id": "id_of_template_option",
        "replacements": {
            "{custom_placeholder}": "custom_value"
        }
    }
    """
    try:
        template = EmailTemplate.objects.get(id=template_id)
        data = request.get_json()
        
        option_id = data.get('option_id')
        if not option_id:
            return jsonify({
                'status': 'error',
                'error': 'option_id is required'
            }), 400
        
        try:
            option = TemplateOption.objects.get(id=option_id)
        except DoesNotExist:
            return jsonify({
                'status': 'error',
                'error': 'Template option not found'
            }), 404
        
        body = template.body
        replacements = data.get('replacements', {})
        
        # Auto-fill from template option
        replacements.setdefault('{animal_type}', option.animal_type)
        replacements.setdefault('{case_type}', option.case_type)
        replacements.setdefault('{case_label}', option.case_label)
        if option.description:
            replacements.setdefault('{description}', option.description)
        
        # Apply all replacements
        for key, value in replacements.items():
            body = body.replace(key, str(value))
        
        return jsonify({
            'status': 'success',
            'template_id': template_id,
            'template_name': template.name,
            'option_id': option_id,
            'final_email': {
                'title': template.title,
                'body': body
            }
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Email template not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
