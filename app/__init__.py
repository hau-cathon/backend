from flask import Flask, jsonify
from .config import Config
from .extensions import init_db, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_db(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})

    from .routes.auth_routes import auth_bp
    from .routes.user_routes import user_bp
    from .routes.model_routes import model_bp
    from .routes.email_routes import email_bp
    from .routes.duplicate_routes import duplicate_bp
    from .routes.issue_routes import issue_bp
    from .routes.email_case_type_routes import email_case_type_bp
    from .routes.email_template_routes import email_template_bp
    from .routes.template_option_routes import template_option_bp

    app.register_blueprint(duplicate_bp, url_prefix='/api/duplicates')
    app.register_blueprint(email_bp, url_prefix='/api/email')
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(model_bp, url_prefix="/api/model")
    app.register_blueprint(issue_bp, url_prefix="/api/issues")
    app.register_blueprint(email_case_type_bp, url_prefix="/api/email-case-types")
    app.register_blueprint(email_template_bp, url_prefix="/api/email-templates")
    app.register_blueprint(template_option_bp, url_prefix="/api/template-options")
    
    # Register error handlers
    register_error_handlers(app)

    @app.shell_context_processor
    def make_shell_context():
        from app.models import User, Issue, IssueDuplicate, EmailCaseType, EmailTemplate, TemplateOption
        return {
            'User': User,
            'Issue': Issue,
            'IssueDuplicate': IssueDuplicate,
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