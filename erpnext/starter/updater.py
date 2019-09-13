# Copyright 2019 libracore and contributors
#
# Entry point for update processes

import frappe
from role_deployement import create_roles

def before_migrate():
    create_roles()
    return
