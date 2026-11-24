# StaffLog – Simplifying Employee Management Through Smart Attendance

A modular, beginner-friendly Employee Attendance Management System built with **HTML5, CSS3, Vanilla JavaScript, Python Flask, and MySQL**.

## Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python Flask (Blueprints, Session Auth, Role-Based Access Control)
- **Database:** MySQL (`mysql-connector-python`)

## User Roles
1. **Employee** – Daily check-in/check-out, personal attendance calendar, leave requests, monthly summary.
2. **Team Manager** – Personal attendance + Manager Dashboard, team absent employee list, leave approval/rejection, team monthly reports & CSV export.
3. **HR Administrator** – Organization-wide dashboard, employee & role management, full absent list, leave management, company-wide monthly reports & CSV export, and attendance cutoff time settings.

## Default Attendance Timing
- **Default Shift Start Time:** `09:30 AM`
- **Default Late Cutoff Time:** `09:30 AM`
  - Check-in **before or at** `09:30 AM` -> **On Time** (`present`)
  - Check-in **after** `09:30 AM` -> **Late** (`late`)
- Stored in `config.py` and persisted in MySQL `attendance_settings`. HR Administrators can update the cutoff time from the **Employees & Settings** page, and updates apply automatically to future check-ins.

## Running Locally in VS Code

### 1. Prerequisites
- Python 3.10+
- MySQL Server (MySQL 8.0+ or XAMPP/MariaDB)

### 2. Configure Environment
Copy `.env.example` to `.env` and update your MySQL credentials:
```bash
cp .env.example .env
```

### 3. Install Python Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Initialize MySQL Database
Run the automated setup script (creates `stafflog_db`, tables, and sample users with secure password hashes):
```bash
python setup_db.py
```
*(Or manually import `database/schema.sql` and `database/seed.sql` into MySQL Workbench / phpMyAdmin.)*

### 5. Start the Flask Server
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

## Demo Login Accounts
All seeded demo accounts use the password **`Password@123`**:
- **HR Administrator:** `hr@stafflog.local`
- **Team Manager (Engineering):** `manager.eng@stafflog.local`
- **Team Manager (Operations):** `manager.ops@stafflog.local`
- **Employee (Engineering):** `aarav@stafflog.local`
- **Employee (Engineering):** `priya@stafflog.local`
- **Employee (Operations):** `rohan@stafflog.local`
