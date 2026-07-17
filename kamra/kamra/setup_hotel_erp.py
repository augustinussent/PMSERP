import frappe

def setup_hotel_erp():
    """
    Complete Hotel ERP Setup for Spencer Green Hotel (Bintang 3).
    Creates: Accounts, Cost Centers, Warehouses, Item Groups,
    Designations, POS Profile, Purchase workflow.
    """
    print("=" * 60)
    print("COMPLETE HOTEL ERP SETUP - SPENCER GREEN HOTEL")
    print("=" * 60)

    company = "Spencer Green Hotel"
    abbr = frappe.db.get_value("Company", company, "abbr") or "SGH"
    currency = frappe.db.get_value("Company", company, "default_currency") or "IDR"

    if not frappe.db.exists("Company", company):
        print("ABORT: Company not found!")
        return

    # ══════════════════════════════════════════════════════════
    # STEP 1: CHART OF ACCOUNTS
    # ══════════════════════════════════════════════════════════
    print(f"\n{'═' * 50}")
    print("STEP 1: Chart of Accounts")
    print(f"{'═' * 50}")

    def get_or_create_account(account_name, root_type, account_type=None,
                              parent_name=None, is_group=0, account_number=None):
        """Find existing or create new account."""
        # Try find by account_number first
        if account_number:
            existing = frappe.db.get_value("Account",
                {"company": company, "account_number": account_number}, "name")
            if existing:
                return existing

        # Try find by name
        full_name = f"{account_name} - {abbr}"
        if account_number:
            full_name = f"{account_number} - {account_name} - {abbr}"
        if frappe.db.exists("Account", full_name):
            return full_name

        # Find parent
        if parent_name:
            parent = f"{parent_name} - {abbr}"
            if not frappe.db.exists("Account", parent):
                parent = frappe.db.get_value("Account",
                    {"company": company, "root_type": root_type, "is_group": 1}, "name")
        else:
            parent = frappe.db.get_value("Account",
                {"company": company, "root_type": root_type, "is_group": 1}, "name")

        if not parent:
            print(f"    [!] Cannot find parent for {account_name} (root_type={root_type})")
            return None

        acc = frappe.new_doc("Account")
        acc.account_name = account_name
        if account_number:
            acc.account_number = account_number
        acc.company = company
        acc.root_type = root_type
        acc.account_type = account_type
        acc.parent_account = parent
        acc.is_group = is_group
        try:
            acc.insert(ignore_permissions=True)
            print(f"    [+] {acc.name}")
            return acc.name
        except frappe.DuplicateEntryError:
            return frappe.db.get_value("Account",
                {"company": company, "account_name": account_name}, "name")
        except Exception as e:
            print(f"    [!] Error creating {account_name}: {e}")
            return None

    # ── Income Accounts ──
    print("\n  Income Accounts:")
    income_accounts = [
        ("Pendapatan Kamar", "4110.001", "Income Account"),
        ("Pendapatan F&B Dine In", "4110.002", "Income Account"),
        ("Pendapatan F&B Online - Gojek", "4110.003", "Income Account"),
        ("Pendapatan F&B Online - Shopee Food", "4110.004", "Income Account"),
        ("Pendapatan F&B Online - Grab Food", "4110.005", "Income Account"),
        ("Pendapatan Banquet & Meeting", "4110.006", "Income Account"),
        ("Pendapatan MICE", "4110.007", "Income Account"),
        ("Pendapatan Grup", "4110.008", "Income Account"),
        ("Pendapatan Lain-lain", "4120.001", "Income Account"),
    ]
    for name, num, atype in income_accounts:
        get_or_create_account(name, "Income", atype, account_number=num)

    # ── COGS / HPP Accounts ──
    print("\n  COGS / HPP Accounts:")
    cogs_accounts = [
        ("HPP F&B - Bahan Makanan", "5210.001", "Cost of Goods Sold"),
        ("HPP F&B - Bahan Minuman", "5210.002", "Cost of Goods Sold"),
        ("HPP Amenities Kamar", "5210.003", "Cost of Goods Sold"),
        ("HPP Linen & Laundry", "5210.004", "Cost of Goods Sold"),
    ]
    for name, num, atype in cogs_accounts:
        get_or_create_account(name, "Expense", atype, account_number=num)

    # ── Liability Accounts ──
    print("\n  Liability Accounts:")
    # Ensure liability root group
    liability_root = frappe.db.get_value("Account",
        {"company": company, "root_type": "Liability", "is_group": 1}, "name")
    if not liability_root:
        get_or_create_account("Liabilities", "Liability", is_group=1)

    liability_accounts = [
        ("Hutang Dagang", "2111.001", "Payable"),
        ("Hutang Pajak PPN Keluaran", "2112.001", "Tax"),
        ("Hutang Pajak PPh 21", "2113.001", "Tax"),
        ("Hutang Gaji", "2114.001", "Payable"),
        ("Deposit Tamu", "2115.001", None),
        ("Pendapatan Diterima di Muka", "2116.001", None),
    ]
    for name, num, atype in liability_accounts:
        get_or_create_account(name, "Liability", atype, account_number=num)

    # ── Equity Accounts ──
    print("\n  Equity Accounts:")
    equity_root = frappe.db.get_value("Account",
        {"company": company, "root_type": "Equity", "is_group": 1}, "name")
    if not equity_root:
        get_or_create_account("Equity", "Equity", is_group=1)

    equity_accounts = [
        ("Modal Disetor", "3111.001", "Equity"),
        ("Laba Ditahan", "3211.001", "Equity"),
    ]
    for name, num, atype in equity_accounts:
        get_or_create_account(name, "Equity", atype, account_number=num)

    frappe.db.commit()

    # ══════════════════════════════════════════════════════════
    # STEP 2: COST CENTERS
    # ══════════════════════════════════════════════════════════
    print(f"\n{'═' * 50}")
    print("STEP 2: Cost Centers")
    print(f"{'═' * 50}")

    parent_cc = frappe.db.get_value("Cost Center",
        {"company": company, "is_group": 1}, "name")

    new_cost_centers = [
        "Front Office",
        "Housekeeping",
        "Marketing & Sales",
        "Engineering",
        "Administration",
        "Security",
        "Human Resources",
    ]

    for cc_name in new_cost_centers:
        cc_id = f"{cc_name} - {abbr}"
        if not frappe.db.exists("Cost Center", cc_id):
            cc = frappe.new_doc("Cost Center")
            cc.cost_center_name = cc_name
            cc.company = company
            cc.parent_cost_center = parent_cc
            cc.is_group = 0
            try:
                cc.insert(ignore_permissions=True)
                print(f"  [+] {cc.name}")
            except Exception as e:
                print(f"  [!] {cc_name}: {e}")
        else:
            print(f"  [=] {cc_id}")

    frappe.db.commit()

    # ══════════════════════════════════════════════════════════
    # STEP 3: WAREHOUSES
    # ══════════════════════════════════════════════════════════
    print(f"\n{'═' * 50}")
    print("STEP 3: Warehouses")
    print(f"{'═' * 50}")

    new_warehouses = [
        "Bar - Rintik Rindu",
        "Linen Store",
        "Amenities Store",
        "General Store",
        "Housekeeping Store",
    ]

    for wh_name in new_warehouses:
        wh_id = f"{wh_name} - {abbr}"
        if not frappe.db.exists("Warehouse", wh_id):
            wh = frappe.new_doc("Warehouse")
            wh.warehouse_name = wh_name
            wh.company = company
            try:
                wh.insert(ignore_permissions=True)
                print(f"  [+] {wh.name}")
            except Exception as e:
                print(f"  [!] {wh_name}: {e}")
        else:
            print(f"  [=] {wh_id}")

    frappe.db.commit()

    # ══════════════════════════════════════════════════════════
    # STEP 4: ITEM GROUPS
    # ══════════════════════════════════════════════════════════
    print(f"\n{'═' * 50}")
    print("STEP 4: Item Groups")
    print(f"{'═' * 50}")

    parent_ig = "All Item Groups"
    new_item_groups = [
        "Raw Materials - Food",
        "Raw Materials - Beverage",
        "Linen",
        "Amenities",
        "Cleaning Supplies",
        "Bar Supplies",
        "Office Supplies",
        "Engineering Supplies",
    ]

    for ig_name in new_item_groups:
        if not frappe.db.exists("Item Group", ig_name):
            ig = frappe.new_doc("Item Group")
            ig.item_group_name = ig_name
            ig.parent_item_group = parent_ig
            try:
                ig.insert(ignore_permissions=True)
                print(f"  [+] {ig_name}")
            except Exception as e:
                print(f"  [!] {ig_name}: {e}")
        else:
            print(f"  [=] {ig_name}")

    frappe.db.commit()

    # ══════════════════════════════════════════════════════════
    # STEP 5: EMPLOYEE DESIGNATIONS
    # ══════════════════════════════════════════════════════════
    print(f"\n{'═' * 50}")
    print("STEP 5: Employee Designations")
    print(f"{'═' * 50}")

    designations = [
        "General Manager",
        "Front Office Manager",
        "Food & Beverage Manager",
        "Marketing Manager",
        "Front Officer",
        "Housekeeping Attendant",
        "Executive Housekeeper",
        "Supervisor Housekeeping",
        "Order Taker",
        "Chef",
        "Supervisor F&B",
        "Cook",
        "Cook Helper",
        "Steward",
        "Waiters",
        "F&B Banquet",
        "Public Area Attendant",
        "Driver",
        "Security",
        "Barista",
        "Gardener",
        "Digital Marketing",
        "Engineering Staff",
        "Chief Engineering",
        "Accounting Staff",
        "HRM Staff",
        "Admin Store",
        "Receptionist",
    ]

    for d in designations:
        if not frappe.db.exists("Designation", d):
            doc = frappe.new_doc("Designation")
            doc.designation = d
            try:
                doc.insert(ignore_permissions=True)
                print(f"  [+] {d}")
            except Exception as e:
                print(f"  [!] {d}: {e}")
        else:
            print(f"  [=] {d}")

    frappe.db.commit()

    # ══════════════════════════════════════════════════════════
    # STEP 6: POS PROFILE
    # ══════════════════════════════════════════════════════════
    print(f"\n{'═' * 50}")
    print("STEP 6: POS Profile")
    print(f"{'═' * 50}")

    # Get the correct references
    warehouse = frappe.db.get_value("Warehouse",
        {"company": company, "warehouse_name": "Central Kitchen"}, "name") or \
        frappe.db.get_value("Warehouse",
        {"company": company, "is_group": 0}, "name")

    write_off_account = frappe.db.get_value("Account",
        {"company": company, "account_name": "Write Off"}, "name") or \
        frappe.db.get_value("Account",
        {"company": company, "account_type": "Expense Account", "is_group": 0}, "name")

    cost_center = f"Main - {abbr}"
    if not frappe.db.exists("Cost Center", cost_center):
        cost_center = frappe.db.get_value("Cost Center",
            {"company": company, "is_group": 0}, "name")

    cash_account = frappe.db.get_value("Account",
        {"company": company, "account_type": "Cash", "is_group": 0}, "name")

    income_account = frappe.db.get_value("Account",
        {"company": company, "account_number": "4110.002"}, "name") or \
        frappe.db.get_value("Account",
        {"company": company, "account_type": "Income Account", "is_group": 0}, "name")

    price_list = frappe.db.get_value("Price List", {"selling": 1}, "name")
    if not price_list:
        pl = frappe.new_doc("Price List")
        pl.price_list_name = "Standard Selling"
        pl.selling = 1
        pl.currency = currency
        pl.insert(ignore_permissions=True)
        price_list = pl.name
        print(f"  [+] Created Price List: {price_list}")

    # Mode of Payment
    if not frappe.db.exists("Mode of Payment", "Cash"):
        mop = frappe.new_doc("Mode of Payment")
        mop.mode_of_payment = "Cash"
        mop.type = "Cash"
        mop.append("accounts", {"company": company, "default_account": cash_account})
        mop.insert(ignore_permissions=True)
        print(f"  [+] Created Mode of Payment: Cash")

    print(f"\n  POS Config:")
    print(f"    Warehouse: {warehouse}")
    print(f"    Write-off: {write_off_account}")
    print(f"    Cost Center: {cost_center}")
    print(f"    Cash: {cash_account}")
    print(f"    Income: {income_account}")
    print(f"    Price List: {price_list}")

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
    prof.cost_center = cost_center
    prof.income_account = income_account
    prof.currency = currency
    prof.selling_price_list = price_list
    prof.country = "Indonesia"

    prof.set("payments", [])
    prof.append("payments", {
        "mode_of_payment": "Cash",
        "default": 1,
        "account": cash_account
    })

    prof.set("applicable_for_users", [])
    prof.append("applicable_for_users", {
        "user": "Administrator",
        "default": 1
    })

    try:
        if prof.is_new():
            prof.insert(ignore_permissions=True)
            print(f"\n  [+] Created POS Profile: {profile_name}")
        else:
            prof.save(ignore_permissions=True)
            print(f"\n  [~] Updated POS Profile: {profile_name}")
    except Exception as e:
        print(f"\n  [!] POS Profile Error: {e}")

    frappe.db.commit()

    # ══════════════════════════════════════════════════════════
    # STEP 7: PURCHASE WORKFLOW SETTINGS
    # ══════════════════════════════════════════════════════════
    print(f"\n{'═' * 50}")
    print("STEP 7: Purchase Workflow")
    print(f"{'═' * 50}")

    # Ensure buying price list
    buy_pl = frappe.db.get_value("Price List", {"buying": 1}, "name")
    if not buy_pl:
        pl = frappe.new_doc("Price List")
        pl.price_list_name = "Standard Buying"
        pl.buying = 1
        pl.currency = currency
        pl.insert(ignore_permissions=True)
        print(f"  [+] Created Price List: Standard Buying")

    # Ensure Supplier Group
    if not frappe.db.exists("Supplier Group", "All Supplier Groups"):
        sg = frappe.new_doc("Supplier Group")
        sg.supplier_group_name = "All Supplier Groups"
        sg.insert(ignore_permissions=True)

    supplier_groups = ["Supplier Bahan Makanan", "Supplier Bahan Minuman",
                       "Supplier Amenities", "Supplier Linen",
                       "Supplier Cleaning", "Supplier Umum"]
    for sg_name in supplier_groups:
        if not frappe.db.exists("Supplier Group", sg_name):
            sg = frappe.new_doc("Supplier Group")
            sg.supplier_group_name = sg_name
            sg.parent_supplier_group = "All Supplier Groups"
            try:
                sg.insert(ignore_permissions=True)
                print(f"  [+] Supplier Group: {sg_name}")
            except Exception as e:
                print(f"  [!] {sg_name}: {e}")
        else:
            print(f"  [=] {sg_name}")

    frappe.db.commit()

    # ══════════════════════════════════════════════════════════
    # FINAL AUDIT
    # ══════════════════════════════════════════════════════════
    print(f"\n{'═' * 50}")
    print("FINAL AUDIT")
    print(f"{'═' * 50}")

    audit = {
        "Accounts": frappe.db.count("Account", {"company": company}),
        "Cost Centers": frappe.db.count("Cost Center", {"company": company}),
        "Warehouses": frappe.db.count("Warehouse", {"company": company}),
        "Item Groups": frappe.db.count("Item Group"),
        "Designations": frappe.db.count("Designation"),
        "POS Profiles": frappe.db.count("POS Profile", {"company": company}),
        "Supplier Groups": frappe.db.count("Supplier Group"),
        "Items (menu)": frappe.db.count("Item"),
        "URY Restaurants": frappe.db.count("URY Restaurant"),
        "URY Menus": frappe.db.count("URY Menu"),
    }

    for label, count in audit.items():
        print(f"  {label}: {count}")

    print(f"\n{'=' * 60}")
    print("HOTEL ERP SETUP COMPLETE!")
    print("=" * 60)
