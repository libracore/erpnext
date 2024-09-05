# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
import frappe.defaults
from frappe import msgprint, _
from frappe.utils import cstr, flt, cint
from erpnext.stock.stock_ledger import update_entries_after
from erpnext.controllers.stock_controller import StockController
from erpnext.accounts.utils import get_company_default
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from erpnext.stock.utils import get_stock_balance, get_incoming_rate, get_available_serial_nos
from erpnext.stock.doctype.batch.batch import get_batch_qty

class OpeningEntryAccountError(frappe.ValidationError): pass
class EmptyStockReconciliationItemsError(frappe.ValidationError): pass

class StockReconciliation(StockController):
	def __init__(self, *args, **kwargs):
		super(StockReconciliation, self).__init__(*args, **kwargs)
		self.head_row = ["Item Code", "Warehouse", "Quantity", "Valuation Rate"]

	def validate(self):
		if not self.expense_account:
			self.expense_account = frappe.get_cached_value('Company',  self.company,  "stock_adjustment_account")
		if not self.cost_center:
			self.cost_center = frappe.get_cached_value('Company',  self.company,  "cost_center")
		self.validate_posting_time()
		if not self.ignore_remove_items_with_no_change:
			self.remove_items_with_no_change()
		else:
			self.calculate_difference_amount()
		self.validate_data()
		self.validate_expense_account()
		self.set_total_qty_and_amount()

		if self._action=="submit":
			self.make_batches('warehouse')

	def on_submit(self):
		self.update_stock_ledger()
		self.make_gl_entries()

		from erpnext.stock.doctype.serial_no.serial_no import update_serial_nos_after_submit
		update_serial_nos_after_submit(self, "items")

	def on_cancel(self):
		self.delete_and_repost_sle()
		self.make_gl_entries_on_cancel()

	def remove_items_with_no_change(self):
		"""Remove items if qty or rate is not changed"""
		self.difference_amount = 0.0
		def _changed(item):
			item_dict = get_stock_balance_for(item.item_code, item.warehouse,
				self.posting_date, self.posting_time, batch_no=item.batch_no)
			if (((item.qty is None or item.qty==item_dict.get("qty")) and
				(item.valuation_rate is None or item.valuation_rate==item_dict.get("rate")) and not item.serial_no)
				or (item.serial_no and item.serial_no == item_dict.get("serial_nos"))):
				return False
			else:
				# set default as current rates
				if item.qty is None:
					item.qty = item_dict.get("qty")

				if item.valuation_rate is None:
					item.valuation_rate = item_dict.get("rate")

				if item_dict.get("serial_nos"):
					item.current_serial_no = item_dict.get("serial_nos")

				item.current_qty = item_dict.get("qty")
				item.current_valuation_rate = item_dict.get("rate")
				self.difference_amount += (flt(item.qty, item.precision("qty")) * \
					flt(item.valuation_rate or item_dict.get("rate"), item.precision("valuation_rate")) \
					- flt(item_dict.get("qty"), item.precision("qty")) * flt(item_dict.get("rate"), item.precision("valuation_rate")))
				return True

		items = list(filter(lambda d: _changed(d), self.items))

		if not items:
			frappe.throw(_("None of the items have any change in quantity or value."),
				EmptyStockReconciliationItemsError)

		elif len(items) != len(self.items):
			self.items = items
			for i, item in enumerate(self.items):
				item.idx = i + 1
			frappe.msgprint(_("Removed items with no change in quantity or value."))

	def calculate_difference_amount(self):
		self.difference_amount = 0.0
		for item in self.items:
			self.difference_amount += item.amount_difference


	def validate_data(self):
		def _get_msg(row_num, msg):
			return _("Row # {0}: ").format(row_num+1) + msg

		self.validation_messages = []
		item_warehouse_combinations = []

		default_currency = frappe.db.get_default("currency")

		for row_num, row in enumerate(self.items):
			# find duplicates
			key = [row.item_code, row.warehouse]
			for field in ['serial_no', 'batch_no']:
				if row.get(field):
					key.append(row.get(field))

			if key in item_warehouse_combinations:
				self.validation_messages.append(_get_msg(row_num, _("Duplicate entry")))
			else:
				item_warehouse_combinations.append(key)

			self.validate_item(row.item_code, row)

			# validate warehouse
			if not frappe.db.get_value("Warehouse", row.warehouse):
				self.validation_messages.append(_get_msg(row_num, _("Warehouse not found in the system")))

			# if both not specified
			if row.qty in ["", None] and row.valuation_rate in ["", None]:
				self.validation_messages.append(_get_msg(row_num,
					_("Please specify either Quantity or Valuation Rate or both")))

			# do not allow negative quantity
			if flt(row.qty) < 0:
				self.validation_messages.append(_get_msg(row_num,
					_("Negative Quantity is not allowed")))

			# do not allow negative valuation
			if flt(row.valuation_rate) < 0:
				self.validation_messages.append(_get_msg(row_num,
					_("Negative Valuation Rate is not allowed")))

			if row.qty and row.valuation_rate in ["", None]:
				row.valuation_rate = get_stock_balance(row.item_code, row.warehouse,
							self.posting_date, self.posting_time, with_valuation_rate=True)[1]
				if not row.valuation_rate:
					# try if there is a buying price list in default currency
					buying_rate = frappe.db.get_value("Item Price", {"item_code": row.item_code,
						"buying": 1, "currency": default_currency}, "price_list_rate")
					if buying_rate:
						row.valuation_rate = buying_rate

					else:
						# get valuation rate from Item
						row.valuation_rate = frappe.get_value('Item', row.item_code, 'valuation_rate')

		# throw all validation messages
		if self.validation_messages:
			for msg in self.validation_messages:
				msgprint(msg)

			raise frappe.ValidationError(self.validation_messages)

	def validate_item(self, item_code, row):
		from erpnext.stock.doctype.item.item import validate_end_of_life, \
			validate_is_stock_item, validate_cancelled_item

		# using try except to catch all validation msgs and display together

		try:
			item = frappe.get_doc("Item", item_code)

			# end of life and stock item
			validate_end_of_life(item_code, item.end_of_life, item.disabled, verbose=0)
			validate_is_stock_item(item_code, item.is_stock_item, verbose=0)

			# item should not be serialized
			if item.has_serial_no and not row.serial_no and not item.serial_no_series:
				raise frappe.ValidationError(_("Serial no(s) required for serialized item {0}").format(item_code))

			# item managed batch-wise not allowed
			if item.has_batch_no and not row.batch_no and not item.create_new_batch:
				raise frappe.ValidationError(_("Batch no is required for batched item {0}").format(item_code))

			# docstatus should be < 2
			validate_cancelled_item(item_code, item.docstatus, verbose=0)

		except Exception as e:
			self.validation_messages.append(_("Row # ") + ("%d: " % (row.idx)) + cstr(e))

	def update_stock_ledger(self):
		"""	find difference between current and expected entries
			and create stock ledger entries based on the difference"""
		from erpnext.stock.stock_ledger import get_previous_sle

		sl_entries = []
		for row in self.items:
			item = frappe.get_doc("Item", row.item_code)
			if item.has_serial_no or item.has_batch_no:
				self.get_sle_for_serialized_items(row, sl_entries)
			else:
				previous_sle = get_previous_sle({
					"item_code": row.item_code,
					"warehouse": row.warehouse,
					"posting_date": self.posting_date,
					"posting_time": self.posting_time
				})

				if previous_sle:
					if row.qty in ("", None):
						row.qty = previous_sle.get("qty_after_transaction", 0)

					if row.valuation_rate in ("", None):
						row.valuation_rate = previous_sle.get("valuation_rate", 0)

				if row.qty and not row.valuation_rate:
					frappe.throw(_("Valuation Rate required for Item {0} at row {1}").format(row.item_code, row.idx))

				if ((previous_sle and row.qty == previous_sle.get("qty_after_transaction")
					and (row.valuation_rate == previous_sle.get("valuation_rate") or row.qty == 0))
					or (not previous_sle and not row.qty)):
						continue

				sl_entries.append(self.get_sle_for_items(row))

		if sl_entries:
			self.make_sl_entries(sl_entries)

	def get_sle_for_serialized_items(self, row, sl_entries):
		from erpnext.stock.stock_ledger import get_previous_sle

		serial_nos = get_serial_nos(row.serial_no)


		# To issue existing serial nos
		if row.current_qty and (row.current_serial_no or row.batch_no):
			args = self.get_sle_for_items(row)
			args.update({
				'actual_qty': -1 * row.current_qty,
				'serial_no': row.current_serial_no,
				'batch_no': row.batch_no,
				'valuation_rate': row.current_valuation_rate
			})

			if row.current_serial_no:
				args.update({
					'qty_after_transaction': 0,
				})

			sl_entries.append(args)

		for serial_no in serial_nos:
			args = self.get_sle_for_items(row, [serial_no])

			previous_sle = get_previous_sle({
				"item_code": row.item_code,
				"posting_date": self.posting_date,
				"posting_time": self.posting_time,
				"serial_no": serial_no
			})

			if previous_sle and row.warehouse != previous_sle.get("warehouse"):
				# If serial no exists in different warehouse

				new_args = args.copy()
				new_args.update({
					'actual_qty': -1,
					'qty_after_transaction': cint(previous_sle.get('qty_after_transaction')) - 1,
					'warehouse': previous_sle.get("warehouse", '') or row.warehouse,
					'valuation_rate': previous_sle.get("valuation_rate")
				})

				sl_entries.append(new_args)

		if row.qty:
			args = self.get_sle_for_items(row)

			args.update({
				'actual_qty': row.qty,
				'incoming_rate': row.valuation_rate,
				'valuation_rate': row.valuation_rate
			})

			sl_entries.append(args)

		if serial_nos == get_serial_nos(row.current_serial_no):
			# update valuation rate
			self.update_valuation_rate_for_serial_nos(row, serial_nos)

	def update_valuation_rate_for_serial_nos(self, row, serial_nos):
		valuation_rate = row.valuation_rate if self.docstatus == 1 else row.current_valuation_rate
		for d in serial_nos:
			frappe.db.set_value("Serial No", d, 'purchase_rate', valuation_rate)

	def get_sle_for_items(self, row, serial_nos=None):
		"""Insert Stock Ledger Entries"""

		if not serial_nos and row.serial_no:
			serial_nos = get_serial_nos(row.serial_no)

		data = frappe._dict({
			"doctype": "Stock Ledger Entry",
			"item_code": row.item_code,
			"warehouse": row.warehouse,
			"posting_date": self.posting_date,
			"posting_time": self.posting_time,
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"voucher_detail_no": row.name,
			"company": self.company,
			"stock_uom": frappe.db.get_value("Item", row.item_code, "stock_uom"),
			"is_cancelled": "No" if self.docstatus != 2 else "Yes",
			"serial_no": '\n'.join(serial_nos) if serial_nos else '',
			"batch_no": row.batch_no,
			"valuation_rate": flt(row.valuation_rate, row.precision("valuation_rate"))
		})

		if not row.batch_no:
			data.qty_after_transaction = flt(row.qty, row.precision("qty"))

		return data

	def delete_and_repost_sle(self):
		"""	Delete Stock Ledger Entries related to this voucher
			and repost future Stock Ledger Entries"""

		existing_entries = frappe.db.sql("""select distinct item_code, warehouse
			from `tabStock Ledger Entry` where voucher_type=%s and voucher_no=%s""",
			(self.doctype, self.name), as_dict=1)

		# delete entries
		frappe.db.sql("""delete from `tabStock Ledger Entry`
			where voucher_type=%s and voucher_no=%s""", (self.doctype, self.name))

		sl_entries = []
		for row in self.items:
			if row.serial_no or row.batch_no or row.current_serial_no:
				self.get_sle_for_serialized_items(row, sl_entries)

		if sl_entries:
			sl_entries.reverse()
			allow_negative_stock = frappe.db.get_value("Stock Settings", None, "allow_negative_stock")
			self.make_sl_entries(sl_entries, allow_negative_stock=allow_negative_stock)

		# repost future entries for selected item_code, warehouse
		for entries in existing_entries:
			update_entries_after({
				"item_code": entries.item_code,
				"warehouse": entries.warehouse,
				"posting_date": self.posting_date,
				"posting_time": self.posting_time
			})

	def get_gl_entries(self, warehouse_account=None):
		if not self.cost_center:
			msgprint(_("Please enter Cost Center"), raise_exception=1)

		return super(StockReconciliation, self).get_gl_entries(warehouse_account,
			self.expense_account, self.cost_center)

	def validate_expense_account(self):
		if not cint(erpnext.is_perpetual_inventory_enabled(self.company)):
			return

		if not self.expense_account:
			frappe.throw(_("Please enter Expense Account"))
		elif self.purpose == "Opening Stock" or not frappe.db.sql("""select name from `tabStock Ledger Entry` limit 1"""):
			if frappe.db.get_value("Account", self.expense_account, "report_type") == "Profit and Loss":
				frappe.throw(_("Difference Account must be a Asset/Liability type account, since this Stock Reconciliation is an Opening Entry"), OpeningEntryAccountError)

	def set_total_qty_and_amount(self):
		for d in self.get("items"):
			d.amount = flt(d.qty, d.precision("qty")) * flt(d.valuation_rate, d.precision("valuation_rate"))
			d.current_amount = (flt(d.current_qty,
				d.precision("current_qty")) * flt(d.current_valuation_rate, d.precision("current_valuation_rate")))

			d.quantity_difference = flt(d.qty) - flt(d.current_qty)
			d.amount_difference = flt(d.amount) - flt(d.current_amount)

	def get_items_for(self, warehouse):
		self.items = []
		for item in get_items(warehouse, self.posting_date, self.posting_time, self.company):
			self.append("items", item)

	def submit(self):
		if len(self.items) > 100:
			msgprint(_("The task has been enqueued as a background job. In case there is any issue on processing in background, the system will add a comment about the error on this Stock Reconciliation and revert to the Draft stage"))
			self.queue_action('submit')
		else:
			self._submit()

	def cancel(self):
		if len(self.items) > 100:
			self.queue_action('cancel')
		else:
			self._cancel()

@frappe.whitelist()
def get_items(warehouse, posting_date, posting_time, company):
	lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
	items = frappe.db.sql("""
		select i.name, i.item_name, bin.warehouse
		from tabBin bin, tabItem i
		where i.name=bin.item_code and i.disabled=0 and i.is_stock_item = 1
		and i.has_variants = 0 and i.has_serial_no = 0 and i.has_batch_no = 0
		and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=bin.warehouse)
	""", (lft, rgt))

	items += frappe.db.sql("""
		select i.name, i.item_name, id.default_warehouse
		from tabItem i, `tabItem Default` id
		where i.name = id.parent
			and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=id.default_warehouse)
			and i.is_stock_item = 1 and i.has_serial_no = 0 and i.has_batch_no = 0
			and i.has_variants = 0 and i.disabled = 0 and id.company=%s
		group by i.name
	""", (lft, rgt, company))

	res = []
	for d in set(items):
		stock_bal = get_stock_balance(d[0], d[2], posting_date, posting_time,
			with_valuation_rate=True)

		if frappe.db.get_value("Item", d[0], "disabled") == 0:
			res.append({
				"item_code": d[0],
				"warehouse": d[2],
				"qty": stock_bal[0],
				"item_name": d[1],
				"valuation_rate": stock_bal[1],
				"current_qty": stock_bal[0],
				"current_valuation_rate": stock_bal[1]
			})

	return res

@frappe.whitelist()
def get_stock_balance_for(item_code, warehouse,
	posting_date, posting_time, batch_no=None, with_valuation_rate= True):
	frappe.has_permission("Stock Reconciliation", "write", throw = True)

	item_dict = frappe.db.get_value("Item", item_code,
		["has_serial_no", "has_batch_no"], as_dict=1)

	serial_nos = ""
	if item_dict.get("has_serial_no"):
		qty, rate, serial_nos = get_qty_rate_for_serial_nos(item_code,
			warehouse, posting_date, posting_time, item_dict)
	else:
		qty, rate = get_stock_balance(item_code, warehouse,
			posting_date, posting_time, with_valuation_rate=with_valuation_rate)

	if item_dict.get("has_batch_no"):
		qty = get_batch_qty(batch_no, warehouse) or 0

	return {
		'qty': qty,
		'rate': rate,
		'serial_nos': serial_nos
	}

def get_qty_rate_for_serial_nos(item_code, warehouse, posting_date, posting_time, item_dict):
	args = {
		"item_code": item_code,
		"warehouse": warehouse,
		"posting_date": posting_date,
		"posting_time": posting_time,
	}

	serial_nos_list = [serial_no.get("name")
			for serial_no in get_available_serial_nos(item_code, warehouse)]

	qty = len(serial_nos_list)
	serial_nos = '\n'.join(serial_nos_list)
	args.update({
		'qty': qty,
		"serial_nos": serial_nos
	})

	rate = get_incoming_rate(args, raise_error_if_no_rate=False) or 0

	return qty, rate, serial_nos

@frappe.whitelist()
def get_difference_account(purpose, company):
	if purpose == 'Stock Reconciliation':
		account = get_company_default(company, "stock_adjustment_account")
	else:
		account = frappe.db.get_value('Account', {'is_group': 0,
			'company': company, 'account_type': 'Temporary'}, 'name')

	return account
