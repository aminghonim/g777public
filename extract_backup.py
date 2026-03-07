import tarfile
import os

backup_path = r"d:\WORK\2\BACKUP_FROM_CLOUD\FULL_SERVER_BACKUP.tar.gz"
extract_path = r"d:\WORK\2\BACKUP_FROM_CLOUD\extracted"

if not os.path.exists(extract_path):
    os.makedirs(extract_path)

try:
    with tarfile.open(backup_path, "r:gz") as tar:
        tar.extractall(path=extract_path)
        print(f"Extracted to {extract_path}")
        # List contents
        for root, dirs, files in os.walk(extract_path):
            level = root.replace(extract_path, "").count(os.sep)
            indent = " " * 4 * (level)
            print(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 4 * (level + 1)
            for f in files:
                print(f"{subindent}{f}")
except Exception as e:
    print(f"Extraction failed: {e}")
