"""Indonesia localization pack: 21% combined PB1 (10%) and Service Charge (10% compound),
NPWP, IDR."""

from decimal import Decimal

import frappe


def _dec(v):
	return Decimal(str(v or 0))


def calculate_room_tax(property, room_type_doc, nightly_rate) -> Decimal:
	"""Indonesia uses a 21% combined tax and service charge (10% Service + 10% PB1 on top)."""
	return Decimal("21.0")


def fnb_tax_rate(property) -> float:
	return 21.0


def tax_rate_options(property) -> list:
	return [0, 11, 21]


def invoice_context(prop_doc) -> dict:
	return {
		"tax_label": "PB1 & Service",
		"tax_id_label": "NPWP",
		"service_code": None,
		"sac": None,
		"place_of_supply": prop_doc.get("state"),
		# 21% total: 10% service, 11% PB1 (10% of 110%)
		"split": [("service", Decimal("0.47619047619")), ("pb1", Decimal("0.52380952381"))],
		"footer": "Ini adalah invoice yang dihasilkan secara otomatis.",
	}


def locale(prop_doc) -> dict:
	return {
		"currency_symbol": "Rp",
		"locale": "id-ID",
		"currency": prop_doc.get("currency") or "IDR",
		"tax_label": "PB1 & Service",
		"tax_id_label": "NPWP",
		"tax_rates": tax_rate_options(prop_doc.name),
	}
