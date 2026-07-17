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
        
        # 3. Create or Update URY Menu for this Outlet
        menu_name = f"Menu - {outlet_name}"
        if not frappe.db.exists("URY Menu", menu_name):
            menu_doc = frappe.new_doc("URY Menu")
            # URY Menu uses naming series or we can set it? Usually it's autoname.
            # We'll just create it and see its name
            menu_doc.name = menu_name
            menu_doc.branch = branch
            menu_doc.enabled = 1
            menu_doc.insert(ignore_permissions=True)
            actual_menu_name = menu_doc.name
            print(f"  Created URY Menu: {actual_menu_name}")
        else:
            menu_doc = frappe.get_doc("URY Menu", menu_name)
            actual_menu_name = menu_doc.name
            print(f"  Using existing URY Menu: {actual_menu_name}")
            
        # Clear existing items to avoid duplicates
        menu_doc.set("items", [])
        
        # 4. Fetch all Kamra Menu Items for this outlet
        kamra_items = frappe.get_all("Menu Item", 
                                     filters={"outlet": outlet_id},
                                     fields=["name", "item", "item_name", "price", "category", "available"])
        
        for item in kamra_items:
            # Ensure URY Menu Course exists
            course_name = item.category
            if course_name and not frappe.db.exists("URY Menu Course", course_name):
                course_doc = frappe.new_doc("URY Menu Course")
                # URY Menu Course probably has just a name or title
                try:
                    course_doc.name = course_name
                    course_doc.course_name = course_name
                    course_doc.insert(ignore_permissions=True)
                except:
                    # If it fails, maybe it uses a different field. We'll skip creating course safely
                    pass
            
            # Append to URY Menu
            menu_doc.append("items", {
                "item": item.item,  # This links to the core ERPNext Item (shared inventory!)
                "item_name": item.item_name,
                "rate": item.price,
                "course": course_name if frappe.db.exists("URY Menu Course", course_name) else None,
                "disabled": 0 if item.available else 1
            })
            
        menu_doc.save(ignore_permissions=True)
        print(f"  Synced {len(kamra_items)} items to URY Menu '{actual_menu_name}'.")
        
        # 5. Link Menu to URY Restaurant
        # Try to find matching URY Restaurant
        match_key = outlet_name.lower()
        matched_ury_rest = None
        for key, val in ury_rest_map.items():
            if match_key in key or key in match_key:
                matched_ury_rest = val
                break
                
        if matched_ury_rest:
            rest_doc = frappe.get_doc("URY Restaurant", matched_ury_rest)
            rest_doc.active_menu = actual_menu_name
            rest_doc.save(ignore_permissions=True)
            print(f"  Linked menu to URY Restaurant: {matched_ury_rest}")
        else:
            print(f"  Warning: Could not find a matching URY Restaurant for '{outlet_name}'.")
            print("  You may need to manually select this Active Menu in your URY Restaurant settings.")

    print("\nSynchronization complete!")
