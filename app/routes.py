# app/routes.py
"""
All Flask routes – login, register, logout, task views, todo list.
"""

from datetime import date, datetime, timedelta

from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)

from . import db
from .models import User, TaskList, DailyTask, TodoItem
from .forms import LoginForm, RegistrationForm

# ----------------------------------------------------------------------
# Blueprint
# ----------------------------------------------------------------------
bp = Blueprint('main', __name__)


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def _default_task_names():
    """Return the list of default task names."""
    return [
        'Wake Up By 8:30',
        'Log Weight',
        'Make Bed',
        'Morning Mantra',
        'Meditate',
        'Morning Sun',
        'Stretch',
        'Check Email',
        'Morning Hygiene',
        'Vitamins/Creatine',
        'Workout Regime',
        'Feed & Take Out Sharron',
        'Work Goals',
        'Tidy Up',
        'ToDo (~30min)',
        'Music Production Goals',
        'Protein Shake',
        'Count Macros',
        'Meet Macros',
        'Close Rings',
        'Nighttime Hygiene',
        'Nighttime Stretch',
        'Bed By Midnight',
    ]


def _init_user_task_list(user: User) -> None:
    """Create the default TaskList entries for a new user."""
    for idx, name in enumerate(_default_task_names(), start=1):
        task = TaskList(user_id=user.id, name=name, position=idx)
        db.session.add(task)
    db.session.commit()


def _get_monthly_view(user: User, year: int, month: int):
    """Generate data for the monthly overview."""
    first_day = date(year, month, 1)
    last_day = (
        date(year, month, 31)
        if month == 12
        else date(year, month + 1, 1) - timedelta(days=1)
    )
    num_days = last_day.day

    # Ordered list of tasks for this user
    tasks = TaskList.query.filter_by(user_id=user.id).order_by(TaskList.position).all()

    # Ensure DailyTask rows exist for every (date, task)
    for day in range(1, num_days + 1):
        day_date = date(year, month, day)
        for task in tasks:
            if not DailyTask.query.filter_by(
                user_id=user.id, date=day_date, task_id=task.id
            ).first():
                dt = DailyTask(
                    user_id=user.id, date=day_date, task_id=task.id, status=False
                )
                db.session.add(dt)
    db.session.commit()

    days = []
    for day in range(1, num_days + 1):
        day_date = date(year, month, day)
        day_str = day_date.isoformat()
        # Build a dict of status: {task_name: bool}
        status_map = {t.name: False for t in tasks}
        for dt in DailyTask.query.filter_by(user_id=user.id, date=day_date).all():
            task_name = TaskList.query.get(dt.task_id).name
            status_map[task_name] = dt.status

        days.append({
            'date': day_str,
            'day': day,
            'weekday': day_date.strftime('%a'),
            'statuses': status_map,
        })

    task_names = [t.name for t in tasks]
    return days, task_names


def _get_daily_status(user: User, date_str: str):
    """Return status dict for a single date."""
    day_obj = date.fromisoformat(date_str)
    tasks = TaskList.query.filter_by(user_id=user.id).order_by(TaskList.position).all()
    status_map = {t.name: False for t in tasks}
    for dt in DailyTask.query.filter_by(user_id=user.id, date=day_obj).all():
        task_name = TaskList.query.get(dt.task_id).name
        status_map[task_name] = dt.status
    return status_map


def _update_daily_status(user: User, date_str: str, statuses: dict):
    """Persist daily status changes."""
    day_obj = date.fromisoformat(date_str)
    for task_name, done in statuses.items():
        task = TaskList.query.filter_by(user_id=user.id, name=task_name).first()
        if not task:
            continue
        dt = DailyTask.query.filter_by(
            user_id=user.id, date=day_obj, task_id=task.id
        ).first()
        if not dt:
            dt = DailyTask(user_id=user.id, date=day_obj, task_id=task.id, status=done)
            db.session.add(dt)
        else:
            dt.status = done
    db.session.commit()


# ----------------------------------------------------------------------
# Public routes
# ----------------------------------------------------------------------
@bp.route('/')
def index():
    """Home page – redirect to login if not authenticated."""
    if current_user.is_authenticated:
        return redirect(url_for('main.monthly'))
    return redirect(url_for('main.login'))


# ----------------------------------------------------------------------
# Authentication
# ----------------------------------------------------------------------
@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.monthly'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.monthly'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Account registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.monthly'))

    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        _init_user_task_list(new_user)  # populate default tasks
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# ----------------------------------------------------------------------
# Calendar views
# ----------------------------------------------------------------------
@bp.route('/monthly')
@login_required
def monthly():
    """Render the monthly overview."""
    today = date.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))

    days, tasks = _get_monthly_view(current_user, year, month)

    # Helper to compute prev/next month
    def prev_month(y, m):
        return (y - 1, 12) if m == 1 else (y, m - 1)

    def next_month(y, m):
        return (y + 1, 1) if m == 12 else (y, m + 1)

    prev_year, prev_month_val = prev_month(year, month)
    next_year, next_month_val = next_month(year, month)

    return render_template(
        'monthly.html',
        year=year,
        month=month,
        month_name=date(year, month, 1).strftime('%B'),
        days=days,
        tasks=tasks,
        prev_year=prev_year,
        prev_month=prev_month_val,
        next_year=next_year,
        next_month=next_month_val,
    )


@bp.route('/daily', methods=['GET', 'POST'])
@login_required
def daily():
    """Render and handle the daily overview."""
    date_str = request.args.get('date')
    if not date_str:
        date_str = date.today().isoformat()

    try:
        date.fromisoformat(date_str)
    except ValueError:
        return redirect(url_for('main.monthly'))

    if request.method == 'POST':
        # Build status dict from form inputs
        task_names = [t.name for t in TaskList.query.filter_by(user_id=current_user.id).order_by(TaskList.position).all()]
        statuses = {name: f'task_{i}' in request.form for i, name in enumerate(task_names)}
        _update_daily_status(current_user, date_str, statuses)
        flash('Daily tasks updated.', 'success')
        return redirect(url_for('main.daily', date=date_str))

    statuses = _get_daily_status(current_user, date_str)
    task_names = [t.name for t in TaskList.query.filter_by(user_id=current_user.id).order_by(TaskList.position).all()]
    return render_template(
        'daily.html',
        date=date_str,
        tasks=task_names,
        statuses=statuses,
    )


@bp.route('/add_task', methods=['POST'])
@login_required
def add_task():
    """Handle addition of a new daily task via the monthly view."""
    name = request.form.get('name', '').strip()
    pos = request.form.get('position', '').strip()

    if not name:
        flash('Task name cannot be empty.', 'warning')
        return redirect(url_for('main.monthly'))

    try:
        pos_int = int(pos)
    except (ValueError, TypeError):
        pos_int = None

    # Existing tasks for ordering
    existing = TaskList.query.filter_by(user_id=current_user.id).order_by(TaskList.position).all()

    if pos_int is None or pos_int < 1:
        pos_int = len(existing) + 1
    else:
        # bump positions for tasks that come after the insertion point
        for i, t in enumerate(existing, start=1):
            if i >= pos_int:
                t.position += 1
        db.session.commit()

    new_task = TaskList(user_id=current_user.id, name=name, position=pos_int)
    db.session.add(new_task)
    db.session.commit()

    flash('New task added.', 'success')
    return redirect(url_for('main.monthly'))


# ----------------------------------------------------------------------
# To‑Do list
# ----------------------------------------------------------------------
@bp.route('/todolist', methods=['GET', 'POST'])
@login_required
def todolist():
    """Render the To‑Do list and handle add/complete/remove actions."""
    if request.method == 'POST':
        action = request.form.get('action')

        # ---- Add ---------------------------------------------------------
        if action == 'add':
            name = request.form.get('name', '').strip()
            if name:
                due_checkbox = request.form.get('due_checkbox')
                raw_due = request.form.get('due_date')
                due_date = None
                if due_checkbox == 'on' and raw_due:
                    try:
                        due_date = datetime.strptime(raw_due, '%Y-%m-%dT%H:%M')
                    except ValueError:
                        pass

                new_item = TodoItem(
                    user_id=current_user.id,
                    name=name,
                    completed=False,
                    due_date=due_date,
                )
                db.session.add(new_item)
                db.session.commit()
            flash('Item added.', 'success')
            return redirect(url_for('main.todolist'))

        # ---- Complete ----------------------------------------------------
        if action == 'complete':
            item_id = request.form.get('item_id')
            if item_id:
                item = TodoItem.query.get(item_id)
                if item and item.user_id == current_user.id:
                    item.completed = True
                    item.timestamp = datetime.utcnow()
                    db.session.commit()
            flash('Item marked completed.', 'success')
            return redirect(url_for('main.todolist'))

        # ---- Remove ------------------------------------------------------
        if action == 'remove':
            item_id = request.form.get('item_id')
            if item_id:
                item = TodoItem.query.get(item_id)
                if item and item.user_id == current_user.id:
                    db.session.delete(item)
                    db.session.commit()
            flash('Item removed.', 'info')
            return redirect(url_for('main.todolist'))

    # ----- GET -----------------------------------------------------------
    items = TodoItem.query.filter_by(user_id=current_user.id).order_by(TodoItem.timestamp.asc()).all()
    pending, scheduled, completed = [], [], []
    now = datetime.utcnow()

    for itm in items:
        if itm.completed:
            completed.append(itm)
            continue
        due = itm.due_date
        if due:
            diff = due - now
            if diff.total_seconds() < 0:
                status_class = 'red'
            elif diff <= timedelta(hours=24):
                status_class = 'orange'
            elif diff <= timedelta(hours=48):
                status_class = 'yellow'
            else:
                status_class = ''
            scheduled.append((itm, status_class, due.strftime('%Y-%m-%d %H:%M')))
        else:
            pending.append(itm)

    return render_template(
        'todolist.html',
        pending=pending,
        scheduled=scheduled,
        completed=completed,
    )

