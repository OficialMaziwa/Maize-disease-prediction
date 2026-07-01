import os
import psycopg2
from psycopg2.extras import RealDictCursor

print("=" * 50)
print("Transferring database from local to Neon")
print("=" * 50)

# Local database connection
print("\n1. Connecting to local database...")
try:
    local_conn = psycopg2.connect(
        host="127.0.0.1",
        user="postgres",
        password="Malaba@2003",
        database="maize_disease_db",
        port=5432
    )
    local_cursor = local_conn.cursor(cursor_factory=RealDictCursor)
    print("   ✅ Connected to local database")
except Exception as e:
    print(f"   ❌ Error connecting to local: {e}")
    exit(1)

# Neon database connection
print("\n2. Connecting to Neon database...")
try:
    neon_conn = psycopg2.connect("postgresql://neondb_owner:npg_PyY4a2UEzdBh@ep-super-wildflower-aofmcegd-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")
    neon_cursor = neon_conn.cursor()
    print("   ✅ Connected to Neon database")
except Exception as e:
    print(f"   ❌ Error connecting to Neon: {e}")
    exit(1)

# List of tables to transfer
tables = ['maziwa', 'diagnosis_history', 'diseases', 'user_activity_logs', 'in_app_notifications']

print("\n3. Transferring data...")
for table in tables:
    print(f"   📦 Transferring {table}...")
    
    try:
        # Get data from local
        local_cursor.execute(f"SELECT * FROM {table}")
        rows = local_cursor.fetchall()
        
        if rows:
            # Get column names
            columns = list(rows[0].keys())
            placeholders = ','.join(['%s'] * len(columns))
            columns_str = ','.join(columns)
            
            # Insert into Neon
            count = 0
            for row in rows:
                values = [row[col] for col in columns]
                try:
                    # Convert None to appropriate values
                    values = [v if v is not None else None for v in values]
                    neon_cursor.execute(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING", values)
                    count += 1
                except Exception as e:
                    print(f"      ⚠️  Error inserting row: {e}")
            
            neon_conn.commit()
            print(f"      ✅ Transferred {count} rows")
        else:
            print(f"      ℹ️  No data found")
    except Exception as e:
        print(f"      ❌ Error with table {table}: {e}")

print("\n4. Closing connections...")
local_cursor.close()
local_conn.close()
neon_cursor.close()
neon_conn.close()

print("\n" + "=" * 50)
print("✅ Database transfer complete!")
print("=" * 50)
