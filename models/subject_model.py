from models.db import get_db

class SubjectModel:
    """Model for managing subjects."""

    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, c.name AS class_name, u.username AS teacher_name
            FROM subjects s
            LEFT JOIN classes c ON s.class_id = c.id
            LEFT JOIN users u ON s.id = u.id
            ORDER BY s.id DESC
        """)
        data = cursor.fetchall()
        cursor.close()
        return data

    @staticmethod
    def add(name, class_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO subjects (name, class_id)
            VALUES (%s, %s)
        """, (name, class_id))
        db.commit()
        cursor.close()

    @staticmethod
    def assign_teacher(subject_id, teacher_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE subjects SET id = %s WHERE id = %s
        """, (teacher_id, subject_id))
        db.commit()
        cursor.close()
