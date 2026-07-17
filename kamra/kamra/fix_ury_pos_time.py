import os

def fix_ury_datetime():
    print("Fixing URY POS Invoice hook datetime error...")
    
    # Path on the VPS
    file_path = '/home/frappeuser/frappe-bench/apps/ury/ury/ury/hooks/ury_pos_invoice.py'
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    with open(file_path, 'r') as f:
        content = f.read()
        
    if "get_datetime(doc.creation)" not in content:
        # We need to make sure frappe.utils.get_datetime is available. 
        # But maybe we can just do: type check for string.
        # Or even easier, replace doc.creation with frappe.utils.get_datetime(doc.creation)
        
        # In frappe hooks, 'import frappe' is usually there.
        # We'll just replace "doc.creation" with "frappe.utils.get_datetime(doc.creation)"
        
        content = content.replace(
            "time_difference = current_time - doc.creation",
            "time_difference = current_time - frappe.utils.get_datetime(doc.creation)"
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        print("[+] Successfully patched ury_pos_invoice.py")
    else:
        print("[=] Already patched.")

if __name__ == "__main__":
    fix_ury_datetime()
