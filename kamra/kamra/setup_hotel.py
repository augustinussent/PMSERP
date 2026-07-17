import frappe

def setup_hotel():
    if not frappe.db.exists("Property", "Spencer Green Hotel"):
        doc = frappe.new_doc("Property")
        doc.property_name = "Spencer Green Hotel"
        doc.currency = "IDR"
        doc.timezone = "Asia/Jakarta"
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Property 'Spencer Green Hotel' created successfully!")
    else:
        print("Property 'Spencer Green Hotel' already exists.")
