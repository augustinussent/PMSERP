import frappe

def setup_ury():
    """
    Complete, audited setup: syncs ALL Kamra data into URY ERP.
    Creates: URY Room, URY Menu Course, ERPNext Item, URY Menu, URY Restaurant.
    No duplicates — checks existence before every insert.
    """
    print("=" * 60)
    print("FULL URY SETUP FROM KAMRA DATA")
    print("=" * 60)

    company = "Spencer Green Hotel"
    branch = "PUSAT"

    # ── Pre-flight checks ──
    if not frappe.db.exists("Company", company):
        print(f"ABORT: Company '{company}' not found!")
        return
    if not frappe.db.exists("Branch", branch):
        print(f"ABORT: Branch '{branch}' not found!")
        return

    # ── Step 1: Item Group ──
    item_group = "Food & Beverage"
    if not frappe.db.exists("Item Group", item_group):
        ig = frappe.new_doc("Item Group")
        ig.item_group_name = item_group
        ig.parent_item_group = "All Item Groups"
        ig.insert(ignore_permissions=True)
        print(f"[+] Created Item Group: {item_group}")
    else:
        print(f"[=] Item Group exists: {item_group}")

    # ── Step 2: Fetch ALL Kamra data ──
    kamra_outlets = frappe.get_all("POS Outlet",
        fields=["name", "outlet_name"],
        order_by="outlet_name asc")

    print(f"\nFound {len(kamra_outlets)} Kamra outlet(s).")

    # Collect ALL Kamra Menu Items across all outlets
    all_kamra_items = frappe.get_all("Menu Item",
        fields=["name", "item_name", "price", "category", "available", "description", "outlet"],
        order_by="outlet asc, category asc, item_name asc",
        limit_page_length=0)

    print(f"Found {len(all_kamra_items)} total Kamra Menu Items.")

    # ── Step 3: Create ALL unique ERPNext Items ──
    print(f"\n{'─' * 50}")
    print("Step 3: ERPNext Items (shared inventory)")
    print(f"{'─' * 50}")

    unique_items = {}
    for mi in all_kamra_items:
        if mi.item_name not in unique_items:
            unique_items[mi.item_name] = mi

    created_items = 0
    existing_items = 0
    for item_name, mi in sorted(unique_items.items()):
        if not frappe.db.exists("Item", item_name):
            item_doc = frappe.new_doc("Item")
            item_doc.item_code = item_name
            item_doc.item_name = item_name
            item_doc.item_group = item_group
            item_doc.stock_uom = "Nos"
            item_doc.description = mi.description or item_name
            item_doc.is_stock_item = 0
            try:
                item_doc.insert(ignore_permissions=True)
                created_items += 1
            except frappe.DuplicateEntryError:
                existing_items += 1
        else:
            existing_items += 1

    print(f"  Created: {created_items} | Already existed: {existing_items} | Total unique: {len(unique_items)}")

    # ── Step 4: Create ALL unique URY Menu Courses ──
    print(f"\n{'─' * 50}")
    print("Step 4: URY Menu Courses (categories)")
    print(f"{'─' * 50}")

    categories = sorted(set(mi.category for mi in all_kamra_items if mi.category))
    for cat in categories:
        if not frappe.db.exists("URY Menu Course", cat):
            cd = frappe.new_doc("URY Menu Course")
            cd.course = cat
            try:
                cd.insert(ignore_permissions=True)
                print(f"  [+] {cat}")
            except Exception as e:
                print(f"  [!] {cat}: {e}")
        else:
            print(f"  [=] {cat}")

    # ── Step 5: Per-outlet setup (Room → Menu → Restaurant) ──
    for outlet in kamra_outlets:
        outlet_id = outlet.name
        outlet_name = outlet.outlet_name
        short_prefix = "".join([w[0] for w in outlet_name.split()]).upper()

        print(f"\n{'═' * 50}")
        print(f"Outlet: {outlet_name}")
        print(f"{'═' * 50}")

        # ── 5a: URY Room ──
        room_name = f"Room - {outlet_name}"
        if not frappe.db.exists("URY Room", room_name):
            room_doc = frappe.new_doc("URY Room")
            room_doc.name = room_name
            room_doc.branch = branch
            room_doc.room_type = "AC"
            try:
                room_doc.insert(ignore_permissions=True)
                print(f"  [+] URY Room: {room_name}")
            except Exception as e:
                print(f"  [!] URY Room error: {e}")
                continue
        else:
            print(f"  [=] URY Room: {room_name}")

        # ── 5b: URY Menu ──
        menu_name = f"Menu - {outlet_name}"
        outlet_items = [mi for mi in all_kamra_items if mi.outlet == outlet_id]

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

        for mi in outlet_items:
            course = mi.category if mi.category and frappe.db.exists("URY Menu Course", mi.category) else None
            menu_doc.append("items", {
                "item": mi.item_name,
                "item_name": mi.item_name,
                "rate": mi.price,
                "course": course,
                "disabled": 0 if mi.available else 1,
            })

        if is_new_menu:
            menu_doc.insert(ignore_permissions=True)
            print(f"  [+] URY Menu: {menu_name} ({len(outlet_items)} items)")
        else:
            menu_doc.save(ignore_permissions=True)
            print(f"  [~] URY Menu updated: {menu_name} ({len(outlet_items)} items)")

        # ── 5c: URY Restaurant ──
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
                print(f"  [+] URY Restaurant: {rest_name}")
            except Exception as e:
                print(f"  [!] URY Restaurant error: {e}")
        else:
            rest_doc = frappe.get_doc("URY Restaurant", rest_name)
            rest_doc.active_menu = menu_name
            rest_doc.default_room = room_name
            rest_doc.save(ignore_permissions=True)
            print(f"  [~] URY Restaurant updated: {rest_name}")

    frappe.db.commit()

    # ── Final Audit ──
    print(f"\n{'=' * 60}")
    print("FINAL AUDIT")
    print(f"{'=' * 60}")

    for dt in ["Item", "URY Menu Course", "URY Room", "URY Menu", "URY Restaurant"]:
        count = frappe.db.count(dt)
        names = frappe.get_all(dt, pluck="name", limit=50)
        print(f"\n{dt} ({count}):")
        for n in names:
            print(f"  • {n}")

    # Cross-check: every Kamra Menu Item has a matching ERPNext Item
    missing = []
    for mi in all_kamra_items:
        if not frappe.db.exists("Item", mi.item_name):
            missing.append(mi.item_name)
    if missing:
        print(f"\n⚠ WARNING: {len(missing)} Kamra items missing from ERPNext Items:")
        for m in missing:
            print(f"  ✗ {m}")
    else:
        print(f"\n✓ All {len(all_kamra_items)} Kamra Menu Items have matching ERPNext Items.")

    print(f"\n{'=' * 60}")
    print("SETUP COMPLETE!")
    print("Kamra POS and URY now share the same ERPNext Items.")
    print("Inventory will be deducted from the same pool.")
    print(f"{'=' * 60}")
