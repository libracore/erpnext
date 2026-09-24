// Copyright (c) 2022, libracore AG and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Depreciation Overview"] = {
    "filters": [
        {
            "fieldname":"company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": new Date((new Date().getFullYear() - 1), 0, 1),
            "reqd": 1
        },
        {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": new Date((new Date().getFullYear() - 1), 11, 31),
            "reqd": 1
        },
        {
            "fieldname":"expense_account",
            "label": __("Expense Account"),
            "fieldtype": "Link",
            "options": "Account",
            "get_query": function() {
                return {
                    filters: {
                        "account_type": "Expense Account"
                    }
                }
            }
        },
        {
            "fieldname":"depreciation_account",
            "label": __("Depreciation Account"),
            "fieldtype": "Link",
            "options": "Account",
            "get_query": function() {
                return {
                    filters: {
                        "account_type": "Accumulated Depreciation"
                    }
                }
            }
        }
    ]
};
