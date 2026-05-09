# app/routes/auth.py
"""Authentication routes: login, register, logout."""

from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from . import bp
from .. import db
from ..forms import LoginForm, RegistrationForm
from ..models import User
from ..helpers import init_user_task_list

@bp.route('/')
def index():
    """Home page – redirect to login or monthly overview."""
    if current_user.is_authenticated:
        return redirect(url_for('main.monthly'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Render and process the login form."""
    if current_user.is_authenticated:
        return redirect(url_for('main.monthly'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.monthly'))
        flash('Invalid username or password', 'danger')
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Render and process the registration form."""
    if current_user.is_authenticated:
        return redirect(url_for('main.monthly'))

    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        # Populate default tasks
        init_user_task_list(new_user)
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))
