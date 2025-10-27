from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.class_model import ClassModel
from models.subject_model import SubjectModel
from models.db import get_db

subjects_bp = Blueprint('subjects', __name__, url_prefix='/subjects')

# ============================================================
# CLASS MANAGEMENT
# ============================================================
@subjects_bp.route('/classes')
def class_list():
    classes = ClassModel.get_all()
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username FROM users WHERE role='teacher'")
    teachers = cursor.fetchall()
    cursor.close()
    return render_template('subjects/class_list.html', classes=classes, teachers=teachers)


@subjects_bp.route('/classes/add', methods=['POST'])
def add_class():
    name = request.form.get('name')
    year = request.form.get('year')
    teacher_id = request.form.get('id') or None

    if not name or not year:
        flash('Please fill all required fields!', 'danger')
        return redirect(url_for('subjects.class_list'))

    ClassModel.add(name, year, teacher_id)
    flash('✅ Class added successfully!', 'success')
    return redirect(url_for('subjects.class_list'))


@subjects_bp.route('/classes/delete/<int:id>')
def delete_class(id):
    ClassModel.delete(id)
    flash('🗑️ Class deleted successfully!', 'success')
    return redirect(url_for('subjects.class_list'))


# ============================================================
# SUBJECT MANAGEMENT
# ============================================================
@subjects_bp.route('/')
def subject_list():
    subjects = SubjectModel.get_all()
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM classes")
    classes = cursor.fetchall()
    cursor.execute("SELECT id, username FROM users WHERE role='teacher'")
    teachers = cursor.fetchall()
    cursor.close()
    return render_template('subjects/subject_list.html', subjects=subjects, classes=classes, teachers=teachers)


@subjects_bp.route('/add', methods=['POST'])
def add_subject():
    name = request.form.get('name')
    class_id = request.form.get('class_id')

    if not name or not class_id:
        flash('Please fill all fields', 'danger')
        return redirect(url_for('subjects.subject_list'))

    SubjectModel.add(name, class_id)
    flash('📚 Subject added successfully!', 'success')
    return redirect(url_for('subjects.subject_list'))


@subjects_bp.route('/assign', methods=['POST'])
def assign_teacher():
    subject_id = request.form.get('subject_id')
    teacher_id = request.form.get('id')

    if not subject_id or not teacher_id:
        flash('Please select both subject and teacher', 'danger')
        return redirect(url_for('subjects.subject_list'))

    SubjectModel.assign_teacher(subject_id, teacher_id)
    flash('👩‍🏫 Teacher assigned successfully!', 'success')
    return redirect(url_for('subjects.subject_list'))


@subjects_bp.route('/assign_page')
def assign_page():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch subjects with class & teacher info
    cursor.execute("""
        SELECT s.id, s.name AS subject_name, c.name AS class_name, u.username AS teacher_name
        FROM subjects s
        LEFT JOIN classes c ON s.class_id = c.id
        LEFT JOIN users u ON s.id = u.id
    """)
    subjects = cursor.fetchall()

    # Fetch all teachers
    cursor.execute("SELECT id, username FROM users WHERE role = 'teacher'")
    teachers = cursor.fetchall()

    cursor.close()
    return render_template('subjects/assign_subject.html', subjects=subjects, teachers=teachers)
