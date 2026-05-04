#!/usr/bin/env python3
"""
Simple Flask application for tracking daily tasks.
Author: $sudo

Personal Task Tracker – Routes module.

This module implements the Flask routes for the application.
"""

import os
import json
import datetime
import uuid

from flask import render_template, request, redirect, url_for
from . import app


# ----------------------------------------------------------------------
# Configuration & file names
# ----------------------------------------------------------------------
BASE_DIR = os.path.join(app.root_path, '..', 'data')

DAILY_TASKS_FILE = os.path.join(BASE_DIR, 'DailyTasks.json')
TODO_LIST_FILE   = os.path.join(BASE_DIR, 'ToDoList.json')
DAILY_TASKS_LIST = os.path.join(BASE_DIR, 'DailyTasksList.json')

DEFAULT_DAILY_TASKS = [
    'Wake Up By 8:30',
    'Log Weight',
    'Make Bed',
    'Morning Mantra',
    'Meditate',
    'Morning Sun',
    'Stretch',
    'Check Email',
    'Morning Hygine',
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
    'Nighttime Hygine',
    'Nighttime Stretch',
    'Bed By Midnight',
]


# ----------------------------------------------------------------------
# Persistent storage helpers
# ----------------------------------------------------------------------
def load_task_names() -> list:
    """Return the list of task names, creating the file if it does not exist."""
    if not os.path.exists(DAILY_TASKS_LIST):
        with open(DAILY_TASKS_LIST, 'w') as f:
            json.dump(DEFAULT_DAILY_TASKS, f, indent=4)
        return DEFAULT_DAILY_TASKS.copy()

    with open(DAILY_TASKS_LIST, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return DEFAULT_DAILY_TASKS.copy()


def save_task_names(task_names: list) -> None:
    """Persist the list of task names."""
    with open(DAILY_TASKS_LIST, 'w') as f:
        json.dump(task_names, f, indent=4)


def load_daily_tasks() -> dict:
    """Load the per‑date status map."""
    if not os.path.exists(DAILY_TASKS_FILE):
        with open(DAILY_TASKS_FILE, 'w') as f:
            json.dump({}, f)
        return {}

    with open(DAILY_TASKS_FILE, 'r') as f:
        try:
            data = json.load(f)
            return {str(k): v for k, v in data.items()}
        except json.JSONDecodeError:
            return {}


def save_daily_tasks(data: dict) -> None:
    """Persist the per‑date status map."""
    with open(DAILY_TASKS_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def load_todo_items() -> list:
    """Return the list of To‑Do items, creating the file if it does not exist."""
    if not os.path.exists(TODO_LIST_FILE):
        with open(TODO_LIST_FILE, 'w') as f:
            json.dump([], f)
        return []

    with open(TODO_LIST_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_todo_items(items: list) -> None:
    """Persist the To‑Do items list."""
    with open(TODO_LIST_FILE, 'w') as f:
        json.dump(items, f, indent=4)


# ----------------------------------------------------------------------
# Calendar navigation helpers
# ----------------------------------------------------------------------
def get_previous_month(year: int, month: int) -> tuple[int, int]:
    """Return (prev_year, prev_month)."""
    return (year - 1, 12) if month == 1 else (year, month - 1)


def get_next_month(year: int, month: int) -> tuple[int, int]:
    """Return (next_year, next_month)."""
    return (year + 1, 1) if month == 12 else (year, month + 1)


# ----------------------------------------------------------------------
# Monthly view generator
# ----------------------------------------------------------------------
def generate_month_view(year: int, month: int):
    """Return a list of day info dicts for the month."""
    first_day = datetime.date(year, month, 1)
    if month == 12:
        last_day = datetime.date(year, month, 31)
    else:
        last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    num_days = last_day.day

    data = load_daily_tasks()
    task_names = load_task_names()
    days = []

    for day in range(1, num_days + 1):
        date_obj = datetime.date(year, month, day)
        date_str = date_obj.isoformat()

        if date_str not in data:
            data[date_str] = {task: False for task in task_names}
        else:
            # Ensure any newly added task names are present
            for task in task_names:
                if task not in data[date_str]:
                    data[date_str][task] = False

        days.append({
            'date': date_str,
            'day': day,
            'weekday': date_obj.strftime('%a'),
            'statuses': data[date_str],
        })

    save_daily_tasks(data)
    return days


# ----------------------------------------------------------------------
# Per‑date helpers
# ----------------------------------------------------------------------
def get_daily_status(date_str: str) -> dict:
    """Return status dict for a date, ensuring all tasks exist."""
    data = load_daily_tasks()
    task_names = load_task_names()

    if date_str not in data:
        data[date_str] = {task: False for task in task_names}
        save_daily_tasks(data)
    else:
        for task in task_names:
            if task not in data[date_str]:
                data[date_str][task] = False
        save_daily_tasks(data)

    return data[date_str]


def update_daily_status(date_str: str, statuses: dict) -> None:
    """Update the status map for a date and persist."""
    data = load_daily_tasks()
    data[date_str] = statuses
    save_daily_tasks(data)


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.route('/monthly')
def monthly():
    """Render the monthly overview."""
    today = datetime.date.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))

    days = generate_month_view(year, month)

    prev_year, prev_month = get_previous_month(year, month)
    next_year, next_month = get_next_month(year, month)

    task_names = load_task_names()

    return render_template(
        'monthly.html',
        year=year,
        month=month,
        month_name=datetime.date(year, month, 1).strftime('%B'),
        days=days,
        tasks=task_names,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
    )


@app.route('/daily', methods=['GET', 'POST'])
def daily():
    """Render and handle the daily overview."""
    date_str = request.args.get('date')
    if not date_str:
        date_str = datetime.date.today().isoformat()

    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return redirect(url_for('monthly'))

    if request.method == 'POST':
        task_names = load_task_names()
        statuses = {task: f'task_{i}' in request.form for i, task in enumerate(task_names)}
        update_daily_status(date_str, statuses)
        return redirect(url_for('daily', date=date_str))

    day_statuses = get_daily_status(date_str)
    task_names = load_task_names()
    return render_template(
        'daily.html',
        date=date_str,
        tasks=task_names,
        statuses=day_statuses,
    )


@app.route('/add_task', methods=['POST'])
def add_task():
    """Handle addition of a new daily task via the monthly view."""
    name = request.form.get('name', '').strip()
    pos = request.form.get('position', '').strip()

    if not name:
        return redirect(url_for('monthly'))

    try:
        pos_int = int(pos)
    except (ValueError, TypeError):
        pos_int = None

    task_names = load_task_names()

    if pos_int is None or pos_int < 1 or pos_int > len(task_names) + 1:
        pos_int = len(task_names) + 1

    task_names.insert(pos_int - 1, name)
    save_task_names(task_names)

    # Add the new task to all existing dates
    data = load_daily_tasks()
    for date_str, statuses in data.items():
        if name not in statuses:
            statuses[name] = False
    save_daily_tasks(data)

    return redirect(url_for('monthly'))


@app.route('/todolist', methods=['GET', 'POST'])
def todo():
    """Render the To‑Do list page and handle add/complete actions."""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name', '').strip()
            if name:
                new_item = {
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'completed': False,
                    'timestamp': None,
                }
                items = load_todo_items()
                items.append(new_item)
                save_todo_items(items)
            return redirect(url_for('todo'))

        if action == 'complete':
            item_id = request.form.get('item_id')
            if item_id:
                items = load_todo_items()
                for itm in items:
                    if itm['id'] == item_id:
                        itm['completed'] = True
                        itm['timestamp'] = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
                        break
                save_todo_items(items)
            return redirect(url_for('todo'))

    items = load_todo_items()
    pending = [i for i in items if not i.get('completed')]
    completed = [i for i in items if i.get('completed')]
    return render_template('todolist.html', pending=pending, completed=completed)

