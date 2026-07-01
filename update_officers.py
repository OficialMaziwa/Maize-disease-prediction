import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    database_url = "postgresql://neondb_owner:npg_PyY4a2UEzdBh@ep-super-wildflower-aofmcegd-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Set all extension officers to pending
cursor.execute("UPDATE maziwa SET is_approved = FALSE WHERE role = 'extension_officer'")
conn.commit()
print('✅ All extension officers set to pending (FALSE)')

# Verify
cursor.execute("SELECT user_id, full_name, role, is_approved FROM maziwa WHERE role = 'extension_officer'")
users = cursor.fetchall()
print("\nUpdated officers:")
for user in users:
    print(f"  ID: {user[0]}, Name: {user[1]}, Approved: {user[3]}")

cursor.close()
conn.close()
