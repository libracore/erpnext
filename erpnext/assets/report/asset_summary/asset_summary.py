# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import formatdate, getdate, flt, add_days

def execute(filters=None):
    filters.day_before_from_date = add_days(filters.from_date, -1)
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    return [
        {
            "label": _("Asset"),
            "fieldname": "asset",
            "fieldtype": "Link",
            "options": "Asset",
            "width": 120
        },
        {
            "label": _("Asset Name"),
            "fieldname": "asset_name",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Asset Category"),
            "fieldname": "asset_category",
            "fieldtype": "Link",
            "options": "Asset Category",
            "width": 120
        },
        {
            "label": _("Account"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 120
        },
        {
            "label": _("Purchase Date"),
            "fieldname": "purchase_date",
            "fieldtype": "Date",
            "width": 80
        },
        {
            "label": _("Disposal Date"),
            "fieldname": "disposal_date",
            "fieldtype": "Date",
            "width": 80
        },
        {
            "label": _("Purchase Amount"),
            "fieldname": "gross_purchase_amount",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Accumulated Depreciation"),
            "fieldname": "accumulated_depreciation_as_on_from_date",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Opening Value"),
            "fieldname": "net_asset_value_as_on_from_date",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Depreciation"),
            "fieldname": "depreciation_amount_during_the_period",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Closing Value"),
            "fieldname": "net_asset_value_as_on_to_date",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Duration (Years)"),
            "fieldname": "duration_years",
            "fieldtype": "Float",
            "precision": 2,
            "width": 100
        }
    ]

def get_data(filters):
    data = []
    
    assets = get_assets(filters)
    asset_costs = get_asset_costs(assets, filters)
    asset_depreciations = get_accumulated_depreciations(assets, filters)
    
    intermediate_sum = None
    
    for asset in assets:
        if not intermediate_sum or intermediate_sum['asset_category'] != asset.asset_category:
            if intermediate_sum and intermediate_sum['asset_category'] != asset.asset_category:
                # insert summation row
                row = {
                    'asset_name': _("Sum"),
                    'asset_category': intermediate_sum['asset_category'],
                    'gross_purchase_amount': intermediate_sum['gross_purchase_amount'], 
                    'accumulated_depreciation_as_on_from_date': intermediate_sum['accumulated_depreciation_as_on_from_date'],
                    'net_asset_value_as_on_from_date': intermediate_sum['net_asset_value_as_on_from_date'],
                    'depreciation_amount_during_the_period': intermediate_sum['depreciation_amount_during_the_period'],
                    'net_asset_value_as_on_to_date': intermediate_sum['net_asset_value_as_on_to_date']
                }
                if filters.show_sums:
                    data.append(row)
                
            # reset counter
            intermediate_sum = {'asset_category': asset.asset_category, 
                'gross_purchase_amount': 0, 
                'accumulated_depreciation_as_on_from_date': 0,
                'net_asset_value_as_on_from_date': 0,
                'depreciation_amount_during_the_period': 0,
                'net_asset_value_as_on_to_date': 0
            }
        
        # create new row for this asset (in case it has not been disposed off before this period)
        if not asset.disposal_date or getdate(asset.disposal_date) >= getdate(filters.from_date):
            row = {
                'asset': asset.name,
                'asset_name': asset.asset_name, 
                'asset_category': asset.asset_category,
                'account': asset.account,
                'purchase_date': asset.purchase_date,
                'gross_purchase_amount': asset.gross_purchase_amount,
                'duration_years': asset.duration_years,
                'disposal_date': asset.disposal_date
            }
            # insert costs from this asset
            row.update(asset_costs.get(asset.name))
            # compute end cost
            row['cost_as_on_to_date'] = (flt(row.get('cost_as_on_from_date')) + flt(row.get('cost_of_new_purchase'))
                - flt(row.get('cost_of_sold_asset')) - flt(row.get('cost_of_scrapped_asset')))
            # insert depreciation  
            row.update(asset_depreciations.get(asset.name))
            # compute accumulated depreciation
            row['accumulated_depreciation_as_on_to_date'] = (flt(row.get('accumulated_depreciation_as_on_from_date')) + 
                flt(row.get('depreciation_amount_during_the_period')) - flt(row.get('depreciation_eliminated')))
            
            row['net_asset_value_as_on_from_date'] = (flt(row.get('cost_as_on_from_date')) - 
                flt(row.get('accumulated_depreciation_as_on_from_date')))
            
            if asset.disposal_date:
                row['net_asset_value_as_on_to_date'] = 0       # disposed asset: 0-value when an asset has been disposed
            else:
                row['net_asset_value_as_on_to_date'] = (flt(row.get('cost_as_on_to_date')) - 
                    flt(row.get('accumulated_depreciation_as_on_to_date')))
            # adjust depreciation years
            if asset.country_code.lower() == "at" and asset.purchase_date.month > 6 and (row['duration_years'] or 0) > 1:
                row['duration_years'] = row['duration_years'] - 1
                        
            data.append(row)        
        
            # increase counter
            intermediate_sum['gross_purchase_amount'] += row['gross_purchase_amount']
            intermediate_sum['accumulated_depreciation_as_on_from_date'] += row['accumulated_depreciation_as_on_from_date']
            intermediate_sum['net_asset_value_as_on_from_date'] += row['net_asset_value_as_on_from_date']
            intermediate_sum['depreciation_amount_during_the_period'] += row['depreciation_amount_during_the_period']
            intermediate_sum['net_asset_value_as_on_to_date'] += row['net_asset_value_as_on_to_date']

    # insert last sum
    row = {
        'asset_name': _("Sum"),
        'asset_category': intermediate_sum['asset_category'],
        'gross_purchase_amount': intermediate_sum['gross_purchase_amount'], 
        'accumulated_depreciation_as_on_from_date': intermediate_sum['accumulated_depreciation_as_on_from_date'],
        'net_asset_value_as_on_from_date': intermediate_sum['net_asset_value_as_on_from_date'],
        'depreciation_amount_during_the_period': intermediate_sum['depreciation_amount_during_the_period'],
        'net_asset_value_as_on_to_date': intermediate_sum['net_asset_value_as_on_to_date']
    }
    if filters.show_sums:
        data.append(row)
    
    return data
        
def get_assets(filters):
    if not filters.asset_category:
        filters.asset_category = "%"
    return frappe.db.sql("""
        SELECT `tabAsset`.`name`, 
               `tabAsset`.`asset_name`,
               `tabAsset`.`asset_category`, 
               `tabAsset`.`purchase_date`, 
               `tabAsset`.`gross_purchase_amount`, 
               `tabAsset`.`disposal_date`, 
               `tabAsset`.`status`,
               (SELECT `tC`.`fixed_asset_account` FROM `tabAsset Category Account` AS `tC`
                WHERE `tC`.`parent` = `tabAsset Category`.`name` ORDER BY `tC`.`idx` ASC LIMIT 1) AS `account`,
               (SELECT (`tF`.`total_number_of_depreciations` * `tF`.`frequency_of_depreciation` / 12) FROM `tabAsset Finance Book` AS `tF`
                WHERE `tF`.`parent` = `tabAsset`.`name` ORDER BY `tF`.`idx` ASC LIMIT 1) AS `duration_years`,
               `tabCountry`.`code` AS `country_code` 
        FROM `tabAsset` 
        LEFT JOIN `tabAsset Category` ON `tabAsset`.`asset_category` = `tabAsset Category`.`name`
        LEFT JOIN `tabCompany` ON `tabCompany`.`name` = `tabAsset`.`company`
        LEFT JOIN `tabCountry` ON `tabCompany`.`country` = `tabCountry`.`name`
        WHERE `tabAsset`.`docstatus` = 1 
          AND `tabAsset`.`company`=%s 
          AND `tabAsset`.`purchase_date` <= %s
          AND `tabAsset`.`asset_category` LIKE %s
        ORDER BY `tabAsset`.`asset_category` ASC, `tabAsset`.`name` ASC;""", 
        (filters.company, filters.to_date, filters.asset_category), as_dict=1)

""" This function computes the cost per asset """
def get_asset_costs(assets, filters):
    asset_costs = {}
    for d in assets:
        costs = {
            'cost_as_on_from_date': 0,
            'cost_of_new_purchase': 0,
            'cost_of_sold_asset': 0,
            'cost_of_scrapped_asset': 0
        }
        
        if getdate(d.purchase_date) < getdate(filters.from_date):
            if not d.disposal_date or getdate(d.disposal_date) >= getdate(filters.from_date):
                costs['cost_as_on_from_date'] += flt(d.gross_purchase_amount)
        else:
            costs['cost_of_new_purchase'] += flt(d.gross_purchase_amount)
            
            if d.disposal_date and getdate(d.disposal_date) >= getdate(filters.from_date) \
                    and getdate(d.disposal_date) <= getdate(filters.to_date):
                if d.status == "Sold":
                    costs['cost_of_sold_asset'] += flt(d.gross_purchase_amount)
                elif d.status == "Scrapped":
                    costs['cost_of_scrapped_asset'] += flt(d.gross_purchase_amount)
        asset_costs[d.name] = costs
         
    return asset_costs
    
def get_accumulated_depreciations(assets, filters):
    asset_depreciations = {}
    for d in assets:
        asset = frappe.get_doc("Asset", d.name)
        
        depr = {
                'accumulated_depreciation_as_on_from_date': asset.opening_accumulated_depreciation,
                'depreciation_amount_during_the_period': 0,
                'depreciation_eliminated_during_the_period': 0
            }

        if not asset.schedules: # if no schedule,
            if asset.disposal_date:
                # and disposal is NOT within the period, then opening accumulated depreciation not included
                #if getdate(asset.disposal_date) < getdate(filters.from_date) or getdate(asset.disposal_date) > getdate(filters.to_date):
                #    depr['accumulated_depreciation_as_on_from_date'] = 0

                # if no schedule, and disposal is within period, accumulated dep is the amount eliminated
                if getdate(asset.disposal_date) >= getdate(filters.from_date) and getdate(asset.disposal_date) <= getdate(filters.to_date):
                    depr['depreciation_eliminated_during_the_period'] = asset.opening_accumulated_depreciation
        
        for schedule in asset.get("schedules"):
            if getdate(schedule.schedule_date) < getdate(filters.from_date):
                if not asset.disposal_date or getdate(asset.disposal_date) >= getdate(filters.from_date):
                    depr['accumulated_depreciation_as_on_from_date'] += flt(schedule.depreciation_amount)
            elif getdate(schedule.schedule_date) <= getdate(filters.to_date):
                if not asset.disposal_date:
                    depr['depreciation_amount_during_the_period'] += flt(schedule.depreciation_amount)
                else:
                    if getdate(schedule.schedule_date) <= getdate(asset.disposal_date):
                        depr['depreciation_amount_during_the_period'] += flt(schedule.depreciation_amount)

            if asset.disposal_date and getdate(asset.disposal_date) >= getdate(filters.from_date) and getdate(asset.disposal_date) <= getdate(filters.to_date):
                if getdate(schedule.schedule_date) <= getdate(asset.disposal_date):
                    depr['depreciation_eliminated_during_the_period'] += flt(schedule.depreciation_amount)
        
        asset_depreciations[d.name] = depr
        
    return asset_depreciations
    
