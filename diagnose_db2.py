import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# The tenant ID is wfccfllcbnlepudnokpu
# Password is 100200300aA
# Try changing the host to the direct DB connection instead of pooler
# According to Supabase, direct connection is usually db.[project-ref].supabase.co:5432

direct_url = "postgresql://postgres:100200300aA@db.wfccfllcbnlepudnokpu.supabase.co:5432/postgres"
print(f"Trying Direct URL: {direct_url}")
try:
    conn = psycopg2.connect(direct_url)
    print(" Connected successfully to Direct URL!")

    # Try the schema changes here since we have a connection
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
    print("Schema fixes applied successfully via Direct URL!")
    conn.close()

    # Also update the .env file with the working URL
    with open(".env", "r") as f:
        env_content = f.read()

    env_content = env_content.replace(DATABASE_URL, direct_url)

    with open(".env", "w") as f:
        f.write(env_content)
    print(" Updated .env file with Direct URL.")

except Exception as e:
    print(f" Failed on Direct URL: {e}")
