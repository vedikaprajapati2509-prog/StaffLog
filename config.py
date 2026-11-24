"""
StaffLog Configuration Module
Stores Flask, MySQL, and default Attendance Timing settings.
"""

import os
import secrets
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base application configuration loaded from environment variables."""

    # Flask settings
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    # MySQL database settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "stafflog")

    # Default Attendance Timing (09:30 AM)
    # Before or at 09:30 AM -> On Time (present)
    # After 09:30 AM -> Late (late)
    DEFAULT_SHIFT_START_TIME = os.getenv("SHIFT_START_TIME", "09:30")
    DEFAULT_LATE_CUTOFF_TIME = os.getenv("LATE_CUTOFF_TIME", "09:30")
