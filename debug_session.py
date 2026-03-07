import os
from pathlib import Path
import json
import uuid


def test_session_creation():
    temp_dir = ".antigravity"
    session_file = "secure_session.json"

    path = Path(temp_dir)
    try:
        path.mkdir(parents=True, exist_ok=True)
        print(f"[SUCCESS] Directory created/verified: {path.absolute()}")

        session_data = {"port": 12345, "token": str(uuid.uuid4()), "pid": os.getpid()}

        lock_file = path / session_file
        with open(lock_file, "w") as f:
            json.dump(session_data, f)

        print(f"[SUCCESS] File written: {lock_file.absolute()}")
        print(f"Content: {session_data}")

    except Exception as e:
        print(f"[ERROR] Failed to create session: {e}")


if __name__ == "__main__":
    test_session_creation()
