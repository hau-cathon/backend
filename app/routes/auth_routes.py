from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import login_user, register_user, refresh_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    """Register a new user"""
    data = request.json
    return register_user(data)


@auth_bp.post("/login")
def login():
    """Login user"""
    data = request.json
    return login_user(data)


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_id = get_jwt_identity()
    return refresh_token(user_id)


@auth_bp.get("/me")
@jwt_required()
def get_current_user():
    """Get current user info"""
    from app.models import User
    
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200