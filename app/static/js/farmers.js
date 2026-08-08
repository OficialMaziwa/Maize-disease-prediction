"""
MAIZE DISEASE PREDICTION SYSTEM - ROUTES
"""

from flask import (
    render_template,
    request,
    Blueprint,
    jsonify,
    session,
    redirect,
    url_for,
    flash,
    send_file,
    abort,
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
from PIL import Image, ImageOps, UnidentifiedImageError
import os
import base64
import io
import uuid
import re
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# APP IMPORTS
try:
    from app.user_db import user_db
    from app.disease_engine import MaizeDiseaseDetector
    from app.language_manager import lang_manager
    from app.logger_config import security_logger
except ImportError as e:
    print(f"Import error: {e}")
    class SimpleLogger:
        def log_access(self, *args, **kwargs): pass
        def log_security_event(self, *args, **kwargs): pass
        def log_auth_event(self, *args, **kwargs): pass
        def log_error(self, *args, **kwargs): pass
        def log_db_operation(self, *args, **kwargs): pass
        def log_api_call(self, *args, **kwargs): pass
        def detect_attack_patterns(self, *args, **kwargs): return False
        def _get_client_ip(self): return "N/A"
        def _get_user_agent(self): return "N/A"
    security_logger = SimpleLogger()

# INITIALIZATION
main = Blueprint("main", __name__)
db = user_db
detector = MaizeDiseaseDetector(model_path=None)

# CONFIGURATION
UPLOAD_FOLDER = "uploads/"
PROFILE_FOLDER = "static/profile_photos/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}

# GMAIL CONFIGURATION
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "malabamalaba26@gmail.com"
MAIL_PASSWORD = "uzvzcvsyyzzysmun"
MAIL_FROM = "malabamalaba26@gmail.com"
APP_URL = "http://localhost:5000"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROFILE_FOLDER, exist_ok=True)

logger = logging.getLogger(__name__)


# EMAIL FUNCTION
def send_email(to_email, subject, html_content, text_content=None):
    """Send email using Mailtrap SMTP directly (no Flask-Mail)"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = MAIL_FROM
        msg['To'] = to_email

        if text_content is None:
            text_content = html_content.replace('<br>', '\n').replace('</p>', '\n')
            text_content = re.sub(r'<[^>]+>', '', text_content)

        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send via Mailtrap SMTP
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, [to_email], msg.as_string())
        
        print(f" Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f" Email error: {e}")
        return False


def send_approval_email(email, officer_name, admin_name):
    """Send account approval email"""
    if not email:
        print("No email address provided")
        return False
    
    subject = "Account Approved - Maize Disease Detection System"
    
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
                <h2>Maize Disease Detection System</h2>
            </div>
            <div class="content">
                <h3>Congratulations, {officer_name}!</h3>
                <p>Your account has been <strong>APPROVED</strong> by <strong>{admin_name}</strong>.</p>
                <p>You can now login to the system and start helping farmers detect maize diseases.</p>
                <p style="text-align: center;">
                    <a href="{APP_URL}/login" class="button">Login to Your Account</a>
                </p>
                <p><strong>Login credentials:</strong><br>
                Phone number: Your registered phone number<br>
                Password: Your chosen password</p>
                <p><em>If you have any questions, please contact the system administrator.</em></p>
            </div>
            <div class="footer">
                <p>Maize Disease Detection System - Helping Farmers Make Better Decisions</p>
                <p>2024 All Rights Reserved</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    CONGRATULATIONS! Dear {officer_name},
    
    Your account has been APPROVED by {admin_name}.
    
    You can now login to the Maize Disease Detection System:
    Login URL: {APP_URL}/login
    
    Use your phone number and password to login.
    
    Maize Disease Detection System
    """
    
    return send_email(email, subject, html_content, text_content)


# HELPER FUNCTIONS
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

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def table_has_column(cursor, table_name, column_name):
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        )
        """,
        (table_name, column_name),
    )
    result = cursor.fetchone()
    if isinstance(result, dict):
        return bool(result.get("exists"))
    return bool(result[0]) if result else False

def sanitize_input(input_string):
    if not input_string:
        return ""
    return re.sub(r"<[^>]*>", "", input_string)

def validate_phone_number(phone):
    pattern = r"^(0[67]\d{8}|255[67]\d{8})$"
    return bool(re.match(pattern, phone))

def secure_session():
    session.permanent = True
    session.permanent_session_lifetime = timedelta(hours=2)
    if not session.get("_fresh"):
        if hasattr(session, "regenerate"):
            session.regenerate()
        session["_fresh"] = True

def is_maize_leaf(image_path):
    try:
        import numpy as np
        if not os.path.exists(image_path):
            return True, 50, "Image file not found, assuming it's a leaf"
        try:
            img = Image.open(image_path)
            if img.mode != "RGB":
                img = img.convert("RGB")
        except Exception:
            return True, 50, "Could not open image, assuming it's a leaf"
        try:
            img_array = np.array(img)
        except Exception:
            return True, 50, "Could not process image, assuming it's a leaf"
        height, width = img_array.shape[0], img_array.shape[1]
        if height < 30 or width < 30:
            return False, 10, "Image is too small. Please upload a larger image."
        try:
            avg_color = np.mean(img_array, axis=(0, 1))
        except Exception:
            return True, 50, "Could not analyze colors, assuming it's a leaf"
        total = avg_color[0] + avg_color[1] + avg_color[2] + 0.001
        green_ratio = avg_color[1] / total
        has_green = avg_color[1] > avg_color[0] and avg_color[1] > avg_color[2]
        try:
            green_mask = (img_array[:, :, 1] > img_array[:, :, 0]) & (
                img_array[:, :, 1] > img_array[:, :, 2]
            )
            green_percentage = np.sum(green_mask) / (height * width)
        except Exception:
            green_percentage = 0.2
        try:
            gray = np.mean(img_array, axis=2)
            sample_h = min(100, height)
            sample_w = min(100, width)
            gray_sample = gray[:sample_h, :sample_w]
            grad_h = np.abs(np.diff(gray_sample, axis=0))
            grad_w = np.abs(np.diff(gray_sample, axis=1))
            if grad_h.size > 0 and grad_w.size > 0:
                edge_density = (np.mean(grad_h) + np.mean(grad_w)) / 2
            else:
                edge_density = 5
        except Exception:
            edge_density = 5
        is_leaf = green_ratio > 0.20 and green_percentage > 0.08 and has_green
        if green_ratio < 0.10 or green_percentage < 0.05:
            is_leaf = False
        confidence = min(100, ((green_ratio * 100 + green_percentage * 100 + (edge_density / 10)) / 3))
        confidence = max(0, min(100, confidence))
        if is_leaf:
            return True, round(confidence, 1), "Maize leaf detected"
        else:
            return False, round(confidence, 1), "Not a maize leaf. Please upload an image of a maize leaf."
    except ImportError:
        return True, 50, "Could not verify image (numpy missing), assuming it's a leaf"
    except Exception:
        return True, 50, "Could not verify image, assuming it's a leaf"

def log_user_activity(activity_type, activity_details, status_code=200, response_time_ms=0, additional_data=None):
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
            status_code = response.status_code if hasattr(response, "status_code") else 200
            security_logger.log_access(status_code, duration)
        except:
            pass
        return response
    return decorated_function


# LANGUAGE ROUTES
@main.before_request
def set_language():
    if "language" not in session:
        session["language"] = "en"

@main.context_processor
def utility_processor():
    def t(key, language=None):
        if not isinstance(language, str):
            language = session.get("language", "en")
        return lang_manager.get_text(key, language)
    current_language = session.get("language", "en")
    return dict(t=t, lang=current_language, current_lang=current_language)

@main.route("/change-language-ajax/<lang>", methods=["POST"])
def change_language_ajax(lang):
    if lang not in ["en", "sw"]:
        return jsonify({"success": False, "message": "Invalid language"}), 400
    try:
        session["language"] = lang
        if "user_id" in session:
            if ensure_db_connection():
                cursor = user_db.get_cursor(dictionary=False)
                cursor.execute(
                    "UPDATE maziwa SET language_preference = %s WHERE user_id = %s",
                    (lang, session["user_id"]),
                )
                user_db.connection.commit()
                cursor.close()
        return jsonify({"success": True, "message": f"Language changed to {lang}", "language": lang})
    except Exception as e:
        print(f"Error changing language: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

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


# AUTHENTICATION ROUTES
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
            return render_template("register.html", lang=lang, t=lang_manager.get_text, request=request)
        if not validate_phone_number(phone_number):
            flash("Please enter a valid phone number", "danger")
            return render_template("register.html", lang=lang, t=lang_manager.get_text, request=request)
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("register.html", lang=lang, t=lang_manager.get_text, request=request)
        if not ensure_db_connection():
            flash("Database connection error", "danger")
            return render_template("register.html", lang=lang, t=lang_manager.get_text, request=request)
        cursor = user_db.get_cursor()
        cursor.execute("SELECT user_id FROM maziwa WHERE phone_number = %s", (phone_number,))
        if cursor.fetchone():
            cursor.close()
            flash("Phone number already registered", "danger")
            return render_template("register.html", lang=lang, t=lang_manager.get_text, request=request)
        if email:
            cursor.execute("SELECT user_id FROM maziwa WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                flash("Email already registered", "danger")
                return render_template("register.html", lang=lang, t=lang_manager.get_text, request=request)
        password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=32)
        is_approved = 1 if role == "farmer" else 0
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
                    request.user_agent.string if hasattr(request, "user_agent") else None,
                ),
            )
            user_db.connection.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("main.login"))
        except Exception as e:
            user_db.connection.rollback()
            print(f"Registration error: {e}")
            flash("Registration failed. Please try again.", "danger")
        finally:
            cursor.close()
    return render_template("register.html", lang=lang, t=lang_manager.get_text, request=request)

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
            return render_template("login.html", lang=lang, t=lang_manager.get_text, request=request)
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
                    return render_template("login.html", lang=lang, t=lang_manager.get_text, request=request)
                if user["role"] == "extension_officer" and user["is_approved"] == 0:
                    flash("Your account is pending approval by admin.", "warning")
                    cursor.close()
                    return render_template("login.html", lang=lang, t=lang_manager.get_text, request=request)
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
    return render_template("login.html", lang=lang, t=lang_manager.get_text, request=request)

@main.route("/logout")
@log_activity
def logout():
    user_id = session.get("user_id")
    if user_id:
        log_user_activity("LOGOUT", "User logged out")
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("main.index"))


# PUBLIC PAGES ROUTES
@main.route("/")
@main.route("/home")
def index():
    lang = session.get("language", "en")
    return render_template("index.html", lang=lang, t=lang_manager.get_text, request=request)

@main.route("/about")
def about():
    lang = session.get("language", "en")
    return render_template("about.html", lang=lang, t=lang_manager.get_text, request=request)

@main.route("/dashboard")
def dashboard():
    lang = session.get("language", "en")
    user_role = session.get("user_role")
    if "user_id" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("main.login"))
    if user_role == "admin":
        return redirect(url_for("main.admin_dashboard"))
    elif user_role == "extension_officer":
        return redirect(url_for("main.officer_dashboard"))
    else:
        return redirect(url_for("main.predict"))

@main.route("/history")
def history():
    if "user_id" not in session:
        flash("Please login to view history", "warning")
        return redirect(url_for("main.login"))
    lang = session.get("language", "en")
    return render_template("history.html", lang=lang, t=lang_manager.get_text, request=request)


# USER PROFILE ROUTES
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
    return render_template("profile.html", lang=lang, t=lang_manager.get_text, user=user, request=request)


# PROFILE PHOTO ROUTES
@main.route("/profile-photo/<filename>")
def serve_profile_photo(filename):
    if "user_id" not in session:
        abort(403)
    if filename.startswith("user_"):
        parts = filename.split("_")
        if len(parts) >= 2:
            photo_user_id = parts[1]
            if photo_user_id != str(session.get("user_id")) and session.get("user_role") != "admin":
                abort(403)
    filepath = os.path.join(PROFILE_FOLDER, filename)
    if not os.path.exists(filepath):
        abort(404)
    response = send_file(filepath, mimetype="image/jpeg")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

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
    file_ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        return jsonify({"success": False, "message": "Invalid file type"}), 400
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    if file_size > 5 * 1024 * 1024:
        return jsonify({"success": False, "message": "File too large. Max 5MB"}), 400
    try:
        img = Image.open(file)
        if img.mode in ("RGBA", "LA", "P"):
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            if img.mode == "RGBA":
                rgb_img.paste(img, mask=img.split()[-1])
            else:
                rgb_img.paste(img)
            img = rgb_img
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.thumbnail((500, 500), Image.Resampling.LANCZOS)
        user_id = session["user_id"]
        unique_id = uuid.uuid4().hex[:8]
        filename = f"user_{user_id}_{unique_id}.jpg"
        filepath = os.path.join(PROFILE_FOLDER, filename)
        img.save(filepath, "JPEG", quality=85, optimize=True)
        cursor = user_db.get_cursor()
        cursor.execute(
            "SELECT profile_picture FROM maziwa WHERE user_id = %s",
            (str(session["user_id"]),),
        )
        old_photo = cursor.fetchone()
        if old_photo and old_photo.get("profile_picture"):
            old_path = os.path.join(PROFILE_FOLDER, old_photo["profile_picture"])
            if os.path.exists(old_path) and old_path != filepath:
                try:
                    os.remove(old_path)
                except:
                    pass
        cursor.execute(
            "UPDATE maziwa SET profile_picture = %s WHERE user_id = %s",
            (filename, str(session["user_id"])),
        )
        db.connection.commit()
        cursor.close()
        log_user_activity("PROFILE", "Uploaded profile photo")
        return jsonify({
            "success": True,
            "message": "Profile photo updated successfully",
            "filename": filename,
            "image_url": url_for("main.serve_profile_photo", filename=filename)
        })
    except Exception as e:
        print(f"Error uploading profile photo: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

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
        return jsonify({"success": True, "message": "Profile photo removed successfully"})
    except Exception as e:
        print(f"Error deleting profile photo: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


# DISEASE PREDICTION ROUTES
@main.route("/predict", methods=["GET"])
def predict():
    lang = session.get("language", "en")
    return render_template("predict.html", lang=lang, t=lang_manager.get_text, request=request)

@main.route("/api/predict", methods=["POST"])
@log_activity
def api_predict():
    temp_path = None
    try:
        language = request.cookies.get("language", session.get("language", "en"))
        if not request.is_json:
            return jsonify({"success": False, "error": "Invalid request format"}), 400
        data = request.get_json()
        image_data = data.get("image")
        if not image_data:
            return jsonify({"success": False, "error": "No image data provided"}), 400
        if "," in image_data:
            image_data = image_data.split(",")[1]
        if not image_data or len(image_data) < 100:
            return jsonify({"success": False, "error": "Invalid image data"}), 400
        try:
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
            img = ImageOps.exif_transpose(img)
        except UnidentifiedImageError:
            return jsonify({
                "success": False,
                "error": "Unsupported image format. Please upload JPG, PNG, WEBP, GIF, or BMP."
            }), 400
        except Exception as e:
            print(f"Image decode error: {e}")
            return jsonify({"success": False, "error": "Failed to process image"}), 400
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        img.thumbnail((224, 224), Image.Resampling.LANCZOS)
        temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        img.save(temp_path, "JPEG", quality=85, optimize=True)
        try:
            is_leaf, leaf_confidence, leaf_message = is_maize_leaf(temp_path)
            print(f"Leaf validation: is_leaf={is_leaf}, confidence={leaf_confidence}%, message={leaf_message}")
        except Exception as e:
            print(f"Leaf validation error: {e}")
            is_leaf = True
            leaf_confidence = 50
            leaf_message = "Could not verify image, proceeding with prediction"
        if not is_leaf or leaf_confidence < 30:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            error_msg = "This image is not a maize leaf. Please upload a clear image of a maize leaf."
            if language == "sw":
                error_msg = "Picha hii sio jani la mahindi. Tafadhali pakia picha ya jani la mahindi iliyo wazi."
            return jsonify({
                "success": False,
                "is_maize_leaf": False,
                "leaf_confidence": leaf_confidence,
                "leaf_message": "Not a maize leaf" if language == "en" else "Sio jani la mahindi",
                "error": error_msg,
                "disease": "Invalid Image",
                "confidence": 0
            }), 400
        import tensorflow as tf
        from tensorflow.keras.preprocessing import image as keras_image
        import numpy as np
        try:
            gpus = tf.config.experimental.list_physical_devices("GPU")
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
            else:
                tf.config.threading.set_intra_op_parallelism_threads(1)
                tf.config.threading.set_inter_op_parallelism_threads(1)
        except Exception as e:
            print(f"Could not configure TF memory: {e}")
        model_path = "app/models/maize_disease_model.h5"
        disease_name = "Healthy"
        confidence = 85.5
        try:
            if os.path.exists(model_path):
                print(f"Loading model from {model_path}")
                model = tf.keras.models.load_model(model_path, compile=False)
                class_names_path = "class_names.json"
                if os.path.exists(class_names_path):
                    with open(class_names_path, "r") as f:
                        class_names = json.load(f)
                    if isinstance(class_names, dict) and "class_names" in class_names:
                        class_names = class_names["class_names"]
                else:
                    class_names = ["Blight", "Common_Rust", "Gray_Leaf_Spot", "Healthy"]
                img_pred = keras_image.load_img(temp_path, target_size=(224, 224))
                img_array = keras_image.img_to_array(img_pred)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = img_array / 255.0
                predictions = model.predict(img_array, verbose=0)
                predicted_idx = np.argmax(predictions[0])
                confidence = float(predictions[0][predicted_idx] * 100)
                disease_name = class_names[predicted_idx] if class_names else "Unknown"
                print(f"API Prediction: {disease_name} ({confidence:.1f}%)")
                del model
                tf.keras.backend.clear_session()
            else:
                print(f"Model not found at {model_path}")
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                return jsonify({
                    "success": False,
                    "error": "Model not found. Please contact administrator.",
                    "disease": "Unknown",
                    "confidence": 0
                }), 500
        except Exception as model_error:
            print(f"Model prediction error: {model_error}")
            import traceback
            traceback.print_exc()
            try:
                tf.keras.backend.clear_session()
            except:
                pass
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return jsonify({
                "success": False,
                "error": f"Model error: {str(model_error)}",
                "disease": "Unknown",
                "confidence": 0
            }), 500
        disease_info = None
        disease_id = None
        try:
            if ensure_db_connection():
                cursor = user_db.get_cursor()
                cursor.execute("SELECT * FROM diseases WHERE disease_name_en = %s", (disease_name,))
                disease_info = cursor.fetchone()
                if disease_info:
                    disease_id = disease_info.get("disease_id")
                cursor.close()
        except Exception as db_error:
            print(f"Database error: {db_error}")
        if language == "sw":
            display_disease_name = disease_info["disease_name_sw"] if disease_info else disease_name
            description = disease_info["description_sw"] if disease_info else "Maelezo hayapatikani."
            symptoms = disease_info["symptoms_sw"] if disease_info else "Dalili hazipatikani."
            treatment = disease_info["treatment_sw"] if disease_info else "Matibabu hayapatikani."
            organic = disease_info.get("organic_treatment_sw", "").split("|") if disease_info else []
            chemical = disease_info.get("chemical_treatment_sw", "").split("|") if disease_info else []
            cultural = disease_info.get("cultural_practices_sw", "").split("|") if disease_info else []
            action = disease_info.get("action_plan_sw", "").split("|") if disease_info else []
        else:
            display_disease_name = disease_info["disease_name_en"] if disease_info else disease_name
            description = disease_info["description_en"] if disease_info else "No description available."
            symptoms = disease_info["symptoms_en"] if disease_info else "No symptoms information available."
            treatment = disease_info["treatment_en"] if disease_info else "No treatment information available."
            organic = disease_info.get("organic_treatment_en", "").split("|") if disease_info else []
            chemical = disease_info.get("chemical_treatment_en", "").split("|") if disease_info else []
            cultural = disease_info.get("cultural_practices_en", "").split("|") if disease_info else []
            action = disease_info.get("action_plan_en", "").split("|") if disease_info else []
        organic = [item.strip() for item in organic if item.strip()]
        chemical = [item.strip() for item in chemical if item.strip()]
        cultural = [item.strip() for item in cultural if item.strip()]
        action = [item.strip() for item in action if item.strip()]
        try:
            if "user_id" in session and ensure_db_connection():
                cursor = user_db.get_cursor(dictionary=False)
                # FIX: Convert confidence to float before saving
                confidence_float = float(confidence)
                cursor.execute(
                    """
                    INSERT INTO diagnosis_history
                    (user_id, disease_id, disease_name, confidence_score, image_path)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        session["user_id"],
                        disease_id,
                        disease_name,
                        confidence_float,
                        temp_path,
                    ),
                )
                user_db.connection.commit()
                cursor.close()
        except Exception as history_error:
            print(f"Failed to save prediction history: {history_error}")
        session["last_prediction_result"] = {
            "disease": display_disease_name,
            "confidence": confidence,
            "description": description,
            "symptoms": symptoms,
            "treatment": treatment,
            "organic_treatment": organic,
            "chemical_treatment": chemical,
            "cultural_practices": cultural,
            "action_plan": action,
        }
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return jsonify({
            "success": True,
            "is_maize_leaf": True,
            "leaf_confidence": leaf_confidence,
            "leaf_message": "Maize leaf detected" if language == "en" else "Jani la mahindi limegunduliwa",
            "disease": display_disease_name,
            "confidence": round(confidence, 2),
            "description": description,
            "symptoms": symptoms,
            "treatment": treatment,
            "organic_treatment": organic,
            "chemical_treatment": chemical,
            "cultural_practices": cultural,
            "action_plan": action,
            "result_url": url_for("main.result"),
        })
    except Exception as e:
        print(f"Error in API prediction: {e}")
        import traceback
        traceback.print_exc()
        try:
            import tensorflow as tf
            tf.keras.backend.clear_session()
        except:
            pass
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return jsonify({
            "success": False,
            "error": "Server error during prediction. Please try again.",
            "disease": "Unknown",
            "confidence": 0
        }), 500

@main.route("/result")
def result():
    lang = session.get("language", "en")
    stored_result = session.get("last_prediction_result", {})
    disease = request.args.get("disease") or stored_result.get("disease", "Unknown")
    
    # FIX: Handle confidence as float
    confidence = request.args.get("confidence") or stored_result.get("confidence", "0")
    try:
        confidence = float(confidence)
    except (ValueError, TypeError):
        confidence = 0.0
    
    description = request.args.get("description") or stored_result.get("description", "No description available.")
    symptoms = request.args.get("symptoms") or stored_result.get("symptoms", "No symptoms information available.")
    treatment = request.args.get("treatment") or stored_result.get("treatment", "No treatment information available.")
    image_data = request.args.get("image_data", "")
    try:
        organic = json.loads(request.args.get("organic")) if request.args.get("organic") else stored_result.get("organic_treatment", [])
        chemical = json.loads(request.args.get("chemical")) if request.args.get("chemical") else stored_result.get("chemical_treatment", [])
        cultural = json.loads(request.args.get("cultural")) if request.args.get("cultural") else stored_result.get("cultural_practices", [])
        action = json.loads(request.args.get("action")) if request.args.get("action") else stored_result.get("action_plan", [])
    except:
        organic = []
        chemical = []
        cultural = []
        action = []
    try:
        confidence = float(confidence)
    except:
        confidence = 0.0
    severity = "Low"
    if disease.lower() != "healthy":
        if confidence > 80:
            severity = "High"
        elif confidence > 50:
            severity = "Medium"
    confidence_level = "Medium"
    if confidence > 80:
        confidence_level = "Very High"
    elif confidence > 70:
        confidence_level = "High"
    elif confidence > 50:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"
    report_data = {
        "detection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "follow_up": "Re-evaluate after 7 days",
    }
    return render_template(
        "result.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        disease=disease,
        confidence=confidence,
        description=description,
        symptoms=symptoms,
        treatment=treatment,
        organic_treatment=organic,
        chemical_treatment=chemical,
        cultural_practices=cultural,
        action_plan=action,
        detection_date=report_data["detection_date"],
        disease_name=disease,
        severity=severity,
        confidence_level=confidence_level,
        economic_impact="Significant yield losses if not controlled promptly",
        response_deadline="Immediate action required",
        monitoring_frequency="Weekly monitoring recommended",
        follow_up=report_data["follow_up"],
        image_data=image_data,
    )



# ADMIN ROUTES


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
        cursor.execute("SELECT * FROM maziwa WHERE LOWER(role) = LOWER('farmer') ORDER BY created_at DESC")
        farmers = cursor.fetchall() or []
        cursor.execute("SELECT * FROM maziwa WHERE LOWER(role) = LOWER('extension_officer') ORDER BY created_at DESC")
        officers = cursor.fetchall() or []
        cursor.execute("SELECT * FROM maziwa WHERE LOWER(role) = LOWER('admin') ORDER BY created_at DESC")
        admins = cursor.fetchall() or []
        cursor.execute("SELECT * FROM maziwa WHERE LOWER(role) = LOWER('extension_officer') AND (is_approved = 0 OR is_approved IS NULL) ORDER BY created_at DESC")
        pending_officers = cursor.fetchall() or []
        cursor.execute("SELECT * FROM diseases ORDER BY disease_id")
        all_diseases = cursor.fetchall() or []
        diseases = []
        model_classes = ["Blight", "Common_Rust", "Gray_Leaf_Spot", "Healthy"]
        for d in all_diseases:
            if d.get("disease_name_en") in model_classes:
                diseases.append(d)
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
        )
    except Exception as e:
        print(f"ERROR in admin_dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash(f"Error loading dashboard: {str(e)}", "danger")
        return redirect(url_for("main.index"))

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
        is_active = 1 if request.form.get("is_active") == "on" else 0
        is_approved = 1 if request.form.get("is_approved") == "on" else 0
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

@main.route("/admin/user/<user_id>/delete", methods=["DELETE"])
@log_activity
def admin_delete_user(user_id):
    if session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    if str(user_id) == str(session.get("user_id")):
        return jsonify({"success": False, "message": "Cannot delete your own account"}), 400
    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500
    cursor = None
    try:
        cursor = user_db.get_cursor(dictionary=False)
        cursor.execute("DELETE FROM public.diagnosis_history WHERE user_id = %s", (str(user_id),))
        cursor.execute("DELETE FROM public.in_app_notifications WHERE user_id = %s", (str(user_id),))
        cursor.execute("DELETE FROM public.notifications WHERE user_id = %s", (str(user_id),))
        cursor.execute("DELETE FROM public.user_activity_logs WHERE user_id = %s", (str(user_id),))
        cursor.execute("DELETE FROM public.user_sessions WHERE user_id = %s", (str(user_id),))
        cursor.execute("DELETE FROM public.login_attempts WHERE user_id = %s", (str(user_id),))
        cursor.execute("DELETE FROM public.maziwa WHERE user_id = %s", (str(user_id),))
        user_db.connection.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        if affected_rows > 0:
            log_user_activity("ADMIN_ACTION", f"Deleted user ID: {user_id} with all related data")
            return jsonify({"success": True, "message": "User and all related data deleted successfully"})
        return jsonify({"success": False, "message": "User not found"}), 404
    except Exception as e:
        if user_db.connection:
            user_db.connection.rollback()
        print(f"Error deleting user: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()

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
            """SELECT user_id, full_name, phone_number, email, region, is_approved 
            FROM maziwa WHERE user_id = %s AND LOWER(role) = LOWER('extension_officer')""",
            (user_id,),
        )
        officer = cursor.fetchone()
        if not officer:
            cursor.close()
            return jsonify({"success": False, "message": "Officer not found"}), 404
        if officer.get("is_approved") == 1:
            cursor.close()
            return jsonify({"success": False, "message": "Officer already approved"}), 400
        update_fields = ["is_approved = 1", "is_active = 1"]
        params = []
        if table_has_column(cursor, "maziwa", "approved_at"):
            update_fields.append("approved_at = CURRENT_TIMESTAMP")
        if table_has_column(cursor, "maziwa", "approved_by"):
            update_fields.append("approved_by = %s")
            params.append(session.get("user_id"))
        if table_has_column(cursor, "maziwa", "rejection_reason"):
            update_fields.append("rejection_reason = NULL")
        params.append(user_id)
        cursor.execute(
            f"UPDATE maziwa SET {', '.join(update_fields)} WHERE user_id = %s", params
        )
        db.connection.commit()
        cursor.close()
        admin_name = session.get("user_name", "Admin")
        officer_name = officer["full_name"]
        officer_email = officer.get("email")
        email_sent = False
        if officer_email:
            email_sent = send_approval_email(officer_email, officer_name, admin_name)
        if email_sent:
            message = f"Officer {officer_name} approved! Email sent to {officer_email}"
        else:
            message = f"Officer {officer_name} approved successfully! (Email not sent - no email address or mail service error)"
        return jsonify({"success": True, "message": message})
    except Exception as e:
        print(f"Error approving officer: {e}")
        try:
            db.connection.rollback()
        except:
            pass
        return jsonify({"success": False, "message": str(e)}), 500

@main.route("/admin/officer/<user_id>/reject", methods=["POST"])
@log_activity
def admin_reject_officer(user_id):
    if session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500
    data = request.get_json(silent=True) or {}
    reason = sanitize_input(data.get("reason", "")).strip()
    if not reason:
        reason = "Application rejected by admin"
    try:
        cursor = user_db.get_cursor()
        cursor.execute(
            """SELECT user_id, full_name, email, is_approved
            FROM maziwa WHERE user_id = %s AND LOWER(role) = LOWER('extension_officer')""",
            (user_id,),
        )
        officer = cursor.fetchone()
        if not officer:
            cursor.close()
            return jsonify({"success": False, "message": "Officer not found"}), 404
        update_fields = ["is_approved = 0", "is_active = 0"]
        params = []
        if table_has_column(cursor, "maziwa", "rejection_reason"):
            update_fields.append("rejection_reason = %s")
            params.append(reason)
        if table_has_column(cursor, "maziwa", "approved_at"):
            update_fields.append("approved_at = NULL")
        if table_has_column(cursor, "maziwa", "approved_by"):
            update_fields.append("approved_by = NULL")
        params.append(user_id)
        cursor.execute(
            f"UPDATE maziwa SET {', '.join(update_fields)} WHERE user_id = %s", params
        )
        db.connection.commit()
        cursor.close()
        log_user_activity(
            "ADMIN_ACTION",
            f"Rejected extension officer ID: {user_id}",
            additional_data={"reason": reason},
        )
        return jsonify({"success": True, "message": f"Officer {officer['full_name']} rejected successfully."})
    except Exception as e:
        print(f"Error rejecting officer: {e}")
        try:
            db.connection.rollback()
        except:
            pass
        return jsonify({"success": False, "message": str(e)}), 500

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
            params.append(1 if data["is_active"] else 0)
        if "is_approved" in data:
            update_fields.append("is_approved = %s")
            params.append(1 if data["is_approved"] else 0)
            if data["is_approved"] == True:
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
            activities.append({
                "activity_id": row.get("activity_id"),
                "user_id": row.get("user_id"),
                "user_name": row.get("user_name") or "Unknown",
                "user_role": row.get("user_role") or "N/A",
                "activity_type": row.get("activity_type") or "N/A",
                "activity_details": row.get("activity_details") or "",
                "ip_address": row.get("ip_address") or "N/A",
                "created_at": created_at,
            })
        cursor.execute("SELECT COUNT(*) as count FROM user_activity_logs WHERE activity_type = 'LOGIN'")
        total_logins = cursor.fetchone()["count"] or 0
        cursor.execute("SELECT COUNT(*) as count FROM user_activity_logs WHERE activity_type = 'LOGOUT'")
        total_logouts = cursor.fetchone()["count"] or 0
        cursor.execute("SELECT COUNT(*) as count FROM user_activity_logs WHERE activity_type = 'PREDICTION'")
        total_predictions = cursor.fetchone()["count"] or 0
        cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM user_activity_logs")
        active_users = cursor.fetchone()["count"] or 0
        cursor.close()
        return jsonify({
            "success": True,
            "activities": activities,
            "stats": {
                "total_logins": total_logins,
                "total_logouts": total_logouts,
                "total_predictions": total_predictions,
                "active_users": active_users,
            },
        })
    except Exception as e:
        return jsonify({
            "success": True,
            "activities": [],
            "stats": {"total_logins": 0, "total_logouts": 0, "total_predictions": 0, "active_users": 0},
        }), 200

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
        cursor.execute("SELECT COUNT(*) as count FROM maziwa WHERE LOWER(role) = LOWER('farmer')")
        total_farmers = cursor.fetchone()["count"] or 0
        cursor.execute("SELECT COUNT(*) as count FROM maziwa WHERE LOWER(role) = LOWER('extension_officer')")
        total_officers = cursor.fetchone()["count"] or 0
        cursor.execute("SELECT COUNT(*) as count FROM maziwa WHERE LOWER(role) = LOWER('admin')")
        total_admins = cursor.fetchone()["count"] or 0
        cursor.execute("SELECT COUNT(*) as count FROM maziwa WHERE LOWER(role) = LOWER('extension_officer') AND (is_approved = 0 OR is_approved IS NULL)")
        pending_officers = cursor.fetchone()["count"] or 0
        cursor.execute("SELECT COUNT(*) as count FROM diagnosis_history")
        total_predictions = cursor.fetchone()["count"] or 0
        cursor.execute("SELECT COUNT(*) as count FROM diseases")
        total_diseases = cursor.fetchone()["count"] or 0
        cursor.close()
        return jsonify({
            "success": True,
            "total_users": total_users,
            "total_farmers": total_farmers,
            "total_officers": total_officers,
            "total_admins": total_admins,
            "pending_officers": pending_officers,
            "total_predictions": total_predictions,
            "total_diseases": total_diseases,
        })
    except Exception as e:
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
            SELECT user_id, full_name, phone_number, email, region, role, is_approved, is_active
            FROM maziwa
            ORDER BY full_name
        """)
        users = cursor.fetchall()
        cursor.close()
        return jsonify({"success": True, "users": users})
    except Exception as e:
        print(f"Error in api_users_list: {e}")
        return jsonify({"success": True, "users": []}), 200


# ADMIN ADD USER ROUTES
@main.route("/admin/farmer/add", methods=["GET", "POST"])
@log_activity
def admin_add_farmer():
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    lang = session.get("language", "en")

    if request.method == "POST":
        full_name = sanitize_input(request.form.get("full_name", "").strip())
        phone_number = sanitize_input(request.form.get("phone_number", "").strip())
        email = sanitize_input(request.form.get("email", "").strip())
        password = request.form.get("password", "")
        location = sanitize_input(request.form.get("location", "").strip())
        district = sanitize_input(request.form.get("district", "").strip())
        region = sanitize_input(request.form.get("region", "").strip())

        if not full_name or not phone_number or not password:
            flash("Full name, phone number and password are required", "danger")
            return redirect(url_for("main.admin_add_farmer"))

        if not validate_phone_number(phone_number):
            flash("Invalid phone number", "danger")
            return redirect(url_for("main.admin_add_farmer"))

        cursor = user_db.get_cursor()
        cursor.execute("SELECT user_id FROM maziwa WHERE phone_number = %s", (phone_number,))
        if cursor.fetchone():
            cursor.close()
            flash("Phone number already registered", "danger")
            return redirect(url_for("main.admin_add_farmer"))

        password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=32)

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
                    "farmer",
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

    return render_template(
        "admin_add_user.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        user_role="farmer",
        title="Add New Farmer"
    )


@main.route("/admin/officer/add", methods=["GET", "POST"])
@log_activity
def admin_add_officer():
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    lang = session.get("language", "en")

    if request.method == "POST":
        full_name = sanitize_input(request.form.get("full_name", "").strip())
        phone_number = sanitize_input(request.form.get("phone_number", "").strip())
        email = sanitize_input(request.form.get("email", "").strip())
        password = request.form.get("password", "")
        region = sanitize_input(request.form.get("region", "").strip())

        if not full_name or not phone_number or not password:
            flash("Full name, phone number and password are required", "danger")
            return redirect(url_for("main.admin_add_officer"))

        if not validate_phone_number(phone_number):
            flash("Invalid phone number", "danger")
            return redirect(url_for("main.admin_add_officer"))

        cursor = user_db.get_cursor()
        cursor.execute("SELECT user_id FROM maziwa WHERE phone_number = %s", (phone_number,))
        if cursor.fetchone():
            cursor.close()
            flash("Phone number already registered", "danger")
            return redirect(url_for("main.admin_add_officer"))

        password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=32)

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
                    "extension_officer",
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

    return render_template(
        "admin_add_user.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        user_role="officer",
        title="Add New Extension Officer"
    )


@main.route("/admin/admin/add", methods=["GET", "POST"])
@log_activity
def admin_add_admin():
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    lang = session.get("language", "en")

    if request.method == "POST":
        full_name = sanitize_input(request.form.get("full_name", "").strip())
        phone_number = sanitize_input(request.form.get("phone_number", "").strip())
        email = sanitize_input(request.form.get("email", "").strip())
        password = request.form.get("password", "")

        if not full_name or not phone_number or not password:
            flash("Full name, phone number and password are required", "danger")
            return redirect(url_for("main.admin_add_admin"))

        if not validate_phone_number(phone_number):
            flash("Invalid phone number", "danger")
            return redirect(url_for("main.admin_add_admin"))

        cursor = user_db.get_cursor()
        cursor.execute("SELECT user_id FROM maziwa WHERE phone_number = %s", (phone_number,))
        if cursor.fetchone():
            cursor.close()
            flash("Phone number already registered", "danger")
            return redirect(url_for("main.admin_add_admin"))

        password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=32)

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
                    "admin",
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

    return render_template(
        "admin_add_user.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        user_role="admin",
        title="Add New Admin"
    )


# ADMIN DISEASE MANAGEMENT ROUTES
@main.route("/admin/disease/<int:disease_id>/view")
@log_activity
def admin_view_disease(disease_id):
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))
    try:
        cursor = user_db.get_cursor()
        cursor.execute("SELECT * FROM diseases WHERE disease_id = %s", (str(disease_id),))
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


@main.route("/admin/disease/<int:disease_id>/edit", methods=["GET", "POST"])
@log_activity
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


@main.route("/admin/disease/<int:disease_id>/delete", methods=["DELETE"])
@log_activity
def admin_delete_disease(disease_id):
    if session.get("user_role") != "admin":
        return jsonify({"success": False, "message": "Access denied"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500

    try:
        cursor = user_db.get_cursor(dictionary=False)
        cursor.execute("SELECT disease_id FROM diseases WHERE disease_id = %s", (str(disease_id),))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"success": False, "message": "Disease not found"}), 404

        cursor.execute("DELETE FROM diseases WHERE disease_id = %s", (str(disease_id),))
        db.connection.commit()
        cursor.close()

        log_user_activity("ADMIN_ACTION", f"Deleted disease ID: {disease_id}")
        return jsonify({"success": True, "message": "Disease deleted successfully"})
    except Exception as e:
        print(f"Error deleting disease: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@main.route("/admin/disease/add", methods=["GET", "POST"])
@log_activity
def admin_add_disease():
    if session.get("user_role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.admin_dashboard"))

    lang = session.get("language", "en")

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

        if not disease_name_en:
            flash("Disease name is required", "danger")
            return redirect(url_for("main.admin_add_disease"))

        cursor = user_db.get_cursor()
        cursor.execute("SELECT disease_id FROM diseases WHERE disease_name_en = %s", (disease_name_en,))
        if cursor.fetchone():
            cursor.close()
            flash("Disease with this name already exists", "danger")
            return redirect(url_for("main.admin_add_disease"))

        try:
            cursor.execute(
                """
                INSERT INTO diseases (disease_name_en, disease_name_sw, scientific_name,
                                    description_en, description_sw, symptoms_en, symptoms_sw,
                                    treatment_en, treatment_sw)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                ),
            )
            db.connection.commit()
            flash("Disease added successfully!", "success")
            cursor.close()
            return redirect(url_for("main.admin_dashboard", _anchor="diseases"))
        except Exception as e:
            flash(f"Error adding disease: {e}", "danger")
            cursor.close()
            return redirect(url_for("main.admin_add_disease"))

    return render_template(
        "admin_add_disease.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
    )


# OFFICER DISEASE MANAGEMENT ROUTES
@main.route("/officer/disease/<int:disease_id>/view")
@log_activity
def officer_view_disease(disease_id):
    if session.get("user_role") != "extension_officer":
        flash("Access denied. Extension officer privileges required.", "danger")
        return redirect(url_for("main.index"))
    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.officer_dashboard"))
    try:
        cursor = user_db.get_cursor()
        cursor.execute("SELECT * FROM diseases WHERE disease_id = %s", (str(disease_id),))
        disease = cursor.fetchone()
        cursor.close()
        if not disease:
            flash("Disease not found", "danger")
            return redirect(url_for("main.officer_dashboard"))
        lang = session.get("language", "en")
        return render_template(
            "officer_view_disease.html",
            lang=lang,
            t=lang_manager.get_text,
            request=request,
            disease=disease,
        )
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for("main.officer_dashboard"))


@main.route("/officer/disease/<int:disease_id>/edit", methods=["GET", "POST"])
@log_activity
def officer_edit_disease(disease_id):
    if session.get("user_role") != "extension_officer":
        flash("Access denied. Extension officer privileges required.", "danger")
        return redirect(url_for("main.index"))
    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.officer_dashboard"))
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
            return redirect(url_for("main.officer_dashboard", _anchor="diseases"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
            cursor.close()
            return redirect(url_for("main.officer_dashboard", _anchor="diseases"))

    cursor.execute("SELECT * FROM diseases WHERE disease_id = %s", (str(disease_id),))
    disease = cursor.fetchone()
    cursor.close()

    if not disease:
        flash("Disease not found", "danger")
        return redirect(url_for("main.officer_dashboard", _anchor="diseases"))

    lang = session.get("language", "en")
    return render_template(
        "officer_edit_disease.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
        disease=disease,
    )


@main.route("/officer/disease/<int:disease_id>/delete", methods=["DELETE"])
@log_activity
def officer_delete_disease(disease_id):
    if session.get("user_role") != "extension_officer":
        return jsonify({"success": False, "message": "Access denied"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500

    try:
        cursor = user_db.get_cursor(dictionary=False)
        cursor.execute("SELECT disease_id FROM diseases WHERE disease_id = %s", (str(disease_id),))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"success": False, "message": "Disease not found"}), 404

        cursor.execute("DELETE FROM diseases WHERE disease_id = %s", (str(disease_id),))
        db.connection.commit()
        cursor.close()

        log_user_activity("OFFICER_ACTION", f"Deleted disease ID: {disease_id}")
        return jsonify({"success": True, "message": "Disease deleted successfully"})
    except Exception as e:
        print(f"Error deleting disease: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@main.route("/officer/disease/add", methods=["GET", "POST"])
@log_activity
def officer_add_disease():
    if session.get("user_role") != "extension_officer":
        flash("Access denied. Extension officer privileges required.", "danger")
        return redirect(url_for("main.index"))

    if not ensure_db_connection():
        flash("Database connection error", "danger")
        return redirect(url_for("main.officer_dashboard"))

    lang = session.get("language", "en")

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

        if not disease_name_en:
            flash("Disease name is required", "danger")
            return redirect(url_for("main.officer_add_disease"))

        cursor = user_db.get_cursor()
        cursor.execute("SELECT disease_id FROM diseases WHERE disease_name_en = %s", (disease_name_en,))
        if cursor.fetchone():
            cursor.close()
            flash("Disease with this name already exists", "danger")
            return redirect(url_for("main.officer_add_disease"))

        try:
            cursor.execute(
                """
                INSERT INTO diseases (disease_name_en, disease_name_sw, scientific_name,
                                    description_en, description_sw, symptoms_en, symptoms_sw,
                                    treatment_en, treatment_sw)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                ),
            )
            db.connection.commit()
            flash("Disease added successfully!", "success")
            cursor.close()
            return redirect(url_for("main.officer_dashboard", _anchor="diseases"))
        except Exception as e:
            flash(f"Error adding disease: {e}", "danger")
            cursor.close()
            return redirect(url_for("main.officer_add_disease"))

    return render_template(
        "officer_add_disease.html",
        lang=lang,
        t=lang_manager.get_text,
        request=request,
    )


# OFFICER DASHBOARD ROUTES
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

@main.route("/api/officer/dashboard-data")
def api_officer_dashboard_data():
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    if not ensure_db_connection():
        return jsonify({"success": False, "error": "Database connection error"}), 500
    try:
        cursor = user_db.get_cursor()
        cursor.execute("SELECT COUNT(*) as count FROM maziwa WHERE role = 'farmer'")
        result = cursor.fetchone()
        total_farmers = result["count"] if result else 0
        cursor.execute("SELECT COUNT(*) as count FROM diagnosis_history")
        result = cursor.fetchone()
        total_predictions = result["count"] if result else 0
        cursor.execute("SELECT COUNT(*) as count FROM diagnosis_history WHERE disease_name != 'Healthy'")
        result = cursor.fetchone()
        diseases_detected = result["count"] if result else 0
        cursor.execute("""SELECT COUNT(DISTINCT user_id) as count FROM diagnosis_history WHERE diagnosis_date::timestamp >= NOW() - INTERVAL '30 days'""")
        result = cursor.fetchone()
        active_farmers = result["count"] if result else 0
        cursor.execute("""SELECT user_id, full_name, phone_number, email, location, district, region, created_at::text as created_at FROM maziwa WHERE role = 'farmer' ORDER BY created_at DESC LIMIT 50""")
        recent_farmers = cursor.fetchall() or []
        cursor.execute("""SELECT dh.id, dh.disease_name, dh.confidence_score, dh.diagnosis_date::text as diagnosis_date, COALESCE(u.full_name, 'Unknown') as farmer_name, COALESCE(u.phone_number, 'N/A') as farmer_phone, COALESCE(u.location, 'N/A') as location FROM diagnosis_history dh LEFT JOIN maziwa u ON dh.user_id::text = u.user_id::text ORDER BY dh.diagnosis_date DESC LIMIT 50""")
        recent_predictions = cursor.fetchall() or []
        cursor.close()
        return jsonify({
            "success": True,
            "stats": {
                "total_farmers": total_farmers,
                "total_predictions": total_predictions,
                "diseases_detected": diseases_detected,
                "active_farmers": active_farmers,
            },
            "recent_farmers": [dict(row) for row in recent_farmers],
            "recent_predictions": [dict(row) for row in recent_predictions],
        })
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@main.route("/api/officer/farmers")
@log_activity
def api_officer_farmers():
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500
    try:
        limit = request.args.get("limit", 500, type=int)
        officer_region = session.get("region")
        cursor = user_db.get_cursor()

        if session.get("user_role") == "extension_officer" and officer_region:
            cursor.execute(
                """SELECT user_id, full_name, phone_number, email, location, district, region, is_active, is_approved, created_at 
                FROM maziwa 
                WHERE LOWER(role) = 'farmer' AND region = %s 
                ORDER BY full_name ASC LIMIT %s""",
                (officer_region, limit),
            )
        else:
            cursor.execute(
                """SELECT user_id, full_name, phone_number, email, location, district, region, is_active, is_approved, created_at 
                FROM maziwa 
                WHERE LOWER(role) = 'farmer'
                ORDER BY full_name ASC LIMIT %s""",
                (limit,),
            )
        farmers = cursor.fetchall() or []
        cursor.close()

        print(f"🔍 Farmers found: {len(farmers)}")
        for f in farmers:
            print(f"👨‍🌾 Farmer: {f.get('full_name')} - Region: {f.get('region')}")

        for farmer in farmers:
            if farmer.get("created_at") and hasattr(farmer["created_at"], "strftime"):
                farmer["created_at"] = farmer["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "success": True,
            "farmers": [dict(f) for f in farmers],
            "total": len(farmers),
        })
    except Exception as e:
        print(f"❌ Error fetching farmers: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500



# OFFICER PREDICTION MANAGEMENT ROUTES (VIEW, DELETE, DOWNLOAD)


@main.route("/api/officer/prediction/<int:prediction_id>")
@log_activity
def api_officer_get_prediction(prediction_id):
    """Get prediction details for officer"""
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500
    
    try:
        cursor = user_db.get_cursor()
        cursor.execute("""
            SELECT 
                dh.id,
                dh.disease_name,
                dh.confidence_score,
                dh.diagnosis_date,
                dh.image_path,
                dh.mode,
                dh.is_synced,
                dh.created_at,
                COALESCE(m.full_name, 'Unknown Farmer') as farmer_name,
                COALESCE(m.phone_number, 'N/A') as farmer_phone,
                COALESCE(m.email, 'N/A') as farmer_email,
                COALESCE(m.location, 'N/A') as farmer_location,
                COALESCE(m.district, 'N/A') as farmer_district,
                COALESCE(m.region, 'N/A') as farmer_region
            FROM diagnosis_history dh
            LEFT JOIN maziwa m ON dh.user_id::text = m.user_id::text
            WHERE dh.id = %s
        """, (prediction_id,))
        
        prediction = cursor.fetchone()
        cursor.close()
        
        if not prediction:
            return jsonify({"success": False, "message": "Prediction not found"}), 404
        
        if prediction.get("diagnosis_date") and hasattr(prediction["diagnosis_date"], "strftime"):
            prediction["diagnosis_date"] = prediction["diagnosis_date"].strftime("%Y-%m-%d %H:%M:%S")
        if prediction.get("created_at") and hasattr(prediction["created_at"], "strftime"):
            prediction["created_at"] = prediction["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        
        if prediction.get("confidence_score"):
            try:
                prediction["confidence_score"] = float(prediction["confidence_score"])
            except:
                prediction["confidence_score"] = 0.0
        
        return jsonify({
            "success": True,
            "prediction": dict(prediction)
        })
    except Exception as e:
        print(f"Error fetching prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/api/officer/prediction/<int:prediction_id>/delete", methods=["DELETE"])
@log_activity
def api_officer_delete_prediction(prediction_id):
    """Delete prediction for officer"""
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500
    
    try:
        cursor = user_db.get_cursor(dictionary=False)
        
        cursor.execute(
            "SELECT id, image_path FROM diagnosis_history WHERE id = %s",
            (prediction_id,)
        )
        prediction = cursor.fetchone()
        
        if not prediction:
            cursor.close()
            return jsonify({"success": False, "message": "Prediction not found"}), 404
        
        if prediction and prediction.get("image_path"):
            image_path = prediction["image_path"]
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Could not delete image: {e}")
        
        cursor.execute(
            "DELETE FROM diagnosis_history WHERE id = %s",
            (prediction_id,)
        )
        db.connection.commit()
        cursor.close()
        
        log_user_activity("OFFICER_DELETE_PREDICTION", f"Officer deleted prediction ID: {prediction_id}")
        return jsonify({"success": True, "message": "Prediction deleted successfully"})
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/api/officer/prediction/<int:prediction_id>/download")
@log_activity
def api_officer_download_prediction(prediction_id):
    """Download prediction report as PDF or CSV"""
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500
    
    try:
        format_type = request.args.get("format", "csv").lower()
        
        cursor = user_db.get_cursor()
        cursor.execute("""
            SELECT 
                dh.id,
                dh.disease_name,
                dh.confidence_score,
                dh.diagnosis_date,
                dh.mode,
                COALESCE(m.full_name, 'Unknown Farmer') as farmer_name,
                COALESCE(m.phone_number, 'N/A') as farmer_phone,
                COALESCE(m.email, 'N/A') as farmer_email,
                COALESCE(m.location, 'N/A') as farmer_location,
                COALESCE(m.district, 'N/A') as farmer_district,
                COALESCE(m.region, 'N/A') as farmer_region
            FROM diagnosis_history dh
            LEFT JOIN maziwa m ON dh.user_id::text = m.user_id::text
            WHERE dh.id = %s
        """, (prediction_id,))
        
        prediction = cursor.fetchone()
        cursor.close()
        
        if not prediction:
            return jsonify({"success": False, "message": "Prediction not found"}), 404
        
        if prediction.get("diagnosis_date") and hasattr(prediction["diagnosis_date"], "strftime"):
            prediction["diagnosis_date"] = prediction["diagnosis_date"].strftime("%Y-%m-%d %H:%M:%S")
        
        if format_type == "csv":
            return download_prediction_csv(prediction)
        elif format_type == "pdf":
            return download_prediction_pdf(prediction)
        else:
            return jsonify({"success": False, "message": "Invalid format. Use 'csv' or 'pdf'"}), 400
    except Exception as e:
        print(f"Error downloading prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


def download_prediction_csv(prediction):
    """Download single prediction as CSV"""
    import csv
    from io import StringIO, BytesIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Field", "Value"])
    
    writer.writerow(["Prediction ID", prediction.get("id", "N/A")])
    writer.writerow(["Farmer Name", prediction.get("farmer_name", "Unknown")])
    writer.writerow(["Phone", prediction.get("farmer_phone", "N/A")])
    writer.writerow(["Email", prediction.get("farmer_email", "N/A")])
    writer.writerow(["Location", prediction.get("farmer_location", "N/A")])
    writer.writerow(["District", prediction.get("farmer_district", "N/A")])
    writer.writerow(["Region", prediction.get("farmer_region", "N/A")])
    writer.writerow(["Disease", prediction.get("disease_name", "Unknown")])
    
    # FIX: Format confidence as float
    confidence = prediction.get('confidence_score', 0)
    try:
        confidence = float(confidence)
        writer.writerow(["Confidence", f"{confidence:.2f}%"])
    except:
        writer.writerow(["Confidence", "N/A"])
    
    writer.writerow(["Diagnosis Date", prediction.get("diagnosis_date", "N/A")])
    writer.writerow(["Mode", prediction.get("mode", "online")])
    
    output.seek(0)
    csv_data = BytesIO(output.getvalue().encode("utf-8"))
    
    return send_file(
        csv_data,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"prediction_{prediction.get('id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )


def download_prediction_pdf(prediction):
    """Download single prediction as PDF"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        title_style.alignment = 1
        
        elements = []
        
        elements.append(Paragraph("Maize Disease Prediction Report", title_style))
        elements.append(Spacer(1, 0.25 * inch))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 0.25 * inch))
        elements.append(Paragraph(f"Prediction ID: {prediction.get('id', 'N/A')}", styles['Normal']))
        elements.append(Spacer(1, 0.25 * inch))
        
        elements.append(Paragraph("<b>Farmer Information</b>", styles['Heading2']))
        farmer_data = [
            ["Name:", prediction.get("farmer_name", "Unknown")],
            ["Phone:", prediction.get("farmer_phone", "N/A")],
            ["Email:", prediction.get("farmer_email", "N/A")],
            ["Location:", prediction.get("farmer_location", "N/A")],
            ["District:", prediction.get("farmer_district", "N/A")],
            ["Region:", prediction.get("farmer_region", "N/A")],
        ]
        farmer_table = Table(farmer_data, colWidths=[1.5*inch, 3.5*inch])
        farmer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        elements.append(farmer_table)
        elements.append(Spacer(1, 0.25 * inch))
        
        elements.append(Paragraph("<b>Prediction Results</b>", styles['Heading2']))
        
        # FIX: Format confidence as float
        confidence = prediction.get('confidence_score', 0)
        try:
            confidence = float(confidence)
            confidence_display = f"{confidence:.2f}%"
        except:
            confidence_display = "N/A"
        
        pred_data = [
            ["Disease:", prediction.get("disease_name", "Unknown")],
            ["Confidence Score:", confidence_display],
            ["Diagnosis Date:", prediction.get("diagnosis_date", "N/A")],
            ["Mode:", prediction.get("mode", "online")],
        ]
        pred_table = Table(pred_data, colWidths=[1.5*inch, 3.5*inch])
        pred_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        elements.append(pred_table)
        
        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"prediction_{prediction.get('id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    except ImportError:
        return download_prediction_csv(prediction)


# OFFICER API ROUTES (Diseases)
@main.route("/api/officer/diseases", methods=["GET"])
def api_officer_get_diseases():
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    cursor = user_db.get_cursor()
    cursor.execute("""
        SELECT * FROM diseases
        WHERE disease_name_en IN ('Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy')
        ORDER BY disease_id
    """)
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
    disease_name_en = data.get("disease_name_en", "").strip()
    if not disease_name_en:
        return jsonify({"success": False, "message": "Disease name required"}), 400
    cursor = user_db.get_cursor()
    cursor.execute("SELECT disease_id FROM diseases WHERE disease_name_en = %s", (disease_name_en,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"success": False, "message": "Disease with this name already exists"}), 400
    cursor.execute(
        """INSERT INTO diseases (disease_name_en, disease_name_sw, scientific_name, description_en, description_sw, symptoms_en, symptoms_sw, treatment_en, treatment_sw) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            disease_name_en,
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
    return jsonify({"success": True, "message": "Disease added successfully"})

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
    try:
        cursor = user_db.get_cursor()
        cursor.execute("DELETE FROM public.diagnosis_history WHERE disease_id = %s", (str(disease_id),))
        cursor.execute("DELETE FROM diseases WHERE disease_id = %s", (str(disease_id),))
        db.connection.commit()
        cursor.close()
        return jsonify({"success": True, "message": "Disease deleted"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@main.route("/api/officer/farmer-diagnoses/<user_id>")
@log_activity
def api_officer_farmer_diagnoses(user_id):
    if session.get("user_role") not in ["extension_officer", "admin"]:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not ensure_db_connection():
        return jsonify({"success": False, "message": "Database connection error"}), 500
    try:
        cursor = user_db.get_cursor()
        cursor.execute("SELECT user_id, full_name, region FROM maziwa WHERE user_id = %s AND role = 'farmer'", (user_id,))
        farmer = cursor.fetchone()
        if not farmer:
            cursor.close()
            return jsonify({"success": False, "message": "Farmer not found"}), 404
        if session.get("user_role") == "extension_officer":
            officer_region = session.get("region")
            if officer_region and farmer.get("region") != officer_region:
                cursor.close()
                return jsonify({"success": False, "message": "Access denied. Farmer is not in your region."}), 403
        cursor.execute(
            """SELECT id, disease_name, confidence_score, image_path, diagnosis_date, mode, created_at, is_synced FROM diagnosis_history WHERE user_id = %s ORDER BY diagnosis_date DESC""",
            (user_id,),
        )
        diagnoses = cursor.fetchall() or []
        cursor.close()
        for diagnosis in diagnoses:
            if diagnosis.get("diagnosis_date") and hasattr(diagnosis["diagnosis_date"], "strftime"):
                diagnosis["diagnosis_date"] = diagnosis["diagnosis_date"].strftime("%Y-%m-%d %H:%M:%S")
            # FIX: Convert confidence to float
            if diagnosis.get("confidence_score"):
                try:
                    diagnosis["confidence_score"] = float(diagnosis["confidence_score"])
                except:
                    diagnosis["confidence_score"] = 0.0
        return jsonify({
            "success": True,
            "diagnoses": [dict(d) for d in diagnoses],
            "total": len(diagnoses),
        })
    except Exception as e:
        print(f"Error fetching farmer diagnoses: {e}")
        return jsonify({"success": False, "message": str(e)}), 500



# FARMER HISTORY ROUTES


@main.route("/api/farmer/predictions")
@log_activity
def api_farmer_predictions():
    """Get predictions for logged in farmer"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401

    if session.get("user_role") != "farmer":
        return jsonify({"success": False, "error": "Access denied"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        user_id = session.get("user_id")
        cursor = user_db.get_cursor()
        cursor.execute(
            """
            SELECT
                id as prediction_id,
                disease_name,
                confidence_score,
                diagnosis_date,
                image_path,
                mode,
                is_synced,
                created_at
            FROM diagnosis_history
            WHERE user_id = %s
            ORDER BY diagnosis_date DESC
            """,
            (str(user_id),),
        )
        predictions = cursor.fetchall() or []
        cursor.close()
        total = len(predictions)
        avg_confidence = 0
        offline_count = 0

        if total > 0:
            total_confidence = sum(
                float(p.get("confidence_score", 0)) for p in predictions
            )
            avg_confidence = round(total_confidence / total, 1)
            offline_count = sum(1 for p in predictions if p.get("mode") == "offline")
        for p in predictions:
            if p.get("diagnosis_date") and hasattr(p["diagnosis_date"], "strftime"):
                p["diagnosis_date"] = p["diagnosis_date"].strftime("%Y-%m-%d %H:%M:%S")
            if p.get("created_at") and hasattr(p["created_at"], "strftime"):
                p["created_at"] = p["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            # FIX: Convert confidence to float
            if p.get("confidence_score"):
                try:
                    p["confidence_score"] = float(p["confidence_score"])
                except:
                    p["confidence_score"] = 0.0

        return jsonify(
            {
                "success": True,
                "predictions": [dict(p) for p in predictions],
                "total": total,
                "avg_confidence": avg_confidence,
                "offline_count": offline_count,
            }
        )
    except Exception as e:
        print(f"Error fetching farmer predictions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/api/farmer/predictions/delete/<int:prediction_id>", methods=["DELETE"])
@log_activity
def api_farmer_delete_prediction(prediction_id):
    """Delete a single prediction for farmer"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401

    if session.get("user_role") != "farmer":
        return jsonify({"success": False, "error": "Access denied"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        user_id = session.get("user_id")
        cursor = user_db.get_cursor(dictionary=False)
        cursor.execute(
            "SELECT id, image_path FROM diagnosis_history WHERE id = %s AND user_id = %s",
            (prediction_id, str(user_id)),
        )
        prediction = cursor.fetchone()

        if not prediction:
            cursor.close()
            return jsonify({"success": False, "error": "Prediction not found"}), 404

        if prediction and prediction.get("image_path"):
            image_path = prediction["image_path"]
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Could not delete image: {e}")
        cursor.execute(
            "DELETE FROM diagnosis_history WHERE id = %s AND user_id = %s",
            (prediction_id, str(user_id)),
        )
        db.connection.commit()
        cursor.close()

        log_user_activity(
            "DELETE_PREDICTION", f"Farmer deleted prediction ID: {prediction_id}"
        )
        return jsonify({"success": True, "message": "Prediction deleted successfully"})
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/api/farmer/predictions/clear-all", methods=["DELETE"])
@log_activity
def api_farmer_clear_all_predictions():
    """Clear all predictions for farmer"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401

    if session.get("user_role") != "farmer":
        return jsonify({"success": False, "error": "Access denied"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        user_id = session.get("user_id")
        cursor = user_db.get_cursor(dictionary=False)
        cursor.execute(
            "SELECT image_path FROM diagnosis_history WHERE user_id = %s",
            (str(user_id),),
        )
        predictions = cursor.fetchall() or []
        for p in predictions:
            if p and p.get("image_path"):
                image_path = p["image_path"]
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except:
                        pass

        cursor.execute(
            "DELETE FROM diagnosis_history WHERE user_id = %s", (str(user_id),)
        )
        db.connection.commit()
        cursor.close()

        log_user_activity("CLEAR_ALL_PREDICTIONS", f"Farmer cleared all predictions")
        return jsonify(
            {"success": True, "message": "All predictions cleared successfully"}
        )
    except Exception as e:
        print(f"Error clearing predictions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/api/farmer/predictions/sync", methods=["POST"])
@log_activity
def api_farmer_sync_predictions():
    """Sync offline predictions to online"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401

    if session.get("user_role") != "farmer":
        return jsonify({"success": False, "error": "Access denied"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        user_id = session.get("user_id")
        cursor = user_db.get_cursor(dictionary=False)
        cursor.execute(
            """
            UPDATE diagnosis_history
            SET is_synced = '1', mode = 'online'
            WHERE user_id = %s AND mode = 'offline' AND is_synced = '0'
            RETURNING id
            """,
            (str(user_id),),
        )

        synced_count = cursor.rowcount
        db.connection.commit()
        cursor.close()

        log_user_activity(
            "SYNC_PREDICTIONS", f"Farmer synced {synced_count} predictions"
        )
        return jsonify(
            {
                "success": True,
                "message": f"Synced {synced_count} predictions",
                "synced_count": synced_count,
            }
        )
    except Exception as e:
        print(f"Error syncing predictions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/api/farmer/predictions/download")
@log_activity
def api_farmer_download_predictions():
    """Download predictions as CSV"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401

    if session.get("user_role") != "farmer":
        return jsonify({"success": False, "error": "Access denied"}), 403

    if not ensure_db_connection():
        return jsonify({"success": False, "error": "Database connection error"}), 500

    try:
        import csv
        from io import StringIO, BytesIO

        user_id = session.get("user_id")
        cursor = user_db.get_cursor()
        cursor.execute(
            """
            SELECT
                disease_name,
                confidence_score,
                diagnosis_date,
                mode,
                is_synced
            FROM diagnosis_history
            WHERE user_id = %s
            ORDER BY diagnosis_date DESC
            """,
            (str(user_id),),
        )
        predictions = cursor.fetchall() or []
        cursor.close()

        if not predictions:
            return (
                jsonify({"success": False, "error": "No predictions to download"}),
                404,
            )

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(
            ["Disease Name", "Confidence Score (%)", "Diagnosis Date", "Mode", "Synced"]
        )

        for p in predictions:
            # FIX: Format confidence as float
            confidence = p.get("confidence_score", 0)
            try:
                confidence_display = f"{float(confidence):.2f}"
            except:
                confidence_display = "0.00"
                
            writer.writerow(
                [
                    p.get("disease_name", "Unknown"),
                    confidence_display,
                    p.get("diagnosis_date", ""),
                    p.get("mode", "online"),
                    "Yes" if p.get("is_synced") == "1" else "No",
                ]
            )

        output.seek(0)
        csv_data = BytesIO(output.getvalue().encode("utf-8"))

        return send_file(
            csv_data,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"predictions_{datetime.now().strftime('%Y%m%d')}.csv",
        )
    except Exception as e:
        print(f"Error downloading predictions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500



# ERROR HANDLERS

@main.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@main.errorhandler(403)
def forbidden_error(error):
    return render_template("403.html"), 403

@main.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500