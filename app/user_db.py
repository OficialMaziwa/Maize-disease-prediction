"""
User Database Functions with Role-Based Access Control
PostgreSQL Version - PRODUCTION READY
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()


class UserDB:
    """User database operations with role-based access"""

    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """Connect to PostgreSQL database using DATABASE_URL or fallback"""
        try:
            # Close existing connection if any
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass
                self.connection = None

            # Try DATABASE_URL first
            database_url = os.environ.get('DATABASE_URL')
            
            if database_url:
                # Remove +psycopg2 if present
                if '+psycopg2' in database_url:
                    database_url = database_url.replace('+psycopg2', '')
                
                self.connection = psycopg2.connect(database_url)
                self.connection.autocommit = True
                print("✅ PostgreSQL connected successfully using DATABASE_URL")
                return True
            else:
                # Fallback to individual parameters for local development
                db_host = os.environ.get("DB_HOST", "127.0.0.1")
                db_port = int(os.environ.get("DB_PORT", 5432))
                db_user = os.environ.get("DB_USER", "postgres")
                db_password = os.environ.get("DB_PASSWORD", "Malaba@2003")
                db_name = os.environ.get("DB_NAME", "maize_disease_db")

                self.connection = psycopg2.connect(
                    host=db_host,
                    user=db_user,
                    password=db_password,
                    database=db_name,
                    port=db_port,
                )
                self.connection.autocommit = True
                print(f"✅ PostgreSQL connected successfully using local parameters: {db_host}:{db_port}/{db_name}")
                return True
                
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            self.connection = None
            return False

    def is_connected(self):
        """Check if database connection is active"""
        try:
            if self.connection is None:
                return False
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except:
            return False

    def get_cursor(self, dictionary=True):
        """Get a database cursor with connection check"""
        if not self.is_connected():
            print("Connection lost, attempting to reconnect...")
            if not self.connect():
                print("Failed to reconnect to database")
                return None
        try:
            if dictionary:
                return self.connection.cursor(cursor_factory=RealDictCursor)
            return self.connection.cursor()
        except Exception as e:
            print(f"Error creating cursor: {e}")
            return None

    def get_user_by_phone(self, phone_number):
        """Get user by phone number"""
        cursor = self.get_cursor()
        if not cursor:
            return None
        try:
            cursor.execute(
                "SELECT * FROM maziwa WHERE phone_number = %s", (phone_number,)
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_user_by_email(self, email):
        """Get user by email"""
        cursor = self.get_cursor()
        if not cursor:
            return None
        try:
            cursor.execute("SELECT * FROM maziwa WHERE email = %s", (email,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        cursor = self.get_cursor()
        if not cursor:
            return None
        try:
            cursor.execute(
                """SELECT user_id, phone_number, email, full_name, role, location,
                district, region, is_active, is_approved, created_at, last_login, profile_picture
                FROM maziwa WHERE user_id = %s""",
                (user_id,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def authenticate_user(self, identifier, password):
        """Authenticate user by phone or email"""
        cursor = None
        try:
            cursor = self.get_cursor()
            if not cursor:
                return {"success": False, "message": "Database connection error"}

            cursor.execute(
                """
                SELECT * FROM maziwa
                WHERE (phone_number = %s OR email = %s) AND is_active = 1
            """,
                (identifier, identifier),
            )
            user = cursor.fetchone()

            if user and check_password_hash(user["password_hash"], password):
                if user["role"] == "extension_officer" and not user.get(
                    "is_approved", False
                ):
                    return {
                        "success": False,
                        "message": "Your account is pending admin approval.",
                    }
                self.update_last_login(user["user_id"])
                return {"success": True, "user": user, "message": "Login successful"}
            return {"success": False, "message": "Invalid credentials"}
        except Exception as e:
            return {"success": False, "message": f"Authentication error: {str(e)}"}
        finally:
            if cursor:
                cursor.close()

    def update_last_login(self, user_id):
        """Update user's last login time"""
        cursor = self.get_cursor(dictionary=False)
        if not cursor:
            return
        try:
            cursor.execute(
                "UPDATE maziwa SET last_login = NOW() WHERE user_id = %s", (user_id,)
            )
            self.connection.commit()
        except Exception as e:
            print(f"Error updating last login: {e}")
        finally:
            cursor.close()

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


user_db = UserDB()