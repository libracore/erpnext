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
    return
    
# Initialise the permission scheme for Starter User and Manager
def initialise_permissions():
    check_create_permission("Starter User", "Customer", perm_read=1, perm_write=1, perm_create=1)
    
    return
