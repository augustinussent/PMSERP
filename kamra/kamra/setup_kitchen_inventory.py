import frappe

def setup_kitchen_inventory():
    print("Setting up Central Kitchen Inventory and Cost Centers...")
    
    # 1. Get the default company
    company = frappe.defaults.get_user_default("Company")
    if not company:
        companies = frappe.get_all("Company")
        if not companies:
            print("No company found! Please create a Company first in ERPNext.")
            return
        company = companies[0].name
        
    company_abbr = frappe.db.get_value("Company", company, "abbr")
    
    # 2. Get Parent Warehouse
    parent_warehouse = frappe.db.get_value("Warehouse", {"is_group": 1, "company": company, "parent_warehouse": ["in", ["", None]]}, "name")
    if not parent_warehouse:
        parent_warehouse = frappe.db.get_value("Warehouse", {"is_group": 1, "company": company}, "name")
        
    # 3. Create Central Kitchen Warehouse
    warehouse_name = "Central Kitchen"
    warehouse_id = f"{warehouse_name} - {company_abbr}"
    if not frappe.db.exists("Warehouse", warehouse_id):
        doc = frappe.new_doc("Warehouse")
        doc.warehouse_name = warehouse_name
        doc.company = company
        if parent_warehouse:
            doc.parent_warehouse = parent_warehouse
        doc.is_group = 0
        doc.insert(ignore_permissions=True)
        print(f"Created Warehouse: {warehouse_id}")
    else:
        print(f"Warehouse already exists: {warehouse_id}")
        
    # 4. Get Parent Cost Center (try Direct Expenses, then Expenses, then Root)
    parent_cost_center = frappe.db.get_value("Cost Center", {"is_group": 1, "company": company, "cost_center_name": ["like", "%Direct Expense%"]}, "name")
    if not parent_cost_center:
        parent_cost_center = frappe.db.get_value("Cost Center", {"is_group": 1, "company": company, "cost_center_name": ["like", "%Expense%"]}, "name")
    if not parent_cost_center:
        parent_cost_center = frappe.db.get_value("Cost Center", {"is_group": 1, "company": company, "parent_cost_center": ["in", ["", None]]}, "name")

    # 5. Create Cost Centers
    cost_centers = [
        "F&B Kenari Restaurant",
        "F&B Rintik Rindu Pool Cafe",
        "F&B Banquet and Breakfast",
        "HR Staff Meal"
    ]
    
    for cc in cost_centers:
        cc_id = f"{cc} - {company_abbr}"
        if not frappe.db.exists("Cost Center", cc_id):
            doc = frappe.new_doc("Cost Center")
            doc.cost_center_name = cc
            doc.company = company
            if parent_cost_center:
                doc.parent_cost_center = parent_cost_center
            doc.is_group = 0
            doc.insert(ignore_permissions=True)
            print(f"Created Cost Center: {cc_id} under {parent_cost_center}")
        else:
            print(f"Cost Center already exists: {cc_id}")
            
    frappe.db.commit()
    print("Kitchen Inventory Setup Completed Successfully!")
