# Auto‑generated tests for forms.py
import unittest
from app.forms import *

class TestRegistrationForm(unittest.TestCase):
    pass

    def test_validate_username(self):
        obj = RegistrationForm()
        obj.validate_username(None)

class TestLoginForm(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()