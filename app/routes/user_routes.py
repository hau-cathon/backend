"""User routes"""
from flask import Blueprint, jsonify, request
from app.models import User

user_bp = Blueprint('users', __name__)


@user_bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.objects.all()
    return jsonify([user.to_dict() for user in users]), 200


@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get single user by ID"""
    try:
        user = User.objects.get(id=user_id)
        return jsonify(user.to_dict()), 200
    except User.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404


@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged in user"""
    user_id = get_jwt_identity()
    try:
        user = User.objects.get(id=user_id)
        return jsonify(user.to_dict()), 200
    except User.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404


@user_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    
    user.save()
    return jsonify(user.to_dict()), 200


@user_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return jsonify({'message': 'User deleted successfully'}), 200
    except User.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
