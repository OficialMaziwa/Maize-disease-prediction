# app/__init__.py

from flask import Flask, session, request
import os
from flask_mail import Mail, Message  # Import mail directly here


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = "Malaba@2003"
    app.config["UPLOAD_FOLDER"] = "uploads/"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    # ============ EMAIL CONFIGURATION - DIRECT ============
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "malabamalaba26@gmail.com"
    app.config["MAIL_PASSWORD"] = "rgzpzbpiujygwlsz"  # Badilisha kuwa App Password
    app.config["MAIL_DEFAULT_SENDER"] = "malabamalaba26@gmail.com"

    # Initialize mail
    mail = Mail(app)
    print("✅ Mail initialized directly in __init__.py")

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
    from app.routes.main import main

    # Make mail available to blueprint
    from app.routes.main import mail as main_mail

    main_mail.init_app(app)

    app.register_blueprint(main)

    return app
