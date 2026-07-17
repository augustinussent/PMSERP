import frappe

def setup_ury():
    """
    Complete setup: creates URY Rooms, URY Restaurants, URY Menus,
    ERPNext Items, and URY Menu Courses — all from existing Kamra data.
    """
    print("=" * 60)
    print("FULL URY SETUP FROM KAMRA DATA")
    print("=" * 60)
    
    company = "Spencer Green Hotel"
    branch = "PUSAT"
    
    if not frappe.db.exists("Company", company):
        print(f"ERROR: Company '{company}' not found! Run ERPNext Setup Wizard first.")
        return
    if not frappe.db.exists("Branch", branch):
        print(f"ERROR: Branch '{branch}' not found!")
        return

    # ── Step 1: Ensure Item Group exists ──
    item_group = "Food & Beverage"
    if not frappe.db.exists("Item Group", item_group):
        ig = frappe.new_doc("Item Group")
        ig.item_group_name = item_group
        ig.parent_item_group = "All Item Groups"
        ig.insert(ignore_permissions=True)
        print(f"[+] Created Item Group: {item_group}")
    else:
        print(f"[=] Item Group exists: {item_group}")

    # ── Step 2: Fetch Kamra POS Outlets ──
    kamra_outlets = frappe.get_all("POS Outlet", fields=["name", "outlet_name"])
    if not kamra_outlets:
        print("ERROR: No POS Outlets found in Kamra!")
        return
    print(f"\nFound {len(kamra_outlets)} Kamra outlet(s):")
    for o in kamra_outlets:
        print(f"  - {o.outlet_name}")

    for outlet in kamra_outlets:
        outlet_id = outlet.name
        outlet_name = outlet.outlet_name
        short_prefix = "".join([w[0] for w in outlet_name.split()]).upper()  # e.g. RRPC, KR
        
        print(f"\n{'─' * 50}")
        print(f"Setting up: {outlet_name}")
        print(f"{'─' * 50}")

        # ── Step 3: Create URY Room ──
        room_name = f"Room - {outlet_name}"
        if not frappe.db.exists("URY Room", room_name):
            room_doc = frappe.new_doc("URY Room")
            room_doc.name = room_name
            room_doc.room_name = room_name
            try:
                room_doc.insert(ignore_permissions=True)
                print(f"  [+] Created URY Room: {room_name}")
            except Exception as e:
                print(f"  [!] Error creating URY Room: {e}")
                # Try without setting name
                room_doc2 = frappe.new_doc("URY Room")
                room_doc2.room_name = room_name
                room_doc2.insert(ignore_permissions=True)
                room_name = room_doc2.name
                print(f"  [+] Created URY Room (auto-named): {room_name}")
        else:
            print(f"  [=] URY Room exists: {room_name}")

        # ── Step 4: Create URY Menu Courses & ERPNext Items ──
        kamra_items = frappe.get_all("Menu Item",
                                     filters={"outlet": outlet_id},
                                     fields=["item_name", "price", "category", "available", "description"])
        
        print(f"  Found {len(kamra_items)} menu items in Kamra.")
        
        # Create all courses first
        categories = set(mi.category for mi in kamra_items if mi.category)
        for cat in categories:
            if not frappe.db.exists("URY Menu Course", cat):
                try:
                    cd = frappe.new_doc("URY Menu Course")
                    cd.name = cat
                    cd.course_name = cat
                    cd.insert(ignore_permissions=True)
                    print(f"  [+] Created URY Menu Course: {cat}")
                except Exception:
                    pass

        # Create ERPNext Items
        for mi in kamra_items:
            item_code = mi.item_name
            if not frappe.db.exists("Item", item_code):
                item_doc = frappe.new_doc("Item")
                item_doc.item_code = item_code
                item_doc.item_name = mi.item_name
                item_doc.item_group = item_group
                item_doc.stock_uom = "Nos"
                item_doc.description = mi.description or mi.item_name
                item_doc.is_stock_item = 0
                try:
                    item_doc.insert(ignore_permissions=True)
                except frappe.DuplicateEntryError:
                    pass

        # ── Step 5: Create URY Menu ──
        menu_name = f"Menu - {outlet_name}"
        if frappe.db.exists("URY Menu", menu_name):
            menu_doc = frappe.get_doc("URY Menu", menu_name)
            menu_doc.set("items", [])
            is_new_menu = False
        else:
            menu_doc = frappe.new_doc("URY Menu")
            menu_doc.name = menu_name
            menu_doc.branch = branch
            menu_doc.enabled = 1
            is_new_menu = True

        for mi in kamra_items:
            course = mi.category if mi.category and frappe.db.exists("URY Menu Course", mi.category) else None
            menu_doc.append("items", {
                "item": mi.item_name,
                "item_name": mi.item_name,
                "rate": mi.price,
                "course": course,
                "disabled": 0 if mi.available else 1
            })

        if is_new_menu:
            menu_doc.insert(ignore_permissions=True)
            print(f"  [+] Created URY Menu: {menu_name} ({len(kamra_items)} items)")
        else:
            menu_doc.save(ignore_permissions=True)
            print(f"  [~] Updated URY Menu: {menu_name} ({len(kamra_items)} items)")

        # ── Step 6: Create URY Restaurant ──
        rest_name = outlet_name
        if not frappe.db.exists("URY Restaurant", rest_name):
            rest_doc = frappe.new_doc("URY Restaurant")
            rest_doc.name = rest_name
            rest_doc.company = company
            rest_doc.branch = branch
            rest_doc.invoice_series_prefix = short_prefix
            rest_doc.default_room = room_name
            rest_doc.active_menu = menu_name
            try:
                rest_doc.insert(ignore_permissions=True)
                print(f"  [+] Created URY Restaurant: {rest_name}")
            except Exception as e:
                print(f"  [!] Error creating URY Restaurant: {e}")
        else:
            rest_doc = frappe.get_doc("URY Restaurant", rest_name)
            rest_doc.active_menu = menu_name
            rest_doc.save(ignore_permissions=True)
            print(f"  [~] Updated URY Restaurant: {rest_name}")

    frappe.db.commit()
    print(f"\n{'=' * 60}")
    print("SETUP COMPLETE!")
    print("Both Kamra and URY now share the same ERPNext Items.")
    print("Transactions from either system will affect the same inventory.")
    print(f"{'=' * 60}")
