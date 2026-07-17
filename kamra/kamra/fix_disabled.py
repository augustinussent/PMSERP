import frappe

def fix_disabled():
    print("Fixing disabled fields to ensure they are 0 instead of NULL...")
    
    # Fix Property
    properties = frappe.get_all("Property", fields=["name"])
    for p in properties:
        frappe.db.set_value("Property", p.name, "disabled", 0)
        print(f"Property {p.name}: disabled = 0")
        
    # Fix Venues
    venues = frappe.get_all("Venue", fields=["name"])
    for v in venues:
        frappe.db.set_value("Venue", v.name, "disabled", 0)
        print(f"Venue {v.name}: disabled = 0")
        
    # Fix POS Outlets
    outlets = frappe.get_all("POS Outlet", fields=["name"])
    for o in outlets:
        frappe.db.set_value("POS Outlet", o.name, "disabled", 0)
        print(f"POS Outlet {o.name}: disabled = 0")
        
    frappe.db.commit()
    print("Fix completed successfully! You should now be able to select the Property in Ury.")
