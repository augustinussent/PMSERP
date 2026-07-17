import frappe

def fix_remaining():
    """Fix designations, write-off account, and POS Profile."""
    company = "Spencer Green Hotel"
    abbr = frappe.db.get_value("Company", company, "abbr") or "SGH"
    currency = frappe.db.get_value("Company", company, "default_currency") or "IDR"

    # ══════════════════════════════════════════════════
    # FIX 1: Designations (need to set doc.name)
    # ══════════════════════════════════════════════════
    print("FIX 1: Employee Designations")
    designations = [
        "General Manager", "Front Office Manager", "Food & Beverage Manager",
        "Front Officer", "Housekeeping Attendant", "Executive Housekeeper",
        "Supervisor Housekeeping", "Order Taker", "Chef", "Supervisor F&B",
        "Cook", "Cook Helper", "Steward", "Waiters", "F&B Banquet",
        "Public Area Attendant", "Driver", "Security", "Barista", "Gardener",
        "Digital Marketing", "Engineering Staff", "Chief Engineering",
        "Accounting Staff", "HRM Staff", "Admin Store", "Receptionist",
    ]
    for d in designations:
        if not frappe.db.exists("Designation", d):
            doc = frappe.new_doc("Designation")
            doc.name = d
            doc.designation = d
            try:
                doc.insert(ignore_permissions=True, ignore_mandatory=True)
                print(f"  [+] {d}")
            except frappe.DuplicateEntryError:
                print(f"  [=] {d}")
            except Exception as e:
                # Try direct SQL as last resort
                try:
                    frappe.db.sql("""INSERT INTO `tabDesignation` 
                        (name, designation, creation, modified, owner, modified_by)
                        VALUES (%s, %s, NOW(), NOW(), 'Administrator', 'Administrator')""",
                        (d, d))
                    print(f"  [+] {d} (SQL)")
                except Exception:
                    print(f"  [!] {d}: {e}")
        else:
            print(f"  [=] {d}")

    frappe.db.commit()

    # ══════════════════════════════════════════════════
    # FIX 2: Write-off Account
    # ══════════════════════════════════════════════════
    print("\nFIX 2: Write-off Account")
    
    # Find expense root
    expense_root = frappe.db.get_value("Account",
        {"company": company, "root_type": "Expense", "is_group": 1}, "name")
    print(f"  Expense root: {expense_root}")

    wo_name = f"Write Off - {abbr}"
    if not frappe.db.exists("Account", wo_name):
        acc = frappe.new_doc("Account")
        acc.account_name = "Write Off"
        acc.company = company
        acc.root_type = "Expense"
        acc.account_type = "Expense Account"
        acc.parent_account = expense_root
        acc.is_group = 0
        acc.insert(ignore_permissions=True)
        print(f"  [+] Created: {acc.name}")
        wo_account = acc.name
    else:
        print(f"  [=] Exists: {wo_name}")
        wo_account = wo_name

    # Also create COGS accounts that were missing
    print("\n  COGS / HPP Accounts:")
    cogs = [
        ("HPP F&B - Bahan Makanan", "5210.001"),
        ("HPP F&B - Bahan Minuman", "5210.002"),
        ("HPP Amenities Kamar", "5210.003"),
        ("HPP Linen & Laundry", "5210.004"),
    ]
    for name, num in cogs:
        full = f"{num} - {name} - {abbr}"
        if not frappe.db.exists("Account", full):
            acc = frappe.new_doc("Account")
            acc.account_name = name
            acc.account_number = num
            acc.company = company
            acc.root_type = "Expense"
            acc.account_type = "Cost of Goods Sold"
            acc.parent_account = expense_root
            acc.is_group = 0
            try:
                acc.insert(ignore_permissions=True)
                print(f"    [+] {acc.name}")
            except Exception as e:
                print(f"    [!] {name}: {e}")
        else:
            print(f"    [=] {full}")

    frappe.db.commit()

    # ══════════════════════════════════════════════════
    # FIX 3: Price List & POS Profile
    # ══════════════════════════════════════════════════
    print("\nFIX 3: Price List & POS Profile")

    # Create proper selling price list
    if not frappe.db.exists("Price List", "Standard Selling"):
        pl = frappe.new_doc("Price List")
        pl.price_list_name = "Standard Selling"
        pl.selling = 1
        pl.currency = currency
        pl.insert(ignore_permissions=True)
        print(f"  [+] Created Price List: Standard Selling")
    else:
        print(f"  [=] Price List exists: Standard Selling")

    # Get all required values
    warehouse = frappe.db.get_value("Warehouse",
        {"company": company, "warehouse_name": "Central Kitchen"}, "name") or \
        frappe.db.get_value("Warehouse",
        {"company": company, "is_group": 0}, "name")

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
    print(f"    Write-off: {wo_account}")
    print(f"    Cost Center: {cost_center}")
    print(f"    Cash: {cash_account}")
    print(f"    Income: {income_account}")
    print(f"    Price List: Standard Selling")

    # Delete old broken POS Profile if exists
    profile_name = f"POS - {company}"
    if frappe.db.exists("POS Profile", profile_name):
        frappe.delete_doc("POS Profile", profile_name, force=True)
        print(f"\n  [x] Deleted old POS Profile")

    prof = frappe.new_doc("POS Profile")
    prof.name = profile_name
    prof.company = company
    prof.warehouse = warehouse
    prof.write_off_account = wo_account
    prof.write_off_cost_center = cost_center
    prof.cost_center = cost_center
    prof.income_account = income_account
    prof.currency = currency
    prof.selling_price_list = "Standard Selling"

    prof.append("payments", {
        "mode_of_payment": "Cash",
        "default": 1,
        "account": cash_account
    })
    prof.append("applicable_for_users", {
        "user": "Administrator",
        "default": 1
    })

    try:
        prof.insert(ignore_permissions=True)
        print(f"\n  [+] Created POS Profile: {profile_name}")
    except Exception as e:
        print(f"\n  [!] POS Profile Error: {e}")
        # Debug
        print(f"\n  Debug - checking each field:")
        for field in ["company", "warehouse", "write_off_account", 
                       "write_off_cost_center", "cost_center", "income_account",
                       "currency", "selling_price_list"]:
            val = getattr(prof, field, None)
            exists = bool(val)
            print(f"    {field}: {val} (set={exists})")

    frappe.db.commit()
    
    # Final count
    print(f"\n{'=' * 50}")
    print("VERIFICATION")
    print(f"{'=' * 50}")
    print(f"  Designations: {frappe.db.count('Designation')}")
    print(f"  POS Profiles: {frappe.db.count('POS Profile', {'company': company})}")
    print(f"  Accounts: {frappe.db.count('Account', {'company': company})}")
    print("Done!")
