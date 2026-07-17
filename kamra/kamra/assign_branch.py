import frappe

def assign_user_to_branch():
    print("Assigning Administrator to Branch...")
    user = "Administrator"
    
    # Check if Branch exists
    # If not, let's create or find one.
    branches = frappe.get_all("Branch", fields=["name"])
    if not branches:
        print("No Branch found. Creating Spencer Green Hotel branch.")
        branch = frappe.new_doc("Branch")
        branch.branch = "Spencer Green Hotel"
        branch.insert(ignore_permissions=True)
        branch_name = branch.name
    else:
        branch_name = branches[0].name
        
    print(f"Using Branch: {branch_name}")
    
    branch_doc = frappe.get_doc("Branch", branch_name)
    
    # Check if user already in URY User child table
    # Wait, the child table fieldname might not be 'ury_users'. Let's find it.
    # URY User table name is URY User.
    user_exists = False
    for row in branch_doc.get_all_children():
        if row.doctype == "URY User" and row.user == user:
            user_exists = True
            break
            
    if not user_exists:
        # Find the correct table fieldname for URY User in Branch
        meta = frappe.get_meta("Branch")
        field_name = None
        for df in meta.get_table_fields():
            if df.options == "URY User":
                field_name = df.fieldname
                break
                
        if field_name:
            # We also need a room. The query for getBranchRoom checks a.room
            # Let's get the first URY Room available for this branch
            rooms = frappe.get_all("URY Room", filters={"branch": branch_name}, fields=["name"])
            room = rooms[0].name if rooms else None
            
            branch_doc.append(field_name, {
                "user": user,
                "room": room
            })
            branch_doc.save(ignore_permissions=True)
            print(f"[+] Added {user} to Branch {branch_name} with room {room}")
        else:
            print("Could not find URY User table in Branch doctype")
    else:
        print(f"[=] {user} is already assigned to {branch_name}")
        
    frappe.db.commit()

