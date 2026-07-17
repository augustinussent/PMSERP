import frappe

def fix_tabcontact():
    print("Checking and fixing tabContact...")
    # Add is_billing_contact if it doesn't exist
    try:
        frappe.db.sql("ALTER TABLE `tabContact` ADD COLUMN `is_billing_contact` INT(1) NOT NULL DEFAULT 0;")
        print("[+] Added 'is_billing_contact' to tabContact.")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("[=] 'is_billing_contact' already exists.")
        else:
            print(f"[!] Error: {e}")
            
    # There's also is_primary_company, etc, let's just make sure.
    frappe.db.commit()

if __name__ == "__main__":
    fix_tabcontact()
