import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from run import app


# Verify the Flask app instance is created correctly

def test_app_created():
    assert app is not None
    assert hasattr(app, "test_client")

# Test that the root route redirects to the login page when not authenticated

def test_root_redirects_to_login():
    client = app.test_client()
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    # Flask redirects include full absolute URL; check endswith login route
    assert response.headers["Location"].endswith("/login")

# Ensure the login page renders successfully

def test_login_page():
    client = app.test_client()
    response = client.get("/login")
    assert response.status_code == 200
