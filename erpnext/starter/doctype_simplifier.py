# Copyright 2019 libracore and contributors
#
# Simplification model for DocTypes
# 
# Extension through patches to maintain local changes

import frappe

def hide_fields(doctype, fieldname, hidden=1):
    field_matches = frappe.get_all("DocField", filters={'parent': doctype, 'fieldname': fieldname}, fields=['name'])
    if field_matches:
        field = frappe.get_doc("DocField", field_matches[0]['name'])
        field.hidden = hidden
        field.save()
    return
    
def initialise_simple_doctypes():
    hide_fields("Customer", "pan")
    return
