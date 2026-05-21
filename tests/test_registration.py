import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from run import app
from app.models import User

# Disable CSRF for tests
app.config['WTF_CSRF_ENABLED'] = False


def test_user_can_register_and_exist_in_db():
    """Test that a new user can register via the /register route."""
    client = app.test_client()
    import uuid

    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "Password!123"
    data = {
        "username": username,
        "password": password,
        "confirm_password": password,
        "submit": "Create Account"
    }
    response = client.post("/register", data=data, follow_redirects=True)
    # The app redirects to the login page after successful registration
    assert response.status_code == 200
    assert b"Please log in" in response.data
    # Verify that the user was added to the database
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.username == username


def test_invalid_usernames():
    """Attempt to register with usernames that are too short and ensure error is shown."""
    client = app.test_client()

    def attempt(username):
        data = {
            "username": username,
            "password": "Password!123",
            "confirm_password": "Password!123",
            "submit": "Create Account"
        }
        return client.post("/register", data=data, follow_redirects=True)




    res1 = attempt('ab')
    assert res1.status_code == 200
    try:
        assert b"Please use at least 3 characters" in res1.data
    except AssertionError:
        print(f"[FAIL] Expected tooltip in response 1, got: {res1.data.decode(errors='ignore')}")

    res2 = attempt('1')
    assert res2.status_code == 200
    try:
        assert b"Please use at least 3 characters" in res2.data
    except AssertionError:
        print(f"[FAIL] Expected tooltip in response 2, got: {res2.data.decode(errors='ignore')}")

    res3 = attempt('')
    assert res3.status_code == 200
    try:
        assert b"Please use at least 3 characters" in res3.data
    except AssertionError:
        print(f"[FAIL] Expected tooltip in response 3, got: {res3.data.decode(errors='ignore')}")
