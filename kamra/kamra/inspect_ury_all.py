import frappe
import json

def inspect():
    for dt in ["URY Room", "URY Menu Course", "URY Restaurant"]:
        try:
            doc = frappe.get_doc("DocType", dt)
            print(f"\n--- {dt} ---")
            print(f"  autoname: {doc.autoname}")
            print(f"  fields:")
            for f in doc.fields:
                if f.fieldtype not in ("Section Break", "Column Break", "Tab Break"):
                    print(f"    {f.fieldname} ({f.fieldtype}) reqd={f.reqd} options={f.options}")
        except Exception as e:
            print(f"\n--- {dt} --- ERROR: {e}")
    
    # Also check what data already exists
    print("\n\n--- EXISTING DATA ---")
    for dt in ["URY Room", "URY Menu Course", "URY Menu", "URY Restaurant", "Item"]:
        try:
            count = frappe.db.count(dt)
            items = frappe.get_all(dt, pluck="name", limit=10)
            print(f"{dt}: {count} records -> {items}")
        except:
            print(f"{dt}: table not found or error")
