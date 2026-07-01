import psycopg2

# Connect to Neon
neon_conn = psycopg2.connect("postgresql://neondb_owner:npg_PyY4a2UEzdBh@ep-super-wildflower-aofmcegd-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")
neon_cursor = neon_conn.cursor()

print("Adding missing columns to maziwa table...")
maziwa_columns = [
    "ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0",
    "ADD COLUMN IF NOT EXISTS last_failed_login TIMESTAMP",
    "ADD COLUMN IF NOT EXISTS user_id_int INTEGER",
    "ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255)",
    "ADD COLUMN IF NOT EXISTS rejection_reason TEXT",
    "ADD COLUMN IF NOT EXISTS cover_image VARCHAR(255)",
    "ADD COLUMN IF NOT EXISTS password_reset_expiry TIMESTAMP",
    "ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
]

for col in maziwa_columns:
    try:
        neon_cursor.execute(f"ALTER TABLE maziwa {col}")
        print(f"  ✅ Added: {col.split('IF NOT EXISTS')[-1].strip() if 'IF NOT EXISTS' in col else col}")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")

print("\nAdding missing columns to diagnosis_history table...")
diagnosis_columns = [
    "ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
    "ADD COLUMN IF NOT EXISTS notes TEXT"
]

for col in diagnosis_columns:
    try:
        neon_cursor.execute(f"ALTER TABLE diagnosis_history {col}")
        print(f"  ✅ Added: {col.split('IF NOT EXISTS')[-1].strip() if 'IF NOT EXISTS' in col else col}")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")

print("\nAdding missing columns to diseases table...")
diseases_columns = [
    "ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
    "ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "ADD COLUMN IF NOT EXISTS image_url VARCHAR(255)",
    "ADD COLUMN IF NOT EXISTS prevention_en TEXT",
    "ADD COLUMN IF NOT EXISTS prevention_sw TEXT",
    "ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
]

for col in diseases_columns:
    try:
        neon_cursor.execute(f"ALTER TABLE diseases {col}")
        print(f"  ✅ Added: {col.split('IF NOT EXISTS')[-1].strip() if 'IF NOT EXISTS' in col else col}")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")

neon_conn.commit()
neon_cursor.close()
neon_conn.close()

print("\n✅ All missing columns added successfully!")
