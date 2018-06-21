// Copyright (c) 2018, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Report', {
    /* setup: function(frm) {
        if (frm.doc.name.startsWith("New")) {
            frappe.call({
                method: 'fill',
                doc: frm.doc,
                callback: function(response) {
                    refresh_field(['items', 'week', 'date', 'this_year', 'last_year']);
                }
            }); 
        }
    },*/
    refresh: function(frm) {
	// set defaults
	if (frm.doc.__islocal) {
	    frappe.call({
                method: 'fill',
                doc: frm.doc,
                callback: function(response) {
                    refresh_field(['items', 'week', 'date', 'this_year', 'last_year']);
                }
            });
	}
        // add utility buttons
        frm.add_custom_button(__("Update totals"), function() {
            frappe.call({
                method: 'update_totals',
                doc: frm.doc,
                callback: function(response) {
                    refresh_field(['total_qty_7days', 'total_qty_7days',
                    'total_qty_ytd', 'total_demand_qty_ytd',
                    'total_demand_qty_py', 'total_qty_py',
                    'total_revenue_7days', 'total_revenue_ytd',
                    'total_demand_revenue_ytd', 'total_demand_revenue_py',
                    'total_revenue_py']);
                }
            });
        });
    }

});
