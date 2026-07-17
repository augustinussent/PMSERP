import frappe

def sync_menus():
    print("Starting synchronization from Kamra to URY ERP...")
    
    company = "Spencer Green Hotel"
    branch = "PUSAT"
    
    if not frappe.db.exists("Company", company):
        print(f"Error: Company '{company}' not found!")
        return
        
    if not frappe.db.exists("Branch", branch):
        print(f"Error: Branch '{branch}' not found!")
        return

    # Get default Item Group (or create one for F&B)
    item_group = "Products"
    if not frappe.db.exists("Item Group", "Food & Beverage"):
        if frappe.db.exists("Item Group", "All Item Groups"):
            ig = frappe.new_doc("Item Group")
            ig.item_group_name = "Food & Beverage"
            ig.parent_item_group = "All Item Groups"
            ig.insert(ignore_permissions=True)
            item_group = "Food & Beverage"
            print(f"Created Item Group: Food & Beverage")
    else:
        item_group = "Food & Beverage"

    # 1. Fetch all Kamra POS Outlets
    kamra_outlets = frappe.get_all("POS Outlet", fields=["name", "outlet_name"])
    
    # 2. Get all URY Restaurants
    try:
        ury_restaurants = frappe.get_all("URY Restaurant", fields=["name"])
        ury_rest_map = {r.name.lower(): r.name for r in ury_restaurants}
    except Exception as e:
        print(f"Error fetching URY Restaurants: {e}")
        ury_rest_map = {}
        
    for outlet in kamra_outlets:
        outlet_id = outlet.name
        outlet_name = outlet.outlet_name
        
        print(f"\nProcessing Menu for: {outlet_name}")
        
        # Fetch all Kamra Menu Items for this outlet
        kamra_items = frappe.get_all("Menu Item", 
                                     filters={"outlet": outlet_id},
                                     fields=["name", "item_name", "price", "category", "available", "description"])
        
        if not kamra_items:
            print(f"  No menu items found for {outlet_name}, skipping.")
            continue
        
        # Create or find URY Menu
        menu_name = f"Menu - {outlet_name}"
        if frappe.db.exists("URY Menu", menu_name):
            menu_doc = frappe.get_doc("URY Menu", menu_name)
            menu_doc.set("items", [])
            is_new = False
        else:
            menu_doc = frappe.new_doc("URY Menu")
            menu_doc.name = menu_name
            menu_doc.branch = branch
            menu_doc.enabled = 1
            is_new = True
        
        item_count = 0
        for mi in kamra_items:
            # --- Ensure ERPNext Item exists (shared inventory!) ---
            item_code = mi.item_name  # use item_name as the Item code
            if not frappe.db.exists("Item", item_code):
                item_doc = frappe.new_doc("Item")
                item_doc.item_code = item_code
                item_doc.item_name = mi.item_name
                item_doc.item_group = item_group
                item_doc.stock_uom = "Nos"
                item_doc.description = mi.description or mi.item_name
                item_doc.is_stock_item = 0  # service/consumable item for now
                item_doc.insert(ignore_permissions=True)
                
            # --- Ensure URY Menu Course exists ---
            course_name = mi.category
            if course_name and not frappe.db.exists("URY Menu Course", course_name):
                try:
                    cd = frappe.new_doc("URY Menu Course")
                    cd.name = course_name
                    cd.course_name = course_name
                    cd.insert(ignore_permissions=True)
                    print(f"  Created URY Menu Course: {course_name}")
                except Exception:
                    pass
            
            # --- Append to URY Menu ---
            menu_doc.append("items", {
                "item": item_code,
                "item_name": mi.item_name,
                "rate": mi.price,
                "course": course_name if course_name and frappe.db.exists("URY Menu Course", course_name) else None,
                "disabled": 0 if mi.available else 1
            })
            item_count += 1
            
        if is_new:
            menu_doc.insert(ignore_permissions=True)
            print(f"  Created URY Menu: {menu_doc.name}")
        else:
            menu_doc.save(ignore_permissions=True)
            print(f"  Updated existing URY Menu: {menu_doc.name}")
            
        print(f"  Synced {item_count} items to URY Menu '{menu_doc.name}'.")
        
        # 5. Link Menu to URY Restaurant
        match_key = outlet_name.lower()
        matched_ury_rest = None
        for key, val in ury_rest_map.items():
            if match_key in key or key in match_key:
                matched_ury_rest = val
                break
                
        if matched_ury_rest:
            rest_doc = frappe.get_doc("URY Restaurant", matched_ury_rest)
            rest_doc.active_menu = menu_doc.name
            rest_doc.save(ignore_permissions=True)
            print(f"  Linked menu to URY Restaurant: {matched_ury_rest}")
        else:
            print(f"  Warning: No matching URY Restaurant for '{outlet_name}'.")
            print(f"  Please manually set Active Menu = '{menu_doc.name}' in your URY Restaurant.")

    frappe.db.commit()
    print("\nSynchronization complete!")
    print("Both Kamra POS and URY now point to the same ERPNext Items for shared inventory.")
