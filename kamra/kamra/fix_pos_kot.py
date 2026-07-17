import frappe

def fix_kot():
    print("Fixing KOT Naming Series in POS Profile...")
    pos_profile = "POS - Spencer Green Hotel"
    
    if frappe.db.exists("POS Profile", pos_profile):
        doc = frappe.get_doc("POS Profile", pos_profile)
        
        # Check if the field exists
        meta = frappe.get_meta("POS Profile")
        has_custom_kot = False
        for df in meta.fields:
            if df.fieldname == "custom_kot_naming_series":
                has_custom_kot = True
                break
                
        if has_custom_kot:
            # Setting it to standard KOT naming series or whatever is available
            # Let's get the options for KOT if it exists, otherwise just set KOT-.YYYY.-
            doc.custom_kot_naming_series = "KOT-.YYYY.-"
            try:
                doc.save(ignore_permissions=True)
                print(f"[+] Successfully set custom_kot_naming_series to {doc.custom_kot_naming_series}")
            except Exception as e:
                print(f"Error saving POS Profile: {e}")
        else:
            print("Field custom_kot_naming_series not found in POS Profile.")
    else:
        print(f"POS Profile {pos_profile} not found!")
        
    frappe.db.commit()

if __name__ == "__main__":
    fix_kot()
