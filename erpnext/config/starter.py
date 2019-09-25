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
            "label": _("Items"),
            "icon": "octicon octicon-package",
            "items": [
                {
                    "type": "doctype",
                    "name": "Item",
                    "onboard": 1
                },
                {
                    "type": "doctype",
                    "name": "Item Price",
                    "onboard": 1,
                    "dependencies": ["Item", "Price List"]
                },
                {
                    "type": "doctype",
                    "name": "Stock Entry",
                    "onboard": 1,
                    "dependencies": ["Item"]
                }
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
                    "name": "Payment Entry",
                    "onboard": 1,
                    "dependencies": ["Item"]
                },
                {
                    "type": "doctype",
                    "name": "Payment Reminder",
                    "onboard": 1,
                    "dependencies": ["Item", "Sales Invoice"]
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
        },
        {
            "label": _("Tools"),
            "icon": "octicon octicon-tools",
            "items": [
                {
                    "type": "doctype",
                    "name": "Note",
                    "onboard": 1
                },
                {
                    "type": "doctype",
                    "name": "ToDo",
                    "onboard": 1
                }
            ]
        },
        {
            "label": _("Definitions"),
            "icon": "octicon octicon-briefcase",
            "items": [
                {
                    "type": "doctype",
                    "name": "Item Group",
                    "onboard": 1
                },
                {
                    "type": "doctype",
                    "name": "Territory",
                    "onboard": 1
                },
                {
                    "type": "doctype",
                    "name": "Customer Group",
                    "onboard": 1
                }
            ]
        }
    ]
