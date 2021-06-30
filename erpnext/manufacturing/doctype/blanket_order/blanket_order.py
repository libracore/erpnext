# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.doctype.item.item import get_item_defaults


class BlanketOrder(Document):
    def update_ordered_qty(self):
        if self.blanket_order_type == "Selling":
            for d in self.items:
                item_query = frappe.db.sql("""SELECT
                                                    SUM(`map`.`fulfilled_qty`) AS `fulfilled_qty`
                                                FROM
                                                 (SELECT
                                                      (CASE WHEN `so`.`status` NOT IN ('Closed', 'Stopped') AND SUM(`soi`.`stock_qty`) > SUM(`soi`.`delivered_qty`)
                                                        THEN SUM(`soi`.`stock_qty`)
                                                        ELSE SUM(`soi`.`delivered_qty`)
                                                      END) AS `fulfilled_qty`,
                                                      `bo`.`name` AS `blanket_order`
                                                    FROM
                                                      `tabSales Order` AS `so`
                                                      INNER JOIN `tabSales Order Item` AS `soi` ON `soi`.`parent` = `so`.`name`
                                                      LEFT JOIN (
                                                        `tabBlanket Order Item` AS `boi` INNER JOIN `tabBlanket Order` AS `bo` ON `bo`.`name` = `boi`.`parent`
                                                      ) ON `boi`.`item_code` = `soi`.`item_code` AND `bo`.`name` = `soi`.`blanket_order` AND `bo`.`docstatus` = 1
                                                    WHERE
                                                      `soi`.`item_code` = '{item_code}' AND
                                                      `so`.`docstatus` = 1
                                                      AND `bo`.`name` = '{blanket_order}'
                                                    GROUP BY
                                                      `so`.`name`
                                                    ORDER BY
                                                      `so`.`transaction_date`) AS `map`""".format(item_code=d.item_code, blanket_order=self.name), as_dict=True)
                if item_query[0].fulfilled_qty:
                    d.db_set("ordered_qty", item_query[0].fulfilled_qty)
                else:
                    d.db_set("ordered_qty", 0)
      
        else:
            ref_doctype = "Purchase Order"
            item_ordered_qty = frappe._dict(frappe.db.sql("""
                select trans_item.item_code, sum(trans_item.stock_qty) as qty
                from `tab{0} Item` trans_item, `tab{0}` trans
                where trans.name = trans_item.parent
                    and trans_item.blanket_order=%s
                    and trans.docstatus=1
                    and trans.status not in ('Closed', 'Stopped')
                group by trans_item.item_code
            """.format(ref_doctype), self.name))
            for d in self.items:
                d.db_set("ordered_qty", item_ordered_qty.get(d.item_code, 0))

@frappe.whitelist()
def make_sales_order(source_name):
    def update_item(source, target, source_parent):
        target_qty = source.get("qty") - source.get("ordered_qty")
        target.qty = target_qty if not flt(target_qty) < 0 else 0
        item = get_item_defaults(target.item_code, source_parent.company)
        if item:
            target.item_name = item.get("item_name")
            target.description = item.get("description")
            target.uom = item.get("stock_uom")

    target_doc = get_mapped_doc("Blanket Order", source_name, {
        "Blanket Order": {
            "doctype": "Sales Order"
        },
        "Blanket Order Item": {
            "doctype": "Sales Order Item",
            "field_map": {
                "rate": "blanket_order_rate",
                "parent": "blanket_order"
            },
            "postprocess": update_item
        }
    })
    return target_doc

@frappe.whitelist()
def make_purchase_order(source_name):
    def update_item(source, target, source_parent):
        target_qty = source.get("qty") - source.get("ordered_qty")
        target.qty = target_qty if not flt(target_qty) < 0 else 0
        item = get_item_defaults(target.item_code, source_parent.company)
        if item:
            target.item_name = item.get("item_name")
            target.description = item.get("description")
            target.uom = item.get("stock_uom")
            target.warehouse = item.get("default_warehouse")

    target_doc = get_mapped_doc("Blanket Order", source_name, {
        "Blanket Order": {
            "doctype": "Purchase Order"
        },
        "Blanket Order Item": {
            "doctype": "Purchase Order Item",
            "field_map": {
                "rate": "blanket_order_rate",
                "parent": "blanket_order"
            },
            "postprocess": update_item
        }
    })
    return target_doc
