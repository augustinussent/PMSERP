import frappe

def setup_pos_profile():
    """Create POS Profile for URY so /pos page works."""
    print("Setting up POS Profile for URY...")
    
    company = "Spencer Green Hotel"
    
    if not frappe.db.exists("Company", company):
        print(f"ABORT: Company '{company}' not found!")
        return

    comp_doc = frappe.get_doc("Company", company)
    
    # Query directly - don't rely on Company attributes
    warehouse = frappe.db.get_value("Warehouse", 
        {"company": company, "is_group": 0}, "name")
    
    write_off_account = frappe.db.get_value("Account",
        {"company": company, "account_type": "Expense Account", "is_group": 0}, "name")
    
    write_off_cost_center = frappe.db.get_value("Cost Center",
        {"company": company, "is_group": 0}, "name")
    
    income_account = frappe.db.get_value("Account", 
        {"company": company, "account_type": "Income Account", "is_group": 0}, "name")
    
    print(f"  Company: {company}")
    print(f"  Warehouse: {warehouse}")
    print(f"  Write-off Account: {write_off_account}")
    print(f"  Cost Center: {write_off_cost_center}")
    print(f"  Income Account: {income_account}")

    if not warehouse:
        print("WARNING: No warehouse found. Creating default one...")
        wh = frappe.new_doc("Warehouse")
        wh.warehouse_name = "Stores"
        wh.company = company
        wh.insert(ignore_permissions=True)
        warehouse = wh.name
        print(f"  Created Warehouse: {warehouse}")

    profile_name = f"POS - {company}"
    
    if frappe.db.exists("POS Profile", profile_name):
        print(f"  POS Profile already exists: {profile_name}")
        prof = frappe.get_doc("POS Profile", profile_name)
    else:
        prof = frappe.new_doc("POS Profile")
        prof.name = profile_name
        
    prof.company = company
    prof.warehouse = warehouse
    prof.write_off_account = write_off_account
    prof.write_off_cost_center = write_off_cost_center
    prof.currency = comp_doc.default_currency or "IDR"
    
    # Set selling price list
    price_list = frappe.db.get_value("Price List", {"selling": 1}, "name") or "Standard Selling"
    prof.selling_price_list = price_list
    
    # Add payment method (Cash)
    if not prof.get("payments"):
        # Find or create a Mode of Payment
        if not frappe.db.exists("Mode of Payment", "Cash"):
            mop = frappe.new_doc("Mode of Payment")
            mop.mode_of_payment = "Cash"
            mop.type = "Cash"
            mop.insert(ignore_permissions=True)
            print("  Created Mode of Payment: Cash")
            
        # Find a cash/bank account
        cash_account = frappe.db.get_value("Account",
            {"company": company, "account_type": "Cash", "is_group": 0}, "name")
        if not cash_account:
            cash_account = frappe.db.get_value("Account",
                {"company": company, "account_type": "Bank", "is_group": 0}, "name")
        
        prof.append("payments", {
            "mode_of_payment": "Cash",
            "default": 1,
            "account": cash_account
        })
    
    # Add applicable user (Administrator)
    if not prof.get("applicable_for_users"):
        prof.append("applicable_for_users", {
            "user": "Administrator",
            "default": 1
        })
    
    try:
        if prof.is_new():
            prof.insert(ignore_permissions=True)
            print(f"\n[+] Created POS Profile: {profile_name}")
        else:
            prof.save(ignore_permissions=True)
            print(f"\n[~] Updated POS Profile: {profile_name}")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        # Print what we have for debugging
        print(f"\n  Debug - all accounts:")
        accounts = frappe.get_all("Account", 
            filters={"company": company, "is_group": 0},
            fields=["name", "account_type"],
            limit=20)
        for a in accounts:
            print(f"    {a.account_type}: {a.name}")
        
        print(f"\n  Debug - all warehouses:")
        whs = frappe.get_all("Warehouse", 
            filters={"company": company},
            fields=["name", "is_group"],
            limit=10)
        for w in whs:
            print(f"    {w.name} (group={w.is_group})")
        return
    
    frappe.db.commit()
    print("\nPOS Profile setup complete!")
    print("You should now be able to access http://43.134.40.189/pos")
