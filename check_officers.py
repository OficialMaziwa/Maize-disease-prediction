import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    database_url = "postgresql://neondb_owner:npg_PyY4a2UEzdBh@ep-super-wildflower-aofmcegd-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Check extension officers
cursor.execute("SELECT user_id, full_name, role, is_approved FROM maziwa WHERE role = 'extension_officer' ORDER BY user_id DESC")
users = cursor.fetchall()

print("=" * 50)
print("EXTENSION OFFICERS LIST")
print("=" * 50)
for user in users:
    print(f"ID: {user[0]}, Name: {user[1]}, Role: {user[2]}, Approved: {user[3]}")

print("\n" + "=" * 50)
print(f"Total extension officers: {len(users)}")
print("=" * 50)

# Check pending count
cursor.execute("SELECT COUNT(*) FROM maziwa WHERE role = 'extension_officer' AND (is_approved = FALSE OR is_approved IS NULL)")
pending_count = cursor.fetchone()[0]
print(f"Pending officers: {pending_count}")

cursor.close()
conn.close()
