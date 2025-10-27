# ===============================================================
# FILE: routes/auth.py
# DESCRIPTION: Authentication & User Management Routes
# ===============================================================
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.users_model import UserModel
from functools import wraps
from models.db import get_db
from werkzeug.security import check_password_hash

# Blueprint setup
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ---------------- Middleware: Require login ----------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# ---------------- Middleware: Require admin ----------------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("You do not have permission to access this page.", "danger")
            # ✅ Fix redirect endpoint
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


# ---------------- Login ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login with hashing for users, plain text for admin"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Please enter both username and password", "warning")
            return render_template('login.html')

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # ✅ Check login by role
            if user['role'] == 'admin':
                # Admin uses plain-text password
                if user['password_hash'] == password:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    flash(f"Welcome Admin, {user['username']}!", "success")
                    return redirect(url_for('dashboard.index'))
                else:
                    flash("Invalid admin password", "danger")

            else:
                # Teachers/Students use hashed passwords
                if check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    flash(f"Welcome back, {user['username']}!", "success")
                    return redirect(url_for('dashboard.index'))
                else:
                    flash("Invalid username or password", "danger")

        else:
            flash("User not found", "danger")

    return render_template('login.html')

# ---------------- Logout ----------------
@auth_bp.route('/logout')
def logout():
    """Logs the user out"""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))


# ---------------- View Profile ----------------
@auth_bp.route('/profile')
@login_required
def view_profile():
    """Display current user profile"""
    user = UserModel.get_user_by_id(session['user_id'])
    return render_template('profile.html', user=user)


# ---------------- Update User ----------------
@auth_bp.route('/update/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_user(user_id):
    """Admin can update user info"""
    user = UserModel.get_user_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.manage_users'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('password')

        # Update user info
        UserModel.update_user(
            user_id,
            username=username,
            email=email,
            role=role,
            password=password if password else None
        )

        flash("✅ User updated successfully!", "success")
        return redirect(url_for('auth.manage_users'))

    return render_template('update_user.html', user=user)


# ---------------- Create User (Admin Only) ----------------
@auth_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Admin can create a new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'teacher')

        existing_user = UserModel.get_user_by_username(username)
        if existing_user:
            flash("⚠️ Username already exists. Choose another.", "warning")
        else:
            UserModel.create_user(username=username, email=email, password=password, role=role)
            flash("✅ User created successfully!", "success")
            return redirect(url_for('auth.manage_users'))

    return render_template('create_user.html')


# ---------------- Delete User (Admin Only) ----------------
@auth_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Admin can delete a user"""
    user = UserModel.get_user_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.manage_users'))

    UserModel.delete_user(user_id)
    flash("🗑️ User deleted successfully!", "info")
    return redirect(url_for('auth.manage_users'))


# ---------------- Manage Users (Admin Only) ----------------
@auth_bp.route('/manage')
@login_required
@admin_required
def manage_users():
    """Admin view to manage all users"""
    users = UserModel.get_all_users(exclude_admin=False)
    return render_template('manage_users.html', users=users)
