import os

def list_project_files(directory="."):
    print(f"--- Scanning Directory: {os.path.abspath(directory)} ---")
    # الملفات التي نريد تجاهلها (المجلدات المخفية والمكتبات)
    ignore_list = {'.git', '__pycache__', '.venv', 'venv', '.idea', '.vscode'}
    
    for root, dirs, files in os.walk(directory):
        # تصفية المجلدات لتجاهل غير الضروري
        dirs[:] = [d for d in dirs if d not in ignore_list]
        
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}[{os.path.basename(root)}/]")
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith(('.py', '.json', '.yaml', '.txt', '.xlsx')):
                print(f"{sub_indent} {f}")

if __name__ == "__main__":
    list_project_files()
