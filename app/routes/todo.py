# app/routes/todo.py
"""Routes for the To‑Do list."""
from datetime import datetime, timedelta
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
from ..models import TodoList, TodoItem

# ---------- 1. Lists overview (create / delete) ----------
@bp.route('/todolists', methods=['GET', 'POST'])
@login_required
def todolists():
    """Show all todo lists for the current user, and handle list creation."""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            name = request.form.get('name', '').strip()
            if not name:
                flash('List name cannot be empty.', 'warning')
            else:
                new_list = TodoList(user_id=current_user.id, name=name)
                db.session.add(new_list)
                db.session.commit()
                flash(f'List "{name}" created.', 'success')
            return redirect(url_for('main.todolists'))

    todo_lists = (
        TodoList.query.filter_by(user_id=current_user.id)
        .order_by(TodoList.id)
        .all()
    )
    return render_template('todo/lists.html', todo_lists=todo_lists)

# ---------- 2. Delete‑confirmation flow ----------
# NOTE: The trailing space in the original path broke the URL; it is now corrected.
@bp.route('/todolists/delete/<int:list_id>', methods=['GET', 'POST'])
@login_required
def confirm_delete_list(list_id):
    """Confirm deletion of a todo list."""
    todo_list = (
        TodoList.query.filter_by(id=list_id, user_id=current_user.id)
        .first_or_404()
    )
    if request.method == 'POST':
        db.session.delete(todo_list)
        db.session.commit()
        flash(f'List "{todo_list.name}" deleted.', 'info')
        return redirect(url_for('main.todolists'))
    return render_template('todo/confirm_delete.html', todo_list=todo_list)

# ---------- 3. Individual to‑do list (add / complete / remove) ----------
@bp.route('/todolist/<int:list_id>', methods=['GET', 'POST'])
@login_required
def todolist(list_id):
    """Render the To‑Do list for a given list_id and handle add/complete/remove actions."""
    todo_list = (
        TodoList.query.filter_by(id=list_id, user_id=current_user.id)
        .first_or_404()
    )

    if request.method == 'POST':
        action = request.form.get('action')

        # ---- Add ----
        if action == 'add':
            name = request.form.get('name', '').strip()
            if not name:
                flash('Item name cannot be empty.', 'warning')
                return redirect(url_for('main.todolist', list_id=list_id))

            due_checkbox = request.form.get('due_checkbox')
            raw_due = request.form.get('due_date')
            due_date = None
            if due_checkbox == 'on' and raw_due:
                try:
                    due_date = datetime.strptime(raw_due, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('Invalid due date format.', 'warning')
                    return redirect(url_for('main.todolist', list_id=list_id))

            new_item = TodoItem(
                user_id=current_user.id,
                todo_list_id=list_id,
                name=name,
                completed=False,
                due_date=due_date,
            )
            db.session.add(new_item)
            db.session.commit()
            flash('Item added.', 'success')
            return redirect(url_for('main.todolist', list_id=list_id))

        # ---- Complete ----
        if action == 'complete':
            item_id = request.form.get('item_id')
            if item_id:
                item = TodoItem.query.get(item_id)
                if (
                    item
                    and item.user_id == current_user.id
                    and item.todo_list_id == list_id
                ):
                    item.completed = True
                    item.timestamp = datetime.utcnow()
                    db.session.commit()
                    flash('Item marked completed.', 'success')
            return redirect(url_for('main.todolist', list_id=list_id))

        # ---- Remove ----
        if action == 'remove':
            item_id = request.form.get('item_id')
            if item_id:
                item = TodoItem.query.get(item_id)
                if (
                    item
                    and item.user_id == current_user.id
                    and item.todo_list_id == list_id
                ):
                    db.session.delete(item)
                    db.session.commit()
                    flash('Item removed.', 'info')
            return redirect(url_for('main.todolist', list_id=list_id))

    # ---- GET ----
    items = (
        TodoItem.query.filter_by(user_id=current_user.id, todo_list_id=list_id)
        .order_by(TodoItem.timestamp.asc())
        .all()
    )
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
        'todo/todolist.html',
        todo_list=todo_list,
        pending=pending,
        scheduled=scheduled,
        completed=completed,
    )
