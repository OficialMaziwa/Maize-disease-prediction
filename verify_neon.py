import psycopg2

# Connect to Neon
conn = psycopg2.connect("postgresql://neondb_owner:npg_PyY4a2UEzdBh@ep-super-wildflower-aofmcegd-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")
cursor = conn.cursor()

print("=" * 50)
print("NEON DATABASE VERIFICATION")
print("=" * 50)

# Check admin user
cursor.execute("SELECT full_name, email, role FROM maziwa WHERE email = 'malabamalaba26@gmail.com'")
admin = cursor.fetchone()
if admin:
    print(f"✅ Admin found: {admin[0]} - {admin[1]} - {admin[2]}")
else:
    print("❌ Admin not found")

# Check total users
cursor.execute("SELECT COUNT(*) FROM maziwa")
total_users = cursor.fetchone()[0]
print(f"📊 Total users: {total_users}")

# Check diseases
cursor.execute("SELECT COUNT(*) FROM diseases")
total_diseases = cursor.fetchone()[0]
print(f"📊 Total diseases: {total_diseases}")

# Check diagnosis history
cursor.execute("SELECT COUNT(*) FROM diagnosis_history")
total_diagnosis = cursor.fetchone()[0]
print(f"📊 Total diagnoses: {total_diagnosis}")

# Check user activity logs
cursor.execute("SELECT COUNT(*) FROM user_activity_logs")
total_logs = cursor.fetchone()[0]
print(f"📊 Total activity logs: {total_logs}")

# Show all users
print("\n" + "=" * 50)
print("USERS LIST:")
print("=" * 50)
cursor.execute("SELECT user_id, full_name, phone_number, email, role FROM maziwa LIMIT 10")
users = cursor.fetchall()
for user in users:
    print(f"  ID: {user[0]}, Name: {user[1]}, Phone: {user[2]}, Email: {user[3]}, Role: {user[4]}")

# Show diseases
print("\n" + "=" * 50)
print("DISEASES LIST:")
print("=" * 50)
cursor.execute("SELECT disease_id, disease_name_en FROM diseases")
diseases = cursor.fetchall()
for disease in diseases:
    print(f"  ID: {disease[0]}, Name: {disease[1]}")

cursor.close()
conn.close()

print("\n" + "=" * 50)
print("✅ Verification complete!")
print("=" * 50)
