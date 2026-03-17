import sqlite3
import os

db_path = os.path.expanduser("~/.antigravity_tools/token_stats.db")

if not os.path.exists(db_path):
    print(f"Error: DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("--- Database Tables ---")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
for table in tables:
    table_name = table[0]
    print(f"\nTable: {table_name}")

    c.execute(f"PRAGMA table_info({table_name})")
    columns = c.fetchall()
    print("Columns:", [col[1] for col in columns])

    c.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = c.fetchall()
    print("Recent Content:")
    for row in rows:
        print(row)

conn.close()
