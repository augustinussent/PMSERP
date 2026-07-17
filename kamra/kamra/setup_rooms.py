import frappe

def setup_rooms():
    property_name = "Spencer Green Hotel"
    
    # Define Room Types
    room_types = [
        {"name": "DELUXE", "code": "DLX", "base_price": 500000},
        {"name": "SUPERIOR", "code": "SUP", "base_price": 750000},
        {"name": "DELUXE BALCONY", "code": "DLXB", "base_price": 600000},
        {"name": "EXECUTIVE", "code": "EXE", "base_price": 1000000}
    ]

    # Create Room Types
    print("Setting up Room Types...")
    for rt in room_types:
        rt_id = f"{property_name}-{rt['code']}"
        if not frappe.db.exists("Room Type", rt_id):
            doc = frappe.new_doc("Room Type")
            doc.property = property_name
            doc.room_type_name = rt["name"]
            doc.room_type_code = rt["code"]
            doc.base_price = rt["base_price"]
            doc.insert(ignore_permissions=True)
            print(f"Created Room Type: {rt['name']}")
        else:
            print(f"Room Type {rt['name']} already exists.")

    # Define Rooms
    rooms = {
        "DELUXE": ["101", "102", "103", "104", "105", "106", "107", "108", "109"],
        "SUPERIOR": ["110", "111", "112", "114", "115", "117", "118", "119", "120", "121", "122", "123", "124", "125", "218", "219", "220", "221", "001", "002", "003", "004", "312", "314", "315", "316"],
        "DELUXE BALCONY": ["201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", "212", "214", "215", "217", "222", "223", "224", "225"],
        "EXECUTIVE": ["301", "302", "303", "304", "305", "306", "307", "308", "309", "310", "311"]
    }

    # Map room types to their actual Frappe ID (autoname format: {property}-{code})
    room_type_ids = {
        "DELUXE": f"{property_name}-DLX",
        "SUPERIOR": f"{property_name}-SUP",
        "DELUXE BALCONY": f"{property_name}-DLXB",
        "EXECUTIVE": f"{property_name}-EXE"
    }

    # Create Rooms
    print("\nSetting up Rooms...")
    frappe.db.commit()
    for room_type_name, room_numbers in rooms.items():
        rt_id = room_type_ids[room_type_name]
        for number in room_numbers:
            # Check if room already exists
            if not frappe.db.exists("Room", {"property": property_name, "room_number": number}):
                doc = frappe.new_doc("Room")
                doc.property = property_name
                doc.room_number = number
                doc.room_type = rt_id
                
                # Assign floor based on the first digit of room number (except for "001" etc)
                if len(number) >= 3 and number.isdigit():
                    if number.startswith("0"):
                        doc.floor = "Ground Floor"
                    else:
                        doc.floor = f"Floor {number[0]}"
                
                doc.insert(ignore_permissions=True)
                print(f"Created Room: {number} ({room_type})")
    
    frappe.db.commit()
    print("\nAll rooms have been set up successfully!")
