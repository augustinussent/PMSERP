import frappe

def fix_company_query():
    print("Fixing 'Field not permitted in query' for Company doctype...")
    
    # Tambahkan default_letter_head ke search_fields di Company via Property Setter
    doctype = "Company"
    
    # Get current search fields
    meta = frappe.get_meta(doctype)
    current_search_fields = meta.search_fields or ""
    
    fields_to_add = ["default_letter_head", "country"]
    
    for field in fields_to_add:
        if field not in current_search_fields:
            if current_search_fields:
                current_search_fields += f",{field}"
            else:
                current_search_fields = field

    # Set using Property Setter
    if not frappe.db.exists("Property Setter", {"doc_type": doctype, "property": "search_fields"}):
        ps = frappe.new_doc("Property Setter")
        ps.doc_type = doctype
        ps.doctype_or_field = "DocType"
        ps.property = "search_fields"
        ps.property_type = "Data"
        ps.value = current_search_fields
        ps.insert(ignore_permissions=True)
    else:
        ps = frappe.get_doc("Property Setter", {"doc_type": doctype, "property": "search_fields"})
        ps.value = current_search_fields
        ps.save(ignore_permissions=True)
        
    frappe.clear_cache(doctype="Company")
    print(f"[+] Successfully updated search_fields for Company to: {current_search_fields}")

