import frappe

def setup_pos_profile():
    """Create POS Profile for URY so /pos page works."""
    print("Setting up POS Profile for URY...")
    
    company = "Spencer Green Hotel"
    abbr = frappe.db.get_value("Company", company, "abbr") or "SGH"
    currency = frappe.db.get_value("Company", company, "default_currency") or "IDR"
    
    if not frappe.db.exists("Company", company):
        print(f"ABORT: Company '{company}' not found!")
        return

    # ── Debug: show what exists ──
    print("\n  Existing Accounts:")
    accounts = frappe.get_all("Account", 
        filters={"company": company, "is_group": 0},
        fields=["name", "account_type", "root_type"],
        limit=50)
    for a in accounts:
        print(f"    [{a.root_type}] {a.account_type or 'N/A'}: {a.name}")
    
    print("\n  Existing Warehouses:")
    warehouses = frappe.get_all("Warehouse",
        filters={"company": company},
        fields=["name", "is_group"])
    for w in warehouses:
        print(f"    {w.name} (group={w.is_group})")
        
    print("\n  Existing Cost Centers:")
    cost_centers = frappe.get_all("Cost Center",
        filters={"company": company},
        fields=["name", "is_group"])
    for cc in cost_centers:
        print(f"    {cc.name} (group={cc.is_group})")

    # ── Find or create Warehouse ──
    warehouse = frappe.db.get_value("Warehouse", 
        {"company": company, "is_group": 0}, "name")
    if not warehouse:
        wh = frappe.new_doc("Warehouse")
        wh.warehouse_name = "Stores"
        wh.company = company
        wh.insert(ignore_permissions=True)
        warehouse = wh.name
        print(f"\n  [+] Created Warehouse: {warehouse}")

    # ── Find or create root accounts ──
    # We need the root account groups first
    def ensure_root_account(root_type, account_name):
        existing = frappe.db.get_value("Account", 
            {"company": company, "root_type": root_type, "is_group": 1}, "name")
        if existing:
            return existing
        acc = frappe.new_doc("Account")
        acc.account_name = account_name
        acc.company = company
        acc.root_type = root_type
        acc.is_group = 1
        acc.insert(ignore_permissions=True)
        print(f"  [+] Created root account: {acc.name}")
        return acc.name

    def ensure_account(account_name, account_type, root_type, parent=None):
        # Try to find existing
        existing = frappe.db.get_value("Account",
            {"company": company, "account_type": account_type, "is_group": 0}, "name")
        if existing:
            return existing
        
        if not parent:
            parent = frappe.db.get_value("Account",
                {"company": company, "root_type": root_type, "is_group": 1}, "name")
        
        acc = frappe.new_doc("Account")
        acc.account_name = account_name
        acc.company = company
        acc.root_type = root_type
        acc.account_type = account_type
        acc.parent_account = parent
        acc.is_group = 0
        acc.insert(ignore_permissions=True)
        print(f"  [+] Created account: {acc.name} (type={account_type})")
        return acc.name

    # Ensure we have expense and income accounts
    expense_root = ensure_root_account("Expense", "Expenses")
    income_root = ensure_root_account("Income", "Income")
    asset_root = ensure_root_account("Asset", "Assets")

    write_off_account = ensure_account("Write Off", "Expense Account", "Expense", expense_root)
    income_account = ensure_account("Sales", "Income Account", "Income", income_root)
    cash_account = ensure_account("Cash", "Cash", "Asset", asset_root)

    # ── Find or create Cost Center ──
    cost_center = frappe.db.get_value("Cost Center",
        {"company": company, "is_group": 0}, "name")
    if not cost_center:
        # Need a parent cost center first
        parent_cc = frappe.db.get_value("Cost Center",
            {"company": company, "is_group": 1}, "name")
        if not parent_cc:
            pcc = frappe.new_doc("Cost Center")
            pcc.cost_center_name = company
            pcc.company = company
            pcc.is_group = 1
            pcc.insert(ignore_permissions=True)
            parent_cc = pcc.name
            print(f"  [+] Created parent Cost Center: {parent_cc}")
        
        cc = frappe.new_doc("Cost Center")
        cc.cost_center_name = "Main"
        cc.company = company
        cc.parent_cost_center = parent_cc
        cc.is_group = 0
        cc.insert(ignore_permissions=True)
        cost_center = cc.name
        print(f"  [+] Created Cost Center: {cost_center}")

    print(f"\n  Final config:")
    print(f"    Warehouse: {warehouse}")
    print(f"    Write-off Account: {write_off_account}")
    print(f"    Cost Center: {cost_center}")
    print(f"    Cash Account: {cash_account}")
    print(f"    Income Account: {income_account}")

    # ── Create POS Profile ──
    profile_name = f"POS - {company}"
    
    if frappe.db.exists("POS Profile", profile_name):
        prof = frappe.get_doc("POS Profile", profile_name)
    else:
        prof = frappe.new_doc("POS Profile")
        prof.name = profile_name
        
    prof.company = company
    prof.warehouse = warehouse
    prof.write_off_account = write_off_account
    prof.write_off_cost_center = cost_center
    prof.currency = currency
    
    # Selling price list
    price_list = frappe.db.get_value("Price List", {"selling": 1}, "name")
    if not price_list:
        pl = frappe.new_doc("Price List")
        pl.price_list_name = "Standard Selling"
        pl.selling = 1
        pl.currency = currency
        pl.insert(ignore_permissions=True)
        price_list = pl.name
        print(f"  [+] Created Price List: {price_list}")
    prof.selling_price_list = price_list
    
    # Mode of Payment: Cash
    if not frappe.db.exists("Mode of Payment", "Cash"):
        mop = frappe.new_doc("Mode of Payment")
        mop.mode_of_payment = "Cash"
        mop.type = "Cash"
        mop.append("accounts", {"company": company, "default_account": cash_account})
        mop.insert(ignore_permissions=True)
        print("  [+] Created Mode of Payment: Cash")

    # Payment method
    prof.set("payments", [])
    prof.append("payments", {
        "mode_of_payment": "Cash",
        "default": 1,
        "account": cash_account
    })
    
    # Applicable user
    prof.set("applicable_for_users", [])
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
        print(f"\n[!] Error saving POS Profile: {e}")
        return
    
    frappe.db.commit()
    print("\nPOS Profile setup complete!")
    print("Try accessing: http://43.134.40.189/pos")
