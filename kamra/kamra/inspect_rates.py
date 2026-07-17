import frappe
def inspect_rates():
    print("--- Room Types ---")
    for rt in frappe.get_all("Room Type", fields=["name", "type_name", "base_price"]):
        print(f"  {rt.name}: base={rt.base_price}")
        
    print("\n--- Rate Plans ---")
    for rp in frappe.get_all("Rate Plan", fields=["name", "rate_plan_name", "modifier_type", "modifier_value"]):
        print(f"  {rp.name} - {rp.rate_plan_name} ({rp.modifier_type}: {rp.modifier_value})")
        
    print("\n--- Meal Plans ---")
    for mp in frappe.get_all("Meal Plan", fields=["name", "code", "label", "price_per_adult"]):
        print(f"  {mp.name} - {mp.code} - {mp.label} (Adult: {mp.price_per_adult})")
        
    print("\n--- Company Billing Rules ---")
    try:
        for cbr in frappe.get_all("Company Billing Rule", fields=["name", "charge_type", "income_account"]):
            print(f"  {cbr.name} - {cbr.charge_type} -> {cbr.income_account}")
    except Exception as e:
        print("  Error:", e)
