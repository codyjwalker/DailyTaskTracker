# app/routes/tasks.py
"""Routes for daily and monthly task views."""

from datetime import date
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from . import bp
from .. import db
from ..models import TaskList
from ..helpers import get_monthly_view, get_daily_status, update_daily_status

@bp.route('/monthly')
@login_required
def monthly():
    """Render the monthly overview."""
    today = date.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))

    days, tasks = get_monthly_view(current_user, year, month)

    def prev_month(y, m):
        return (y - 1, 12) if m == 1 else (y, m - 1)

    def next_month(y, m):
        return (y + 1, 1) if m == 12 else (y, m + 1)

    prev_year, prev_month_val = prev_month(year, month)
    next_year, next_month_val = next_month(year, month)

    return render_template(
        'tasks/monthly.html',
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

    # Validate the date format
    try:
        date.fromisoformat(date_str)
    except ValueError:
        return redirect(url_for('main.monthly'))

    if request.method == 'POST':
        # Build status dict from form inputs
        task_names = [t.name for t in TaskList.query.filter_by(user_id=current_user.id).order_by(TaskList.position).all()]
        statuses = {name: (f'task_{i}' in request.form) for i, name in enumerate(task_names)}
        update_daily_status(current_user, date_str, statuses)
        flash('Daily tasks updated.', 'success')
        return redirect(url_for('main.daily', date=date_str))

    statuses = get_daily_status(current_user, date_str)
    task_names = [t.name for t in TaskList.query.filter_by(user_id=current_user.id).order_by(TaskList.position).all()]
    return render_template(
        'tasks/daily.html',
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
