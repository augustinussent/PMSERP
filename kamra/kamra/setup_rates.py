import frappe

def setup_rates_and_meals():
    property_name = "Spencer Green Hotel"
    abbr = frappe.db.get_value("Company", property_name, "abbr") or "SGH"
    
    print("=" * 50)
    print("SETUP MEAL PLAN & RATE PLANS")
    print("=" * 50)

    # 1. Pastikan akun Breakfast Revenue ada
    expense_root = frappe.db.get_value("Account",
        {"company": property_name, "root_type": "Income", "is_group": 1}, "name")
    
    breakfast_acc = frappe.db.get_value("Account", {"account_number": "4110.006"}) or f"4110.006 - Pendapatan Banquet & Meeting - {abbr}"
    
    # We will set Kamra ERPNext Settings to use this for F&B Revenue
    settings = frappe.get_doc("ERPNext Settings")
    settings.fnb_revenue_account = breakfast_acc
    settings.room_revenue_account = frappe.db.get_value("Account", {"account_number": "4110.001"}) or f"4110.001 - Pendapatan Kamar - {abbr}"
    settings.save(ignore_permissions=True)
    print(f"[+] Updated ERPNext Settings to map F&B to: {settings.fnb_revenue_account}")

    # 2. Buat Meal Plan untuk Breakfast (CP)
    if not frappe.db.exists("Meal Plan", f"{property_name}-CP"):
        mp = frappe.new_doc("Meal Plan")
        mp.property = property_name
        mp.code = "CP"
        mp.label = "Breakfast"
        mp.price_per_adult = 85000
        mp.price_per_child = 42500 # asumsikan half price
        mp.is_default = 1
        mp.insert(ignore_permissions=True)
        print(f"[+] Created Meal Plan: Breakfast (Rp 85.000/pax)")
    else:
        mp = frappe.get_doc("Meal Plan", f"{property_name}-CP")
        mp.price_per_adult = 85000
        mp.save(ignore_permissions=True)
        print(f"[~] Updated Meal Plan: Breakfast (Rp 85.000/pax)")

    # 3. Buat Rate Plan per Room Type (Absolute Pricing)
    # The user asked for "Room Only" and "Room Breakfast" FOR EACH room type.
    # We will create Absolute rate plans so they can be explicitly selected.
    room_types = frappe.get_all("Room Type", filters={"property": property_name}, fields=["name", "room_type_name", "room_type_code", "base_price"])
    
    for rt in room_types:
        # RO (Room Only)
        ro_code = f"RO-{rt.room_type_code}"
        ro_name = f"Room Only - {rt.room_type_name}"
        if not frappe.db.exists("Rate Plan", f"{property_name}-{ro_code}"):
            rp = frappe.new_doc("Rate Plan")
            rp.property = property_name
            rp.rate_plan_name = ro_name
            rp.code = ro_code
            rp.modifier_type = "Absolute"
            rp.modifier_value = rt.base_price
            rp.insert(ignore_permissions=True)
            print(f"  [+] {ro_name} (Rp {rt.base_price})")
        else:
            print(f"  [=] {ro_name} exists")

        # RB (Room Breakfast)
        rb_code = f"RB-{rt.room_type_code}"
        rb_name = f"Room Breakfast - {rt.room_type_name}"
        
        # Calculate RB price
        # Breakfast is 85.000 per person.
        # Superior (SUP) gets 3 persons, others get 2 persons.
        if "SUP" in rt.room_type_code:
            breakfast_total = 85000 * 3
        else:
            breakfast_total = 85000 * 2
            
        rb_price = rt.base_price + breakfast_total

        if not frappe.db.exists("Rate Plan", f"{property_name}-{rb_code}"):
            rp = frappe.new_doc("Rate Plan")
            rp.property = property_name
            rp.rate_plan_name = rb_name
            rp.code = rb_code
            rp.modifier_type = "Absolute"
            rp.modifier_value = rb_price
            rp.insert(ignore_permissions=True)
            print(f"  [+] {rb_name} (Rp {rb_price} = Base {rt.base_price} + BF {breakfast_total})")
        else:
            rp = frappe.get_doc("Rate Plan", f"{property_name}-{rb_code}")
            rp.modifier_value = rb_price
            rp.save(ignore_permissions=True)
            print(f"  [~] {rb_name} updated to Rp {rb_price}")

    frappe.db.commit()
    print("=" * 50)
    print("DONE")

