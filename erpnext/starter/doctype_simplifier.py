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
    hide_fields("Customer", "from_lead")
    hide_fields("Customer", "default_bank_account")
    hide_fields("Customer", "tax_category")
    hide_fields("Customer", "is_internal_customer")
    hide_fields("Customer", "column_break_38") # locality points section
    hide_fields("Customer", "sales_team_section_break")
    hide_fields("Customer", "sales_team_section")
    hide_fields("Customer", "account_manager")
    hide_fields("Customer", "is_frozen")
    
    return
