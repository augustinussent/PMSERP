import frappe

def setup_venues():
    property_name = "Spencer Green Hotel"
    venues = ["LAVENDER", "GARBERRA"]
    
    print("Setting up Venues...")
    for venue_name in venues:
        # Venue autoname is usually format:{property}-{venue_name}
        # But we'll just check if it exists using frappe.db.exists on Venue
        # Since we don't know the exact autoname, we can just search by property and venue_name
        if not frappe.db.exists("Venue", {"property": property_name, "venue_name": venue_name}):
            doc = frappe.new_doc("Venue")
            doc.property = property_name
            doc.venue_name = venue_name
            doc.insert(ignore_permissions=True)
            print(f"Created Venue: {venue_name}")
        else:
            print(f"Venue already exists: {venue_name}")
    
    frappe.db.commit()
    print("\nAll venues have been set up successfully!")
