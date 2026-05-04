# app/__init__.py
"""
Flask application package.
"""
from flask import Flask

# Create the Flask app.
app = Flask(
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# Import routes **after** the app object is created
# to avoid circular import problems.
from . import routes  # noqa: F401

