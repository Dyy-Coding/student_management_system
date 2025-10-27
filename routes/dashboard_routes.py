from flask import Blueprint, render_template, session, redirect, url_for
from models.db import get_db

dashboard_bp = Blueprint('dashboard', __name__)  # ✅ Fixed name

@dashboard_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_students FROM students")
    total_students = cursor.fetchone()['total_students']

    cursor.execute("SELECT COUNT(*) AS total_teachers FROM users WHERE role='teacher'")
    total_teachers = cursor.fetchone()['total_teachers']

    cursor.execute("SELECT COUNT(*) AS total_classes FROM classes")
    total_classes = cursor.fetchone()['total_classes']

    cursor.close()

    return render_template(
        'dashboard_admin.html',
        total_students=total_students,
        total_teachers=total_teachers,
        total_classes=total_classes
    )
