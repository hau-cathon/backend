"""Email Case Type routes - basic CRUD operations"""
from flask import Blueprint, jsonify, request
from app.models.email_case_type import EmailCaseType
from datetime import datetime
from mongoengine.errors import ValidationError, DoesNotExist, NotUniqueError

email_case_type_bp = Blueprint('email_case_types', __name__)


@email_case_type_bp.route('/', methods=['GET'])
def get_email_case_types():
    """Get all email case types"""
    try:
        # Optional filter for active only
        is_active = request.args.get('is_active')
        
        if is_active is not None:
            case_types = EmailCaseType.objects(is_active=is_active.lower() == 'true').order_by('label')
        else:
            case_types = EmailCaseType.objects.all().order_by('label')
        
        return jsonify({
            'status': 'success',
            'count': len(case_types),
            'case_types': [ct.to_dict() for ct in case_types]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_case_type_bp.route('/<case_type_id>', methods=['GET'])
def get_email_case_type(case_type_id):
    """Get single email case type by ID"""
    try:
        case_type = EmailCaseType.objects.get(id=case_type_id)
        return jsonify({
            'status': 'success',
            'case_type': case_type.to_dict()
        }), 200
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Email case type not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_case_type_bp.route('/code/<code>', methods=['GET'])
def get_email_case_type_by_code(code):
    """Get email case type by code"""
    try:
        case_type = EmailCaseType.objects.get(code=code)
        return jsonify({
            'status': 'success',
            'case_type': case_type.to_dict()
        }), 200
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Email case type not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_case_type_bp.route('/', methods=['POST'])
def create_email_case_type():
    """Create new email case type"""
    try:
        data = request.get_json()
        
        # Required fields validation
        required_fields = ['code', 'label']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create case type
        case_type = EmailCaseType(
            code=data['code'],
            label=data['label'],
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        case_type.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Email case type created successfully',
            'case_type': case_type.to_dict()
        }), 201
        
    except NotUniqueError:
        return jsonify({
            'status': 'error',
            'error': 'Email case type with this code already exists'
        }), 409
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


@email_case_type_bp.route('/<case_type_id>', methods=['PUT'])
def update_email_case_type(case_type_id):
    """Update email case type"""
    try:
        case_type = EmailCaseType.objects.get(id=case_type_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'code' in data:
            case_type.code = data['code']
        if 'label' in data:
            case_type.label = data['label']
        if 'description' in data:
            case_type.description = data['description']
        if 'is_active' in data:
            case_type.is_active = data['is_active']
        
        case_type.updated_at = datetime.utcnow()
        case_type.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Email case type updated successfully',
            'case_type': case_type.to_dict()
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Email case type not found'
        }), 404
    except NotUniqueError:
        return jsonify({
            'status': 'error',
            'error': 'Email case type with this code already exists'
        }), 409
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


@email_case_type_bp.route('/<case_type_id>', methods=['DELETE'])
def delete_email_case_type(case_type_id):
    """Delete email case type"""
    try:
        case_type = EmailCaseType.objects.get(id=case_type_id)
        case_type.delete()
        
        return jsonify({
            'status': 'success',
            'message': 'Email case type deleted successfully'
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Email case type not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
