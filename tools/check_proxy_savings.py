import sqlite3
import os

db_path = os.path.expanduser("~/.antigravity_tools/proxy_logs.db")


def check_last_log():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        # Checking actual column names for request_logs
        c.execute("PRAGMA table_info(request_logs)")
        cols = [col[1] for col in c.fetchall()]

        # Select latest log
        c.execute("SELECT * FROM request_logs ORDER BY id DESC LIMIT 1")
        row = c.fetchone()

        if row:
            data = dict(zip(cols, row))
            print("\n--- ACTUAL PROXY LOG ---")
            print(f"Original Model (Requested): {data.get('original_model')}")
            print(f"Target Model (Mapped): {data.get('target_model')}")
            print(f"Status: {data.get('status_code')}")

            orig = data.get("original_model")
            target = data.get("target_model")

            if orig and target and orig != target:
                print(f"\n✅ PROOF: The proxy changed {orig} to {target}!")
            else:
                print("\nℹ️ No model swap needed for this request.")
        else:
            print("No logs found.")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()


if __name__ == "__main__":
    check_last_log()
