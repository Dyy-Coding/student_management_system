from models.db import get_db

class TeacherModel:
    """Model for managing teacher-related operations."""

    @staticmethod
    def get_all_teachers():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id, u.username, u.email, t.specialization, u.status
            FROM teachers t
            JOIN users u ON t.user_id = u.id
            ORDER BY u.username ASC
        """)
        data = cursor.fetchall()
        cursor.close()
        return data

    @staticmethod
    def add_teacher(username, email, password_hash, department):
        db = get_db()
        cursor = db.cursor()

        # Insert into users table
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role)
            VALUES (%s, %s, %s, 'teacher')
        """, (username, email, password_hash))
        user_id = cursor.lastrowid

        # Insert into teachers table
        cursor.execute("""
            INSERT INTO teachers (user_id, specialization)
            VALUES (%s, %s)
        """, (user_id, department))

        db.commit()
        cursor.close()

    @staticmethod
    def delete_teacher(teacher_id):
        db = get_db()
        cursor = db.cursor()

        # Delete teacher record
        cursor.execute("DELETE FROM teachers WHERE user_id = %s", (teacher_id,))
        # Delete corresponding user record
        cursor.execute("DELETE FROM users WHERE id = %s", (teacher_id,))

        db.commit()
        cursor.close()

    @staticmethod
    def get_teacher_by_id(teacher_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id, u.username, u.email, t.specialization
            FROM teachers t
            JOIN users u ON t.user_id = u.id
            WHERE u.id = %s
        """, (teacher_id,))
        data = cursor.fetchone()
        cursor.close()
        return data

    @staticmethod
    def update_teacher(teacher_id, username, email, department):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE users u
            JOIN teachers t ON u.id = t.user_id
            SET u.username = %s, u.email = %s, t.specialization = %s
            WHERE u.id = %s
        """, (username, email, department, teacher_id))
        db.commit()
        cursor.close()
