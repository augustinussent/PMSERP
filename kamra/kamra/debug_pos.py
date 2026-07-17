import frappe

def debug_pos_outlets():
    print("Checking Property and POS Outlets...")
    properties = frappe.get_all("Property", fields=["name", "disabled"])
    print(f"Properties found: {properties}")
    
    outlets = frappe.get_all("POS Outlet", fields=["name", "outlet_name", "property", "disabled"])
    print(f"POS Outlets found: {outlets}")

    menus = frappe.get_all("Menu Item", fields=["name", "item_name", "outlet", "available"], limit=5)
    print(f"Sample Menu Items: {menus}")
