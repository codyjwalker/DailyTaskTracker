# app/routes/__init__.py
"""
Package initialiser for route modules.

Defines the single blueprint that all modules share and imports the
individual route files so that they execute and register their routes.
"""

from flask import Blueprint

bp = Blueprint('main', __name__)

# Import all route modules – the imports are side‑effects
# that register the routes on `bp`.
from .auth import *   # noqa: F401
from .tasks import *  # noqa: F401
from .todo import *   # noqa: F401
