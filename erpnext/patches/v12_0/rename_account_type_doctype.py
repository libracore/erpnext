import frappe


def execute():
	try:
		frappe.rename_doc("DocType", "Account Type", "Bank Account Type", force=True)
		frappe.rename_doc("DocType", "Account Subtype", "Bank Account Subtype", force=True)
		frappe.reload_doc("accounts", "doctype", "bank_account")
	except Exception as err:
		print("Renaming account type failed: {0}".format(err))

