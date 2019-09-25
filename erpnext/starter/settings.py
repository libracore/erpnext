# Copyright 2019 libracore and contributors
#
# Deployement file for settings

import frappe
    
def initialise_settings():
    # item
    # stock settings
    # item_naming_by: "Naming Series"
    # item disable quick entry
    # item: name mandatory
    
    # erpnextswiss settings
    # intermediate bank account
    # default customer
    # default supplier
    
    # Naming series: 
    # item: 0.######
    # quotation: ANG-.#####
    # sales order: AB-.#####
    # delivery note: LS-.#####
    # sales invoice: RE-.#####
    # payment reminder: MNG-.#####
    # stock entry: LG-.#####
    
    # override country names EN > DE
    
    # address template: configure a proper template
    
    # quotation
    # apply_discount_on: default_ Net Total

    # sales order
    # apply_discount_on: default_ Net Total
    
    # sales invoice
    # apply_discount_on: default_ Net Total    
    return
