import re

files = [
    "test/login_page_test.dart",
    "test/number_filter_page_test.dart",
]


def fix_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add flutter_secure_storage import if not there
    if "package:flutter_secure_storage/flutter_secure_storage.dart" not in content:
        content = (
            "import 'package:flutter_secure_storage/flutter_secure_storage.dart';\n"
            + content
        )

    # Add mock setup before tests
    if "FlutterSecureStorage.setMockInitialValues({});" not in content:
        content = content.replace(
            "void main() {",
            "void main() {\n  setUpAll(() {\n    FlutterSecureStorage.setMockInitialValues({});\n  });\n",
        )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


for f in files:
    try:
        fix_file(f)
        print(f"Fixed {f}")
    except Exception as e:
        print(f"Error {f}: {e}")
