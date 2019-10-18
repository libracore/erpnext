# coding=utf-8

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		# Modules
		{
			"module_name": "Getting Started",
			"category": "Modules",
			"label": _("Getting Started"),
			"color": "#1abc9c",
			"icon": "icon start-blue",
			"type": "module",
			"disable_after_onboard": 1,
			"description": "Dive into the basics for your organisation's needs.",
			"onboard_present": 1
		},
		{
			"module_name": "Accounting",
			"category": "Modules",
			"label": _("Accounting"),
			"color": "#3498db",
			"icon": "icon accounting-blue",
			"type": "module",
			"description": "Accounts, billing, payments, cost center and budgeting."
		},
		{
			"module_name": "Selling",
			"category": "Modules",
			"label": _("Selling"),
			"color": "#1abc9c",
			"icon": "icon selling-blue",
			"type": "module",
			"description": "Sales orders, quotations, customers and items."
		},
		{
			"module_name": "Buying",
			"category": "Modules",
			"label": _("Buying"),
			"color": "#c0392b",
			"icon": "icon buying-blue",
			"type": "module",
			"description": "Purchasing, suppliers, material requests, and items."
		},
		{
			"module_name": "Stock",
			"category": "Modules",
			"label": _("Stock"),
			"color": "#f39c12",
			"icon": "icon stock-blue",
			"type": "module",
			"description": "Stock transactions, reports, serial numbers and batches."
		},
		{
			"module_name": "Assets",
			"category": "Modules",
			"label": _("Assets"),
			"color": "#4286f4",
			"icon": "icon assets-blue",
			"type": "module",
			"description": "Asset movement, maintainance and tools."
		},
		{
			"module_name": "Projects",
			"category": "Modules",
			"label": _("Projects"),
			"color": "#8e44ad",
			"icon": "icon projects-blue",
			"type": "module",
			"description": "Updates, Timesheets and Activities."
		},
		{
			"module_name": "CRM",
			"category": "Modules",
			"label": _("CRM"),
			"color": "#EF4DB6",
			"icon": "icon crm-blue",
			"type": "module",
			"description": "Sales pipeline, leads, opportunities and customers."
		},
		{
			"module_name": "Support",
			"category": "Modules",
			"label": _("Support"),
			"color": "#1abc9c",
			"icon": "icon support-blue",
			"type": "module",
			"description": "User interactions, support issues and knowledge base."
		},
		{
			"module_name": "HR",
			"category": "Modules",
			"label": _("Human Resources"),
			"color": "#2ecc71",
			"icon": "icon hr-blue",
			"type": "module",
			"description": "Employees, attendance, payroll, leaves and shifts."
		},
		{
			"module_name": "Quality Management",
			"category": "Modules",
			"label": _("Quality"),
			"color": "#1abc9c",
			"icon": "icon quality-blue",
			"type": "module",
			"description": "Quality goals, procedures, reviews and action."
		},


		# Category: "Domains"
		{
			"module_name": "Manufacturing",
			"category": "Domains",
			"label": _("Manufacturing"),
			"color": "#7f8c8d",
			"icon": "icon manufacture-blue",
			"type": "module",
			"description": "BOMS, work orders, operations, and timesheets."
		},
		{
			"module_name": "Retail",
			"category": "Domains",
			"label": _("Retail"),
			"color": "#7f8c8d",
			"icon": "icon retail-blue",
			"type": "module",
			"description": "Point of Sale and cashier closing."
		},
		{
			"module_name": "Education",
			"category": "Domains",
			"label": _("Education"),
			"color": "#428B46",
			"icon": "icon education-blue",
			"type": "module",
			"description": "Student admissions, fees, courses and scores."
		},

		{
			"module_name": "Healthcare",
			"category": "Domains",
			"label": _("Healthcare"),
			"color": "#FF888B",
			"icon": "icon healthcare-blue",
			"type": "module",
			"description": "Patient appointments, procedures and tests."
		},
		{
			"module_name": "Agriculture",
			"category": "Domains",
			"label": _("Agriculture"),
			"color": "#8BC34A",
			"icon": "icon agriculture-blue",
			"type": "module",
			"description": "Crop cycles, land areas, soil and plant analysis."
		},
		{
			"module_name": "Hotels",
			"category": "Domains",
			"label": _("Hotels"),
			"color": "#EA81E8",
			"icon": "icon hotel-blue",
			"type": "module",
			"description": "Hotel rooms, pricing, reservation and amenities."
		},

		{
			"module_name": "Non Profit",
			"category": "Domains",
			"label": _("Non Profit"),
			"color": "#DE2B37",
			"icon": "icon non-profit-blue",
			"type": "module",
			"description": "Volunteers, memberships, grants and chapters."
		},
		{
			"module_name": "Restaurant",
			"category": "Domains",
			"label": _("Restaurant"),
			"color": "#EA81E8",
			"icon": "icon restaurant-blue",
			"_doctype": "Restaurant",
			"type": "module",
			"link": "List/Restaurant",
			"description": "Menu, Orders and Table Reservations."
		},

		{
			"module_name": "Help",
			"category": "Administration",
			"label": _("Learn"),
			"color": "#FF888B",
			"icon": "icon learn-blue",
			"type": "module",
			"is_help": True,
			"description": "Explore Help Articles and Videos."
		},
		{
			"module_name": 'Marketplace',
			"category": "Places",
			"label": _('Marketplace'),
			"icon": "icon marketplace-blue",
			"type": 'link',
			"link": '#marketplace/home',
			"color": '#FF4136',
			'standard': 1,
			"description": "Publish items to other ERPNext users."
		},
	]
