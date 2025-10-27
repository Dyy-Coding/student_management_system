# models/student_model.py
from models.db import get_db

class StudentModel:
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.id, s.name, s.gender, s.dob, s.address, c.name AS class_name
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.id
        """)
        students = cursor.fetchall()
        cursor.close()
        return students

    @staticmethod
    def get_by_id(student_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        cursor.close()
        return student

    @staticmethod
    def add(name, gender, dob, address, class_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO students (name, gender, dob, address, class_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, gender, dob, address, class_id))
        db.commit()
        cursor.close()

    @staticmethod
    def update(student_id, name, gender, date_of_birth, address, class_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE students
            SET name = %s, gender = %s, dob = %s, address = %s, class_id = %s
            WHERE id = %s
        """, (name, gender, date_of_birth, address, class_id, student_id))
        db.commit()
        cursor.close()

    @staticmethod
    def delete(student_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        db.commit()
        cursor.close()
