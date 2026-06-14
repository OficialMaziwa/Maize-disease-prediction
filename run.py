from flask import Flask
from flask_mail import Mail
import os

# Create Flask app
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Basic configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(24))
app.config["UPLOAD_FOLDER"] = "uploads/"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# ============ EMAIL CONFIGURATION ============
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

# Initialize mail
mail = Mail(app)
print("✅ Mail initialized successfully")

# Create uploads folder
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Create static subfolders
os.makedirs("static/profile_photos", exist_ok=True)
os.makedirs("static/covers", exist_ok=True)

# Import and register blueprint
from app.routes.main import main

# Make mail available to main blueprint
import app.routes.main as main_module

main_module.mail = mail
main_module.MAIL_AVAILABLE = True

app.register_blueprint(main)


# ============ HEALTH CHECK ENDPOINT ============
@app.route("/health")
def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "message": "Maize Disease Detection System is running"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    host = "0.0.0.0"

    print("=" * 50)
    print("🌽 MAIZE DISEASE DETECTION SYSTEM")
    print("=" * 50)
    print("🚀 Server starting...")
    print(f"📱 Access: http://0.0.0.0:{port}")
    print("=" * 50)
    app.run(debug=debug, host=host, port=port)
