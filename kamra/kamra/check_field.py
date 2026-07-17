import frappe
meta = frappe.get_meta("Company")
fields = [df.fieldname for df in meta.fields]
print("default_letter_head exists:", "default_letter_head" in fields)
if "default_letter_head" not in fields:
    print("Fields in Company:", fields)
