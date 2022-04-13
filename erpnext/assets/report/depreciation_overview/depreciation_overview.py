# Copyright (c) 2022, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {'fieldname': 'date', 'label': _("Date"), 'fieldtype': 'Date', 'width': 80},
        {'fieldname': 'document', 'label': _("Document"), 'fieldtype': 'Link', 'options': 'Journal Entry', 'width': 100},
        {'fieldname': 'asset', 'label': _("Asset"), 'fieldtype': 'Link', 'options': 'Asset', 'width': 150},
        {'fieldname': 'amount', 'label': _("Amount"), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'expense_account', 'label': _("Expense Account"), 'fieldtype': 'Link', 'options': 'Account', 'width': 150},
        {'fieldname': 'depreciation_account', 'label': _("Depreciation Account"), 'fieldtype': 'Link', 'options': 'Account', 'width': 150},
        {'fieldname': 'cost_center', 'label': _("Cost Center"), 'fieldtype': 'Link', 'options': 'Cost Center', 'width': 150},
        {'fieldname': 'blank', 'label': _(""), 'fieldtype': 'Data', 'width': 20}
    ]
    
def get_data(filters):
    sql_query = """SELECT 
            `tabJournal Entry`.`posting_date` AS `date`,
            `tabJournal Entry`.`name` AS `document`, 
            `tDebit`.`reference_name` AS `asset`, 
            `tDebit`.`debit` AS `amount`, 
            `tDebit`.`account` AS `expense_account`, 
            `tCredit`.`account` AS `depreciation_account`, 
            `tDebit`.`cost_center` AS `cost_center`
        FROM `tabJournal Entry`
        LEFT JOIN `tabJournal Entry Account` AS `tDebit` ON 
            (`tDebit`.`parent` = `tabJournal Entry`.`name` AND `tDebit`.`debit` > 0)
        LEFT JOIN `tabJournal Entry Account` AS `tCredit` ON 
            (`tCredit`.`parent` = `tabJournal Entry`.`name` AND `tCredit`.`credit` > 0)
        WHERE
            `tabJournal Entry`.`posting_date` >= "{from_date}"
            AND `tabJournal Entry`.`posting_date` <= "{to_date}"
            AND `tabJournal Entry`.`docstatus` = 1
            AND `tabJournal Entry`.`company` = "{company}"
            AND `tabJournal Entry`.`voucher_type` = "Depreciation Entry"
            AND `tDebit`.`account` LIKE "{expense_account}"
            AND `tCredit`.`account` LIKE "{depreciation_account}"
        ORDER BY `tabJournal Entry`.`posting_date` ASC;""".format(
            from_date=filters.from_date, to_date=filters.to_date, company=filters.company,
            expense_account=filters.expense_account or "%", depreciation_account=filters.depreciation_account or "%")
    data = frappe.db.sql(sql_query, as_dict=True)
    return data
