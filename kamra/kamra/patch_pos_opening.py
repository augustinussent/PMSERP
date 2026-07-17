import os
import re

def patch_pos_check():
    print("Patching pos_opening_check in URY API...")
    file_path = '/home/frappeuser/frappe-bench/apps/ury/ury/ury/doctype/ury_order/ury_order.py'
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    with open(file_path, 'r') as f:
        content = f.read()
        
    # Replace False with True for Administrator
    old_code = '''    if user == "Administrator":
        return {
            "opening_exists": False,  # Assuming no POS opening entry is needed for Administrator
            "cashier": None,
            "pos_profile": None,
        }'''
        
    new_code = '''    if user == "Administrator":
        return {
            "opening_exists": True,  
            "cashier": "Administrator",
            "pos_profile": "POS - Spencer Green Hotel",
        }'''
        
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(file_path, 'w') as f:
            f.write(content)
        print("[+] Successfully patched Administrator access in pos_opening_check!")
    else:
        # Check if already patched
        if '"opening_exists": True' in content and 'user == "Administrator"' in content:
            print("[=] Already patched.")
        else:
            print("[!] Could not find the exact code block to patch.")
            print(old_code)

if __name__ == "__main__":
    patch_pos_check()
