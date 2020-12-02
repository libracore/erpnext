# Copyright (c) 2013-2020, libracore AG and contributors
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
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
        {"label": _("Item"), "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 120},
        {"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 75},
        {"label": _("Price list rate"), "fieldname": "price_list_rate", "fieldtype": "Currency", "width": 100},
        {"label": _("Pricing Rule"), "fieldname": "pricing_rule", "fieldtype": "Link", "options": "Pricing Rule", "width": 120},
        {"label": _("Discount"), "fieldname": "discount_percentage", "fieldtype": "Percent", "width": 100},
        {"label": _("Rate"), "fieldname": "discounted_rate", "fieldtype": "Currency", "width": 100},
        {"label": _("DB1"), "fieldname": "db1", "fieldtype": "Currency", "width": 100}
    ]

def get_data(filters):
    if not filters.item_group:
        filters.item_group = "%"
    sql_query = """SELECT 
  `raw`.`item_code`,
  `raw`.`item_name`,
  `raw`.`item_group`,
  `raw`.`stock_uom`,
  `raw`.`price_list_rate`,
  `raw`.`pricing_rule`,
  `tPR`.`discount_percentage` AS `discount_percentage`,
  ((100 - `tPR`.`discount_percentage`)/100) * `raw`.`price_list_rate` AS `discounted_rate`,
  ((((100 - `tPR`.`discount_percentage`)/100) * `raw`.`price_list_rate`) - `raw`.`last_purchase_rate`) AS `db1`
FROM (
SELECT 
  `tabItem`.`item_code` AS `item_code`,
  `tabItem`.`item_name` AS `item_name`,
  `tabItem`.`item_group` AS `item_group`,
  `tabItem`.`last_purchase_rate` AS `last_purchase_rate`,
  CONCAT(ROUND(`tabItem`.`weight_per_unit`, 1), " ", `tabItem`.`weight_uom`) AS `stock_uom`,
  (SELECT `tabItem Price`.`price_list_rate` 
   FROM `tabItem Price` 
   WHERE `tabItem Price`.`item_code` = `tabItem`.`item_code`
     AND `tabItem Price`.`price_list` = "Standard-Vertrieb") AS `price_list_rate`,
  (SELECT `tabPricing Rule`.`name`
   FROM `tabPricing Rule`
   WHERE `tabPricing Rule`.`selling` = 1
     AND `tabPricing Rule`.`customer` = "{customer}"
     AND `tabPricing Rule`.`disable` = 0
     AND (`tabPricing Rule`.`item_code` = `tabItem`.`item_code`
          OR `tabPricing Rule`.`item_group` = `tabItem`.`item_group`
          OR `tabPricing Rule`.`item_group` = "Alle Artikelgruppen")
   ORDER BY `tabPricing Rule`.`priority` DESC
   LIMIT 1) AS `pricing_rule`
FROM `tabItem`
WHERE `tabItem`.`is_sales_item` = 1
  AND `tabItem`.`item_group` LIKE "{item_group}") AS `raw`
LEFT JOIN `tabPricing Rule` AS `tPR` ON `tPR`.`name` = `raw`.`pricing_rule`;""".format(customer=filters.customer, item_group=filters.item_group)
    data = frappe.db.sql(sql_query, as_list=True)
    return data

@frappe.whitelist()
def create_pricing_rule(customer, discount_percentage, item_group=None, item_code=None):
    # check if a similar set exists already
    target_prio = "1"
    if item_group:
        target_prio = "2"
        matches = frappe.get_all("Pricing Rule", filters={'customer': customer, 'priority': target_prio, 'item_group': item_group}, fields=['name'])
    elif item_code:
        target_prio = "3"
        matches = frappe.get_all("Pricing Rule", filters={'customer': customer, 'priority': target_prio, 'item_code': item_code}, fields=['name'])
    else:
        matches = frappe.get_all("Pricing Rule", filters={'customer': customer, 'priority': target_prio}, fields=['name'])
    if matches and len(matches) > 0:
        # update discount of existing rule
        pricing_rule = frappe.get_doc("Pricing Rule", matches[0]['name'])
        pricing_rule.discount_percentage = discount_percentage
        pr = pricing_rule.save()
    else:
        # create new pricing rule
        pricing_rule = frappe.get_doc({
            'doctype': "Pricing Rule",
            'selling': 1,
            'applicable_for': 'Customer',
            'customer': customer,
            'price_or_discount': 'Discount Percentage',
            'discount_percentage': discount_percentage,
            'priority': target_prio
         })
        if item_group:
            pricing_rule.title = "{c} {g} ({d})".format(c=customer, g=item_group, d=discount_percentage)
            pricing_rule.apply_on = "Item Group"
            pricing_rule.item_group = item_group
        elif item_code:
            pricing_rule.title = "{c} {i} ({d})".format(c=customer, i=item_code, d=discount_percentage)
            pricing_rule.apply_on = "Item Code"
            pricing_rule.item_code = item_code
        else:
            pricing_rule.title = "{c} Basis ({d})".format(c=customer, d=discount_percentage)
            pricing_rule.apply_on = "Item Group"
            pricing_rule.item_group = "Alle Artikelgruppen"
        pr = pricing_rule.insert()
    
    return pr.name
