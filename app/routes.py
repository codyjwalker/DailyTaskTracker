#!/usr/bin/env python3
"""
Simple Flask application for tracking daily tasks.
Author: $sudo
"""

import os
import json
import datetime
import uuid


from flask import (
    render_template,
    request,
    redirect,
    url_for,
)

# Import the Flask app that lives in app/__init__.py
# (This is the actual application object, not the proxy.)
from . import app


# ------------------------------------------------------------------
# Data‑file paths – relative to the package root
# ------------------------------------------------------------------
BASE_DIR = os.path.join(app.root_path, '..', 'data')
DATA_FILE = os.path.join(BASE_DIR, 'tasks.json')
TODO_FILE = os.path.join(BASE_DIR, 'todolist.json')

# The fixed list of tasks for each day
TASKS = [
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
      'Bed By Midnight'
]

def get_previous_month(year: int, month: int) -> tuple[int, int]:
    """Return (prev_year, prev_month)."""
    return (year - 1, 12) if month == 1 else (year, month - 1)

def get_next_month(year: int, month: int) -> tuple[int, int]:
    """Return (next_year, next_month)."""
    return (year + 1, 1) if month == 12 else (year, month + 1)

def load_data():
    """Load the tasks data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        # Create an empty file if it doesn't exist
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
        return {}
    with open(DATA_FILE, 'r') as f:
        try:
            data = json.load(f)
            # Ensure keys are strings
            return {str(k): v for k, v in data.items()}
        except json.JSONDecodeError:
            # Corrupted file, reset
            return {}

def save_data(data):
    """Save the tasks data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_date_data(date_str):
    """Get the tasks dictionary for a specific date string (YYYY-MM-DD).
    If the date does not exist, initialize with all tasks set to False.
    """
    data = load_data()
    if date_str not in data:
        # Initialize
        data[date_str] = {task: False for task in TASKS}
        save_data(data)
    return data[date_str]

def update_date_data(date_str, statuses):
    """Update the tasks statuses for a given date string.
    `statuses` is a dict mapping task names to bool.
    """
    data = load_data()
    data[date_str] = statuses
    save_data(data)

def generate_month_view(year, month):
    """Generate data for rendering the monthly overview.
    Returns a list of days with date strings, weekday, and task statuses.
    """
    # First day of month
    first_day = datetime.date(year, month, 1)
    # Last day
    if month == 12:
        last_day = datetime.date(year, month, 31)
    else:
        last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    num_days = last_day.day

    data = load_data()
    days = []
    for day in range(1, num_days + 1):
        date_obj = datetime.date(year, month, day)
        date_str = date_obj.isoformat()
        # Ensure data exists
        if date_str not in data:
            data[date_str] = {task: False for task in TASKS}
        day_info = {
            'date': date_str,
            'day': day,
            'weekday': date_obj.strftime('%a'),
            'statuses': data[date_str]
        }
        days.append(day_info)
    # Persist any new dates
    save_data(data)
    return days

def load_todo_data():
    """Return the list of todo items.  Create the file if it does not exist."""
    if not os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'w') as f:
            json.dump([], f)
        return []

    with open(TODO_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_todo_data(data):
    """Persist the todo list."""
    with open(TODO_FILE, 'w') as f:
        json.dump(data, f, indent=4)


@app.context_processor
def inject_now():
    """Provide the current year to templates for the footer."""
    return {'current_year': datetime.datetime.utcnow().year}


@app.route('/todolist', methods=['GET', 'POST'])
def todo():
    """ Render the ToDo list page and process add/complete actions """
    if request.method == 'POST':
        action = request.form.get('action')

        # ----- Add a new item ------------------------------------
        if action == 'add':
            name = request.form.get('name', '').strip()
            if name:                                       # guard against empty strings
                new_item = {
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'completed': False,
                    'timestamp': None,
                }
                todo_items = load_todo_data()
                todo_items.append(new_item)
                save_todo_data(todo_items)

            return redirect(url_for('todo'))

        # ----- Mark an item as completed --------------------------
        elif action == 'complete':
            item_id = request.form.get('item_id')
            if item_id:
                todo_items = load_todo_data()
                for itm in todo_items:
                    if itm['id'] == item_id:
                        itm['completed'] = True
                        itm['timestamp'] = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
                        break
                save_todo_data(todo_items)

            return redirect(url_for('todo'))

    # ----- GET ----------------------------------------------------
    todo_items = load_todo_data()
    pending = [i for i in todo_items if not i.get('completed')]
    completed = [i for i in todo_items if i.get('completed')]
    return render_template('todolist.html', pending=pending, completed=completed)

@app.route('/')
@app.route('/monthly')
def monthly():
    """Render the monthly view for an arbitrary month/year."""
    """If no `year`/`month` is supplied the current month is used."""

    """ Resolve the requested month & year """
    today = datetime.date.today()
    month = int(request.args.get('month', today.month))
    year  = int(request.args.get('year', today.year))

    """ Build the calendar and calculate prev/next """
    days = generate_month_view(year, month)

    prev_year, prev_month = get_previous_month(year, month)
    next_year, next_month = get_next_month(year, month)

    """ Render """
    return render_template(
        'monthly.html',
        year=year,
        month=month,
        month_name=datetime.date(year, month, 1).strftime('%B'),
        days=days,
        tasks=TASKS,
        # The four values below are used by the navigation links
        prev_year=prev_year, prev_month=prev_month,
        next_year=next_year, next_month=next_month
    )


@app.route('/daily', methods=['GET', 'POST'])
def daily():
    """Render and handle the daily overview page."""
    # Determine date: from query param or today's date
    date_str = request.args.get('date')
    if not date_str:
        date_str = datetime.date.today().isoformat()

    # Validate date format
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        # Invalid date, redirect to monthly
        return redirect(url_for('monthly'))

    if request.method == 'POST':
        # Process form submission
        statuses = {}
        for idx, task in enumerate(TASKS):
            key = f'task_{idx}'
            statuses[task] = key in request.form
        update_date_data(date_str, statuses)
        return redirect(url_for('daily', date=date_str))

    # For GET request, load data
    day_statuses = get_date_data(date_str)
    return render_template(
        'daily.html',
        date=date_str,
        tasks=TASKS,
        statuses=day_statuses
    )

if __name__ == '__main__':
    # Host 0.0.0.0 to allow access from other devices on the LAN
    app.run(host='0.0.0.0', port=5000, debug=True)
