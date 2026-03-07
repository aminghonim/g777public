import tarfile
import os

backup_path = r"d:\WORK\2\BACKUP_FROM_CLOUD\FULL_SERVER_BACKUP.tar.gz"

if not os.path.exists(backup_path):
    print(f"Error: {backup_path} not found.")
else:
    try:
        with tarfile.open(backup_path, "r:gz") as tar:
            print(f"Listing contents of {backup_path}:")
            for member in tar.getmembers()[
                :20
            ]:  # Only list the first 20 to check structure
                print(f"{member.name} ({member.size} bytes)")
    except Exception as e:
        print(f"Error reading tar file: {e}")
