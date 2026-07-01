# app/__init__.py

from flask import Flask, session, request
import os
from flask_mail import Mail, Message


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "Malaba@2003")
    app.config["UPLOAD_FOLDER"] = "uploads/"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    # ============ EMAIL CONFIGURATION - USE ENVIRONMENT VARIABLES ============
    # Use environment variables for production (Render)
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = (
        os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
    )
    app.config["MAIL_USE_SSL"] = (
        os.environ.get("MAIL_USE_SSL", "False").lower() == "true"
    )
    app.config["MAIL_USERNAME"] = os.environ.get(
        "MAIL_USERNAME", "malabamalaba26@gmail.com"
    )
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
        "MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"]
    )

    # Initialize mail
    mail = Mail(app)
    print("✅ Mail initialized in __init__.py")

    # Create uploads folder if it doesn't exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Language middleware - set default language
    @app.before_request
    def set_language():
        # Check if language is set in URL parameter
        lang_param = request.args.get("lang")
        if lang_param and lang_param in ["en", "sw"]:
            session["language"] = lang_param
        # If not in session, set default
        elif "language" not in session:
            session["language"] = "en"

    # Register blueprints
    from app.routes.main import main as main_blueprint

    # Make mail available to the blueprint module
    import app.routes.main as main_module

    main_module.mail = mail
    main_module.MAIL_AVAILABLE = True

    app.register_blueprint(main_blueprint)

    return app
