import frappe

def fix_all_pos_query_issues():
    print("Fixing POS security query issues forcefully...")
    
    # We will set 'in_standard_filter' and 'in_list_view' to 1 for the problematic fields
    doctype = "Company"
    fields = ["default_letter_head", "country"]
    
    for field in fields:
        # Create or update Property Setter for in_standard_filter
        if not frappe.db.exists("Property Setter", {"doc_type": doctype, "field_name": field, "property": "in_standard_filter"}):
            ps = frappe.new_doc("Property Setter")
            ps.doc_type = doctype
            ps.field_name = field
            ps.doctype_or_field = "DocField"
            ps.property = "in_standard_filter"
            ps.property_type = "Check"
            ps.value = "1"
            ps.insert(ignore_permissions=True)
            print(f"[+] Allowed standard filter for: {field}")
        else:
            ps = frappe.get_doc("Property Setter", {"doc_type": doctype, "field_name": field, "property": "in_standard_filter"})
            ps.value = "1"
            ps.save(ignore_permissions=True)
            print(f"[~] Updated standard filter for: {field}")

        # Create or update Property Setter for in_list_view
        if not frappe.db.exists("Property Setter", {"doc_type": doctype, "field_name": field, "property": "in_list_view"}):
            ps = frappe.new_doc("Property Setter")
            ps.doc_type = doctype
            ps.field_name = field
            ps.doctype_or_field = "DocField"
            ps.property = "in_list_view"
            ps.property_type = "Check"
            ps.value = "1"
            ps.insert(ignore_permissions=True)
            print(f"[+] Allowed list view for: {field}")

    # For good measure, let's also fix Customer if it has similar issues with 'loyalty_program'
    cust_fields = ["loyalty_program", "default_price_list"]
    for field in cust_fields:
        if frappe.db.exists("DocField", {"parent": "Customer", "fieldname": field}):
            if not frappe.db.exists("Property Setter", {"doc_type": "Customer", "field_name": field, "property": "in_standard_filter"}):
                ps = frappe.new_doc("Property Setter")
                ps.doc_type = "Customer"
                ps.field_name = field
                ps.doctype_or_field = "DocField"
                ps.property = "in_standard_filter"
                ps.property_type = "Check"
                ps.value = "1"
                ps.insert(ignore_permissions=True)

    # Finally clear cache globally
    frappe.clear_cache(doctype="Company")
    frappe.clear_cache(doctype="Customer")
    frappe.clear_cache()
    
    print("DONE! Cache cleared.")
