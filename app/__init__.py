from flask import Flask, jsonify
from .config import Config
from .extensions import init_db, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    init_db(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize WebSocket
    from .utils.websocket_handler import socketio
    socketio.init_app(app)
    
    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.user_routes import user_bp
    from .routes.model_routes import model_bp
    from .routes.email_routes import email_bp
    from .routes.duplicate_routes import duplicate_bp
    from .routes.stt_routes import stt_bp
    from .routes.form_routes import form_bp

    app.register_blueprint(duplicate_bp, url_prefix='/api/duplicates')
    app.register_blueprint(email_bp, url_prefix='/api/email')
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(model_bp, url_prefix="/api/model")
    app.register_blueprint(stt_bp, url_prefix="/api/stt")
    app.register_blueprint(form_bp, url_prefix="/api/form")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register shell context for flask shell command
    @app.shell_context_processor
    def make_shell_context():
        from app.models import User, Role, Issue, EmailCaseType, EmailTemplate, TemplateOption
        return {
            'User': User,
            'Role': Role,
            'Issue': Issue,
            'EmailCaseType': EmailCaseType,
            'EmailTemplate': EmailTemplate,
            'TemplateOption': TemplateOption
        }
    
    return app, socketio


def register_error_handlers(app):
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403