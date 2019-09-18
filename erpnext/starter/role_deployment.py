# Copyright 2019 libracore and contributors
#
# Deployement file for role schemes

import frappe

# Assure that the Starter roles are in the system
def create_roles():
    check_create_role("Starter User")
    check_create_role("Starter Manager")
        
def check_create_role(role):
    if not frappe.db.exists("Role", dict(role_name=role)): 
        # create role
        frappe.get_doc({
            "doctype": "Role",
            "role_name": role,
            "disabled": 0,
            "desk_access": 1,
            "two_factor_auth": 0
        }).insert(ignore_permissions=True)
    return

def check_create_permission(role, doctype, permlevel=0, perm_read=1, perm_write=0, 
    perm_create=0, perm_submit=0, perm_cancel=0, perm_delete=0, perm_amend=0, 
    perm_report=0, perm_export=0, perm_import=0, perm_share=0, perm_print=0, 
    perm_email=0):
    perm_match = frappe.get_all("DocPerm", 
        filters={'role': role, 'permlevel': permlevel, 'parent': doctype},
        fields=['name'])
    if not perm_match:
        # create role
        frappe.get_doc({
            "doctype": "DocPerm",
            "parent": doctype,
            "parentfield": "permissions",
            "parenttype": "DocType",
            "permlevel": permlevel,
            "role": role,
            "read": perm_read,
            "write": perm_write, 
            "create": perm_create, 
            "submit": perm_submit, 
            "cancel": perm_cancel, 
            "delete": perm_delete, 
            "amend": perm_amend, 
            "report": perm_report, 
            "export": perm_export, 
            "import": perm_import, 
            "share": perm_share, 
            "print": perm_print, 
            "email": perm_email
        }).insert(ignore_permissions=True)
    else:
        # update permission
        perm = frappe.get_doc("DocPerm", perm_match[0]['name'])
        perm.read = perm_read
        perm.write = perm_write
        perm.create = perm_create
        perm.submit = perm_submit
        perm.cancel = perm_cancel
        perm.delete = perm_delete
        perm.amend = perm_amend
        perm.report = perm_report
        perm.export = perm_export
        #perm.import = perm_import # reserved keyword, cannot be used
        perm.share = perm_share
        #perm.print = perm_print # reserved keyword, cannot be used
        perm.email = perm_email
        perm.save()
    return

def check_create_permission_page(page, roles):
    perm_match = frappe.get_all("Custom Role", 
        filters={'page': page},
        fields=['name'])
    if not perm_match:
        # create role
        system_roles = []
        for r in roles:
            system_roles.append({'role': r})
        frappe.get_doc({
            "doctype": "Custom Role",
            "page": page,
            "roles": system_roles
        }).insert(ignore_permissions=True)
    else:
        perm = frappe.get_doc("Custom Role", perm_match[0]['name'])
        perm.roles = []
        for r in roles:
            n = perm.append('roles', {'role': r})
        perm.save()
    return

def check_create_permission_report(report, roles):
    perm_match = frappe.get_all("Custom Role", 
        filters={'report': report},
        fields=['name'])
    if not perm_match:
        # create role
        system_roles = []
        for r in roles:
            system_roles.append({'role': r})
        frappe.get_doc({
            "doctype": "Custom Role",
            "report": report,
            "roles": system_roles
        }).insert(ignore_permissions=True)
    else:
        perm = frappe.get_doc("Custom Role", perm_match[0]['name'])
        perm.roles = []
        for r in roles:
            n = perm.append('roles', {'role': r})
        perm.save()
    return

# Initialise the permission scheme for Starter User and Manager
def initialise_permissions():
    # general doctypes
    check_create_permission("Starter User", "ToDo", perm_read=1, perm_write=1, perm_create=1, perm_report=1)
    check_create_permission("Starter User", "Note", perm_read=1, perm_write=1, perm_create=1, perm_report=1)
    # base crm    
    check_create_permission("Starter User", "Customer", perm_read=1, perm_write=1, perm_create=1, perm_report=1)
    # sales and orders
    check_create_permission("Starter Manager", "Item", perm_read=1, perm_write=1, perm_create=1, perm_report=1)
    check_create_permission("Starter Manager", "Item Group", perm_read=1, perm_write=1, perm_create=1, perm_report=1)
    check_create_permission("Starter Manager", "Territory", perm_read=1, perm_write=1, perm_create=1, perm_report=1)
    check_create_permission("Starter Manager", "Customer Group", perm_read=1, perm_write=1, perm_create=1, perm_report=1)
    check_create_permission("Starter User", "Country", perm_read=1)
    check_create_permission("Starter User", "Account", perm_read=1)
    check_create_permission("Starter User", "Currency", perm_read=1)
    check_create_permission("Starter User", "Item Price", perm_read=1)
    check_create_permission("Starter User", "Price List", perm_read=1)
    check_create_permission("Starter User", "Item", perm_read=1)
    check_create_permission("Starter Manager", "Quotation", perm_read=1, perm_write=1, perm_create=1, perm_submit=1, perm_cancel=1, perm_amend=1, perm_report=1)
    check_create_permission("Starter Manager", "Sales Order", perm_read=1, perm_write=1, perm_create=1, perm_submit=1, perm_cancel=1, perm_amend=1, perm_report=1)
    check_create_permission("Starter Manager", "Delivery Note", perm_read=1, perm_write=1, perm_create=1, perm_submit=1, perm_cancel=1, perm_amend=1, perm_report=1)
    check_create_permission("Starter Manager", "Sales Invoice", perm_read=1, perm_write=1, perm_create=1, perm_submit=1, perm_cancel=1, perm_amend=1, perm_report=1)
    check_create_permission("Starter Manager", "Payment Entry", perm_read=1, perm_write=1, perm_create=1, perm_submit=1, perm_cancel=1, perm_amend=1, perm_report=1)
    check_create_permission("Starter Manager", "Item Price", perm_read=1, perm_write=1, perm_create=1)
    check_create_permission("Starter Manager", "Account", perm_read=1, perm_write=1, perm_create=1)
    check_create_permission("Starter Manager", "Payment Reminder", perm_read=1, perm_write=1, perm_create=1, perm_submit=1, perm_cancel=1, perm_amend=1, perm_report=1)
    
    # pages and reports
    check_create_permission_report("Accounts Receivable", ['Accounts Manager', 'Accounts User', 'Starter Manager', 'System Manager'])
    check_create_permission_report("Accounts Receivable Summary", ['Accounts Manager', 'Accounts User', 'Starter Manager', 'System Manager'])
    check_create_permission_page("bank_wizard", ['Accounts Manager', 'Accounts User', 'Starter Manager', 'System Manager'])
    
    return
