# Copyright (c) 2026, HeyKoala and contributors
# For license information, please see license.txt

# pyrefly: ignore [missing-import]
import frappe
from frappe import _

def is_sync_enabled():
	if not frappe.db.exists("DocType", "ERPNext Settings"):
		return False
	return frappe.db.get_single_value("ERPNext Settings", "enable_sync")

def get_settings():
	return frappe.get_doc("ERPNext Settings")

def erpnext_installed():
	return "erpnext" in frappe.get_installed_apps()

def sync_guest(doc, method):
	if not is_sync_enabled() or not erpnext_installed():
		return
	
	customer_name = doc.full_name or doc.name
	if frappe.db.exists("Customer", customer_name):
		customer = frappe.get_doc("Customer", customer_name)
	else:
		customer = frappe.new_doc("Customer")
		customer.customer_name = customer_name
		customer.customer_type = "Individual"
		customer.customer_group = "Commercial"
		customer.territory = "All Territories"
	
	customer.mobile_no = doc.phone
	customer.email_id = doc.email
	customer.save(ignore_permissions=True)

def sync_folio(doc, method):
	if not is_sync_enabled() or not erpnext_installed():
		return
	
	settings = get_settings()
	if not settings.default_company:
		return

	# Only sync closed or settled folios? The hook is on_submit, meaning the folio is settled
	si = frappe.new_doc("Sales Invoice")
	
	customer_id = None
	if doc.guest:
		customer_id = frappe.db.get_value("Guest", doc.guest, "full_name") or doc.guest
	elif doc.company:
		customer_id = doc.company
	
	if not customer_id:
		return
		
	# Ensure customer exists before linking
	if not frappe.db.exists("Customer", customer_id):
		if doc.guest:
			sync_guest(frappe.get_doc("Guest", doc.guest), None)
		else:
			return # Company not created yet? Wait, Kamra company should also sync to ERPNext customer, but let's assume it exists or falls back

	si.customer = customer_id
	si.company = settings.default_company
	si.update_stock = 0 # No stock impact for PMS services
	
	has_items = False
	for charge in doc.charges:
		income_account = settings.room_revenue_account
		if charge.type == "F&B":
			income_account = settings.fnb_revenue_account
		elif charge.type == "Laundry":
			income_account = settings.laundry_revenue_account
		elif charge.type == "Event" or charge.type == "Group":
			income_account = settings.event_revenue_account
		
		# Skip taxes in item line, map them to sales taxes and charges?
		# Wait, Kamra puts tax in the Folio Charge table too? No, in POS order tax is separate, in Folio... let's treat everything as items for now, or just map as best effort
		if charge.type == "Tax":
			if "PB1" in charge.description:
				si.append("taxes", {
					"charge_type": "Actual",
					"account_head": settings.pb1_tax_account,
					"tax_amount": charge.amount,
					"description": charge.description
				})
			elif "Service" in charge.description:
				si.append("taxes", {
					"charge_type": "Actual",
					"account_head": settings.service_charge_account,
					"tax_amount": charge.amount,
					"description": charge.description
				})
			continue
			
		if not income_account:
			continue
			
		si.append("items", {
			"item_name": charge.description or charge.type,
			"description": charge.description or charge.type,
			"qty": charge.qty or 1,
			"rate": (charge.amount / (charge.qty or 1)) if charge.qty else charge.amount,
			"income_account": income_account
		})
		has_items = True
		
	if has_items:
		si.set_missing_values()
		si.save(ignore_permissions=True)
		si.submit()

def sync_pos_order(doc, method):
	if not is_sync_enabled() or not erpnext_installed():
		return
	
	# Only sync if it's settled directly (not routed to Folio)
	# If room is set, it goes to Folio, and sync_folio handles it
	if getattr(doc, "room", None) or getattr(doc, "reservation", None):
		return
		
	settings = get_settings()
	if not settings.default_company or not settings.fnb_revenue_account:
		return
		
	si = frappe.new_doc("Sales Invoice")
	si.is_pos = 1
	si.company = settings.default_company
	
	# Determine customer
	customer_id = doc.customer_name or "Walk-in"
	if not frappe.db.exists("Customer", customer_id):
		c = frappe.new_doc("Customer")
		c.customer_name = customer_id
		c.customer_type = "Individual"
		c.customer_group = "Commercial"
		c.territory = "All Territories"
		c.save(ignore_permissions=True)
		
	si.customer = customer_id
	
	for item in doc.items:
		si.append("items", {
			"item_code": item.menu_item,
			"item_name": item.item_name,
			"qty": item.qty,
			"rate": item.rate,
			"income_account": settings.fnb_revenue_account
		})
	
	# Add tax lines based on pos order tax
	if doc.tax_amount > 0:
		# Use localization split logic if possible, or just apply it
		# For PB1 and Service
		si.append("taxes", {
			"charge_type": "Actual",
			"account_head": settings.pb1_tax_account,
			"tax_amount": doc.tax_amount * 0.5, # Assuming 50/50 if split is not easily readable here
			"description": "PB1"
		})
		si.append("taxes", {
			"charge_type": "Actual",
			"account_head": settings.service_charge_account,
			"tax_amount": doc.tax_amount * 0.5,
			"description": "Service Charge"
		})

	si.set_missing_values()
	si.save(ignore_permissions=True)
	si.submit()

def sync_payment(doc, method):
	if not is_sync_enabled() or not erpnext_installed():
		return
		
	settings = get_settings()
	if not settings.default_company or not settings.cash_bank_account:
		return
		
	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Receive"
	pe.company = settings.default_company
	
	customer_id = None
	# If this is linked to a folio
	if doc.folio:
		folio = frappe.get_doc("Folio", doc.folio)
		if folio.guest:
			customer_id = frappe.db.get_value("Guest", folio.guest, "full_name") or folio.guest
			
	if not customer_id:
		return
		
	pe.party_type = "Customer"
	pe.party = customer_id
	pe.paid_to = settings.cash_bank_account
	pe.paid_amount = doc.amount
	pe.received_amount = doc.amount
	
	pe.set_missing_values()
	pe.save(ignore_permissions=True)
	pe.submit()

def intercept_ury_invoice(doc, method):
	if not is_sync_enabled() or not erpnext_installed():
		return

	# Only intercept POS Invoices
	if not getattr(doc, "is_pos", 0):
		return

	# Check if paid using "Charge to Room" or "Folio"
	charge_to_room = False
	for payment in getattr(doc, "payments", []):
		if payment.mode_of_payment in ("Charge to Room", "Folio") and payment.amount > 0:
			charge_to_room = True
			break

	if not charge_to_room:
		return

	# Find active Kamra Folio for this customer
	customer_name = doc.customer
	# Find Guest where name or full_name matches customer_name
	guest_id = frappe.db.get_value("Guest", {"full_name": customer_name}, "name")
	if not guest_id:
		guest_id = frappe.db.get_value("Guest", {"name": customer_name}, "name")
	
	if not guest_id:
		frappe.throw(f"Tamu {customer_name} tidak ditemukan di sistem Kamra.")

	# Find active folio
	folio_id = frappe.db.get_value("Folio", {"guest": guest_id, "status": "Open"}, "name")
	if not folio_id:
		frappe.throw(f"Tidak ada Folio/kamar yang aktif untuk tamu {customer_name}.")

	folio = frappe.get_doc("Folio", folio_id)
	
	# Add charge to folio
	folio.append("charges", {
		"type": "F&B",
		"description": f"Ury POS: {doc.name}",
		"qty": 1,
		"amount": doc.grand_total,
		"reference_doctype": "Sales Invoice",
		"reference_name": doc.name
	})
	
	folio.save(ignore_permissions=True)
	
	# The Ury Sales Invoice remains in ERPNext, but we should mark it as paid by this mode.
	# Kamra Folio settling will handle clearing the Folio clearing account later.
