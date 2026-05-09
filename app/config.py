# app/config.py
"""
Utility module that fetches the Flask SECRET_KEY from a file
(or falls back to an environment variable).

The file must contain a single line: the key itself (no quotes).
"""

import os
from pathlib import Path

# Path to the secret key file, one level above the package
SECRET_KEY_FILE = Path(__file__).resolve().parent.parent / 'secret_key.txt'

def _load_secret_key() -> str:
    """Return the secret key, or raise RuntimeError if not found."""
    # Try the file first
    if SECRET_KEY_FILE.is_file():
        key = SECRET_KEY_FILE.read_text(encoding='utf-8').strip()
        if key:
            return key
    # Fallback to environment variable (useful for Docker / CI)
    key = os.getenv('FLASK_SECRET_KEY')
    if key:
        return key
    # Nothing found – abort loudly
    raise RuntimeError(
        'SECRET_KEY not found. Create secret_key.txt or set FLASK_SECRET_KEY.'
    )

class Config:
    """Base configuration shared by all environments."""
    SECRET_KEY = _load_secret_key()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLite file lives inside the instance folder – cast to string
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{Path(__file__).resolve().parent.parent / 'instance' / 'app.db'}"
    )
    # Flask‑Login helpers
    LOGIN_VIEW = 'main.login'
    LOGIN_MESSAGE_CATEGORY = 'info'
    # Flask‑WTF CSRF protection
    WTF_CSRF_ENABLED = True

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
