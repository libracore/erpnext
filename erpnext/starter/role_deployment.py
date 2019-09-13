# Copyright 2019 libracore and contributors
#
# Deployement file for role schemes

import frappe

def create_roles():
    check_create_role("Starter User")
    check_create_role("Starter Manager")
        
def check_create_role(role):
    # check if the role already exists
    r = frappe.get_all("Role", filters={'role_name': role}, fields=['role_name'])
    if not r: 
        # create role
        new_role = frappe.get_doc({
            "doctype": "Role",
            "role_name": role,
            "disabled": 0,
            "desk_access": 1,
            "two_factor_auth": 0
        })
        new_role.insert()
