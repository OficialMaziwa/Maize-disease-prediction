import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    database_url = "postgresql://neondb_owner:npg_PyY4a2UEzdBh@ep-super-wildflower-aofmcegd-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Check admin email
cursor.execute("SELECT user_id, full_name, email FROM maziwa WHERE role = 'admin'")
admins = cursor.fetchall()

print("=" * 50)
print("ADMINS IN DATABASE")
print("=" * 50)
for admin in admins:
    email = admin[2] if admin[2] else "NO EMAIL!"
    print(f"  ID: {admin[0]}")
    print(f"  Name: {admin[1]}")
    print(f"  Email: {email}")
    print("-" * 30)

# Check if admin email exists
if not admins:
    print("❌ No admin found in database!")
else:
    print(f"✅ Found {len(admins)} admin(s)")

cursor.close()
conn.close()
