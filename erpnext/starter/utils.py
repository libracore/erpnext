# Copyright 2019 libracore and contributors
#
# Utilities for starter

import frappe

@frappe.whitelist()
def set_starter_desktop(user):
    if frappe.db.exists("User", user):
        set = frappe.get_doc("User", user)
		set.home_settings = """{"modules_by_category": {"Modules": ["Starter"]}, "links_by_module": {"Starter": ["Customer"]}, hidden_modules": ["Website", "Social", "dashboard", "Marketplace", "Getting Started", "Accounting", "Selling", "Buying", "Stock", "Assets", "Projects", "CRM", "Support", "HR", "Quality Management", "ERPNextSwiss", "ERPNextAustria", "Finkzeit", "Desk", "Settings", "Users and Permissions", "Customization", "Integrations", "Help"], "links_by_module": {"Starter": ["Customer", "Quotation", "Sales Order", "Delivery Note", "Sales Invoice", "Item"]}}"""
        set.save()
	return