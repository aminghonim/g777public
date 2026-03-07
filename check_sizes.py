import os

def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                try:
                    total_size += os.path.getsize(fp)
                except:
                    pass
    return total_size

for item in os.listdir('.'):
    if os.path.isdir(item):
        size = get_size(item)
        print(f"{item}: {size / (1024*1024):.2f} MB")
    else:
        size = os.path.getsize(item)
        print(f"{item} (file): {size / (1024*1024):.2f} MB")
