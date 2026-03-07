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
    
    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.user_routes import user_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    
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
    
    return app


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