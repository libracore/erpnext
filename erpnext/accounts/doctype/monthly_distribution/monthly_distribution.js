// Copyright (c) 2015-2025, libracore and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on('Monthly Distribution', {
    onload(frm) {
        if(frm.doc.__islocal) {
            return frm.call('get_months').then(() => {
                frm.refresh_field('percentages');
            });
        }
    },

    refresh(frm) {
        frm.toggle_display('distribution_id', frm.doc.__islocal);
    }
});

frappe.ui.form.on('Monthly Distribution Percentage', {
    percentage_allocation(frm, cdt, cdn) {
        update_total(frm);
    }
});

function update_total(frm) {
    let total = 0;
    if (frm.doc.percentages) {
        for (let i = 0; i < frm.doc.percentages.length; i++) {
            total += frm.doc.percentages[i].percentage_allocation;
        }
    }
    cur_frm.set_value("total", total);
}
