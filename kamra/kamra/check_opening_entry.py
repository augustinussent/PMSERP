import frappe

def diagnose_opening_entry():
    user = frappe.session.user
    print(f"Current User: {user}")
    
    entries = frappe.get_all("POS Opening Entry", 
        fields=["name", "user", "pos_profile", "status", "docstatus"], 
        order_by="creation desc")
        
    print("\n--- All POS Opening Entries ---")
    for e in entries:
        print(f"Name: {e.name}, User: {e.user}, Profile: {e.pos_profile}, Status: {e.status}, Docstatus: {e.docstatus}")
        
    # How URY checks:
    # ury_pos_profile = frappe.get_doc("POS Profile", pos_profile_name) 
    # check pos opening entry where user=user, status='Open', docstatus=1
    
    open_entries = [e for e in entries if e.docstatus == 1 and e.status == "Open"]
    if not open_entries:
        print("\n[!] NO Open POS Opening Entries found that are SUBMITTED (docstatus=1)!")
    else:
        print("\n[+] Found OPEN and SUBMITTED entries:")
        for e in open_entries:
            print(f"  - {e.name} (User: {e.user}, Profile: {e.pos_profile})")
            
        # Is the current user matching?
        if user not in [e.user for e in open_entries]:
            print(f"\n[!] WARNING: You are logged in as {user}, but the open entry belongs to someone else!")

if __name__ == "__main__":
    diagnose_opening_entry()
