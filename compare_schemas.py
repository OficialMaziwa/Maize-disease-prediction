import psycopg2
from psycopg2.extras import RealDictCursor

# Local database
local_conn = psycopg2.connect(
    host="127.0.0.1",
    user="postgres",
    password="Malaba@2003",
    database="maize_disease_db",
    port=5432
)
local_cursor = local_conn.cursor(cursor_factory=RealDictCursor)

# Neon database
neon_conn = psycopg2.connect("postgresql://neondb_owner:npg_PyY4a2UEzdBh@ep-super-wildflower-aofmcegd-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")
neon_cursor = neon_conn.cursor(cursor_factory=RealDictCursor)

tables = ['maziwa', 'diagnosis_history', 'diseases']

for table in tables:
    print(f"\n=== {table} ===")
    
    # Get columns from local
    local_cursor.execute(f"""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    local_columns = local_cursor.fetchall()
    print("Local columns:", [col['column_name'] for col in local_columns])
    
    # Get columns from Neon
    neon_cursor.execute(f"""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    neon_columns = neon_cursor.fetchall()
    print("Neon columns:", [col['column_name'] for col in neon_columns])
    
    # Find missing columns in Neon
    local_col_names = {col['column_name'] for col in local_columns}
    neon_col_names = {col['column_name'] for col in neon_columns}
    missing = local_col_names - neon_col_names
    if missing:
        print(f"Missing in Neon: {missing}")

local_cursor.close()
local_conn.close()
neon_cursor.close()
neon_conn.close()
