# -*- coding: utf-8 -*-
# Copyright (c) 2018-2023, libracore, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document
from frappe.model.meta import get_field_precision
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.doctype.journal_entry.journal_entry import get_balance_on

class ExchangeRateRevaluation(Document):
    def validate(self):
        self.set_total_gain_loss()

    def set_total_gain_loss(self):
        total_gain_loss = 0
        for d in self.accounts:
            d.gain_loss = flt(d.new_balance_in_base_currency, d.precision("new_balance_in_base_currency")) \
                - flt(d.balance_in_base_currency, d.precision("balance_in_base_currency"))
            total_gain_loss += flt(d.gain_loss, d.precision("gain_loss"))
        self.total_gain_loss = flt(total_gain_loss, self.precision("total_gain_loss"))

    def validate_mandatory(self):
        if not (self.company and self.posting_date):
            frappe.throw(_("Please select Company and Posting Date to getting entries"))

    def get_accounts_data(self, account=None):
        accounts = []
        self.validate_mandatory()
        company_currency = erpnext.get_company_currency(self.company)
        precision = get_field_precision(frappe.get_meta("Exchange Rate Revaluation Account")
            .get_field("new_balance_in_base_currency"), company_currency)

        account_details = self.get_accounts_from_gle()
        for d in account_details:
            current_exchange_rate = d.balance / d.balance_in_account_currency \
                if d.balance_in_account_currency else 0
            new_exchange_rate = get_exchange_rate(d.account_currency, company_currency, self.posting_date)
            new_balance_in_base_currency = flt(d.balance_in_account_currency * new_exchange_rate)
            gain_loss = flt(new_balance_in_base_currency, precision) - flt(d.balance, precision)
            if gain_loss:
                accounts.append({
                    "account": d.account,
                    "party_type": d.party_type,
                    "party": d.party,
                    "account_currency": d.account_currency,
                    "balance_in_base_currency": d.balance,
                    "balance_in_account_currency": d.balance_in_account_currency,
                    "current_exchange_rate": current_exchange_rate,
                    "new_exchange_rate": new_exchange_rate,
                    "new_balance_in_base_currency": new_balance_in_base_currency
                })

        if not accounts:
            self.throw_invalid_response_message(account_details)

        return accounts

    def get_accounts_from_gle(self):
        company_currency = erpnext.get_company_currency(self.company)
        accounts = frappe.db.sql_list("""
            SELECT `name`
            FROM `tabAccount`
            WHERE `is_group` = 0
                AND `report_type` = 'Balance Sheet'
                AND `root_type` in ('Asset', 'Liability', 'Equity')
                AND `account_type` != 'Stock'
                AND `company` = "{company}"
                AND `account_currency` != "{currency}"
            ORDER BY `name` ASC;""".format(company=self.company, currency=company_currency))
        
        account_details = []
        if accounts:
            account_details = frappe.db.sql("""
                SELECT
                    `account`, 
                    `party_type`, 
                    `party`, 
                    `account_currency`,
                    SUM(`debit_in_account_currency`) - SUM(`credit_in_account_currency`) AS `balance_in_account_currency`,
                    SUM(`debit`) - SUM(`credit`) AS `balance`
                FROM `tabGL Entry`
                WHERE `account` IN ({accounts})
                  AND `posting_date` <= "{date}"
                GROUP BY `account` {with_parties}
                HAVING SUM(`debit`) != SUM(`credit`)
                ORDER BY `account` ASC;
            """.format(accounts="""\"{0}\"""".format("""\", \"""".join(accounts)),
                date=self.posting_date,
                with_parties=", `party_type`, `party`" if self.with_parties else ""), as_dict=1)
        
        return account_details

    def throw_invalid_response_message(self, account_details):
        if account_details:
            message = _("No outstanding invoices require exchange rate revaluation")
        else:
            message = _("No outstanding invoices found")
        frappe.msgprint(message)

    def make_jv_entry(self):
        if self.total_gain_loss == 0:
            return

        unrealized_exchange_gain_loss_account = frappe.get_cached_value('Company',  self.company,
            "unrealized_exchange_gain_loss_account")
        if not unrealized_exchange_gain_loss_account:
            frappe.throw(_("Please set Unrealized Exchange Gain/Loss Account in Company {0}")
                .format(self.company))

        journal_entry = frappe.new_doc('Journal Entry')
        journal_entry.voucher_type = 'Exchange Rate Revaluation'
        journal_entry.company = self.company
        journal_entry.posting_date = self.posting_date
        journal_entry.multi_currency = 1

        journal_entry_accounts = []
        for d in self.accounts:
            dr_or_cr = "debit_in_account_currency" \
                if d.get("balance_in_account_currency") > 0 else "credit_in_account_currency"

            reverse_dr_or_cr = "debit_in_account_currency" \
                if dr_or_cr=="credit_in_account_currency" else "credit_in_account_currency"

            journal_entry_accounts.append({
                "account": d.get("account"),
                "party_type": d.get("party_type"),
                "party": d.get("party"),
                "account_currency": d.get("account_currency"),
                "balance": d.get("balance_in_account_currency"),
                dr_or_cr: abs(d.get("balance_in_account_currency")),
                "exchange_rate":d.get("new_exchange_rate"),
                "reference_type": "Exchange Rate Revaluation",
                "reference_name": self.name,
                })
            journal_entry_accounts.append({
                "account": d.get("account"),
                "party_type": d.get("party_type"),
                "party": d.get("party"),
                "account_currency": d.get("account_currency"),
                "balance": d.get("balance_in_account_currency"),
                reverse_dr_or_cr: abs(d.get("balance_in_account_currency")),
                "exchange_rate": d.get("current_exchange_rate"),
                "reference_type": "Exchange Rate Revaluation",
                "reference_name": self.name
                })

        journal_entry_accounts.append({
            "account": unrealized_exchange_gain_loss_account,
            "balance": get_balance_on(unrealized_exchange_gain_loss_account),
            "debit_in_account_currency": abs(self.total_gain_loss) if self.total_gain_loss < 0 else 0,
            "credit_in_account_currency": self.total_gain_loss if self.total_gain_loss > 0 else 0,
            "exchange_rate": 1,
            "reference_type": "Exchange Rate Revaluation",
            "reference_name": self.name,
            })

        journal_entry.set("accounts", journal_entry_accounts)
        journal_entry.set_amounts_in_company_currency()
        journal_entry.set_total_debit_credit()
        return journal_entry.as_dict()

@frappe.whitelist()
def get_account_details(account, company, posting_date, party_type=None, party=None):
    account_currency, account_type = frappe.db.get_value("Account", account,
        ["account_currency", "account_type"])
    if account_type in ["Receivable", "Payable"] and not (party_type and party):
        frappe.throw(_("Party Type and Party is mandatory for {0} account").format(account_type))

    account_details = {}
    company_currency = erpnext.get_company_currency(company)
    balance = get_balance_on(account, party_type=party_type, party=party, in_account_currency=False)
    if balance:
        balance_in_account_currency = get_balance_on(account, party_type=party_type, party=party)
        current_exchange_rate = balance / balance_in_account_currency if balance_in_account_currency else 0
        new_exchange_rate = get_exchange_rate(account_currency, company_currency, posting_date)
        new_balance_in_base_currency = balance_in_account_currency * new_exchange_rate
        account_details = {
            "account_currency": account_currency,
            "balance_in_base_currency": balance,
            "balance_in_account_currency": balance_in_account_currency,
            "current_exchange_rate": current_exchange_rate,
            "new_exchange_rate": new_exchange_rate,
            "new_balance_in_base_currency": new_balance_in_base_currency
        }

    return account_details
