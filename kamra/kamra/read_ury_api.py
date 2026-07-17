import os

def read_method():
    file_path = '/home/frappeuser/frappe-bench/apps/ury/ury/ury/doctype/ury_order/ury_order.py'
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        in_method = False
        method_lines = []
        for line in lines:
            if "def pos_opening_check" in line:
                in_method = True
            
            if in_method:
                method_lines.append(line)
                if line.strip() == "" and len(method_lines) > 5 and not line.startswith(" ") and not line.startswith("\t"):
                    # Basic heuristic to end method
                    # But let's just grab the next 20 lines
                    if len(method_lines) > 30:
                        break
                        
        print("".join(method_lines[:30]))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_method()
