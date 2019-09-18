# Copyright 2019 libracore and contributors
#
# Entry point for update processes

import frappe
from erpnext.starter.role_deployment import create_roles, initialise_permissions
from erpnext.starter.doctype_simplifier import initialise_simple_doctypes
from erpnext.starter.print_format import initialise_letter_head

def after_migrate():
    print("Starter updates...")
    create_roles()
    return

def initialise():
    print("Initialising roles...")
    initialise_permissions()
    print("Simplifying doctypes...")
    initialise_simple_doctypes()
    print("Creating letter head template...")
    initialise_letter_head
    print("Done")
    return
