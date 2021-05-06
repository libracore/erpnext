// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Asset Movements"] = {
    "filters": [
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            "reqd": 1
        },
                {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
                {
            "fieldname":"asset_category",
            "label": __("Asset Category"),
            "fieldtype": "Link",
            "options": "Asset Category"
        }
    ]
};
