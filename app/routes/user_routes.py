"""User routes"""
from flask import Blueprint, jsonify, request
<<<<<<< HEAD
=======
from flask_jwt_extended import jwt_required, get_jwt_identity
>>>>>>> 4a013070d883cb0704b509532196fe7739905744
from app.models import User

user_bp = Blueprint('users', __name__)


@user_bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.objects.all()
    return jsonify([user.to_dict() for user in users]), 200


@user_bp.route('/<user_id>', methods=['GET'])
<<<<<<< HEAD
def get_user(user_id):
    """Get single user by ID"""
    try:
        user = User.objects.get(id=user_id)
        return jsonify(user.to_dict()), 200
    except User.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
=======
@jwt_required()
def get_user(user_id):
    """Get single user by ID"""
    user = User.objects(id=user_id).first_or_404()
    return jsonify(user.to_dict()), 200
>>>>>>> 4a013070d883cb0704b509532196fe7739905744


@user_bp.route('/me', methods=['GET'])
def get_current_user():
<<<<<<< HEAD
    """Get current logged in user - requires user_id in query params"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id query parameter required'}), 400
    try:
        user = User.objects.get(id=user_id)
        return jsonify(user.to_dict()), 200
    except User.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404


@user_bp.route('/<user_id>', methods=['PUT'])
=======
    """Get current logged in user"""
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first_or_404()
    return jsonify(user.to_dict()), 200


@user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
>>>>>>> 4a013070d883cb0704b509532196fe7739905744
def update_user(user_id):
    """Update user"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
    
<<<<<<< HEAD
=======
    # Users can only update their own profile
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.objects(id=user_id).first_or_404()
>>>>>>> 4a013070d883cb0704b509532196fe7739905744
    data = request.get_json()
    
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    
    user.save()
    return jsonify(user.to_dict()), 200


@user_bp.route('/<user_id>', methods=['DELETE'])
<<<<<<< HEAD
def delete_user(user_id):
    """Delete user"""
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return jsonify({'message': 'User deleted successfully'}), 200
    except User.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
=======
@jwt_required()
def delete_user(user_id):
    """Delete user"""
    current_user_id = get_jwt_identity()
    
    # Users can only delete their own profile
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.objects(id=user_id).first_or_404()
    user.delete()
    
    return jsonify({'message': 'User deleted successfully'}), 200
>>>>>>> 4a013070d883cb0704b509532196fe7739905744
