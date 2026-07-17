import os
import subprocess

def find_error():
    print("Grepping for error message in URY app...")
    result = subprocess.run(
        ["grep", "-rnC", "5", "POS Opening Entry is not created", "/home/frappeuser/frappe-bench/apps/ury/"],
        capture_output=True, text=True
    )
    print(result.stdout)
    
if __name__ == "__main__":
    find_error()
