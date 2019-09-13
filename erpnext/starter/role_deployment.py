# Copyright 2019 libracore and contributors
#
# Deployement file for role schemes

import frappe

def create_roles():
    check_create_role("Starter User")
    check_create_role("Starter Manager")
        
def check_create_role(role):
    if not frappe.db.exists("Role", dict(role_name=role)): 
        # create role
        frappe.db.sql("""INSERT INTO `tabRole` 
            (`name`, `role_name`, `disabled`, `desk_access`, `two_factor_auth`)
            VALUES ('{role}', '{role}', 0, 1, 0);""")
    return
