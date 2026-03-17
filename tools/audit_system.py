import os
import re
import ast
import sys

# Add parent directory to path to import translations
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from ui.translations import TRANSLATIONS
except ImportError:
    print("CRITICAL: Could not import TRANSLATIONS from ui.translations")
    sys.exit(1)

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
UI_DIR = os.path.join(PROJECT_ROOT, 'ui')

valid_keys = set(TRANSLATIONS.get('ar', {}).keys()) | set(TRANSLATIONS.get('en', {}).keys())

errors = []
missing_keys = set()

def scan_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Check Syntax
    try:
        ast.parse(content)
    except SyntaxError as e:
        errors.append(f"SYNTAX ERROR in {os.path.basename(filepath)}: {e}")
        return

    # 2. Extract lang_manager.get('KEY') calls
    # Matches: lang_manager.get('key') or lang_manager.get("key")
    matches = re.findall(r"lang_manager\.get\(['\"]([^'\"]+)['\"]", content)
    
    for key in matches:
        if key not in valid_keys:
            missing_keys.add(key)
            errors.append(f"MISSING KEY in {os.path.basename(filepath)}: '{key}'")

def main():
    print("Starting System Audit...")
    print(f"Loaded {len(valid_keys)} valid translation keys.")
    
    for root, dirs, files in os.walk(UI_DIR):
        for file in files:
            if file.endswith('.py'):
                scan_file(os.path.join(root, file))

    print("\nXXX AUDIT RESULTS XXX")
    if not errors:
        print("SUCCESS: No errors found!")
    else:
        print(f"FOUND {len(errors)} ERRORS:")
        for err in errors:
            print(f"- {err}")
    
    if missing_keys:
        print("\nSUMMARY OF MISSING KEYS (Add to translations.py):")
        for k in sorted(missing_keys):
            print(f'        "{k}": "TODO_TRANSLATE",')

if __name__ == "__main__":
    main()
