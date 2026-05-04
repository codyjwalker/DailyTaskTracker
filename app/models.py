# app/models.py
"""
SQLAlchemy ORM models for the Personal Task Tracker.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


class User(UserMixin, db.Model):
    """A registered user."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships
    task_lists = db.relationship('TaskList', backref='user', lazy='dynamic')
    daily_tasks = db.relationship('DailyTask', backref='user', lazy='dynamic')
    todo_items = db.relationship('TodoItem', backref='user', lazy='dynamic')

    # ---------------------------------------------------------------------
    # Password helpers
    # ---------------------------------------------------------------------
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


class TaskList(db.Model):
    """Defines the list of task names for a user."""

    __tablename__ = 'task_lists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)


class DailyTask(db.Model):
    """Stores the completion status of a task on a particular date."""

    __tablename__ = 'daily_tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task_lists.id'), nullable=False)
    status = db.Column(db.Boolean, default=False)


class TodoItem(db.Model):
    """A to‑do item that can be scheduled and marked completed."""

    __tablename__ = 'todo_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime)  # when the item was completed
    due_date = db.Column(db.DateTime)   # optional due date

