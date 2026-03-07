import os

def update_gemini_version(root_dir):
    for root, dirs, files in os.walk(root_dir):
        # Skip unnecessary directories
        if any(skip in root for skip in ['.git', '.venv', 'node_modules', '__pycache__']):
            continue
            
        for file in files:
            if file.endswith(('.py', '.json', '.bat', '.env')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if 'gemini-2.0-flash' in content:
                        new_content = content.replace('gemini-2.0-flash', 'gemini-2.0-flash')
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Successfully Updated: {file_path}")
                except Exception as e:
                    print(f"Error updating {file_path}: {e}")

if __name__ == "__main__":
    update_gemini_version(r"D:\WORK\2")
