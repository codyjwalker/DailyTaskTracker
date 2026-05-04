# app/__init__.py
"""
Application factory for the Personal Task Tracker.

Now loads SECRET_KEY from app/config.py (which in turn reads a
private file that lives outside version control).
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

# Import the helper that fetches the secret key
from .config import get_secret_key


def create_app():
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        instance_relative_config=True,  # instance folder is the parent dir
    )

    # ---------- Configuration ---------------------------------------------
    app.config.from_mapping(
        SECRET_KEY=get_secret_key(),
        SQLALCHEMY_DATABASE_URI='sqlite:///../instance/app.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        LOGIN_VIEW='main.login',
        LOGIN_MESSAGE_CATEGORY='info',
    )

    # ---------- Initialise extensions -------------------------------------
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ---------- Register routes -------------------------------------------
    from . import routes  # noqa: F401
    app.register_blueprint(routes.bp)

    # ---------- Create database tables if missing -------------------------
    with app.app_context():
        db.create_all()

    return app

