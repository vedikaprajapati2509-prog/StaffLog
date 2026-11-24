"""
StaffLog Database Initializer Script
Run once in VS Code terminal (`python setup_db.py`) to create the MySQL
database, tables, attendance timing defaults (09:30 AM), and demo accounts.
"""

from datetime import date, datetime, timedelta
import os
from werkzeug.security import generate_password_hash
from config import Config
from database.db import get_db_connection


def split_sql_statements(sql_text):
    """Split a .sql file into individual statements safely."""
    statements = []
    current = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(current).rstrip(";").strip())
            current = []
    if current:
        statements.append("\n".join(current).strip())
    return [stmt for stmt in statements if stmt]


def setup_database():
    schema_path = os.path.join(os.path.dirname(__file__), "database", "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as file:
        schema_sql = file.read()

    # Step 1: Create database and tables
    conn = get_db_connection(use_database=False)
    cursor = conn.cursor()
    try:
        for stmt in split_sql_statements(schema_sql):
            cursor.execute(stmt)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    # Step 2: Seed departments, attendance timing, users, and sample records
    conn = get_db_connection(use_database=True)
    cursor = conn.cursor(dictionary=True)
    try:
        departments = ["Human Resources", "Engineering", "Operations", "Design"]
        for dept_name in departments:
            cursor.execute(
                "INSERT IGNORE INTO departments (name) VALUES (%s)",
                (dept_name,),
            )

        cursor.execute("SELECT id, name FROM departments")
        dept_map = {row["name"]: row["id"] for row in cursor.fetchall()}

        # Ensure default attendance timing (09:30 AM from config.py) exists
        cursor.execute("SELECT COUNT(*) AS cnt FROM attendance_settings")
        if cursor.fetchone()["cnt"] == 0:
            cursor.execute(
                """
                INSERT INTO attendance_settings (shift_start_time, late_cutoff_time)
                VALUES (%s, %s)
                """,
                (Config.DEFAULT_SHIFT_START_TIME, Config.DEFAULT_LATE_CUTOFF_TIME),
            )

        demo_password_hash = generate_password_hash("Password@123")

        # Insert HR Admin & Team Managers first so manager_id FK can reference them
        leadership = [
            ("EMP001", "Meera Nair", "hr@stafflog.local", "hr_admin", dept_map["Human Resources"], None, "HR Administrator"),
            ("EMP002", "Vikram Rao", "manager.eng@stafflog.local", "manager", dept_map["Engineering"], None, "Engineering Team Manager"),
            ("EMP003", "Ananya Deshmukh", "manager.ops@stafflog.local", "manager", dept_map["Operations"], None, "Operations Team Manager"),
        ]
        for code, name, email, role, dept_id, mgr_id, title in leadership:
            cursor.execute(
                """
                INSERT IGNORE INTO users
                    (employee_code, full_name, email, password_hash, role, department_id, manager_id, job_title)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (code, name, email, demo_password_hash, role, dept_id, mgr_id, title),
            )

        cursor.execute("SELECT id, email FROM users")
        user_map = {row["email"]: row["id"] for row in cursor.fetchall()}

        employees = [
            ("EMP004", "Aarav Sharma", "aarav@stafflog.local", "employee", dept_map["Engineering"], user_map["manager.eng@stafflog.local"], "Software Developer"),
            ("EMP005", "Priya Patel", "priya@stafflog.local", "employee", dept_map["Engineering"], user_map["manager.eng@stafflog.local"], "QA Engineer"),
            ("EMP006", "Kabir Verma", "kabir@stafflog.local", "employee", dept_map["Engineering"], user_map["manager.eng@stafflog.local"], "Backend Developer"),
            ("EMP007", "Rohan Kulkarni", "rohan@stafflog.local", "employee", dept_map["Operations"], user_map["manager.ops@stafflog.local"], "Operations Analyst"),
            ("EMP008", "Sneha Iyer", "sneha@stafflog.local", "employee", dept_map["Design"], user_map["manager.eng@stafflog.local"], "UI/UX Designer"),
        ]
        for code, name, email, role, dept_id, mgr_id, title in employees:
            cursor.execute(
                """
                INSERT IGNORE INTO users
                    (employee_code, full_name, email, password_hash, role, department_id, manager_id, job_title)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (code, name, email, demo_password_hash, role, dept_id, mgr_id, title),
            )

        cursor.execute("SELECT id, email FROM users")
        user_map = {row["email"]: row["id"] for row in cursor.fetchall()}

        # Seed realistic attendance logs for the past 10 weekdays
        today = date.today()
        cursor.execute("SELECT COUNT(*) AS cnt FROM attendance")
        if cursor.fetchone()["cnt"] == 0:
            sample_emails = [
                "hr@stafflog.local",
                "manager.eng@stafflog.local",
                "manager.ops@stafflog.local",
                "aarav@stafflog.local",
                "priya@stafflog.local",
                "rohan@stafflog.local",
            ]
            for offset in range(1, 12):
                log_day = today - timedelta(days=offset)
                if log_day.weekday() >= 5:  # Skip Saturday/Sunday
                    continue
                for idx, email in enumerate(sample_emails):
                    uid = user_map.get(email)
                    if not uid:
                        continue
                    # Alternate between On Time (09:15 / 09:30) and occasional Late (09:42)
                    if (offset + idx) % 5 == 0:
                        in_dt = datetime.combine(log_day, datetime.strptime("09:44", "%H:%M").time())
                        status = "late"
                    elif (offset + idx) % 4 == 0:
                        in_dt = datetime.combine(log_day, datetime.strptime("09:30", "%H:%M").time())
                        status = "present"
                    else:
                        in_dt = datetime.combine(log_day, datetime.strptime("09:15", "%H:%M").time())
                        status = "present"
                    out_dt = datetime.combine(log_day, datetime.strptime("18:05", "%H:%M").time())
                    hours = round((out_dt - in_dt).total_seconds() / 3600.0, 2)
                    cursor.execute(
                        """
                        INSERT IGNORE INTO attendance
                            (user_id, attendance_date, check_in_time, check_out_time, work_hours, status, cutoff_applied)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (uid, log_day, in_dt, out_dt, hours, status, Config.DEFAULT_LATE_CUTOFF_TIME),
                    )

        # Seed sample leave requests if empty
        cursor.execute("SELECT COUNT(*) AS cnt FROM leave_requests")
        if cursor.fetchone()["cnt"] == 0:
            aarav_id = user_map.get("aarav@stafflog.local")
            priya_id = user_map.get("priya@stafflog.local")
            kabir_id = user_map.get("kabir@stafflog.local")
            mgr_eng_id = user_map.get("manager.eng@stafflog.local")

            if aarav_id:
                cursor.execute(
                    """
                    INSERT INTO leave_requests (user_id, leave_type, start_date, end_date, reason, status)
                    VALUES (%s, 'casual', %s, %s, %s, 'pending')
                    """,
                    (
                        aarav_id,
                        today + timedelta(days=3),
                        today + timedelta(days=4),
                        "Family travel out of town",
                    ),
                )
            if priya_id and mgr_eng_id:
                cursor.execute(
                    """
                    INSERT INTO leave_requests
                        (user_id, leave_type, start_date, end_date, reason, status, reviewed_by, review_comment, reviewed_at)
                    VALUES (%s, 'sick', %s, %s, %s, 'approved', %s, %s, %s)
                    """,
                    (
                        priya_id,
                        today - timedelta(days=3),
                        today - timedelta(days=3),
                        "Seasonal fever and doctor appointment",
                        mgr_eng_id,
                        "Approved. Take rest and recover well.",
                        datetime.now(),
                    ),
                )
            if kabir_id:
                cursor.execute(
                    """
                    INSERT INTO leave_requests (user_id, leave_type, start_date, end_date, reason, status)
                    VALUES (%s, 'earned', %s, %s, %s, 'pending')
                    """,
                    (
                        kabir_id,
                        today + timedelta(days=6),
                        today + timedelta(days=7),
                        "Personal errands and bank work",
                    ),
                )

        conn.commit()
        print("StaffLog MySQL database initialized and seeded successfully!")
        print("Default demo password for all accounts: Password@123")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    setup_database()
