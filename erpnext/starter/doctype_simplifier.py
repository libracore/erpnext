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
    # customer
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
    hide_fields("Customer", "steuerregion")
    hide_fields("Customer", "lead_name")
    hide_fields("Customer", "section_retailer")
    
    # item
    hide_fields("Item", "hub_publishing_sb")
    hide_fields("Item", "is_fixed_asset")
    hide_fields("Item", "deferred_revenue")
    hide_fields("Item", "deferred_expense_section")
    hide_fields("Item", "customer_details")
    hide_fields("Item", "inspection_criteria")

    # quotation
    hide_fields("Qutation", "taxes_section")
        
    # sales order
    hide_fields("Sales Order", "sec_warehouse")
    hide_fields("Sales Order", "loyality_points_redemption")
    hide_fields("Sales Order", "packing_list")
    hide_fields("Sales Order", "taxes_section")
    hide_fields("Sales Order", "sales_team_section_break")
    hide_fields("Sales Order", "subscription_section")
    hide_fields("Sales Order", "section_break1")
                            
    # delivery note
    
    # sales invoice
    
    # payment entry
    
    
    return
