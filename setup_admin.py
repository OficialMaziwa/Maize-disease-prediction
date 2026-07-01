import os
import psycopg2
from werkzeug.security import generate_password_hash

# Database connection
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Fallback to hardcoded for now
    database_url = "postgresql://neondb_owner:npg_PyY4a2UEzdBh@ep-super-wildflower-aofmcegd-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

print("Connecting to database...")
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Check if admin exists
cursor.execute("SELECT user_id, full_name, phone_number, email, role FROM maziwa WHERE email = %s OR role = %s", 
               ('malabamalaba26@gmail.com', 'admin'))
users = cursor.fetchall()

if users:
    print("✅ Found users:")
    for user in users:
        print(f"   ID: {user[0]}, Name: {user[1]}, Phone: {user[2]}, Email: {user[3]}, Role: {user[4]}")
else:
    print("❌ Admin user not found. Creating...")
    
    # Create admin user
    full_name = "Admin Malaba"
    phone_number = "0712345678"
    email = "malabamalaba26@gmail.com"
    password = "Malaba@03"
    password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=32)
    
    try:
        cursor.execute("""
            INSERT INTO maziwa (full_name, phone_number, email, password_hash, role, is_approved, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (full_name, phone_number, email, password_hash, 'admin', True, True))
        conn.commit()
        print("✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")

cursor.close()
conn.close()
print("Done!")
