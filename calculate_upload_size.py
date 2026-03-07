import os

# المجلدات والملفات التي سنستبعدها (التي تسبب الضخم)
ignored = [
    '.git', '.antigravity', 'Backups', 'venv', '.venv', 
    'chrome_profile', 'node_modules', '.agent', 'tests', 
    'baileys-service', '.pytest_cache', 'htmlcov', 
    'coverage_report', 'coverage_frontend'
]

def get_clean_size(start_path='.'):
    total_size = 0
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        # تصفية المجلدات المستبعدة
        dirnames[:] = [d for d in dirnames if d not in ignored]
        
        for f in filenames:
            if any(ext in f for ext in ['.mp4', '.zip', '.tar.gz', '.exe']):
                continue
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
                file_count += 1
            except:
                pass
    return total_size, file_count

size, count = get_clean_size()
print(f"Total Clean Size: {size / (1024*1024):.2f} MB")
print(f"Total Files to Upload: {count}")
