import frappe

def fix_item_prices():
    print("Checking and fixing ERPNext Item Prices...")
    
    # Ambil semua item dari Kamra menu items
    menu_items = frappe.get_all("Kamra Menu Item", fields=["item_code", "base_price"])
    
    price_list = "Standard Selling"
    
    # Ensure Standard Selling exists
    if not frappe.db.exists("Price List", price_list):
        pl = frappe.new_doc("Price List")
        pl.price_list_name = price_list
        pl.selling = 1
        pl.insert(ignore_permissions=True)
    
    fixed_count = 0
    for mi in menu_items:
        item_code = mi.item_code
        rate = mi.base_price or 0
        
        if rate == 0:
            continue
            
        # Periksa apakah sudah ada Item Price
        exists = frappe.db.exists("Item Price", {"item_code": item_code, "price_list": price_list})
        
        if not exists:
            ip = frappe.new_doc("Item Price")
            ip.item_code = item_code
            ip.price_list = price_list
            ip.price_list_rate = rate
            ip.insert(ignore_permissions=True)
            fixed_count += 1
            print(f"[+] Set price Rp {rate} for {item_code}")
        else:
            # Update jika perlu
            ip = frappe.get_doc("Item Price", exists)
            if ip.price_list_rate != rate:
                ip.price_list_rate = rate
                ip.save(ignore_permissions=True)
                fixed_count += 1
                print(f"[~] Updated price to Rp {rate} for {item_code}")
                
    frappe.db.commit()
    print(f"DONE! Fixed {fixed_count} item prices.")

if __name__ == "__main__":
    fix_item_prices()
