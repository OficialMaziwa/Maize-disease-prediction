from flask import Flask, session, request
from flask_mail import Mail
import os

from app.language_manager import lang_manager

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(24))
app.config["UPLOAD_FOLDER"] = "uploads/"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USE_SSL"] = os.environ.get("MAIL_USE_SSL", "False").lower() == "true"
app.config["MAIL_USERNAME"] = os.environ.get(
    "MAIL_USERNAME", "malabamalaba26@gmail.com"
)
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
    "MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"]
)

mail = Mail(app)
print("Mail initialized successfully")

@app.before_request
def set_language():
    lang_param = request.args.get("lang")
    if lang_param in ["en", "sw"]:
        session["language"] = lang_param
    elif "language" not in session:
        session["language"] = "en"

@app.context_processor
def utility_processor():
    def t(key, language=None):
        if language is None:
            language = session.get("language", "en")
        return lang_manager.get_text(key, language)
    
    current_language = session.get("language", "en")
    return dict(t=t, lang=current_language, current_lang=current_language)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

os.makedirs("static/profile_photos", exist_ok=True)
os.makedirs("static/covers", exist_ok=True)

from app.routes.main import main

import app.routes.main as main_module

main_module.mail = mail
main_module.MAIL_AVAILABLE = True

app.register_blueprint(main)


@app.route("/health")
def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "message": "Maize Disease Detection System is running"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    host = "0.0.0.0"

    print("=" * 50)
    print("MAIZE DISEASE DETECTION SYSTEM")
    print("=" * 50)
    print("Server starting...")
    print(f"Access: http://127.0.0.1:{port}")
    print("=" * 50)
    app.run(debug=debug, host=host, port=port)
