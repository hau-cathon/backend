"""User routes"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, db

user_bp = Blueprint('users', __name__)


@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
<<<<<<< HEAD
=======
    """Get all users"""
>>>>>>> ac7c0dbb5c4f71f5f7eee16a8dff7d65b0b0f73f
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
<<<<<<< HEAD
=======
    """Get single user by ID"""
>>>>>>> ac7c0dbb5c4f71f5f7eee16a8dff7d65b0b0f73f
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
<<<<<<< HEAD
=======
    """Get current logged in user"""
>>>>>>> ac7c0dbb5c4f71f5f7eee16a8dff7d65b0b0f73f
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
<<<<<<< HEAD
    current_user_id = get_jwt_identity()

=======
    """Update user"""
    current_user_id = get_jwt_identity()
    
    # Users can only update their own profile
>>>>>>> ac7c0dbb5c4f71f5f7eee16a8dff7d65b0b0f73f
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
<<<<<<< HEAD

=======
    
    # Users can only delete their own profile
>>>>>>> ac7c0dbb5c4f71f5f7eee16a8dff7d65b0b0f73f
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200
