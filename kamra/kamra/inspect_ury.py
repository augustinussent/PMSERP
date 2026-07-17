import frappe
import json

def get_schema():
    try:
        doc = frappe.get_doc('DocType', 'URY Restaurant')
        print("--- URY Restaurant Schema ---")
        print(json.dumps([{'fieldname': f.fieldname, 'fieldtype': f.fieldtype, 'options': f.options, 'reqd': f.reqd} for f in doc.fields], indent=2))
    except Exception as e:
        print(f"Error fetching URY Restaurant: {e}")
        
    try:
        doc = frappe.get_doc('DocType', 'URY Menu')
        print("\n--- URY Menu Schema ---")
        print(json.dumps([{'fieldname': f.fieldname, 'fieldtype': f.fieldtype, 'options': f.options, 'reqd': f.reqd} for f in doc.fields], indent=2))
    except Exception as e:
        print(f"Error fetching URY Menu: {e}")
