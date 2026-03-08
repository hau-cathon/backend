"""Role routes - basic CRUD operations"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.role import Role
from datetime import datetime
from mongoengine.errors import ValidationError, DoesNotExist, NotUniqueError

role_bp = Blueprint('roles', __name__)


@role_bp.route('/', methods=['GET'])
@jwt_required()
def get_roles():
    """Get all roles"""
    try:
        roles = Role.objects.all().order_by('name')
        return jsonify({
            'status': 'success',
            'count': len(roles),
            'roles': [role.to_dict() for role in roles]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@role_bp.route('/<role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    """Get single role by ID"""
    try:
        role = Role.objects.get(id=role_id)
        return jsonify({
            'status': 'success',
            'role': role.to_dict()
        }), 200
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Role not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@role_bp.route('/', methods=['POST'])
@jwt_required()
def create_role():
    """Create new role"""
    try:
        data = request.get_json()
        
        # Required fields validation
        if 'name' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Missing required field: name'
            }), 400
        
        # Create role
        role = Role(
            name=data['name'],
            description=data.get('description', '')
        )
        
        role.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Role created successfully',
            'role': role.to_dict()
        }), 201
        
    except NotUniqueError:
        return jsonify({
            'status': 'error',
            'error': 'Role with this name already exists'
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


@role_bp.route('/<role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    """Update role"""
    try:
        role = Role.objects.get(id=role_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            role.name = data['name']
        if 'description' in data:
            role.description = data['description']
        
        role.updated_at = datetime.utcnow()
        role.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Role updated successfully',
            'role': role.to_dict()
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Role not found'
        }), 404
    except NotUniqueError:
        return jsonify({
            'status': 'error',
            'error': 'Role with this name already exists'
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


@role_bp.route('/<role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    """Delete role"""
    try:
        role = Role.objects.get(id=role_id)
        role.delete()
        
        return jsonify({
            'status': 'success',
            'message': 'Role deleted successfully'
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Role not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
