from frappe import qb
import frappe

def execute():
    """
    Clear `tabSingles` and Payment Reconciliation tables of values
    """
    frappe.reload_doc("accounts", "doctype", "payment_reconciliation_invoice", force=True)
    frappe.reload_doc("accounts", "doctype", "payment_reconciliation_payment", force=True)
    frappe.reload_doc("accounts", "doctype", "payment_reconciliation_allocation", force=True)
    
    singles = qb.DocType("Singles")
    qb.from_(singles).delete().where(singles.doctype == "Payment Reconciliation").run()
    doctypes = [
        "Payment Reconciliation Invoice",
        "Payment Reconciliation Payment",
        "Payment Reconciliation Allocation",
    ]
    
    for x in doctypes:
        dt = qb.DocType(x)
        try:
            qb.from_(dt).delete().run()
        except Exception as err:
            print("Failed to delete entries for {0}: {1}".format(x, err))
    
    return
