import os
path = '/home/frappeuser/frappe-bench/apps/ury/ury/ury_pos/api.py'
if os.path.exists(path):
    with open(path, 'r') as f:
        print(f.read())
else:
    print("API file not found at", path)
