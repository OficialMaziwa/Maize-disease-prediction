import psycopg2
from psycopg2.extras import RealDictCursor

print("=" * 50)
print("Transferring database from local to Neon (with type conversion)")
print("=" * 50)

# Local database connection
print("\n1. Connecting to local database...")
local_conn = psycopg2.connect(
    host="127.0.0.1",
    user="postgres",
    password="Malaba@2003",
    database="maize_disease_db",
    port=5432
)
local_cursor = local_conn.cursor(cursor_factory=RealDictCursor)
print("   ✅ Connected to local database")

# Neon database connection
print("\n2. Connecting to Neon database...")
neon_conn = psycopg2.connect("postgresql://neondb_owner:npg_PyY4a2UEzdBh@ep-super-wildflower-aofmcegd-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")
neon_cursor = neon_conn.cursor()
print("   ✅ Connected to Neon database")

# Clear existing data in Neon (optional - be careful!)
print("\n3. Clearing existing data in Neon...")
tables = ['user_activity_logs', 'in_app_notifications', 'diagnosis_history', 'diseases', 'maziwa']
for table in tables:
    try:
        neon_cursor.execute(f"DELETE FROM {table}")
        print(f"   ✅ Cleared {table}")
    except Exception as e:
        print(f"   ⚠️ Could not clear {table}: {e}")
neon_conn.commit()

print("\n4. Transferring data...")

# Transfer maziwa
print("   📦 Transferring maziwa...")
local_cursor.execute("SELECT * FROM maziwa")
rows = local_cursor.fetchall()
count = 0
for row in rows:
    # Convert boolean fields (1/0 to True/False)
    for key in ['is_active', 'is_approved']:
        if key in row and row[key] is not None:
            if isinstance(row[key], int):
                row[key] = bool(row[key])
    
    columns = list(row.keys())
    placeholders = ','.join(['%s'] * len(columns))
    columns_str = ','.join(columns)
    values = [row[col] for col in columns]
    
    try:
        neon_cursor.execute(f"INSERT INTO maziwa ({columns_str}) VALUES ({placeholders}) ON CONFLICT (user_id) DO NOTHING", values)
        count += 1
        if count % 10 == 0:
            print(f"      Transferred {count} rows...")
    except Exception as e:
        print(f"      ⚠️ Error inserting row: {e}")
neon_conn.commit()
print(f"      ✅ Transferred {count} rows")

# Transfer diagnosis_history
print("   📦 Transferring diagnosis_history...")
local_cursor.execute("SELECT * FROM diagnosis_history")
rows = local_cursor.fetchall()
count = 0
for row in rows:
    # Convert boolean fields
    if 'is_active' in row and row['is_active'] is not None and isinstance(row['is_active'], int):
        row['is_active'] = bool(row['is_active'])
    if 'is_synced' in row and row['is_synced'] is not None and isinstance(row['is_synced'], int):
        row['is_synced'] = bool(row['is_synced'])
    
    columns = list(row.keys())
    placeholders = ','.join(['%s'] * len(columns))
    columns_str = ','.join(columns)
    values = [row[col] for col in columns]
    
    try:
        neon_cursor.execute(f"INSERT INTO diagnosis_history ({columns_str}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING", values)
        count += 1
    except Exception as e:
        print(f"      ⚠️ Error: {e}")
neon_conn.commit()
print(f"      ✅ Transferred {count} rows")

# Transfer diseases
print("   📦 Transferring diseases...")
local_cursor.execute("SELECT * FROM diseases")
rows = local_cursor.fetchall()
count = 0
for row in rows:
    # Convert boolean fields
    if 'is_active' in row and row['is_active'] is not None and isinstance(row['is_active'], int):
        row['is_active'] = bool(row['is_active'])
    
    columns = list(row.keys())
    placeholders = ','.join(['%s'] * len(columns))
    columns_str = ','.join(columns)
    values = [row[col] for col in columns]
    
    try:
        neon_cursor.execute(f"INSERT INTO diseases ({columns_str}) VALUES ({placeholders}) ON CONFLICT (disease_id) DO NOTHING", values)
        count += 1
    except Exception as e:
        print(f"      ⚠️ Error: {e}")
neon_conn.commit()
print(f"      ✅ Transferred {count} rows")

# Transfer user_activity_logs
print("   📦 Transferring user_activity_logs...")
try:
    local_cursor.execute("SELECT * FROM user_activity_logs")
    rows = local_cursor.fetchall()
    count = 0
    for row in rows:
        columns = list(row.keys())
        placeholders = ','.join(['%s'] * len(columns))
        columns_str = ','.join(columns)
        values = [row[col] for col in columns]
        try:
            neon_cursor.execute(f"INSERT INTO user_activity_logs ({columns_str}) VALUES ({placeholders}) ON CONFLICT (activity_id) DO NOTHING", values)
            count += 1
        except Exception as e:
            pass
    neon_conn.commit()
    print(f"      ✅ Transferred {count} rows")
except Exception as e:
    print(f"      ⚠️ No data or error: {e}")

# Transfer in_app_notifications
print("   📦 Transferring in_app_notifications...")
try:
    local_cursor.execute("SELECT * FROM in_app_notifications")
    rows = local_cursor.fetchall()
    count = 0
    for row in rows:
        columns = list(row.keys())
        placeholders = ','.join(['%s'] * len(columns))
        columns_str = ','.join(columns)
        values = [row[col] for col in columns]
        try:
            neon_cursor.execute(f"INSERT INTO in_app_notifications ({columns_str}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING", values)
            count += 1
        except Exception as e:
            pass
    neon_conn.commit()
    print(f"      ✅ Transferred {count} rows")
except Exception as e:
    print(f"      ⚠️ No data or error: {e}")

print("\n5. Closing connections...")
local_cursor.close()
local_conn.close()
neon_cursor.close()
neon_conn.close()

print("\n" + "=" * 50)
print("✅ Database transfer complete!")
print("=" * 50)
