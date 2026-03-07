import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    print("Applying Schema Fixes (Rule 11: Tenant Shield) ...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    tables_to_update = [
        "tenant_settings",
        "business_offerings",
        "customer_profiles",
        "conversations",
        "messages",
        "customer_memory",
        "system_prompts",
        "orders",
    ]

    for table in tables_to_update:
        print(f"Adding instance_name to {table}...")
        cursor.execute(
            f"""
            ALTER TABLE {table} 
            ADD COLUMN IF NOT EXISTS instance_name VARCHAR(100) NOT NULL DEFAULT 'G777';
        """
        )

    print("Adding UNIQUE constraint to tenant_settings...")
    cursor.execute(
        """
        ALTER TABLE tenant_settings 
        DROP CONSTRAINT IF EXISTS tenant_settings_instance_name_key;
        
        ALTER TABLE tenant_settings 
        ADD CONSTRAINT tenant_settings_instance_name_key UNIQUE (instance_name);
    """
    )

    conn.commit()
    print("Schema fixes applied successfully!")

    # Check if the tables now have the column
    for table in tables_to_update:
        cursor.execute(
            f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='{table}' and column_name='instance_name';
        """
        )
        if cursor.fetchone():
            print(f"✅ {table} has instance_name")
        else:
            print(f"❌ {table} missing instance_name")

    conn.close()
except Exception as e:
    print(f"Schema update failed: {e}")
