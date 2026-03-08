"""Template Option routes - pre-filled template values for case scenarios"""
from flask import Blueprint, jsonify, request
from app.models.template_option import TemplateOption
from datetime import datetime
from mongoengine.errors import ValidationError, DoesNotExist

template_option_bp = Blueprint('template_options', __name__)


@template_option_bp.route('/', methods=['GET'])
def get_template_options():
    """Get all template options with optional filtering"""
    try:
        animal_type = request.args.get('animal_type')
        case_type = request.args.get('case_type')
        
        query = {}
        if animal_type:
            query['animal_type'] = animal_type
        if case_type:
            query['case_type'] = case_type
        
        options = TemplateOption.objects(**query).order_by('animal_type', 'case_type')
        
        return jsonify({
            'status': 'success',
            'count': len(options),
            'options': [option.to_dict() for option in options]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@template_option_bp.route('/<option_id>', methods=['GET'])
def get_template_option(option_id):
    """Get single template option by ID"""
    try:
        option = TemplateOption.objects.get(id=option_id)
        return jsonify({
            'status': 'success',
            'option': option.to_dict()
        }), 200
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Template option not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@template_option_bp.route('/animal-types', methods=['GET'])
def get_animal_types():
    """Get list of distinct animal types"""
    try:
        animal_types = TemplateOption.objects.distinct('animal_type')
        return jsonify({
            'status': 'success',
            'animal_types': animal_types
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@template_option_bp.route('/animal/<animal_type>', methods=['GET'])
def get_options_by_animal(animal_type):
    """Get all template options for specific animal type"""
    try:
        options = TemplateOption.objects(animal_type=animal_type).order_by('case_type')
        return jsonify({
            'status': 'success',
            'count': len(options),
            'options': [option.to_dict() for option in options]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@template_option_bp.route('/', methods=['POST'])
def create_template_option():
    """Create new template option (pre-filled values)"""
    try:
        data = request.get_json()
        
        required_fields = ['animal_type', 'case_type', 'case_label']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'error': f'Missing required field: {field}'
                }), 400
        
        option = TemplateOption(
            animal_type=data['animal_type'],
            case_type=data['case_type'],
            case_label=data['case_label'],
            description=data.get('description', '')
        )
        
        option.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Template option created successfully',
            'option': option.to_dict()
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


@template_option_bp.route('/<option_id>', methods=['PUT'])
def update_template_option(option_id):
    """Update template option"""
    try:
        option = TemplateOption.objects.get(id=option_id)
        data = request.get_json()
        
        if 'animal_type' in data:
            option.animal_type = data['animal_type']
        if 'case_type' in data:
            option.case_type = data['case_type']
        if 'case_label' in data:
            option.case_label = data['case_label']
        if 'description' in data:
            option.description = data['description']
        
        option.updated_at = datetime.utcnow()
        option.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Template option updated successfully',
            'option': option.to_dict()
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Template option not found'
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


@template_option_bp.route('/<option_id>', methods=['DELETE'])
def delete_template_option(option_id):
    """Delete template option"""
    try:
        option = TemplateOption.objects.get(id=option_id)
        option.delete()
        
        return jsonify({
            'status': 'success',
            'message': 'Template option deleted successfully'
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Template option not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Template option deleted successfully'
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Template option not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
