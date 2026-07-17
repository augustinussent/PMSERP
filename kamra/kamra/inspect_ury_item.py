import frappe
import json

def get_schema():
    try:
        doc = frappe.get_doc('DocType', 'URY Menu Item')
        print("--- URY Menu Item Schema ---")
        print(json.dumps([{'fieldname': f.fieldname, 'fieldtype': f.fieldtype, 'options': f.options, 'reqd': f.reqd} for f in doc.fields], indent=2))
    except Exception as e:
        print(f"Error fetching URY Menu Item: {e}")
        
    try:
        companies = frappe.get_all("Company", pluck="name")
        print(f"\nCompanies found: {companies}")
        
        branches = frappe.get_all("Branch", pluck="name")
        print(f"Branches found: {branches}")
        
        rooms = frappe.get_all("URY Room", pluck="name")
        print(f"URY Rooms found: {rooms}")
    except Exception as e:
        print(f"Error fetching dependencies: {e}")
