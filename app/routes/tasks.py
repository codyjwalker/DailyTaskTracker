# app/routes/tasks.py
"""Routes for daily, monthly and Task‑Overview views."""
from datetime import date, timedelta

from flask import (
    render_template,
    redirect,
    url_for,
    request,
    flash,
)
from flask_login import login_required, current_user

from . import bp
from .. import db
from ..models import TaskList, DailyTask
from ..helpers import (
    get_monthly_view,
    get_daily_status,
    update_daily_status,
)

@bp.route("/monthly")
@login_required
def monthly():
    """Render the monthly overview."""
    today = date.today()
    month = int(request.args.get("month", today.month))
    year = int(request.args.get("year", today.year))

    days, tasks = get_monthly_view(current_user, year, month)

    def prev_month(y, m):
        return (y - 1, 12) if m == 1 else (y, m - 1)

    def next_month(y, m):
        return (y + 1, 1) if m == 12 else (y, m + 1)

    prev_year, prev_month_val = prev_month(year, month)
    next_year, next_month_val = next_month(year, month)

    return render_template(
        "tasks/monthly.html",
        year=year,
        month=month,
        month_name=date(year, month, 1).strftime("%B"),
        days=days,
        tasks=tasks,
        prev_year=prev_year,
        prev_month=prev_month_val,
        next_year=next_year,
        next_month=next_month_val,
    )

# ------------------------------------------------------------------
# NEW: Task‑Overview – yearly heat‑map style overview for a single task
# ------------------------------------------------------------------
@bp.route("/task")
@login_required
def task_overview():
    """Render a yearly heat‑map style overview for a single task."""
    # All tasks that belong to the current user
    tasks = TaskList.query.filter_by(user_id=current_user.id).order_by(TaskList.position).all()

    # Selected task (query‑string “task” contains the task ID)
    task_id = request.args.get("task", type=int)
    selected_task = None
    if task_id:
        selected_task = TaskList.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not selected_task and tasks:
        selected_task = tasks[0]

    if not selected_task:
        flash("No tasks found.", "warning")
        return redirect(url_for("main.monthly"))

    today = date.today()
    earliest_date = today - timedelta(days=363)   # 364 days including today

    # Map of dates → completion status for the chosen task
    daily_tasks = DailyTask.query.filter_by(
        user_id=current_user.id, task_id=selected_task.id
    ).filter(DailyTask.date >= earliest_date, DailyTask.date <= today).all()
    status_map = {dt.date: dt.status for dt in daily_tasks}

    rows, cols = 26, 14
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            offset = r * cols + (cols - 1 - c)  # right‑to‑left mapping
            cell_date = today - timedelta(days=offset)
            exists = (
                selected_task.start_date <= cell_date
                and (selected_task.end_date is None or selected_task.end_date > cell_date)
            )
            if exists:
                status = status_map.get(cell_date, False)
                color = "green" if status else "red"
            else:
                color = "blank"
            row.append({
                "date": cell_date,
                "color": color,
                "exists": exists,
                "month": f"{cell_date.month:02d}",
                "day": f"{cell_date.day:02d}",
            })
        grid.append(row)

    return render_template(
        "tasks/task_overview.html",
        selected_task=selected_task,
        tasks=tasks,
        grid=grid,
    )
@bp.route("/daily", methods=["GET", "POST"])
@login_required
def daily():
    """Render and handle the daily overview."""
    date_str = request.args.get("date")
    if not date_str:
        date_str = date.today().isoformat()

    # Validate the date format
    try:
        date.fromisoformat(date_str)
    except ValueError:
        return redirect(url_for("main.monthly"))

    if request.method == "POST":
        # Build status dict from form inputs
        day_obj = date.fromisoformat(date_str)
        active_tasks = (
            TaskList.query.filter_by(user_id=current_user.id)
            .filter(TaskList.start_date <= day_obj)
            .filter(
                (TaskList.end_date == None) | (TaskList.end_date > day_obj)
            )
            .order_by(TaskList.position)
            .all()
        )
        task_names = [t.name for t in active_tasks]
        statuses = {
            name: (f"task_{i}" in request.form)
            for i, name in enumerate(task_names)
        }
        update_daily_status(current_user, date_str, statuses)
        flash("Daily tasks updated.", "success")
        return redirect(url_for("main.daily", date=date_str))

    statuses = get_daily_status(current_user, date_str)
    day_obj = date.fromisoformat(date_str)
    active_tasks = (
        TaskList.query.filter_by(user_id=current_user.id)
        .filter(TaskList.start_date <= day_obj)
        .filter(
            (TaskList.end_date == None) | (TaskList.end_date > day_obj)
        )
        .order_by(TaskList.position)
        .all()
    )
    task_names = [t.name for t in active_tasks]
    return render_template(
        "tasks/daily.html",
        date=date_str,
        tasks=task_names,
        statuses=statuses,
    )


@bp.route("/add_task", methods=["POST"])
@login_required
def add_task():
    """Handle addition of a new daily task via the monthly view."""
    name = request.form.get("name", "").strip()
    pos = request.form.get("position", "").strip()
    month_str = request.form.get("month")
    year_str = request.form.get("year")

    if not name:
        flash("Task name cannot be empty.", "warning")
        return redirect(url_for("main.monthly"))

    if not month_str or not year_str:
        flash("Invalid month/year for adding task.", "warning")
        return redirect(url_for("main.monthly"))

    try:
        month = int(month_str)
        year = int(year_str)
    except ValueError:
        flash("Invalid month/year for adding task.", "warning")
        return redirect(url_for("main.monthly"))

    target_month = date(year, month, 1)
    current_month_start = date.today().replace(day=1)

    if target_month < current_month_start:
        flash("Cannot add tasks to past months.", "warning")
        return redirect(url_for("main.monthly", month=month, year=year))

    try:
        pos_int = int(pos)
    except (ValueError, TypeError):
        pos_int = None

    # Determine existing tasks active for the target month
    existing_tasks = (
        TaskList.query.filter_by(user_id=current_user.id)
        .filter(TaskList.start_date <= target_month)
        .filter((TaskList.end_date == None) | (TaskList.end_date > target_month))
        .order_by(TaskList.position)
        .all()
    )

    if pos_int is None or pos_int < 1:
        pos_int = len(existing_tasks) + 1
    else:
        # bump positions for tasks that come after the insertion point
        for i, t in enumerate(existing_tasks, start=1):
            if i >= pos_int:
                t.position += 1
        db.session.commit()

    new_task = TaskList(
        user_id=current_user.id,
        name=name,
        position=pos_int,
        start_date=target_month,
    )
    db.session.add(new_task)
    db.session.commit()

    flash("New task added.", "success")
    return redirect(url_for("main.monthly", month=month, year=year))


@bp.route("/delete_task", methods=["POST"])
@login_required
def delete_task():
    """Delete a task starting from the current month onward."""
    task_name = request.form.get("task_name")
    month_str = request.form.get("month")
    year_str = request.form.get("year")

    if not task_name or not month_str or not year_str:
        flash("Invalid data for deleting task.", "warning")
        return redirect(url_for("main.monthly"))

    try:
        month = int(month_str)
        year = int(year_str)
    except ValueError:
        flash("Invalid month/year for deleting task.", "warning")
        return redirect(url_for("main.monthly"))

    target_month = date(year, month, 1)
    task = TaskList.query.filter_by(
        user_id=current_user.id, name=task_name
    ).first()

    if not task:
        flash("Task not found.", "warning")
        return redirect(url_for("main.monthly", month=month, year=year))

    # Set the end date to the target month to remove from current/future months
    if task.end_date is None or task.end_date > target_month:
        task.end_date = target_month
        db.session.commit()
        flash(
            f'Task "{task_name}" deleted for current and future months.',
            "success",
        )
    else:
        flash("Task already deleted.", "info")

    return redirect(url_for("main.monthly", month=month, year=year))


@bp.route("/move_task", methods=["POST"])
@login_required
def move_task():
    """Move a task up or down within the current month."""
    task_name = request.form.get("task_name")
    direction = request.form.get("direction")
    month_str = request.form.get("month")
    year_str = request.form.get("year")

    if not task_name or not direction or not month_str or not year_str:
        flash("Invalid data for moving task.", "warning")
        return redirect(url_for("main.monthly"))

    try:
        month = int(month_str)
        year = int(year_str)
    except ValueError:
        flash("Invalid month/year for moving task.", "warning")
        return redirect(url_for("main.monthly"))

    target_month = date(year, month, 1)
    task = TaskList.query.filter_by(
        user_id=current_user.id, name=task_name
    ).first()

    if not task:
        flash("Task not found.", "warning")
        return redirect(url_for("main.monthly", month=month, year=year))

    # Get active tasks for the target month
    active_tasks = (
        TaskList.query.filter_by(user_id=current_user.id)
        .filter(TaskList.start_date <= target_month)
        .filter((TaskList.end_date == None) | (TaskList.end_date > target_month))
        .order_by(TaskList.position)
        .all()
    )
    indices = {t.id: idx for idx, t in enumerate(active_tasks)}
    if task.id not in indices:
        flash("Task is not active in this month.", "info")
        return redirect(url_for("main.monthly", month=month, year=year))

    idx = indices[task.id]
    if direction == "up":
        if idx == 0:
            flash("Task is already at the top.", "info")
        else:
            prev_task = active_tasks[idx - 1]
            task.position, prev_task.position = (
                prev_task.position,
                task.position,
            )
            db.session.commit()
            flash("Task moved up.", "success")
    elif direction == "down":
        if idx == len(active_tasks) - 1:
            flash("Task is already at the bottom.", "info")
        else:
            next_task = active_tasks[idx + 1]
            task.position, next_task.position = (
                next_task.position,
                task.position,
            )
            db.session.commit()
            flash("Task moved down.", "success")
    else:
        flash("Invalid move direction.", "warning")

    return redirect(url_for("main.monthly", month=month, year=year))
