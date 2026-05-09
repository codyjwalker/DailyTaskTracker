# app/helpers.py
"""Utility functions used across the application."""

from datetime import date, timedelta
from . import db
from .models import TaskList, DailyTask

# Default daily task names
DEFAULT_TASK_NAMES = [
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

def init_user_task_list(user):
    """Create default TaskList entries for a new user."""
    for idx, name in enumerate(DEFAULT_TASK_NAMES, start=1):
        task = TaskList(user_id=user.id, name=name, position=idx)
        db.session.add(task)
    db.session.commit()

def get_monthly_view(user, year, month):
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

def get_daily_status(user, date_str):
    """Return status dict for a single date."""
    day_obj = date.fromisoformat(date_str)
    tasks = TaskList.query.filter_by(user_id=user.id).order_by(TaskList.position).all()
    status_map = {t.name: False for t in tasks}
    for dt in DailyTask.query.filter_by(user_id=user.id, date=day_obj).all():
        task_name = TaskList.query.get(dt.task_id).name
        status_map[task_name] = dt.status
    return status_map

def update_daily_status(user, date_str, statuses):
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
