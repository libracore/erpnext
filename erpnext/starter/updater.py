# Copyright 2019 libracore and contributors
#
# Entry point for update processes

import frappe
from erpnext.starter.role_deployment import create_roles

def after_migrate():
    print("Starter updates...")
    create_roles()
    return
