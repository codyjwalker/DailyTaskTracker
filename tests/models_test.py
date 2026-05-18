# Auto‑generated tests for models.py
import unittest
from app.models import *

def test_load_user():
    load_user('')

class TestUser(unittest.TestCase):
    pass

    def test_set_password(self):
        obj = User()
        obj.set_password('')

    def test_check_password(self):
        obj = User()
        obj.check_password('')

class TestTaskList(unittest.TestCase):
    pass

class TestDailyTask(unittest.TestCase):
    pass

class TestTodoList(unittest.TestCase):
    pass

class TestTodoItem(unittest.TestCase):
    pass

class TestSubTask(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()