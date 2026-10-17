"""
SQLite Database Layer for Student Performance Prediction System
Handles table initialization, CRUD operations, searching, filtering, and dashboard aggregations.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "student_performance.db")

@contextmanager
def get_db_connection():
    """Yields a SQLite connection with row factory enabled and ensures clean closure."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initializes the database schema and seeds demo data if empty."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                student_id TEXT NOT NULL,
                attendance REAL NOT NULL,
                internal_marks REAL NOT NULL,
                assignment_marks REAL NOT NULL,
                previous_marks REAL NOT NULL,
                study_hours REAL NOT NULL,
                activity_score REAL NOT NULL,
                predicted_marks REAL NOT NULL,
                performance_category TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    
    seed_sample_students_if_empty()

def insert_student(data: dict) -> int:
    """Inserts a new student prediction record and returns its generated ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (
                student_name,
                student_id,
                attendance,
                internal_marks,
                assignment_marks,
                previous_marks,
                study_hours,
                activity_score,
                predicted_marks,
                performance_category,
                risk_level,
                recommendation,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(data["student_name"]).strip(),
            str(data["student_id"]).strip().upper(),
            float(data["attendance"]),
            float(data["internal_marks"]),
            float(data["assignment_marks"]),
            float(data["previous_marks"]),
            float(data["study_hours"]),
            float(data["activity_score"]),
            float(data["predicted_marks"]),
            str(data["performance_category"]),
            str(data["risk_level"]),
            str(data["recommendation"]),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return cursor.lastrowid

def get_all_students(search: str = None, category: str = None) -> list:
    """Retrieves student records with optional search and category filters."""
    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if search:
        search_pattern = f"%{search.strip()}%"
        query += " AND (student_name LIKE ? OR student_id LIKE ?)"
        params.extend([search_pattern, search_pattern])

    if category and category.lower() != "all":
        query += " AND performance_category = ?"
        params.append(category.strip())

    query += " ORDER BY id DESC"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_student_by_id(student_pk: int):
    """Retrieves a single student record by primary key."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_pk,))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_student_by_id(student_pk: int) -> bool:
    """Deletes a student record by primary key."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_pk,))
        conn.commit()
        return cursor.rowcount > 0

def get_dashboard_stats() -> dict:
    """Computes high-level aggregated performance metrics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total students & Averages
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_count,
                AVG(predicted_marks) AS avg_predicted,
                AVG(attendance) AS avg_att,
                AVG(study_hours) AS avg_study
            FROM students
        """)
        summary = cursor.fetchone()
        
        total_students = summary["total_count"] or 0
        avg_predicted = round(summary["avg_predicted"] or 0.0, 2)
        avg_attendance = round(summary["avg_att"] or 0.0, 2)
        avg_study_hours = round(summary["avg_study"] or 0.0, 2)

        # Performance Categories count
        cursor.execute("""
            SELECT performance_category, COUNT(*) AS count
            FROM students
            GROUP BY performance_category
        """)
        cat_rows = cursor.fetchall()
        cat_map = {row["performance_category"]: row["count"] for row in cat_rows}

        count_excellent = cat_map.get("Excellent", 0)
        count_good = cat_map.get("Good", 0)
        count_average = cat_map.get("Average", 0)
        count_at_risk = cat_map.get("At Risk", 0)

        # Recent 5 students
        cursor.execute("SELECT * FROM students ORDER BY id DESC LIMIT 5")
        recent_records = [dict(r) for r in cursor.fetchall()]

        return {
            "total_students": total_students,
            "avg_predicted_marks": avg_predicted,
            "avg_attendance": avg_attendance,
            "avg_study_hours": avg_study_hours,
            "count_excellent": count_excellent,
            "count_good": count_good,
            "count_average": count_average,
            "count_at_risk": count_at_risk,
            "recent_students": recent_records
        }

def get_chart_data() -> dict:
    """Returns formatted data series for Chart.js rendering."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Category Distribution
        cursor.execute("""
            SELECT performance_category, COUNT(*) as count 
            FROM students 
            GROUP BY performance_category
        """)
        cats = {r["performance_category"]: r["count"] for r in cursor.fetchall()}
        category_distribution = {
            "labels": ["Excellent (75-100)", "Good (60-74)", "Average (50-59)", "At Risk (<50)"],
            "data": [
                cats.get("Excellent", 0),
                cats.get("Good", 0),
                cats.get("Average", 0),
                cats.get("At Risk", 0)
            ],
            "colors": ["#198754", "#0dcaf0", "#ffc107", "#dc3545"]
        }

        # 2. Scatter / Point Data: Attendance vs Predicted Marks
        cursor.execute("""
            SELECT student_name, attendance, predicted_marks, performance_category 
            FROM students 
            ORDER BY id DESC LIMIT 50
        """)
        att_scatter = [
            {
                "x": round(r["attendance"], 1),
                "y": round(r["predicted_marks"], 1),
                "label": r["student_name"],
                "category": r["performance_category"]
            }
            for r in cursor.fetchall()
        ]

        # 3. Internal Marks vs Predicted Marks
        cursor.execute("""
            SELECT student_name, internal_marks, predicted_marks, performance_category 
            FROM students 
            ORDER BY id DESC LIMIT 50
        """)
        internal_scatter = [
            {
                "x": round(r["internal_marks"], 1),
                "y": round(r["predicted_marks"], 1),
                "label": r["student_name"],
                "category": r["performance_category"]
            }
            for r in cursor.fetchall()
        ]

        # 4. Score Ranges Distribution Histogram
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN predicted_marks < 50 THEN 1 ELSE 0 END) as range_under_50,
                SUM(CASE WHEN predicted_marks >= 50 AND predicted_marks < 60 THEN 1 ELSE 0 END) as range_50_59,
                SUM(CASE WHEN predicted_marks >= 60 AND predicted_marks < 75 THEN 1 ELSE 0 END) as range_60_74,
                SUM(CASE WHEN predicted_marks >= 75 AND predicted_marks < 85 THEN 1 ELSE 0 END) as range_75_84,
                SUM(CASE WHEN predicted_marks >= 85 THEN 1 ELSE 0 END) as range_85_100
            FROM students
        """)
        score_bins = cursor.fetchone()
        score_ranges = {
            "labels": ["< 50 (Fail/Risk)", "50 - 59 (Pass/Avg)", "60 - 74 (First Class)", "75 - 84 (Distinction)", "85 - 100 (Exemplary)"],
            "data": [
                score_bins["range_under_50"] or 0,
                score_bins["range_50_59"] or 0,
                score_bins["range_60_74"] or 0,
                score_bins["range_75_84"] or 0,
                score_bins["range_85_100"] or 0
            ]
        }

        return {
            "category_distribution": category_distribution,
            "attendance_vs_marks": att_scatter,
            "internal_vs_marks": internal_scatter,
            "score_ranges": score_ranges
        }

def seed_sample_students_if_empty():
    """Populates the database with initial realistic student records if table is empty."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_students = [
                ("Aarav Sharma", "AI2026-001", 92.5, 84.0, 88.0, 85.0, 5.5, 90.0, 86.8, "Excellent", "Low Risk", "Excellent performance. Continue maintaining your current academic habits.", "2026-08-20 10:15:00"),
                ("Priya Patel", "AI2026-002", 88.0, 78.0, 82.5, 80.0, 4.5, 85.0, 80.4, "Excellent", "Low Risk", "Excellent performance. Continue maintaining your current academic habits.", "2026-08-21 11:30:00"),
                ("Rohan Gupta", "AI2026-003", 78.5, 68.0, 72.0, 70.0, 3.5, 75.0, 71.2, "Good", "Low Risk", "Good performance. Focus on attendance and consistent revision.", "2026-08-22 09:45:00"),
                ("Ananya Verma", "AI2026-004", 82.0, 71.5, 76.0, 74.0, 4.0, 80.0, 74.8, "Good", "Low Risk", "Good performance. Focus on attendance and consistent revision.", "2026-08-22 14:20:00"),
                ("Vikram Singh", "AI2026-005", 65.0, 52.0, 58.0, 55.0, 2.5, 60.0, 56.5, "Average", "Medium Risk", "Your performance can be improved. Increase study hours and assignment performance. Targeted Action Steps: Raise attendance from 65.0% to at least 75% to meet institution requirements. | Increase daily self-study from 2.5 hrs to 3.5-5.0 hrs for thorough concept retention.", "2026-08-23 15:10:00"),
                ("Neha Nair", "AI2026-006", 70.0, 55.0, 54.0, 58.0, 2.8, 65.0, 58.2, "Average", "Medium Risk", "Your performance can be improved. Increase study hours and assignment performance. Targeted Action Steps: Raise attendance from 70.0% to at least 75% to meet institution requirements. | Submit assignments earlier and utilize rubric guidelines (current: 54.0/100).", "2026-08-24 10:05:00"),
                ("Karan Mehta", "AI2026-007", 52.0, 42.0, 45.0, 48.0, 1.5, 40.0, 45.3, "At Risk", "High Risk", "Your performance is at risk. Improve attendance, internal marks, assignments and study consistency. Targeted Action Steps: Raise attendance from 52.0% to at least 75% to meet institution requirements. | Increase daily self-study from 1.5 hrs to 3.5-5.0 hrs for thorough concept retention. | Seek instructor clarification on internal assessment feedback (current: 42.0/100). | Submit assignments earlier and utilize rubric guidelines (current: 45.0/100).", "2026-08-25 11:50:00"),
                ("Sanya Malhotra", "AI2026-008", 96.0, 91.0, 94.0, 92.0, 6.0, 95.0, 92.6, "Excellent", "Low Risk", "Excellent performance. Continue maintaining your current academic habits.", "2026-08-26 13:15:00"),
                ("Aditya Joshi", "AI2026-009", 74.0, 62.0, 65.0, 64.0, 3.2, 70.0, 65.4, "Good", "Low Risk", "Good performance. Focus on attendance and consistent revision. Targeted Action Steps: Raise attendance from 74.0% to at least 75% to meet institution requirements.", "2026-08-27 16:40:00"),
                ("Divya Pillai", "AI2026-010", 48.0, 38.0, 40.0, 42.0, 1.0, 35.0, 41.2, "At Risk", "High Risk", "Your performance is at risk. Improve attendance, internal marks, assignments and study consistency. Targeted Action Steps: Raise attendance from 48.0% to at least 75% to meet institution requirements. | Increase daily self-study from 1.0 hrs to 3.5-5.0 hrs for thorough concept retention. | Seek instructor clarification on internal assessment feedback (current: 38.0/100). | Submit assignments earlier and utilize rubric guidelines (current: 40.0/100).", "2026-08-28 09:30:00")
            ]
            cursor.executemany("""
                INSERT INTO students (
                    student_name, student_id, attendance, internal_marks,
                    assignment_marks, previous_marks, study_hours, activity_score,
                    predicted_marks, performance_category, risk_level,
                    recommendation, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_students)
            conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized and verified successfully!")
    stats = get_dashboard_stats()
    print(f"Total students: {stats['total_students']}, Avg marks: {stats['avg_predicted_marks']}")
