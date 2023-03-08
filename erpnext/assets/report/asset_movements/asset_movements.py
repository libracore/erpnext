# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("In Date"), "fieldname": "in_date", "fieldtype": "Date", "width": 100},
        {"label": _("Out Date"), "fieldname": "out_date", "fieldtype": "Date", "width": 100},
        {"label": _("Asset"), "fieldname": "asset", "fieldtype": "Link", "options": "Asset", "width": 120},        
        {"label": _("Asset Name"), "fieldname": "asset_name", "fieldtype": "Data", "width": 150},
        {"label": _("Asset Category"), "fieldname": "asset_category", "fieldtype": "Link", "options": "Asset Category", "width": 150},
        {"label": _("Value"), "fieldname": "value", "fieldtype": "Currency", "width": 100},
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    # get additional conditions
    conditions = ""
    if 'asset_category' in filters and filters['asset_category']:
        conditions += """ AND `tabAsset`.`asset_category` = "{0}" """.format(filters['asset_category'])
    
    # prepare query
    sql_query = """SELECT 
            `tabAsset`.`name` AS `asset`, 
            `tabAsset`.`asset_name` AS `asset_name`, 
            `tabAsset`.`asset_category` AS `asset_category`, 
            `tabAsset`.`purchase_date` AS `in_date`, 
            `tabAsset`.`disposal_date` AS `out_date`, 
            `tabAsset`.`gross_purchase_amount` AS `value`,
            IFNULL(`tabAsset`.`disposal_date`, `tabAsset`.`purchase_date`) AS `date_key`
        FROM `tabAsset`
        WHERE 
            `tabAsset`.`docstatus` < 2
            AND (`tabAsset`.`purchase_date` >= "{from_date}"
             AND `tabAsset`.`purchase_date` <= "{to_date}")
            OR (`tabAsset`.`disposal_date` >= "{from_date}"
             AND `tabAsset`.`disposal_date` <= "{to_date}")
            {conditions}
        ORDER BY `date_key` ASC;
      """.format(conditions=conditions, from_date=filters['from_date'], to_date=filters['to_date'])
    
    data = frappe.db.sql(sql_query, as_dict=1)

    return data
