import frappe

def restore_company():
    print("Restoring ERPNext's standard Company doctype...")
    
    # Check if Corporate Client doctype exists in db, if not create a stub to avoid errors?
    # No, bench migrate will create it.

    # Fix Company Doctype metadata
    if frappe.db.exists("DocType", "Company"):
        # Reset module to Setup
        frappe.db.set_value("DocType", "Company", "module", "Setup")
        frappe.db.set_value("DocType", "Company", "custom", 0)
        
    # Also we should delete the 'Company' doctype entry if it thinks it belongs to Kamra,
    # but bench migrate will just sync from erpnext if module is Setup.
    
    # We should also rename the tabCompany table to tabCorporate Client?
    # NO! tabCompany holds the actual ERPNext company "Spencer Green Hotel".
    # Kamra's data (like company_name, gstin) was stored there, but we want to KEEP tabCompany for ERPNext.
    # The Corporate Client table (tabCorporate Client) will be newly created by bench migrate.
    # We can just let bench migrate do its job.
    
    frappe.db.commit()
    print("Done. Now you MUST run 'bench migrate'!")

if __name__ == "__main__":
    restore_company()
