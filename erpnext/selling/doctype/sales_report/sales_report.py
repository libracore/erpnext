# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019, lasalesi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime

class SalesReport(Document):       
    def onload(self):
        return

    def setup(self):
        return
              
    def refresh(self):
        return
        
    """ This function is called in a script fashion to populate the report 
        It can be executed from the wrapper
            erpnext.selling.doctype.sales_report.sales_report.create_report
    """
    def fill(self, sales_person):
        # prepare global variables
        today = datetime.now()
        self.date = today.strftime("%Y-%m-%d")
        self.week = today.strftime("%W")
        self.title = "Sales Report " + str(self.date)
        if sales_person != "%":
            self.title += " " + sales_person
        _week = int(today.strftime("%W"))
        _this_year = int(today.strftime("%Y"))
        _last_year = _this_year - 1
        self.this_year = _this_year
        self.last_year = _last_year
        
        # define each line item
	line_items = [{'filter': "`item_name` LIKE 'Superior RS1-20KG-WEISS'", 'description': 'Superior weiss'},
            {'filter': "`item_name` LIKE 'Superior RS1-20KG-RAL9010'", 'description': 'Superior 9010'},
            {'filter': "`item_name` LIKE 'Superior RS1-20KG-RAL9016'", 'description': 'Superior 9016'},
            {'filter': "`item_name` LIKE 'Superior RS1-20KG-NCSS0500N'", 'description': 'Superior 0500'},
            {'filter': "`item_name` LIKE 'Super%L' OR `item_name` LIKE '%20KG' OR `item_name` LIKE 'Super%L-%'", 'description': 'Superior bunt'},
            {'filter': "`item_name` LIKE 'Segasil Premium%WEISS%'", 'description': 'Segasil Premium Weiss'},
            {'filter': "`item_name` LIKE 'Segasil Premium%9010%'", 'description': 'Segasil Premium 9010'},
            {'filter': "`item_name` LIKE 'Segasil Premium%9016%'", 'description': 'Segasil Premium 9016'},
            {'filter': "`item_name` LIKE 'Segasil Premium%0500%'", 'description': 'Segasil Premium 0500'},
            {'filter': "`item_name` LIKE 'Palmatex 7%'", 'description': 'Palmatex 7'},
            {'filter': "`item_name` LIKE 'Polar%'", 'description': 'Polar'},
            {'filter': "`item_name` LIKE 'Isofinish%' OR `item_name` LIKE '%Grund Plus%' OR `item_name` LIKE 'Mineralit Innen%' OR `item_name` LIKE 'Siloxan Primer%'", 'description': 'Spez. Wandfarben'},
            {'filter': "`item_name` LIKE 'Aqua-Floor%'", 'description': 'Bodenfarben'},
            {'filter': "`item_name` LIKE '%Tiefgrund'", 'description': 'Tiefgrund'},
            {'filter': "`item_name` LIKE '%Lasur%' OR `item_name` LIKE '%Bläueschutz%'", 'description': 'Lasuren'},
            {'filter': "`item_name` LIKE '%Fensterlack%' OR `item_name` LIKE '%Novasol Farbe%' OR `item_name` LIKE '%Holzgrundierung LH%' OR `item_name` LIKE 'All-Grund%' OR `item_name` LIKE 'Vorstreichfarbe%'  OR `item_name` LIKE 'Classicmatt 2000%'", 'description': 'Lacke LH'},
            {'filter': "`item_name` LIKE 'Lawicryl%' OR `item_name` LIKE 'Aqua All-Grund%' OR `item_name` LIKE 'Aquamatt%' OR `item_name` LIKE 'Samtacryl%' OR `item_name` LIKE '%Holz-Color%'", 'description': 'Lacke W'},
            {'filter': "`item_name` LIKE 'Siliconharzfarbe%'", 'description': 'Siliconharzfarbe F1'},
            {'filter': "`item_name` LIKE 'Premium FF%'", 'description': 'Premiumfassadenfarbe'},
            {'filter': "`item_name` LIKE 'Mineralit F%' OR `item_name` LIKE 'Mineralit G%'", 'description': 'Allg. Fassadenfarben'},
            {'filter': "`item_name` LIKE 'Anti%' OR `item_name` LIKE '%Universal-Nitroverdünnung' OR `item_name` LIKE '%Lackverdünnung%'", 'description': 'Zusatzprodukte'},
            {'filter': "`item_group` LIKE 'Dienstleistungen Abtönung'", 'description': 'Abtönpasten'},
            {'filter': "`item_name` LIKE 'Kunststoff Eimer%' OR `item_name` LIKE '%Washi-Tec%' OR `item_name` LIKE 'Abdeckvlies Strongline%'", 'description': 'Non-Farben'},
            {'filter': "`item_group` LIKE 'Dienstleistungen'", 'description': 'Dienstleistungen'}]

        for line_item in line_items:
            _description = line_item['description']
            _sql_7days = """SELECT (IFNULL(SUM(`kg`), 0)) AS `qty`,
                    (IFNULL(SUM(`net_amount`), 0)) AS `revenue`
                FROM `viewDelivery`
                WHERE ({filter})
                AND `docstatus` = 1
                AND `posting_date` > DATE_SUB(NOW(), INTERVAL 7 DAY)
                AND `sales_person` LIKE '{sales_person}'
                """.format(filter=line_item['filter'], sales_person=sales_person)
            _qty_7days,_revenue_7days = get_qty_revenue(_sql_7days)
            _sql_YTD = """SELECT (IFNULL(SUM(`kg`), 0)) AS `qty`,
                    (IFNULL(SUM(`net_amount`), 0)) AS `revenue`
                FROM `viewDelivery`
                WHERE ({filter})
                AND `docstatus` = 1
                AND `posting_date` >= '{year}-01-01'
                AND `sales_person` LIKE '{sales_person}'
                """.format(year=today.strftime("%Y"), filter=line_item['filter'], sales_person=sales_person)
            _qty_YTD,_revenue_YTD = get_qty_revenue(_sql_YTD)
            _sql_PY = """SELECT (IFNULL(SUM(`kg`), 0)) AS `qty`,
                    (IFNULL(SUM(`net_amount`), 0)) AS `revenue`
                FROM `viewDelivery`
                WHERE ({filter})
                AND `docstatus` = 1
                AND `posting_date` >= '{year}-01-01'
                AND `posting_date` <= '{year}-12-31'
                AND `sales_person` LIKE '{sales_person}'
                """.format(year=int(today.strftime("%Y")) - 1, filter=line_item['filter'], sales_person=sales_person)
            _qty_PY,_revenue_PY = get_qty_revenue(_sql_PY)

            self.append('items',
                {
                    'description': _description,
                    'qty_7days': _qty_7days,
                    'revenue_7days': _revenue_7days,
                    'qty_ytd': _qty_YTD,
                    'revenue_ytd': _revenue_YTD,
                    'qty_py': _qty_PY,
                    'revenue_py': _revenue_PY,
                    'demand_qty_ytd': (_qty_YTD/_week),
                    'demand_revenue_ytd': (_revenue_YTD/_week),
                    'demand_qty_py': (_qty_PY/52),
                    'demand_revenue_py': (_revenue_PY/52)
                })

        # compute totals
        self.update_totals()
        return

    def update_totals(self):
        _total_qty_7days = 0
        _total_qty_ytd = 0 
        _total_demand_qty_ytd = 0
        _total_demand_qty_py = 0
        _total_qty_py = 0
        _total_revenue_7days = 0
        _total_revenue_ytd = 0
        _total_demand_revenue_ytd = 0
        _total_demand_revenue_py = 0
        _total_revenue_py = 0
        try:
            if self.items:
                for item in self.items:
                    _total_qty_7days = _total_qty_7days + item.qty_7days
                    _total_qty_ytd = _total_qty_ytd + item.qty_ytd
                    _total_demand_qty_ytd = _total_demand_qty_ytd + item.demand_qty_ytd
                    _total_demand_qty_py = _total_demand_qty_py + item.demand_qty_py
                    _total_qty_py = _total_qty_py + item.qty_py
                    _total_revenue_7days = _total_revenue_7days + item.revenue_7days
                    _total_revenue_ytd = _total_revenue_ytd + item.revenue_ytd
                    _total_demand_revenue_ytd = _total_demand_revenue_ytd + item.demand_revenue_ytd
                    _total_demand_revenue_py = _total_demand_revenue_py + item.demand_revenue_py
                    _total_revenue_py = _total_revenue_py + item.revenue_py
        except:
            pass
        self.total_qty_7days = _total_qty_7days
        self.total_qty_ytd = _total_qty_ytd
        self.total_demand_qty_ytd = _total_demand_qty_ytd
        self.total_demand_qty_py = _total_demand_qty_py
        self.total_qty_py = _total_qty_py
        self.total_revenue_7days = _total_revenue_7days
        self.total_revenue_ytd = _total_revenue_ytd
        self.total_demand_revenue_ytd = _total_demand_revenue_ytd
        self.total_demand_revenue_py = _total_demand_revenue_py
        self.total_revenue_py = _total_revenue_py
        return

@frappe.whitelist()
def create_report(sales_person="%"):
    new_report = frappe.get_doc({"doctype": "Sales Report"})
    new_report.fill(sales_person)
    new_report_name = new_report.insert()
    return

""" Extracts `result` from SQL query """
def get_value(sql):
    values = frappe.db.sql(sql, as_dict=True)
    return values[0].result

""" Extracts `qty` and `revenue` from SQL query """
def get_qty_revenue(sql):
    values = frappe.db.sql(sql, as_dict=True)
    return values[0].qty, values[0].revenue
