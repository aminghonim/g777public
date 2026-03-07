import os
import codecs

FILES_TO_CLEAN = [
    r"d:\WORK\2\ui\business_setup_page.py",
    r"d:\WORK\2\ui\pairing_page.py",
    r"d:\WORK\2\ui\theme_manager.py",
    r"d:\WORK\2\ui\theme_settings_page.py",
    r"d:\WORK\2\ui\translations.py",
    r"d:\WORK\2\ui\modules\number_filter.py"
]

def remove_bom(filepath):
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            
        if content.startswith(codecs.BOM_UTF8):
            clean_content = content[len(codecs.BOM_UTF8):]
            with open(filepath, 'wb') as f:
                f.write(clean_content)
            print(f"FIXED (Removed BOM): {filepath}")
        else:
            print(f"OK (No BOM): {filepath}")
            
    except Exception as e:
        print(f"ERROR processing {filepath}: {e}")

if __name__ == "__main__":
    print("Starting BOM Cleanup...")
    for f in FILES_TO_CLEAN:
        remove_bom(f)
    print("Done.")
