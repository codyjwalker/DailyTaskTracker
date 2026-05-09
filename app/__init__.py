# app/__init__.py
"""
Application factory for the Personal Task Tracker.

Now loads configuration from `app.config` (DevelopmentConfig/ProductionConfig).
All extensions are initialised here and the blueprint registry is performed.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

# Extension instances
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# ----------------------------------------------------------------------
# Application factory
# ----------------------------------------------------------------------
def create_app(config_name: str = 'development') -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from the chosen class
    from .config import DevelopmentConfig, ProductionConfig
    config_cls = {
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }[config_name]
    app.config.from_object(config_cls)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError as exc:  # pragma: no cover
        raise RuntimeError(f'Failed to create instance folder: {exc}')

    # Initialise extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Create database tables if missing
    with app.app_context():
        db.create_all()

    # Provide the current year to all templates
    @app.context_processor
    def inject_current_year():
        return {'current_year': __import__('datetime').datetime.utcnow().year}

    return app
