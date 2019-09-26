frappe.ui.form.on("User", {
  refresh: function(frm) {
    frm.add_custom_button(__("Set Starter Desktop"), function() {
      set_starter_desktop(frm);
    });
  }
});

function set_starter_desktop(frm) {
	frappe.call({
	  method: 'erpnext.starter.utils.set_starter_desktop',
	  args: {
		'user': frm.doc.name
	  },
	  callback: function(response) {
		frappe.show_alert(__("Desktop set"));
	  }
	});
}