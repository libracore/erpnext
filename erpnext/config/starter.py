# Copyright 2019 libracore and contributors

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("CRM"),
			"icon": "octicon octicon-person",
			"items": [
				{
					"type": "doctype",
					"name": "Customer",
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Quotation",
					"onboard": 1,
					"dependencies": ["Item"]
				},
			]
		},
		{
			"label": _("Orders"),
			"icon": "octicon octicon-book",
			"items": [
				{
					"type": "doctype",
					"name": "Sales Order",
					"onboard": 1,
					"dependencies": ["Item"]
				},
				{
					"type": "doctype",
					"name": "Delivery Note",
					"onboard": 1,
					"dependencies": ["Item"]
				},
				{
					"type": "doctype",
					"name": "Item",
					"onboard": 1
				}
			]
		},
		{
			"label": _("Finance"),
			"icon": "fa fa-law",
			"items": [
				{
					"type": "doctype",
					"name": "Sales Invoice",
					"onboard": 1,
					"dependencies": ["Item"]
				},
                {
                   "type": "page",
                   "name": "bank_wizard",
                   "label": _("Bank Wizard"),
                   "description": _("Bank Wizard")
                },
				{
					"type": "doctype",
					"name": "Account",
					"icon": "fa fa-sitemap",
					"label": _("Chart of Accounts"),
					"route": "#Tree/Account",
					"description": _("Tree of financial accounts."),
					"onboard": 1,
				},
				{
					"type": "report",
					"name": "General Ledger",
					"doctype": "GL Entry",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Profit and Loss Statement",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Balance Sheet",
					"doctype": "GL Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Accounts Receivable",
					"doctype": "Sales Invoice",
					"is_query_report": True
				}
			]
		}
	]
