# Copyright 2019 libracore and contributors
#
# Deployement file for print formats

import frappe

def check_create_letter_head():
    if frappe.db.exists("Letter Head", "Commercial"):
        letter_head = frappe.get_doc("Letter Head", "Commercial")
    else:
        letter_head = frappe.get_doc({
            "doctype": "Letter Head",
            "letter_head_name": "Commercial"
        }).insert(ignore_permissions=True)
    letter_head.content = """
    <p style="text-align: right;">
      <img src="https://data.libracore.ch/starter/libracore_wordmark.png" style="width: 100px !important;">
    </p>
    """
    letter_head.footer = """
    <center>Ihre Firma<br>Adresszeile | PLZ Ort | Telefon | Email | IBAN</center>
    """
    letter_head.save()
    return
    
def initialise_letter_head():
    check_create_letter_head()
    return
