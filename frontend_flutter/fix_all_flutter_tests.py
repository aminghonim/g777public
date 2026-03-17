import os
import glob
import re

files = glob.glob("test/**/*_test.dart", recursive=True)


def fix_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    changed = False

    if "package:flutter_secure_storage/flutter_secure_storage.dart" not in content:
        content = (
            "import 'package:flutter_secure_storage/flutter_secure_storage.dart';\n"
            + content
        )
        changed = True

    if "FlutterSecureStorage.setMockInitialValues({});" not in content:
        # Avoid creating duplicate setUpAll or inside a weird place
        content = content.replace(
            "void main() {",
            "void main() {\n  setUpAll(() {\n    FlutterSecureStorage.setMockInitialValues({});\n  });\n",
        )
        changed = True

    if changed:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {file_path}")


for f in files:
    try:
        fix_file(f)
    except Exception as e:
        print(f"Error {f}: {e}")
