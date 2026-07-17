// Copyright (c) 2026, HeyKoala and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reservation", {
	amount_before_tax(frm) {
		frm.set_value("auto_price", 0);
	},
	tax_amount(frm) {
		frm.set_value("auto_price", 0);
	},
	amount_after_tax(frm) {
		frm.set_value("auto_price", 0);
	},
});
