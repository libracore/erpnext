// Copyright (c) 2016-2020, libracore AG and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Preisliste"] = {
    "filters": [
        {
            "fieldname":"customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 1
        },
        {
            "fieldname":"item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group"
        }
    ],
    "onload": (report) => {
        report.page.add_inner_button(__('Preisregel erstellen'), function () {
           add_pricing_rule();
        })
    }
}

function add_pricing_rule() {
    var d = new frappe.ui.Dialog({
      'title': __('Preisregel erstellen'),
      'fields': [
        {'fieldname': 'customer', 'fieldtype': 'Link', 'label': __('Customer'), 'options': 'Customer', 'reqd': 1, 'default': frappe.query_report.filters[0].value},
	{'fieldname': 'type', 'fieldtype': 'Select', 'label': __('Typ'), 'options': 'Allgemein\nArtikelgruppe\nArtikel', 'reqd': 1, 'default': 'Allgemein'},
        {'fieldname': 'item_group', 'fieldtype': 'Link', 'label': __('Item Group'), 'options': 'Item Group', 'depends_on': 'eval:doc.type=="Artikelgruppe"'},
        {'fieldname': 'item', 'fieldtype': 'Link', 'label': __('Item'), 'options': 'Item', 'depends_on': 'eval:doc.type=="Artikel"'},
        {'fieldname': 'discount_percent', 'fieldtype': 'Percent', 'label': __('Rabattprozent'), 'reqd': 1}
      ],
      'primary_action': function() {
          d.hide();
          var values = d.get_values();
          frappe.call({
              'method': "erpnext.selling.report.preisliste.preisliste.create_pricing_rule",
              'args':{
                  'customer': values.customer,
                  'discount_percentage': values.discount_percent,
                  'item_group': values.item_group,
                  'item_code': values.item
              },
              'callback': function(r)
              {
                  //frappe.set_route("Form", "Pricing Rule", r.message)
                  frappe.show_alert( __("Neue Preisregel erstellt: ") + "<a href=\"/desk#Form/Pricing Rule/" +  r.message + "\">" + r.message + "</a>");
                  frappe.query_report.refresh();
              }
          });
      },
      'primary_action_label': __('Erstellen')
    });
    d.show();
}

