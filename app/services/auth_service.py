"""Authentication service"""
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import User


def register_user(data):
    """Register a new user"""
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    
    # Validation
    if not email or not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    if User.objects(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if User.objects(username=username).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    # Create new user
    user = User(email=email, username=username)
    user.set_password(password)
    user.save()
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


def login_user(data):
    """Login user"""
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.objects(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


def refresh_token(user_id):
    """Refresh access token"""
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token}), 200
