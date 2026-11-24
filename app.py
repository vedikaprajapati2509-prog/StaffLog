"""
StaffLog – Simplifying Employee Management Through Smart Attendance
Main Python Flask Application Entry Point.
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from routes.auth_routes import auth_bp
from routes.attendance_routes import attendance_bp
from routes.leave_routes import leave_bp
from routes.report_routes import report_bp
from routes.admin_routes import admin_bp


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    CORS(app, supports_credentials=True)

    # Register modular route blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(leave_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "backend": "flask-mysql"})

    # Serve HTML5 pages directly without requiring Jinja tags so the exact same
    # templates can also be previewed in Google AI Studio.
    @app.route("/")
    @app.route("/login")
    def login_page():
        return send_from_directory("templates", "login.html")

    @app.route("/dashboard")
    @app.route("/dashboard.html")
    def dashboard_page():
        return send_from_directory("templates", "dashboard.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)
