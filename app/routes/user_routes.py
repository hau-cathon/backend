"""User routes"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, db

user_bp = Blueprint('users', __name__)


@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get single user by ID"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged in user"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user"""
    current_user_id = get_jwt_identity()
    
    # Users can only update their own profile
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    
    db.session.commit()
    return jsonify(user.to_dict()), 200


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user"""
    current_user_id = get_jwt_identity()
    
    # Users can only delete their own profile
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200
