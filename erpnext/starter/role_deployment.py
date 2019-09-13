# Copyright 2019 libracore and contributors
#
# Deployement file for role schemes

import frappe

def create_roles():
    check_create_role("libracore User")
    check_create_role("libracore Manager")
        
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
