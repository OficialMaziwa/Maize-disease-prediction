from flask import (
    render_template,
    request,
    Blueprint,
    jsonify,
    session,
    redirect,
    url_for,
    flash,
    current_app,
    make_response,
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2.extras import RealDictCursor
import os, base64, io, sys, uuid, re, logging, json
from PIL import Image
from datetime import datetime, timedelta
from functools import wraps
from app.user_db import user_db
from flask import send_file, abort

db = user_db
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
try:
    from app.disease_engine import MaizeDiseaseDetector
    from app.language_manager import lang_manager
    from app.db_logger import db_logger
    from app.logger_config import security_logger
except ImportError as e:
    print(f"Import error: {e}")

    class DummyLogger:
        def log_security_event(self, *args, **kwargs):
            pass

        def log_auth_event(self, *args, **kwargs):
            pass

        def log_access(self, *args, **kwargs):
            pass

        def log_error(self, *args, **kwargs):
            pass

        def log_db_operation(self, *args, **kwargs):
            pass

        def log_api_call(self, *args, **kwargs):
            pass

        def detect_attack_patterns(self, *args, **kwargs):
            return False

        def _get_client_ip(self):
            return "N/A"

        def _get_user_agent(self):
            return "N/A"

    security_logger = DummyLogger()

from services.sms_service import DebugSMSService, SMSService

main = Blueprint("main", __name__)
sms_service = DebugSMSService()

# Configuration
UPLOAD_FOLDER = "uploads/"
PROFILE_FOLDER = "static/profile_photos/"
COVER_FOLDER = "static/covers/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

detector = MaizeDiseaseDetector(model_path=None)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROFILE_FOLDER, exist_ok=True)
os.makedirs(COVER_FOLDER, exist_ok=True)

logger = logging.getLogger(__name__)


def ensure_db_connection():
    from app.user_db import user_db as db

    try:
        if db.connection is not None:
            try:
                cursor = db.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return True
            except Exception:
                db.connection = None
        if db.connection is None:
            db.connect()
            return db.connection is not None
        return True
    except Exception:
        return False


# Africa's Talking
try:
    import africastalking

    AFRICASTALKING_USERNAME = "sandbox"
    AFRICASTALKING_API_KEY = (
        "atsk_18bbc680b2d0962c8280d2d9d28acf5596bf3d67baf4b622a969239c3a475c2d13056458"
    )
    africastalking.initialize(AFRICASTALKING_USERNAME, AFRICASTALKING_API_KEY)
    sms_service_at = africastalking.SMS
    SMS_AVAILABLE = True
except:
    SMS_AVAILABLE = False


# Flask-Mail Configuration
try:
    from flask_mail import Mail, Message
    MAIL_AVAILABLE = True
except:
    MAIL_AVAILABLE = False

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = "malabamalaba26@gmail.com"
MAIL_PASSWORD = "gjgbawyjlciutgrd"  
MAIL_DEFAULT_SENDER = "malabamalaba26@gmail.com"
APP_URL = "http://localhost:5000"

mail = Mail()


def init_mail(app):
    if MAIL_AVAILABLE:
        app.config["MAIL_SERVER"] = MAIL_SERVER
        app.config["MAIL_PORT"] = MAIL_PORT
        app.config["MAIL_USE_TLS"] = MAIL_USE_TLS
        app.config["MAIL_USERNAME"] = MAIL_USERNAME
        app.config["MAIL_PASSWORD"] = MAIL_PASSWORD
        app.config["MAIL_DEFAULT_SENDER"] = MAIL_DEFAULT_SENDER
        mail.init_app(app)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Helper Functions
def sanitize_input(input_string):
    if not input_string:
        return ""
    return re.sub(r"<[^>]*>", "", input_string)


def validate_phone_number(phone):
    pattern = r"^(0[67]\d{8}|255[67]\d{8})$"
    return bool(re.match(pattern, phone))


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password_strength(password):
    if len(password) < 4:
        return False, "Password must be at least 4 characters long"
    return True, "Password is valid"


def secure_session():
    session.permanent = True
    session.permanent_session_lifetime = timedelta(hours=2)
    if not session.get("_fresh"):
        if hasattr(session, "regenerate"):
            session.regenerate()
        session["_fresh"] = True


def log_activity(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = datetime.now()
        try:
            response = f(*args, **kwargs)
        except Exception as e:
            print(f"ERROR in route {f.__name__}: {e}")
            raise
        try:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            status_code = (
                response.status_code if hasattr(response, "status_code") else 200
            )
            security_logger.log_access(status_code, duration)
        except:
            pass
        return response

    return decorated_function


def log_user_activity(
    activity_type,
    activity_details,
    status_code=200,
    response_time_ms=0,
    additional_data=None,
):
    try:
        if "user_id" not in session:
            return
        if not ensure_db_connection():
            return
        session_id = session.get("session_id") or str(uuid.uuid4())
        session["session_id"] = session_id
        additional_data_json = json.dumps(additional_data) if additional_data else None
        cursor = user_db.get_cursor(dictionary=False)
        cursor.execute(
            """
            INSERT INTO user_activity_logs 
            (user_id, user_name, user_role, activity_type, activity_details, 
             ip_address, user_agent, endpoint, method, status_code, response_time_ms, 
             session_id, additional_data, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """,
            (
                session.get("user_id"),
                session.get("user_name"),
                session.get("user_role"),
                activity_type,
                activity_details[:500] if activity_details else None,
                request.remote_addr,
                request.user_agent.string if hasattr(request, "user_agent") else None,
                request.endpoint,
                request.method,
                status_code,
                response_time_ms,
                session_id,
                additional_data_json,
            ),
        )
        user_db.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error logging: {e}")


# Notification Functions
def send_approval_sms(phone_number, officer_name, admin_name):
    """Send SMS approval notification via Africa's Talking"""
    if not SMS_AVAILABLE:
        print("⚠️ SMS service not available")
        return False

    if not phone_number:
        print("⚠️ No phone number provided")
        return False

    try:
        # Format phone number correctly
        phone = str(phone_number).strip()
        if phone.startswith("0"):
            phone = "255" + phone[1:]
        elif phone.startswith("+"):
            phone = phone[1:]
        elif not phone.startswith("255"):
            phone = "255" + phone

        print(f"📱 Sending SMS to: {phone}")

        message = f"CONGRATULATIONS! Dear {officer_name}, your account has been APPROVED by {admin_name}. Login: {APP_URL}/login"

        response = sms_service_at.send(message, [phone])
        print(f"✅ SMS sent successfully to {phone}")
        print(f"📨 SMS Response: {response}")
        return True

    except Exception as e:
        print(f"❌ SMS error: {e}")
        return False


def send_approval_email(email, officer_name, admin_name):
    """Send email approval notification via Gmail"""
    if not MAIL_AVAILABLE:
        print("⚠️ Email service not available")
        return False

    if not email:
        print("⚠️ No email address provided")
        return False

    try:
        print(f"📧 Sending email to: {email}")

        subject = "✅ Account Approved - Maize Disease Detection System"

        # HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #28a745; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🌽 Maize Disease Detection System</h2>
                </div>
                <div class="content">
                    <h3>Congratulations, {officer_name}! 🎉</h3>
                    <p>Your account has been <strong>APPROVED</strong> by <strong>{admin_name}</strong>.</p>
                    <p>You can now login to the system and start helping farmers detect maize diseases.</p>
                    <p style="text-align: center;">
                        <a href="{APP_URL}/login" class="button">🔐 Login to Your Account</a>
                    </p>
                    <p><strong>Login credentials:</strong><br>
                    Phone number: Your registered phone number<br>
                    Password: Your chosen password</p>
                    <p><em>If you have any questions, please contact the system administrator.</em></p>
                </div>
                <div class="footer">
                    <p>Maize Disease Detection System - Helping Farmers Make Better Decisions</p>
                    <p>&copy; 2024 All Rights Reserved</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text version as fallback
        text_content = f"""
        CONGRATULATIONS! Dear {officer_name},
        
        Your account has been APPROVED by {admin_name}.
        
        You can now login to the Maize Disease Detection System:
        Login URL: {APP_URL}/login
        
        Use your phone number and password to login.
        
        Maize Disease Detection System
        """

        msg = Message(subject, recipients=[email])
        msg.body = text_content
        msg.html = html_content

        mail.send(msg)
        print(f"✅ Email sent successfully to {email}")
        return True

    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


def create_in_app_notification(user_id, title, message, notification_type="SYSTEM"):
    try:
        if not ensure_db_connection():
            return False
        cursor = user_db.connection.cursor()
        cursor.execute(
            """
            INSERT INTO in_app_notifications (user_id, title, message, notification_type, created_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        """,
            (user_id, title, message, notification_type),
        )
        user_db.connection.commit()
        cursor.close()
        return True
    except:
        return False


# ==================== AUTHENTICATION ROUTES ====================
@main.route("/register", methods=["GET", "POST"])
@log_activity
def register():
    lang = session.get("language", "en")
    if request.method == "POST":
        full_name = sanitize_input(request.form.get("full_name", "").strip())
        phone_number = sanitize_input(request.form.get("phone_number", "").strip())
        email = sanitize_input(request.form.get("email", "").strip())
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = sanitize_input(request.form.get("role", "farmer"))
        location = sanitize_input(request.form.get("location", ""))
        district = sanitize_input(request.form.get("district", ""))
        region = sanitize_input(request.form.get("region", ""))

        if not full_name or not phone_number or not password:
            flash("All fields are required", "danger")
            return render_template(
                "register.html", lang=lang, t=lang_manager.get_text, request=request
            )

        if not validate_phone_number(phone_number):
            flash("Please enter a valid phone number", "danger")
            return render_template(
                "register.html", lang=lang, t=lang_manager.get_text, request=request
            )

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template(
                "register.html", lang=lang, t=lang_manager.get_text, request=request
            )

        if not ensure_db_connection():
            flash("Database connection error", "danger")
            return render_template(
                "register.html", lang=lang, t=lang_manager.get_text, request=request
            )

        cursor = user_db.get_cursor()
        cursor.execute(
            "SELECT user_id FROM maziwa WHERE phone_number = %s", (phone_number,)
        )
        if cursor.fetchone():
            cursor.close()
            flash("Phone number already registered", "danger")
            return render_template(
                "register.html", lang=lang, t=lang_manager.get_text, request=request
            )

        if email:
            cursor.execute("SELECT user_id FROM maziwa WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                flash("Email already registered", "danger")
                return render_template(
                    "register.html", lang=lang, t=lang_manager.get_text, request=request
                )

        password_hash = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=32
        )
        is_approved = FALSE if role == "extension_officer" else 1

        try:
            cursor.execute(
                """
                INSERT INTO maziwa (full_name, phone_number, email, password_hash, role, 
                                  location, district, region, is_approved, is_active, 
                                  created_at, ip_address, user_agent, password_last_changed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, CURRENT_TIMESTAMP, %s, %s, CURRENT_TIMESTAMP)
            """,
                (
                    full_name,
                    phone_number,
                    email if email else None,
                    password_hash,
                    role,
                    location if location else None,
                    district if district else None,
                    region if region else None,
                    is_approved,
                    request.remote_addr,
                    (
                        request.user_agent.string
                        if hasattr(request, "user_agent")
                        else None
                    ),
                ),
            )
            user_db.connection.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("main.login"))
        except Exception as e:
            user_db.connection.rollback()
            flash("Registration failed. Please try again.", "danger")
        finally:
            cursor.close()
    return render_template(
        "register.html", lang=lang, t=lang_manager.get_text, request=request
    )


@main.route("/login", methods=["GET", "POST"])
@log_activity
def login():
    lang = session.get("language", "en")
    secure_session()
    if request.method == "POST":
        identifier = sanitize_input(request.form.get("identifier", "").strip())
        password = request.form.get("password", "")
        if not identifier or not password:
            flash("Please enter both identifier and password", "danger")
            return render_template(
                "login.html", lang=lang, t=lang_manager.get_text, request=request
            )

        try:
            cursor = user_db.get_cursor()
            cursor.execute(
                """
                SELECT user_id, full_name, phone_number, email, password_hash, role, 
                       region, language_preference, is_active, is_approved
                FROM maziwa WHERE phone_number = %s OR email = %s
            """,
                (identifier, identifier),
            )
            user = cursor.fetchone()

            if user and check_password_hash(user["password_hash"], password):
                if user["is_active"] == 0:
                    flash("Your account is deactivated. Contact admin.", "danger")
                    cursor.close()
                    return render_template(
                        "login.html",
                        lang=lang,
                        t=lang_manager.get_text,
                        request=request,
                    )
                if user["role"] == "extension_officer" and user["is_approved"] == 0:
                    flash("Your account is pending approval by admin.", "warning")
                    cursor.close()
                    return render_template(
                        "login.html",
                        lang=lang,
                        t=lang_manager.get_text,
                        request=request,
                    )

                session.clear()
                session_id = str(uuid.uuid4())
                session["user_id"] = user["user_id"]
                session["user_name"] = user["full_name"]
                session["user_role"] = user["role"]
                session["region"] = user.get("region")
                session["language"] = user.get("language_preference", lang)
                session["session_id"] = session_id

                log_user_activity("LOGIN", f"User logged in with role: {user['role']}")
                flash("Login successful!", "success")
                cursor.close()

                role_redirects = {
                    "admin": url_for("main.admin_dashboard"),
                    "extension_officer": url_for("main.officer_dashboard"),
                    "farmer": url_for("main.index"),
                }
                return redirect(role_redirects.get(user["role"], url_for("main.index")))
            else:
                flash("Invalid credentials", "danger")
            cursor.close()
        except Exception as e:
            print(f"Login error: {e}")
            flash("An error occurred. Please try again.", "danger")
    return render_template(
        "login.html", lang=lang, t=lang_manager.get_text, request=request
    )


@main.route("/logout")
@log_activity
def logout():
    user_id = session.get("user_id")
    if user_id:
        log_user_activity("LOGOUT", "User logged out")
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("main.index"))


# ==================== HOME & MAIN ROUTES ====================
@main.route("/")
def index():
    lang = session.get("language", "en")
    return render_template(
        "index.html", 
        lang=lang, 
        t=lang_manager.get_text, 
        request=request
    )


@main.route("/home")
def home():
    return index()


@main.route("/dashboard")
def dashboard():
    lang = session.get("language", "en")
    user_role = session.get("user_role")

    if not "user_id" in session:
        flash("Please login first", "warning")
        return redirect(url_for("main.login"))

    if user_role == "admin":
        return redirect(url_for("main.admin_dashboard"))
    elif user_role == "extension_officer":
        return redirect(url_for("main.officer_dashboard"))
    else:
        return redirect(url_for("main.predict"))


@main.route("/predict", methods=["GET", "POST"])
def predict():
    lang = session.get("language", "en")
    return render_template(
        "predict.html", lang=lang, t=lang_manager.get_text, request=request
    )


@main.route("/about")
def about():
    lang = session.get("language", "en")
    return render_template(
        "about.html", lang=lang, t=lang_manager.get_text, request=request
    )


@main.route("/history")
def history():
    if "user_id" not in session:
        flash("Please login to view history", "warning")
        return redirect(url_for("main.login"))
    lang = session.get("language", "en")
    return render_template(
        "history.html", lang=lang, t=lang_manager.get_text, request=request
    )


# ==================== PROFILE ROUTES ====================
@main.route("/profile", methods=["GET", "POST"])
@log_activity
def profile():
    if "user_id" not in session:
        flash("Please login to view profile", "warning")
        return redirect(url_for("main.login"))
    lang = session.get("language", "en")
    if request.method == "POST":
        full_name = sanitize_input(request.form.get("full_name", "").strip())
        email = sanitize_input(request.form.get("email", "").strip())
        location = sanitize_input(request.form.get("location", "").strip())
        district = sanitize_input(request.form.get("district", "").strip())
        region = sanitize_input(request.form.get("region", "").strip())
        language_preference = request.form.get("language_preference", "en")

        try:
            cursor = user_db.get_cursor(dictionary=False)
            cursor.execute(
                """
                UPDATE maziwa SET full_name=%s, email=%s, location=%s, district=%s, region=%s, language_preference=%s
                WHERE user_id=%s
            """,
                (
                    full_name,
                    email if email else None,
                    location,
                    district,
                    region,
                    language_preference,
                    session["user_id"],
                ),
            )
            user_db.connection.commit()
            cursor.close()
            session["user_name"] = full_name
            session["language"] = language_preference
            flash("Profile updated successfully!", "success")
        except Exception as e:
            flash("Error updating profile", "danger")
        return redirect(url_for("main.profile"))

    cursor = user_db.get_cursor()
    cursor.execute("SELECT * FROM maziwa WHERE user_id = %s", (session["user_id"],))
    user = cursor.fetchone()
    cursor.close()
    return render_template(
        "profile.html", lang=lang, t=lang_manager.get_text, user=user, request=request
    )


@main.route("/profile-photo/<filename>")
def serve_profile_photo(filename):
    """Serve profile photos directly - no cache issues"""
    if "user_id" not in session:
        abort(403)

    # Security: Only allow access to own photo or admin
    if filename.startswith("user_"):
        parts = filename.split("_")
        if len(parts) >= 2:
            photo_user_id = parts[1]
            if (
                photo_user_id != str(session.get("user_id"))
                and session.get("user_role") != "admin"
            ):
                abort(403)

    filepath = os.path.join(PROFILE_FOLDER, filename)

    if not os.path.exists(filepath):
        abort(404)

    # Send file with no cache headers
    response = send_file(filepath, mimetype="image/jpeg")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@main.route("/change-language/<lang>")
def change_language(lang):
    if lang in ["en", "sw"]:
        session["language"] = lang
        if "user_id" in session:
            try:
                if ensure_db_connection():
                    cursor = user_db.get_cursor(dictionary=False)
                    cursor.execute(
                        "UPDATE maziwa SET language_preference = %s WHERE user_id = %s",
                        (lang, session["user_id"]),
                    )
                    user_db.connection.commit()
                    cursor.close()
            except:
                pass
    next_page = request.args.get("next") or request.referrer or url_for("main.index")
    return redirect(next_page)


# ==================== ADMIN DASHBOARD ====================
@main.route("/admin")
def admin_dashboard():
    if session.get("user_role") != "admin":
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error. Please try again later.", "danger")
        return redirect(url_for("main.index"))

    lang = session.get("language", "en")

    try:
        cursor = user_db.get_cursor()

        cursor.execute(
            "SELECT * FROM maziwa WHERE LOWER(role) = LOWER('farmer') ORDER BY created_at DESC"
        )
        farmers = cursor.fetchall() or []

        cursor.execute(
            "SELECT * FROM maziwa WHERE LOWER(role) = LOWER('extension_officer') ORDER BY created_at DESC"
        )
        officers = cursor.fetchall() or []

        cursor.execute(
            "SELECT * FROM maziwa WHERE LOWER(role) = LOWER('admin') ORDER BY created_at DESC"
        )
        admins = cursor.fetchall() or []

        cursor.execute(
            "SELECT * FROM maziwa WHERE LOWER(role) = LOWER('extension_officer') AND (is_approved = FALSE OR is_approved IS NULL) ORDER BY created_at DESC"
        )
        pending_officers = cursor.fetchall() or []

        cursor.execute("SELECT * FROM diseases ORDER BY disease_id")
        diseases = cursor.fetchall() or []

        cursor.execute("SELECT COUNT(*) as count FROM diagnosis_history")
        predictions_result = cursor.fetchone()
        total_predictions = predictions_result["count"] if predictions_result else 0

        cursor.close()

        stats = {
            "total_users": len(farmers) + len(officers) + len(admins),
            "total_farmers": len(farmers),
            "total_officers": len(officers),
            "total_admins": len(admins),
            "pending_officers": len(pending_officers),
            "total_predictions": total_predictions,
            "active_diseases": len(diseases),
        }

    except Exception as e:
        print(f"Database error in admin_dashboard: {e}")
        farmers = []
        officers = []
        admins = []
        pending_officers = []
        diseases = []
        stats = {
            "total_users": 0,
            "total_farmers": 0,
            "total_officers": 0,
            "total_admins": 0,
            "pending_officers": 0,
            "total_predictions": 0,
            "active_diseases": 0,
        }

    return render_template(
        "admin_dashboard.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        farmers=farmers,
        officers=officers,
        admins=admins,
        pending_officers=pending_officers,
        diseases=diseases,
        stats=stats,
        predictions_by_disease=[],
        recent_predictions=[],
    )


# ==================== ADMIN VIEW USER ====================
@main.route("/admin/user/<user_id>/view")
def admin_view_user(user_id):
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    try:
        cursor = user_db.get_cursor()
        cursor.execute(
            """
            SELECT user_id, full_name, phone_number, email, role, location, district, region,
                   is_active, is_approved, created_at, approved_at, last_login
            FROM maziwa WHERE user_id = %s
        """,
            (str(user_id),),
        )
        user = cursor.fetchone()
        cursor.close()

        if not user:
            flash("User not found", "danger")
            return redirect(url_for("main.admin_dashboard"))

        lang = session.get("language", "en")
        return render_template(
            "admin_view_user.html",
            lang=lang,
            t=lang_manager.get_text,
            request=request,
            user=user,
        )
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for("main.admin_dashboard"))


# ==================== ADMIN EDIT USER ====================
@main.route("/admin/user/<user_id>/edit", methods=["GET", "POST"])
def admin_edit_user(user_id):
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    cursor = user_db.get_cursor()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        role = request.form.get("role", "").strip()
        location = request.form.get("location", "").strip()
        district = request.form.get("district", "").strip()
        region = request.form.get("region", "").strip()
        is_active = request.form.get("is_active") == "on"
        is_approved = request.form.get("is_approved") == "on"

        try:
            cursor.execute(
                """
                UPDATE maziwa 
                SET full_name=%s, email=%s, phone_number=%s, role=%s, 
                    location=%s, district=%s, region=%s, is_active=%s, is_approved=%s
                WHERE user_id=%s
            """,
                (
                    full_name,
                    email if email else None,
                    phone_number,
                    role,
                    location,
                    district,
                    region,
                    is_active,
                    is_approved,
                    str(user_id),
                ),
            )
            db.connection.commit()
            flash("User updated successfully!", "success")
            cursor.close()
            return redirect(url_for("main.admin_dashboard"))
        except Exception as e:
            flash(f"Error updating user: {e}", "danger")
            cursor.close()
            return redirect(url_for("main.admin_dashboard"))

    # GET request - show edit form
    cursor.execute("SELECT * FROM maziwa WHERE user_id = %s", (str(user_id),))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash("User not found", "danger")
        return redirect(url_for("main.admin_dashboard"))

    lang = session.get("language", "en")
    return render_template(
        "admin_edit_user.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        user=user,
    )


# ==================== ADMIN DELETE USER ====================
@main.route("/admin/user/<user_id>/delete", methods=["DELETE"])
@log_activity
def admin_delete_user(user_id):
    if session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if str(user_id) == str(session.get("user_id")):
        return (
            jsonify({"success": False, "message": "Cannot delete your own account"}),
            400,
        )

    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500

    try:
        cursor = user_db.get_cursor(dictionary=False)
        cursor.execute("DELETE FROM maziwa WHERE user_id = %s", (str(user_id),))
        user_db.connection.commit()
        affected_rows = cursor.rowcount
        cursor.close()

        if affected_rows > 0:
            log_user_activity("ADMIN_ACTION", f"Deleted user ID: {user_id}")
            return jsonify({"success": True, "message": "User deleted successfully"})
        else:
            return jsonify({"success": False, "message": "User not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ==================== ADMIN EDIT DISEASE ====================
@main.route("/admin/disease/<int:disease_id>/edit", methods=["GET", "POST"])
def admin_edit_disease(disease_id):
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    cursor = user_db.get_cursor()

    if request.method == "POST":
        disease_name_en = request.form.get("disease_name_en", "").strip()
        disease_name_sw = request.form.get("disease_name_sw", "").strip()
        scientific_name = request.form.get("scientific_name", "").strip()
        description_en = request.form.get("description_en", "").strip()
        description_sw = request.form.get("description_sw", "").strip()
        symptoms_en = request.form.get("symptoms_en", "").strip()
        symptoms_sw = request.form.get("symptoms_sw", "").strip()
        treatment_en = request.form.get("treatment_en", "").strip()
        treatment_sw = request.form.get("treatment_sw", "").strip()

        try:
            cursor.execute(
                """
                UPDATE diseases SET 
                    disease_name_en = %s, disease_name_sw = %s, scientific_name = %s,
                    description_en = %s, description_sw = %s, symptoms_en = %s, symptoms_sw = %s,
                    treatment_en = %s, treatment_sw = %s
                WHERE disease_id = %s
            """,
                (
                    disease_name_en,
                    disease_name_sw,
                    scientific_name,
                    description_en,
                    description_sw,
                    symptoms_en,
                    symptoms_sw,
                    treatment_en,
                    treatment_sw,
                    str(disease_id),
                ),
            )
            db.connection.commit()
            flash("Disease updated successfully!", "success")
            cursor.close()
            return redirect(url_for("main.admin_dashboard", _anchor="diseases"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
            cursor.close()
            return redirect(url_for("main.admin_dashboard", _anchor="diseases"))

    cursor.execute("SELECT * FROM diseases WHERE disease_id = %s", (str(disease_id),))
    disease = cursor.fetchone()
    cursor.close()

    if not disease:
        flash("Disease not found", "danger")
        return redirect(url_for("main.admin_dashboard", _anchor="diseases"))

    lang = session.get("language", "en")
    return render_template(
        "admin_edit_disease.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        disease=disease,
    )


# ==================== ADMIN VIEW DISEASE ====================
@main.route("/admin/disease/<int:disease_id>/view")
def admin_view_disease(disease_id):
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    try:
        cursor = user_db.get_cursor()
        cursor.execute(
            "SELECT * FROM diseases WHERE disease_id = %s", (str(disease_id),)
        )
        disease = cursor.fetchone()
        cursor.close()

        if not disease:
            flash("Disease not found", "danger")
            return redirect(url_for("main.admin_dashboard", _anchor="diseases"))

        lang = session.get("language", "en")
        return render_template(
            "admin_view_disease.html",
            lang=lang,
            t=lang_manager.get_text,
            request=request,
            disease=disease,
        )
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for("main.admin_dashboard", _anchor="diseases"))


# ==================== ADMIN DELETE DISEASE ====================
@main.route("/admin/disease/<int:disease_id>/delete", methods=["DELETE"])
def admin_delete_disease(disease_id):
    if session.get("user_role") != "admin":
        return jsonify({"success": False, "message": "Access denied"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500

    try:
        cursor = user_db.get_cursor(dictionary=False)

        cursor.execute(
            "SELECT disease_id FROM diseases WHERE disease_id = %s", (str(disease_id),)
        )
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"success": False, "message": "Disease not found"}), 404

        cursor.execute("DELETE FROM diseases WHERE disease_id = %s", (str(disease_id),))
        user_db.connection.commit()
        cursor.close()

        log_user_activity("ADMIN_ACTION", f"Deleted disease ID: {disease_id}")
        return jsonify({"success": True, "message": "Disease deleted successfully"})
    except Exception as e:
        print(f"Error deleting disease: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ==================== ADMIN USER ACTIVITY ====================
@main.route("/admin/user-activity")
def admin_user_activity():
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))
    return render_template(
        "user_logs.html",
        lang=session.get("language", "en"),
        t=lang_manager.get_text,
        request=request,
    )


# ==================== ADMIN API ENDPOINTS ====================
@main.route("/api/admin/user-activity")
def api_admin_user_activity():
    if session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        cursor = user_db.get_cursor()
        cursor.execute("SELECT * FROM user_activity_logs ORDER BY created_at DESC")
        all_data = cursor.fetchall() or []

        activities = []
        for row in all_data:
            created_at = row.get("created_at")
            if created_at and hasattr(created_at, "strftime"):
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                created_at = str(created_at) if created_at else None

            activities.append(
                {
                    "activity_id": row.get("activity_id"),
                    "user_id": row.get("user_id"),
                    "user_name": row.get("user_name") or "Unknown",
                    "user_role": row.get("user_role") or "N/A",
                    "activity_type": row.get("activity_type") or "N/A",
                    "activity_details": row.get("activity_details") or "",
                    "ip_address": row.get("ip_address") or "N/A",
                    "created_at": created_at,
                }
            )

        cursor.execute(
            "SELECT COUNT(*) as count FROM user_activity_logs WHERE activity_type = 'LOGIN'"
        )
        total_logins = cursor.fetchone()["count"] or 0

        cursor.execute(
            "SELECT COUNT(*) as count FROM user_activity_logs WHERE activity_type = 'LOGOUT'"
        )
        total_logouts = cursor.fetchone()["count"] or 0

        cursor.execute(
            "SELECT COUNT(*) as count FROM user_activity_logs WHERE activity_type = 'PREDICTION'"
        )
        total_predictions = cursor.fetchone()["count"] or 0

        cursor.execute(
            "SELECT COUNT(DISTINCT user_id) as count FROM user_activity_logs"
        )
        active_users = cursor.fetchone()["count"] or 0

        cursor.close()

        return jsonify(
            {
                "success": True,
                "activities": activities,
                "stats": {
                    "total_logins": total_logins,
                    "total_logouts": total_logouts,
                    "total_predictions": total_predictions,
                    "active_users": active_users,
                },
            }
        )
    except Exception as e:
        print(f"Error: {e}")
        return (
            jsonify(
                {
                    "success": True,
                    "activities": [],
                    "stats": {
                        "total_logins": 0,
                        "total_logouts": 0,
                        "total_predictions": 0,
                        "active_users": 0,
                    },
                }
            ),
            200,
        )


@main.route("/api/admin/stats")
def api_admin_stats():
    if session.get("user_role") != "admin":
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        cursor = user_db.get_cursor()

        cursor.execute("SELECT COUNT(*) as count FROM maziwa")
        total_users = cursor.fetchone()["count"] or 0

        cursor.execute(
            "SELECT COUNT(*) as count FROM maziwa WHERE LOWER(role) = LOWER('farmer')"
        )
        total_farmers = cursor.fetchone()["count"] or 0

        cursor.execute(
            "SELECT COUNT(*) as count FROM maziwa WHERE LOWER(role) = LOWER('extension_officer')"
        )
        total_officers = cursor.fetchone()["count"] or 0

        cursor.execute(
            "SELECT COUNT(*) as count FROM maziwa WHERE LOWER(role) = LOWER('admin')"
        )
        total_admins = cursor.fetchone()["count"] or 0

        cursor.execute(
            "SELECT COUNT(*) as count FROM maziwa WHERE LOWER(role) = LOWER('extension_officer') AND (is_approved = FALSE OR is_approved IS NULL)"
        )
        pending_officers = cursor.fetchone()["count"] or 0

        cursor.execute("SELECT COUNT(*) as count FROM diagnosis_history")
        total_predictions = cursor.fetchone()["count"] or 0

        cursor.execute("SELECT COUNT(*) as count FROM diseases")
        total_diseases = cursor.fetchone()["count"] or 0

        cursor.close()

        return jsonify(
            {
                "success": True,
                "total_users": total_users,
                "total_farmers": total_farmers,
                "total_officers": total_officers,
                "total_admins": total_admins,
                "pending_officers": pending_officers,
                "total_predictions": total_predictions,
                "total_diseases": total_diseases,
            }
        )
    except Exception as e:
        print(f"Error in api_admin_stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/api/admin/maziwa-list")
def api_users_list():
    if session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        cursor = user_db.get_cursor()
        cursor.execute("""
            SELECT user_id, full_name, phone_number, role, is_approved, is_active
            FROM maziwa 
            ORDER BY full_name
        """)
        users = cursor.fetchall()
        cursor.close()
        return jsonify({"success": True, "users": users})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": True, "users": []}), 200


@main.route("/admin/user/<user_id>/update", methods=["POST"])
@log_activity
def admin_update_user(user_id):
    if session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500

    data = request.get_json()

    try:
        cursor = user_db.get_cursor(dictionary=False)
        update_fields = []
        params = []

        if data.get("full_name"):
            update_fields.append("full_name = %s")
            params.append(data["full_name"])
        if "email" in data:
            update_fields.append("email = %s")
            params.append(data["email"] if data["email"] else None)
        if data.get("role"):
            update_fields.append("role = %s")
            params.append(data["role"])
        if "is_active" in data:
            update_fields.append("is_active = %s")
            params.append(data["is_active"])
        if "is_approved" in data:
            update_fields.append("is_approved = %s")
            params.append(data["is_approved"])
            if data["is_approved"] == 1:
                update_fields.append("approved_at = CURRENT_TIMESTAMP")

        if update_fields:
            params.append(str(user_id))
            query = f"UPDATE maziwa SET {', '.join(update_fields)} WHERE user_id = %s"
            cursor.execute(query, params)
            db.connection.commit()

        cursor.close()
        log_user_activity("ADMIN_ACTION", f"Updated user ID: {user_id}")
        return jsonify({"success": True, "message": "User updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ==================== ADMIN OFFICER APPROVAL ====================
@main.route("/admin/officer/<user_id>/approve", methods=["POST"])
@log_activity
def admin_approve_officer(user_id):
    if session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500

    try:
        cursor = user_db.get_cursor()
        cursor.execute(
            """
            SELECT user_id, full_name, phone_number, email, region, is_approved 
            FROM maziwa WHERE user_id = %s AND LOWER(role) = LOWER('extension_officer')
        """,
            (user_id,),
        )
        officer = cursor.fetchone()

        if not officer:
            cursor.close()
            return jsonify({"success": False, "message": "Officer not found"}), 404

        if officer.get("is_approved") == 1:
            cursor.close()
            return (
                jsonify({"success": False, "message": "Officer already approved"}),
                400,
            )

        # Update approval in database
        cursor.execute(
            """
            UPDATE maziwa SET is_approved = TRUE, is_active = TRUE, approved_at = CURRENT_TIMESTAMP, approved_by = %s 
            WHERE user_id = %s
        """,
            (session.get("user_id"), user_id),
        )
        db.connection.commit()
        cursor.close()

        admin_name = session.get("user_name", "Admin")
        officer_name = officer["full_name"]

        # Send BOTH SMS and Email notifications
        notifications = []

        # Send SMS
        sms_sent = send_approval_sms(officer["phone_number"], officer_name, admin_name)
        if sms_sent:
            notifications.append("SMS")

        # Send Email
        email_sent = send_approval_email(officer["email"], officer_name, admin_name)
        if email_sent:
            notifications.append("Email")

        # Create in-app notification
        create_in_app_notification(
            officer["user_id"],
            "Account Approved",
            f"Your account has been approved by {admin_name}. You can now login to the system.",
        )

        if notifications:
            message = f"Officer approved successfully! Notifications sent via: {', '.join(notifications)}"
        else:
            message = (
                "Officer approved but no notifications sent (SMS/Email both failed)."
            )

        return jsonify({"success": True, "message": message})

    except Exception as e:
        print(f"Error approving officer: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@main.route("/admin/officer/<user_id>/reject", methods=["POST"])
@log_activity
def admin_reject_officer(user_id):
    if session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500

    data = request.get_json()
    reason = data.get("reason", "No specific reason provided")

    try:
        cursor = user_db.get_cursor()
        cursor.execute(
            """
            SELECT full_name, phone_number, email 
            FROM maziwa WHERE user_id = %s AND LOWER(role) = LOWER('extension_officer')
        """,
            (user_id,),
        )
        officer = cursor.fetchone()

        if not officer:
            cursor.close()
            return jsonify({"success": False, "message": "Officer not found"}), 404

        cursor.execute("DELETE FROM maziwa WHERE user_id = %s", (user_id,))
        db.connection.commit()
        cursor.close()

        return jsonify({"success": True, "message": "Officer rejected and deleted."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ==================== OFFICER DASHBOARD ====================
@main.route("/officer-dashboard")
@log_activity
def officer_dashboard():
    if session.get("user_role") != "extension_officer":
        flash("Access denied. Extension officer privileges required.", "danger")
        return redirect(url_for("main.index"))
    lang = session.get("language", "en")
    officer_region = session.get("region")
    return render_template(
        "officer_dashboard.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        officer_region=officer_region,
    )


# ==================== OFFICER DISEASE MANAGEMENT ====================
@main.route("/api/officer/diseases", methods=["GET"])
def api_officer_get_diseases():
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    cursor = user_db.get_cursor()
    cursor.execute("SELECT * FROM diseases ORDER BY disease_id")
    diseases = cursor.fetchall() or []
    cursor.close()
    return jsonify({"success": True, "diseases": diseases})


@main.route("/api/officer/disease/<int:disease_id>", methods=["GET"])
def api_officer_get_disease(disease_id):
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    cursor = user_db.get_cursor()
    cursor.execute("SELECT * FROM diseases WHERE disease_id = %s", (str(disease_id),))
    disease = cursor.fetchone()
    cursor.close()

    if not disease:
        return jsonify({"success": False, "error": "Disease not found"}), 404
    return jsonify({"success": True, "disease": disease})


@main.route("/api/officer/disease/create", methods=["POST"])
@log_activity
def api_officer_create_disease():
    if session.get("user_role") != "extension_officer":
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    data = request.get_json()
    if not data.get("disease_name_en"):
        return jsonify({"success": False, "message": "Disease name required"}), 400
    cursor = user_db.get_cursor()
    cursor.execute(
        """INSERT INTO diseases (disease_name_en, disease_name_sw, scientific_name, description_en, description_sw, symptoms_en, symptoms_sw, treatment_en, treatment_sw) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            data.get("disease_name_en"),
            data.get("disease_name_sw"),
            data.get("scientific_name"),
            data.get("description_en"),
            data.get("description_sw"),
            data.get("symptoms_en"),
            data.get("symptoms_sw"),
            data.get("treatment_en"),
            data.get("treatment_sw"),
        ),
    )
    db.connection.commit()
    cursor.close()
    return jsonify({"success": True, "message": "Disease added"})


@main.route("/api/officer/disease/<int:disease_id>/update", methods=["PUT"])
@log_activity
def api_officer_update_disease(disease_id):
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    data = request.get_json()
    cursor = user_db.get_cursor()

    cursor.execute(
        """UPDATE diseases SET 
            disease_name_en=%s, disease_name_sw=%s, scientific_name=%s, 
            description_en=%s, description_sw=%s, symptoms_en=%s, symptoms_sw=%s, 
            treatment_en=%s, treatment_sw=%s 
        WHERE disease_id = %s""",
        (
            data.get("disease_name_en"),
            data.get("disease_name_sw"),
            data.get("scientific_name"),
            data.get("description_en"),
            data.get("description_sw"),
            data.get("symptoms_en"),
            data.get("symptoms_sw"),
            data.get("treatment_en"),
            data.get("treatment_sw"),
            str(disease_id),
        ),
    )
    db.connection.commit()
    cursor.close()
    return jsonify({"success": True, "message": "Disease updated"})


@main.route("/api/officer/disease/<int:disease_id>/delete", methods=["DELETE"])
@log_activity
def api_officer_delete_disease(disease_id):
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    cursor = user_db.get_cursor()
    cursor.execute("DELETE FROM diseases WHERE disease_id = %s", (str(disease_id),))
    db.connection.commit()
    cursor.close()
    return jsonify({"success": True, "message": "Disease deleted"})


@main.route("/admin/user/<user_id>")
def admin_get_user(user_id):
    if session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if not ensure_db_connection():
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = user_db.get_cursor()
        cursor.execute(
            """
            SELECT user_id, full_name, phone_number, email, role, location, district, region,
                   is_active, is_approved, created_at, approved_at, last_login
            FROM maziwa WHERE user_id = %s
        """,
            (str(user_id),),
        )
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_dict = dict(user)
        for key in ["created_at", "approved_at", "last_login"]:
            if user_dict.get(key) and hasattr(user_dict[key], "strftime"):
                user_dict[key] = user_dict[key].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify(user_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== OFFICER DASHBOARD DATA API ====================
@main.route("/api/officer/dashboard-data")
def api_officer_dashboard_data():
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        cursor = user_db.get_cursor()

        # Total Farmers
        cursor.execute("SELECT COUNT(*) as count FROM maziwa WHERE role = 'farmer'")
        result = cursor.fetchone()
        total_farmers = result["count"] if result else 0

        # Total Predictions
        cursor.execute("SELECT COUNT(*) as count FROM diagnosis_history")
        result = cursor.fetchone()
        total_predictions = result["count"] if result else 0

        # Diseases Detected (not Healthy)
        cursor.execute(
            "SELECT COUNT(*) as count FROM diagnosis_history WHERE disease_name != 'Healthy'"
        )
        result = cursor.fetchone()
        diseases_detected = result["count"] if result else 0

        # Active Farmers (last 30 days) - Convert diagnosis_date to timestamp
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count 
            FROM diagnosis_history 
            WHERE diagnosis_date::timestamp >= NOW() - INTERVAL '30 days'
        """)
        result = cursor.fetchone()
        active_farmers = result["count"] if result else 0

        # Recent Farmers (last 50)
        cursor.execute("""
            SELECT user_id, full_name, phone_number, email, location, district, region, 
                   created_at::text as created_at
            FROM maziwa 
            WHERE role = 'farmer' 
            ORDER BY created_at DESC 
            LIMIT 50
        """)
        recent_farmers = cursor.fetchall() or []

        # Recent Predictions (last 50)
        cursor.execute("""
            SELECT dh.id, dh.disease_name, dh.confidence_score, 
                   dh.diagnosis_date::text as diagnosis_date, 
                   COALESCE(u.full_name, 'Unknown') as farmer_name, 
                   COALESCE(u.phone_number, 'N/A') as farmer_phone,
                   COALESCE(u.location, 'N/A') as location
            FROM diagnosis_history dh 
            LEFT JOIN maziwa u ON dh.user_id::text = u.user_id::text
            ORDER BY dh.diagnosis_date DESC 
            LIMIT 50
        """)
        recent_predictions = cursor.fetchall() or []

        cursor.close()

        # Convert to list of dicts
        farmers_list = []
        for row in recent_farmers:
            farmers_list.append(dict(row))

        predictions_list = []
        for row in recent_predictions:
            predictions_list.append(dict(row))

        return jsonify(
            {
                "success": True,
                "stats": {
                    "total_farmers": total_farmers,
                    "total_predictions": total_predictions,
                    "diseases_detected": diseases_detected,
                    "active_farmers": active_farmers,
                },
                "recent_farmers": farmers_list,
                "recent_predictions": predictions_list,
            }
        )
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/api/predict", methods=["POST"])
@log_activity
def api_predict():
    language = request.cookies.get("language", session.get("language", "en"))
    if request.is_json:
        data = request.get_json()
        image_data = data.get("image")
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400
        if "," in image_data:
            image_data = image_data.split(",")[1]
        temp_path = None
        disease_name = "Healthy"
        confidence = 85.5
        try:
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
            temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
            img.save(temp_path, "JPEG", quality=90)

            # ============ FIXED PREDICTION CODE - LOAD MODEL DIRECTLY ============
            import tensorflow as tf
            from tensorflow.keras.preprocessing import image
            import numpy as np
            import json as json_lib

            # Path to model
            model_path = "app/models/maize_disease_model.h5"

            if os.path.exists(model_path):
                print(f"✅ Loading model from {model_path}")
                model = tf.keras.models.load_model(model_path)
                print(f"✅ Model loaded, input shape: {model.input_shape}")

                # Load class names
                class_names_path = "class_names.json"
                if os.path.exists(class_names_path):
                    with open(class_names_path, "r") as f:
                        class_names = json_lib.load(f)
                    if isinstance(class_names, dict) and "class_names" in class_names:
                        class_names = class_names["class_names"]
                else:
                    class_names = ["Blight", "Common_Rust", "Gray_Leaf_Spot", "Healthy"]

                print(f"✅ Class names: {class_names}")

                # Preprocess image
                img_pred = image.load_img(temp_path, target_size=(224, 224))
                img_array = image.img_to_array(img_pred)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = img_array / 255.0

                # Predict
                predictions = model.predict(img_array, verbose=0)[0]
                predicted_idx = np.argmax(predictions)
                confidence = float(predictions[predicted_idx] * 100)
                disease_name = class_names[predicted_idx] if class_names else "Unknown"

                print(f"🎯 API Prediction: {disease_name} ({confidence:.1f}%)")
                print(f"🎯 Raw predictions: {predictions}")
            else:
                print(f"❌ Model not found at {model_path}")
                disease_name = "Healthy"
                confidence = 85.5
            # ============ END OF FIXED PREDICTION CODE ============

            # Translate disease name based on language
            if language == "sw":
                display_disease_name = disease_name
            else:
                display_disease_name = disease_name

            # Recommendations based on disease - WITH TRANSLATION SUPPORT
            if "Blight" in disease_name:
                # English versions
                description_en = "Northern corn leaf blight is a fungal disease caused by Exserohilum turcicum. It thrives in cool, humid conditions and can cause significant yield loss if left untreated."
                symptoms_en = "• Long, elliptical, cigar-shaped lesions (2.5-15 cm long)\n• Lesions are grayish-green to tan in color\n• Lesions may coalesce and kill entire leaves\n• Symptoms first appear on lower leaves"
                treatment_en = "• Apply fungicides containing azoxystrobin or pyraclostrobin\n• Use resistant hybrid varieties\n• Crop rotation with non-host crops\n• Tillage to bury infected crop residue"
                organic_treatment_en = [
                    "🌿 Apply neem oil solution (10ml per liter water) - spray every 7 days",
                    "🍃 Use compost tea as foliar spray - rich in beneficial microbes",
                    "🌱 Plant marigolds as companion plants - natural fungicide properties",
                    "💧 Ensure proper drainage and air circulation between plants",
                ]
                chemical_treatment_en = [
                    "🧪 Azoxystrobin (Amistar) - 0.5ml per liter of water",
                    "🧪 Pyraclostrobin (Headline) - 0.75ml per liter of water",
                    "🧪 Mancozeb (Dithane) - 2g per liter of water",
                    "🧪 Apply every 7-14 days during wet conditions",
                ]
                cultural_practices_en = [
                    "🌾 Practice crop rotation (2-3 years with soybeans or wheat)",
                    "🚜 Remove and destroy infected crop residue after harvest",
                    "💨 Space plants properly (75cm between rows, 25cm within row)",
                    "🌱 Plant disease-resistant hybrid varieties",
                ]
                action_plan_en = [
                    "📅 Day 1-3: Apply fungicide immediately at first sign of disease",
                    "📅 Day 4-7: Remove severely infected leaves to reduce spread",
                    "📅 Day 8-14: Monitor and reapply fungicide if needed",
                    "📅 Next Season: Plan crop rotation and use resistant varieties",
                ]

                # Swahili versions
                description_sw = "Ugonjwa wa kuvu unaosababishwa na Exserohilum turcicum. Huenea katika hali ya hewa ya baridi na unyevunyevu na unaweza kusababisha hasara kubwa ya mavuno ikiachwa bila kudhibitiwa."
                symptoms_sw = "• Madoa marefu, ya umbo la sigara (urefu wa 2.5-15 cm)\n• Madoa ni ya kijivu-kijani hadi kahawia\n• Madoa yanaweza kuungana na kufisha majani yote\n• Dalili huonekana kwanza kwenye majani ya chini"
                treatment_sw = "• Tumia dawa za kuvu zilizo na azoxystrobin au pyraclostrobin\n• Tumia aina za mahindi zinazostahimili ugonjwa\n• Zungusha mazao\n• Fukia mabaki ya mazao baada ya mavuno"
                organic_treatment_sw = [
                    "🌿 Tumia mafuta ya mwarobaini (10ml kwa lita moja ya maji) - piga kila siku 7",
                    "🍃 Tumia chai ya mbolea asili",
                    "🌱 Panda marigolds kama mimea shirikishi",
                    "💧 Hakikisha maji yanatoka vizuri na hewa inazunguka kati ya mimea",
                ]
                chemical_treatment_sw = [
                    "🧪 Azoxystrobin (Amistar) - 0.5ml kwa lita moja ya maji",
                    "🧪 Pyraclostrobin (Headline) - 0.75ml kwa lita moja ya maji",
                    "🧪 Mancozeb (Dithane) - 2g kwa lita moja ya maji",
                    "🧪 Tumia kila siku 7-14 wakati wa mvua",
                ]
                cultural_practices_sw = [
                    "🌾 Zungusha mazao kwa miaka 2-3 na maharage au ngano",
                    "🚜 Ondoa na uharibu mabaki ya mazao yaliyoathirika baada ya mavuno",
                    "💨 Panda kwa umbali sahihi (75cm kati ya mistari, 25cm kati ya mimea)",
                    "🌱 Panda aina za mahindi zinazostahimili magonjwa",
                ]
                action_plan_sw = [
                    "📅 Siku 1-3: Tumia dawa ya kuvu mara moja unapoona dalili za kwanza",
                    "📅 Siku 4-7: Ondoa majani yaliyoathirika sana",
                    "📅 Siku 8-14: Fuatilia na tumia dawa tena ikiwa ni lazima",
                    "📅 Msimu Ujao: Panda aina zinazostahimili na zungusha mazao",
                ]

            elif "Rust" in disease_name:
                description_en = "Common rust is caused by the fungus Puccinia sorghi. It appears as small pustules on leaves and can reduce yield in severe cases."
                symptoms_en = "• Small, circular to oval pustules (1-2 mm diameter)\n• Pustules are reddish-brown to dark brown in color\n• Pustules appear on both leaf surfaces\n• Severely infected leaves may turn yellow and die"
                treatment_en = "• Apply fungicides at first sign of disease\n• Plant resistant hybrid varieties\n• Avoid late planting dates\n• Maintain adequate plant nutrition"
                organic_treatment_en = [
                    "🍃 Apply baking soda solution (1 tbsp per liter water) - weekly spray",
                    "🪴 Use garlic-pepper spray",
                    "🌿 Remove infected leaves promptly",
                    "💧 Improve air circulation by proper plant spacing",
                ]
                chemical_treatment_en = [
                    "🧪 Tebuconazole (Folicur) - 0.5ml per liter",
                    "🧪 Propiconazole (Tilt) - 1ml per liter",
                    "🧪 Azoxystrobin (Amistar) - 0.5ml per liter",
                    "🧪 Apply at first sign of rust pustules",
                ]
                cultural_practices_en = [
                    "🌾 Plant resistant hybrid varieties",
                    "🚜 Avoid overhead irrigation",
                    "💨 Space plants properly for air flow",
                    "🌱 Plant early to avoid peak rust season",
                ]
                action_plan_en = [
                    "📅 Day 1-2: Apply fungicide immediately when rust is observed",
                    "📅 Day 3-5: Remove severely affected leaves",
                    "📅 Day 7-10: Monitor for new pustules, reapply if needed",
                    "📅 Next Season: Select resistant varieties and plant early",
                ]

                # Swahili versions
                description_sw = "Kutu wa kawaida husababishwa na fangasi aitwaye Puccinia sorghi. Huonekana kama madoa madogo kwenye majani na unaweza kupunguza mavuno ikiwa mkali."
                symptoms_sw = "• Madoa madogo ya mviringo (kipenyo cha 1-2 mm)\n• Madoa ni mekundu-kahawia hadi kahawia iliyokolea\n• Madoa huonekana pande zote za jani\n• Majani yaliyoathirika sana yanaweza kuwa njano na kukauka"
                treatment_sw = "• Tumia dawa za kuvu unapoona dalili za kwanza\n• Panda aina za mahindi zinazostahimili\n• Epuka kupanda kuchelewa\n• Dumisha lishe bora ya mimea"
                organic_treatment_sw = [
                    "🍃 Tumia suluhisho la baking soda (kijiko 1 kwa lita moja ya maji)",
                    "🪴 Tumia dawa ya kitunguu saumu na pilipili",
                    "🌿 Ondoa majani yaliyoathirika mara moja",
                    "💧 Boresha mzunguko wa hewa kwa umbali sahihi wa kupanda",
                ]
                chemical_treatment_sw = [
                    "🧪 Tebuconazole (Folicur) - 0.5ml kwa lita moja",
                    "🧪 Propiconazole (Tilt) - 1ml kwa lita moja",
                    "🧪 Azoxystrobin (Amistar) - 0.5ml kwa lita moja",
                    "🧪 Tumia unapoona dalili za kwanza za kutu",
                ]
                cultural_practices_sw = [
                    "🌾 Panda aina za mahindi zinazostahimili",
                    "🚜 Epuka kumwagilia kwa njia ya kunyunyuzia juu",
                    "💨 Panda kwa umbali unaoruhusu hewa kuzunguka",
                    "🌱 Panda mapema ili kuepuka kipindi cha kutu",
                ]
                action_plan_sw = [
                    "📅 Siku 1-2: Tumia dawa ya kuvu mara moja unapoona kutu",
                    "📅 Siku 3-5: Ondoa majani yaliyoathirika sana",
                    "📅 Siku 7-10: Fuatilia kwa madoa mapya, tumia tena ikiwa ni lazima",
                    "📅 Msimu Ujao: Panda aina zinazostahimili na panda mapema",
                ]

            elif "Spot" in disease_name:
                description_en = "Gray leaf spot is caused by Cercospora zeae-maydis. It produces rectangular lesions that can severely damage leaves."
                symptoms_en = "• Small pinpoint spots become rectangular lesions\n• Lesions are gray to tan with dark borders\n• Lesions restricted by leaf veins\n• Severely infected leaves die prematurely"
                treatment_en = "• Apply fungicides preventatively at tasseling\n• Use resistant hybrids\n• Crop rotation with non-host crops\n• Tillage to reduce residue"
                organic_treatment_en = [
                    "🍃 Apply potassium bicarbonate solution (1 tbsp per liter)",
                    "🪴 Use chamomile tea spray",
                    "🌿 Remove infected lower leaves",
                    "💧 Water early morning only",
                ]
                chemical_treatment_en = [
                    "🧪 Chlorothalonil (Bravo) - 2ml per liter",
                    "🧪 Azoxystrobin (Amistar) - 0.5ml per liter",
                    "🧪 Pyraclostrobin (Headline) - 0.75ml per liter",
                    "🧪 Apply at tasseling stage",
                ]
                cultural_practices_en = [
                    "🌾 Rotate with soybeans or wheat for 2 years",
                    "🚜 Bury residue with deep plowing",
                    "💨 Improve air circulation",
                    "🌱 Plant moderately resistant varieties",
                ]
                action_plan_en = [
                    "📅 Pre-planting: Select resistant varieties",
                    "📅 At tasseling: Apply preventative fungicide",
                    "📅 After harvest: Deep plow to bury residue",
                    "📅 Next Season: Rotate with non-host crop",
                ]

                # Swahili versions
                description_sw = "Madoa meusi ya majani husababishwa na fangasi aitwaye Cercospora zeae-maydis. Husababisha madoa yenye umbo la mstatili yanayoweza kuharibu majani."
                symptoms_sw = "• Madoa madogo huwa makubwa na kuwa umbo la mstatili\n• Madoa ni ya kijivu hadi kahawia yenye kingo nyeusi\n• Madoa huzuiliwa na mishipa ya jani\n• Majani yaliyoathirika sana hukauka mapema"
                treatment_sw = "• Tumia dawa za kuvu kabla ya ugonjwa kuonekana wakati wa kuchanua jani la juu\n• Tumia aina zinazostahimili\n• Zungusha mazao\n• Fukia mabaki ya mazao"
                organic_treatment_sw = [
                    "🍃 Tumia suluhisho la bicarbonate ya potasiamu (kijiko 1 kwa lita moja)",
                    "🪴 Tumia dawa ya chai ya chamomile",
                    "🌿 Ondoa majani ya chini yaliyoathirika",
                    "💧 Mugilia maji asubuhi tu",
                ]
                chemical_treatment_sw = [
                    "🧪 Chlorothalonil (Bravo) - 2ml kwa lita moja",
                    "🧪 Azoxystrobin (Amistar) - 0.5ml kwa lita moja",
                    "🧪 Pyraclostrobin (Headline) - 0.75ml kwa lita moja",
                    "🧪 Tumia wakati wa kuchanua jani la juu",
                ]
                cultural_practices_sw = [
                    "🌾 Zungusha mazao na maharage au ngano kwa miaka 2",
                    "🚜 Fukia mabaki ya mazao kwa kulima kwa kina",
                    "💨 Boresha mzunguko wa hewa",
                    "🌱 Panda aina zinazostahimili wastani",
                ]
                action_plan_sw = [
                    "📅 Kabla ya kupanda: Chagua aina zinazostahimili",
                    "📅 Wakati wa kuchanua: Tumia dawa ya kuvu",
                    "📅 Baada ya mavuno: Lima kwa kina kufukia mabaki",
                    "📅 Msimu Ujao: Zungusha mazao",
                ]

            else:  # Healthy
                description_en = "Your maize plant appears healthy with no signs of disease. Continue good agricultural practices to maintain plant health."
                symptoms_en = "• No visible disease symptoms\n• Leaves are green and healthy\n• Normal growth and development\n• Good overall plant vigor"
                treatment_en = "• Continue regular monitoring\n• Maintain good nutrition\n• Practice preventative measures\n• Keep field records"
                organic_treatment_en = [
                    "🍃 Apply compost tea monthly",
                    "🪴 Use neem oil as preventative spray",
                    "🌿 Maintain good soil health",
                    "💧 Water consistently but not excessively",
                ]
                chemical_treatment_en = [
                    "🧪 No chemical treatment needed",
                    "🧪 Consider preventative fungicides in high-risk areas",
                    "🧪 Maintain balanced fertilizer program",
                ]
                cultural_practices_en = [
                    "🌾 Practice crop rotation with legumes",
                    "🚜 Maintain field sanitation",
                    "💨 Ensure proper plant spacing",
                    "🌱 Use certified disease-free seeds",
                ]
                action_plan_en = [
                    "📅 Weekly: Scout fields for early detection",
                    "📅 Monthly: Apply compost tea",
                    "📅 Season: Maintain good nutrition",
                    "📅 Long term: Keep good field records",
                ]

                # Swahili versions
                description_sw = "Mmea wako wa mahindi unaonekana kuwa na afya na hakuna dalili za ugonjwa. Endelea na mazoea mazuri ya kilimo kudumisha afya ya mmea."
                symptoms_sw = "• Hakuna dalili za ugonjwa zinazoonekana\n• Majani ni mabichi na yenye afya\n• Ukuaji na maendeleo ya kawaida\n• Nguvu nzuri ya mmea kwa ujumla"
                treatment_sw = "• Endelea kufuatilia mara kwa mara\n• Dumisha lishe bora\n• Fuata hatua za kuzuia magonjwa\n• Weka rekodi za shamba"
                organic_treatment_sw = [
                    "🍃 Tumia chai ya mbolea asili kila mwezi",
                    "🪴 Tumia mafuta ya mwarobaini kama dawa ya kuzuia",
                    "🌿 Dumisha afya bora ya udongo",
                    "💧 Mugilia maji kwa uwiano lakini si kupita kiasi",
                ]
                chemical_treatment_sw = [
                    "🧪 Hakuna matibabu ya kemikali yanayohitajika",
                    "🧪 Fikiria dawa za kuvu za kuzuia katika maeneo yenye hatari kubwa",
                    "🧪 Dumisha programu bora ya mbolea",
                ]
                cultural_practices_sw = [
                    "🌾 Zungusha mazao na mikunde",
                    "🚜 Dumisha usafi wa shamba",
                    "💨 Hakikisha umbali sahihi wa kupanda",
                    "🌱 Tumia mbolea za asili",
                ]
                action_plan_sw = [
                    "📅 Kila wiki: Kagua mashamba kwa ugunduzi wa mapema",
                    "📅 Kila mwezi: Tumia chai ya mbolea asili",
                    "📅 Msimu: Dumisha lishe bora",
                    "📅 Muda mrefu: Weka rekodi nzuri za shamba",
                ]

            # Select language version
            if language == "sw":
                description = description_sw
                symptoms = symptoms_sw
                treatment = treatment_sw
                organic_treatment = organic_treatment_sw
                chemical_treatment = chemical_treatment_sw
                cultural_practices = cultural_practices_sw
                action_plan = action_plan_sw
            else:
                description = description_en
                symptoms = symptoms_en
                treatment = treatment_en
                organic_treatment = organic_treatment_en
                chemical_treatment = chemical_treatment_en
                cultural_practices = cultural_practices_en
                action_plan = action_plan_en

            return jsonify(
                {
                    "success": True,
                    "disease": display_disease_name,
                    "confidence": confidence,
                    "description": description,
                    "symptoms": symptoms,
                    "treatment": treatment,
                    "organic_treatment": organic_treatment,
                    "chemical_treatment": chemical_treatment,
                    "cultural_practices": cultural_practices,
                    "action_plan": action_plan,
                }
            )
        except Exception as e:
            print(f"Error in prediction: {e}")
            import traceback

            traceback.print_exc()
            return (
                jsonify(
                    {
                        "success": False,
                        "error": str(e),
                        "disease": "Healthy",
                        "confidence": 50.0,
                    }
                ),
                200,
            )
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    return jsonify({"error": "No image data provided", "success": False}), 400


# ==================== FARMER HISTORY API ====================
@main.route("/farmer/history")
def farmer_history():
    if session.get("user_id") is None:
        flash("Please login to access this page.", "warning")
        return redirect(url_for("main.login"))
    if session.get("user_role") != "farmer":
        flash("Access denied. Farmer privileges required.", "danger")
        return redirect(url_for("main.index"))
    lang = session.get("language", "en")
    return render_template(
        "history.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        user_id=session.get("user_id"),
    )


@main.route("/api/farmer/predictions")
def api_farmer_predictions():
    if session.get("user_id") is None:
        return jsonify({"success": False, "error": "Please login first"}), 401
    if session.get("user_role") != "farmer":
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    user_id = str(session.get("user_id"))
    try:
        cursor = user_db.get_cursor()
        cursor.execute(
            """
            SELECT id as prediction_id, disease_name, confidence_score, image_path, diagnosis_date, mode, created_at, is_synced
            FROM diagnosis_history WHERE user_id = %s ORDER BY diagnosis_date DESC LIMIT 100
        """,
            (user_id,),
        )
        predictions = cursor.fetchall() or []
        cursor.close()
        for pred in predictions:
            if pred.get("diagnosis_date") and hasattr(
                pred["diagnosis_date"], "strftime"
            ):
                pred["diagnosis_date"] = pred["diagnosis_date"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
        return jsonify(
            {
                "success": True,
                "predictions": [dict(pred) for pred in predictions],
                "total": len(predictions),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ADMIN ADD FARMER ====================
@main.route("/admin/farmer/add", methods=["GET", "POST"])
def admin_add_farmer():
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        location = request.form.get("location", "").strip()
        district = request.form.get("district", "").strip()
        region = request.form.get("region", "").strip()
        role = "farmer"

        if not full_name or not phone_number or not password:
            flash("Full name, phone number and password are required", "danger")
            return redirect(url_for("main.admin_add_farmer"))

        if not validate_phone_number(phone_number):
            flash("Invalid phone number", "danger")
            return redirect(url_for("main.admin_add_farmer"))

        cursor = user_db.get_cursor()
        cursor.execute(
            "SELECT user_id FROM maziwa WHERE phone_number = %s", (phone_number,)
        )
        if cursor.fetchone():
            cursor.close()
            flash("Phone number already registered", "danger")
            return redirect(url_for("main.admin_add_farmer"))

        password_hash = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=32
        )

        try:
            cursor.execute(
                """
                INSERT INTO maziwa (full_name, phone_number, email, password_hash, role, 
                                  location, district, region, is_approved, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, 1, CURRENT_TIMESTAMP)
            """,
                (
                    full_name,
                    phone_number,
                    email if email else None,
                    password_hash,
                    role,
                    location,
                    district,
                    region,
                ),
            )
            db.connection.commit()
            flash("Farmer added successfully!", "success")
            cursor.close()
            return redirect(url_for("main.admin_dashboard", _anchor="farmers"))
        except Exception as e:
            flash(f"Error adding farmer: {e}", "danger")
            cursor.close()
            return redirect(url_for("main.admin_add_farmer"))

    lang = session.get("language", "en")
    return render_template(
        "admin_add_user.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        user_role="farmer",
        title="Add New Farmer",
    )


# ==================== ADMIN ADD OFFICER ====================
@main.route("/admin/officer/add", methods=["GET", "POST"])
def admin_add_officer():
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        region = request.form.get("region", "").strip()
        role = "extension_officer"

        if not full_name or not phone_number or not password:
            flash("Full name, phone number and password are required", "danger")
            return redirect(url_for("main.admin_add_officer"))

        if not validate_phone_number(phone_number):
            flash("Invalid phone number", "danger")
            return redirect(url_for("main.admin_add_officer"))

        cursor = user_db.get_cursor()
        cursor.execute(
            "SELECT user_id FROM maziwa WHERE phone_number = %s", (phone_number,)
        )
        if cursor.fetchone():
            cursor.close()
            flash("Phone number already registered", "danger")
            return redirect(url_for("main.admin_add_officer"))

        password_hash = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=32
        )

        try:
            cursor.execute(
                """
                INSERT INTO maziwa (full_name, phone_number, email, password_hash, role, 
                                  region, is_approved, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, 0, 1, CURRENT_TIMESTAMP)
            """,
                (
                    full_name,
                    phone_number,
                    email if email else None,
                    password_hash,
                    role,
                    region,
                ),
            )
            db.connection.commit()
            flash("Extension officer added successfully! Pending approval.", "success")
            cursor.close()
            return redirect(url_for("main.admin_dashboard", _anchor="officers"))
        except Exception as e:
            flash(f"Error adding officer: {e}", "danger")
            cursor.close()
            return redirect(url_for("main.admin_add_officer"))

    lang = session.get("language", "en")
    return render_template(
        "admin_add_user.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        user_role="officer",
        title="Add New Extension Officer",
    )


# ==================== ADMIN ADD ADMIN ====================
@main.route("/admin/admin/add", methods=["GET", "POST"])
def admin_add_admin():
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = "admin"

        if not full_name or not phone_number or not password:
            flash("Full name, phone number and password are required", "danger")
            return redirect(url_for("main.admin_add_admin"))

        if not validate_phone_number(phone_number):
            flash("Invalid phone number", "danger")
            return redirect(url_for("main.admin_add_admin"))

        cursor = user_db.get_cursor()
        cursor.execute(
            "SELECT user_id FROM maziwa WHERE phone_number = %s", (phone_number,)
        )
        if cursor.fetchone():
            cursor.close()
            flash("Phone number already registered", "danger")
            return redirect(url_for("main.admin_add_admin"))

        password_hash = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=32
        )

        try:
            cursor.execute(
                """
                INSERT INTO maziwa (full_name, phone_number, email, password_hash, role, 
                                  is_approved, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, 1, 1, CURRENT_TIMESTAMP)
            """,
                (
                    full_name,
                    phone_number,
                    email if email else None,
                    password_hash,
                    role,
                ),
            )
            db.connection.commit()
            flash("Admin added successfully!", "success")
            cursor.close()
            return redirect(url_for("main.admin_dashboard", _anchor="admins"))
        except Exception as e:
            flash(f"Error adding admin: {e}", "danger")
            cursor.close()
            return redirect(url_for("main.admin_add_admin"))

    lang = session.get("language", "en")
    return render_template(
        "admin_add_user.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        user_role="admin",
        title="Add New Admin",
    )


# ==================== API TRANSLATIONS FOR DYNAMIC LANGUAGE SWITCHING ====================
@main.route("/api/translations/<lang>")
def api_translations(lang):
    """Get all translations for a language via AJAX (no page reload)"""
    if lang not in ['en', 'sw']:
        lang = 'en'

    # Common keys used throughout the app
    keys = [
        # Navigation
        'home', 'about', 'dashboard', 'farmers', 'predict_disease', 'history',
        'profile', 'logout', 'login', 'register', 'my_profile', 'prediction_history',
        'farmer', 'officer', 'admin',
        
        # Actions
        'edit', 'delete', 'view', 'add', 'save', 'cancel', 'close', 'back',
        'search', 'refresh', 'export', 'approve', 'reject',
        
        # Dashboard
        'admin_dashboard', 'officer_dashboard', 'total_users', 'total_farmers',
        'total_officers', 'total_predictions', 'pending', 'add_new_farmer',
        'add_new_officer', 'add_new_admin', 'add_new_disease', 'user_activity_logs',
        'refresh_data', 'reports', 'generate_report', 'user_reports',
        'disease_reports', 'analytics',
        
        # Table headers
        'id', 'name', 'phone', 'email', 'location', 'district', 'region',
        'status', 'role', 'actions', 'registered', 'approved', 'active', 'inactive',
        
        # Disease management
        'disease_management', 'disease_name_en', 'disease_name_sw', 'scientific_name',
        
        # Prediction page
        'maize_disease_detection', 'upload_image', 'take_photo', 'click_or_drag',
        'choose_image', 'analyze_disease', 'new_prediction', 'analyzing',
        'change_image', 'retake', 'maize_leaf_only',
        
        # Results
        'diagnosis_result', 'description', 'symptoms', 'organic_treatment',
        'chemical_treatment', 'cultural_practices', 'action_plan', 'confidence',
        
        # Welcome
        'welcome_back', 'full_system_control',
        
        # Footer
        'maize_disease_system', 'helping_farmers', 'powered_by_ai', 'accuracy', 'instant_results'
    ]

    translations = {}
    for key in keys:
        translations[key] = {
            'en': lang_manager.get_text(key, 'en'),
            'sw': lang_manager.get_text(key, 'sw')
        }

    return jsonify(translations)


# ==================== PROFILE PHOTO UPLOAD ====================
@main.route("/upload-profile-photo", methods=["POST"])
@log_activity
def upload_profile_photo():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first"}), 401

    if "profile_photo" not in request.files:
        return jsonify({"success": False, "message": "No file selected"}), 400

    file = request.files["profile_photo"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    # Validate file type
    allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
    file_ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
    if file_ext not in allowed_extensions:
        return jsonify({"success": False, "message": "Invalid file type"}), 400

    # Validate file size (max 5MB)
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    if file_size > 5 * 1024 * 1024:
        return jsonify({"success": False, "message": "File too large. Max 5MB"}), 400

    try:
        # Open image
        img = Image.open(file)

        # Convert to RGB if needed
        if img.mode in ("RGBA", "LA", "P"):
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = rgb_img

        # Resize to reasonable size (500x500)
        img.thumbnail((500, 500), Image.Resampling.LANCZOS)

        # IMPORTANT: Use consistent naming format
        user_id = session["user_id"]
        unique_id = uuid.uuid4().hex[:8]
        filename = f"user_{user_id}_{unique_id}.jpg"
        filepath = os.path.join(PROFILE_FOLDER, filename)

        # Save image
        img.save(filepath, "JPEG", quality=85, optimize=True)

        # Delete old profile photo if exists
        cursor = user_db.get_cursor()
        cursor.execute(
            "SELECT profile_picture FROM maziwa WHERE user_id = %s",
            (str(session["user_id"]),),
        )
        old_photo = cursor.fetchone()

        if old_photo and old_photo.get("profile_picture"):
            old_path = os.path.join(PROFILE_FOLDER, old_photo["profile_picture"])
            if os.path.exists(old_path):
                os.remove(old_path)
                print(f"Deleted old photo: {old_path}")

        # Update database with new filename
        cursor.execute(
            "UPDATE maziwa SET profile_picture = %s WHERE user_id = %s",
            (filename, str(session["user_id"])),
        )
        db.connection.commit()
        cursor.close()

        print(f"✅ Saved new profile photo: {filename}")
        print(f"✅ Full path: {filepath}")
        print(f"✅ File exists: {os.path.exists(filepath)}")

        log_user_activity("PROFILE", "Uploaded profile photo")

        # Return the correct filename
        return jsonify(
            {
                "success": True,
                "message": "Profile photo updated successfully",
                "filename": filename,
            }
        )

    except Exception as e:
        print(f"Error uploading profile photo: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
    
@main.route("/health", methods=["GET", "HEAD"])
def health_check():
    """Health check endpoint for UptimeRobot to keep the service awake.
       This endpoint does not affect your database or application data.
    """
    return {"status": "healthy", "message": "Maize Disease Detection System is running"}


# ==================== DELETE PROFILE PHOTO ====================
@main.route("/delete-profile-photo", methods=["POST"])
@log_activity
def delete_profile_photo():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first"}), 401

    try:
        cursor = user_db.get_cursor()
        cursor.execute(
            "SELECT profile_picture FROM maziwa WHERE user_id = %s",
            (str(session["user_id"]),),
        )
        user = cursor.fetchone()

        if user and user.get("profile_picture"):
            old_path = os.path.join(PROFILE_FOLDER, user["profile_picture"])
            if os.path.exists(old_path):
                os.remove(old_path)

        cursor.execute(
            "UPDATE maziwa SET profile_picture = NULL WHERE user_id = %s",
            (str(session["user_id"]),),
        )
        db.connection.commit()
        cursor.close()

        log_user_activity("PROFILE", "Deleted profile photo")
        return jsonify(
            {"success": True, "message": "Profile photo removed successfully"}
        )

    except Exception as e:
        print(f"Error deleting profile photo: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


# ==================== CHANGE PASSWORD API ====================
@main.route("/api/change-password", methods=["POST"])
@log_activity
def api_change_password():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first"}), 401

    data = request.get_json()
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"success": False, "message": "All fields are required"}), 400

    if len(new_password) < 4:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Password must be at least 4 characters long",
                }
            ),
            400,
        )

    try:
        cursor = user_db.get_cursor()
        cursor.execute(
            "SELECT password_hash FROM maziwa WHERE user_id = %s",
            (str(session["user_id"]),),
        )
        user = cursor.fetchone()

        if not user or not check_password_hash(user["password_hash"], current_password):
            cursor.close()
            return (
                jsonify({"success": False, "message": "Current password is incorrect"}),
                400,
            )

        new_password_hash = generate_password_hash(
            new_password, method="pbkdf2:sha256", salt_length=32
        )

        cursor.execute(
            "UPDATE maziwa SET password_hash = %s, password_last_changed = CURRENT_TIMESTAMP WHERE user_id = %s",
            (new_password_hash, str(session["user_id"])),
        )
        db.connection.commit()
        cursor.close()

        log_user_activity("PROFILE", "Changed password")
        return jsonify({"success": True, "message": "Password changed successfully"})

    except Exception as e:
        print(f"Error changing password: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


# ==================== ERROR HANDLERS ====================
@main.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@main.errorhandler(403)
def forbidden_error(error):
    return render_template("403.html"), 403


@main.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500
