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

# Initialise the permission scheme for Starter User and Manager
def initialise_permissions():
    
