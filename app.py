import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
from loan_reminder_scheduler import send_loan_reminders
import atexit

from flask import Flask, render_template, request, g, redirect, url_for
from flask_login import LoginManager, current_user

from config import Config
from models import db, User
from auth import auth_bp
from admin import admin_bp
from user import user_bp


def load_translations():
    """Load translation files from static/assets"""
    base_dir = os.path.join(os.path.dirname(__file__), "static", "assets")
    translations = {}
    for lang in ("en", "ta"):
        path = os.path.join(base_dir, f"{lang}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                translations[lang] = json.load(f)
        else:
            translations[lang] = {}
    return translations


translations_cache = load_translations()


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Set language before request
    @app.before_request
    def set_language():
        lang = request.args.get("lang") or request.cookies.get("lang") or "en"
        if lang not in app.config["LANGUAGES"]:
            lang = "en"
        g.lang = lang
        g.t = translations_cache.get(lang, {})

    # Global context processor
    @app.context_processor
    def inject_globals():
        def t(key):
            return g.t.get(key, key)

        return {
            "current_user": current_user,
            "lang": getattr(g, "lang", "en"),
            "t": t,
        }

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    # Home route
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for("admin.admin_dashboard"))
            return redirect(url_for("user.user_dashboard"))
        return redirect(url_for("auth.login"))

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    # Initialize scheduler for loan reminders
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=send_loan_reminders,
            trigger="cron",
            hour=9,      # Runs at 9 AM every day
            minute=0
        )
        scheduler.start()
        
        # Shut down scheduler when app exits
        atexit.register(lambda: scheduler.shutdown())
        print("✓ Loan reminder scheduler started successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not start scheduler: {e}")

    return app


if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        # Create instance directory
        os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)
        
        # Initialize database migration
        from flask_migrate import Migrate
        Migrate(app, db)
        
        # Create all tables
        db.create_all()
        print("✓ Database initialized")
    
    # Run Flask app
    print("🚀 Starting Women GateWay application...")
    print("📊 Dashboard: http://localhost:8000/user/dashboard")
    print("🔗 Login: http://localhost:8000/auth/login")
    app.run(debug=True, port=8000)
