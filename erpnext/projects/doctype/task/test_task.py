# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals
import frappe
import unittest
from frappe.utils import getdate, nowdate, add_days

from erpnext.projects.doctype.task.task import CircularReferenceError

class TestTask(unittest.TestCase):
	def test_circular_reference(self):
		task1 = create_task("_Test Task 1", add_days(nowdate(), -15), add_days(nowdate(), -10))
		task2 = create_task("_Test Task 2", add_days(nowdate(), 11), add_days(nowdate(), 15), task1.name)
		task3 = create_task("_Test Task 3", add_days(nowdate(), 11), add_days(nowdate(), 15), task2.name)

		task1.reload()
		task1.append("depends_on", {
			"task": task3.name
		})

		self.assertRaises(CircularReferenceError, task1.save)

		task1.set("depends_on", [])
		task1.save()

		task4 = create_task("_Test Task 4", nowdate(), add_days(nowdate(), 15), task1.name)

		task3.append("depends_on", {
			"task": task4.name
		})

	def test_reschedule_dependent_task(self):
		task1 = create_task("_Test Task 1", nowdate(), add_days(nowdate(), 10))

		task2 = create_task("_Test Task 2", add_days(nowdate(), 11), add_days(nowdate(), 15), task1.name)
		task2.get("depends_on")[0].project = "_Test Project"
		task2.save()

		task3 = create_task("_Test Task 3", add_days(nowdate(), 11), add_days(nowdate(), 15), task2.name)
		task3.get("depends_on")[0].project = "_Test Project"
		task3.save()

		task1.update({
			"exp_end_date": add_days(nowdate(), 20)
		})
		task1.save()

		self.assertEqual(frappe.db.get_value("Task", task2.name, "exp_start_date"),
			getdate(add_days(nowdate(), 21)))
		self.assertEqual(frappe.db.get_value("Task", task2.name, "exp_end_date"),
			getdate(add_days(nowdate(), 25)))

		self.assertEqual(frappe.db.get_value("Task", task3.name, "exp_start_date"),
			getdate(add_days(nowdate(), 26)))
		self.assertEqual(frappe.db.get_value("Task", task3.name, "exp_end_date"),
			getdate(add_days(nowdate(), 30)))

	def test_close_assignment(self):
		if not frappe.db.exists("Task", "Test Close Assignment"):
			task = frappe.new_doc("Task")
			task.subject = "Test Close Assignment"
			task.insert()

		def assign():
			from frappe.desk.form import assign_to
			assign_to.add({
				"assign_to": "test@example.com",
				"doctype": task.doctype,
				"name": task.name,
				"description": "Close this task"
			})

		def get_owner_and_status():
			return frappe.db.get_value("ToDo",
				filters={"reference_type": task.doctype, "reference_name": task.name,
					"description": "Close this task"},
				fieldname=("owner", "status"), as_dict=True)

		assign()
		todo = get_owner_and_status()
		self.assertEqual(todo.owner, "test@example.com")
		self.assertEqual(todo.status, "Open")

		# assignment should be
		task.load_from_db()
		task.status = "Completed"
		task.save()
		todo = get_owner_and_status()
		self.assertEqual(todo.owner, "test@example.com")
		self.assertEqual(todo.status, "Closed")

	def test_overdue(self):
		task = create_task("Testing Overdue", add_days(nowdate(), -10), add_days(nowdate(), -5))

		from erpnext.projects.doctype.task.task import set_tasks_as_overdue
		set_tasks_as_overdue()

		self.assertEqual(frappe.db.get_value("Task", task.name, "status"), "Overdue")

	def test_status_progress_roundtrip(self):
		# completing a task should force progress to 100 and remember the previous progress,
		# reopening it should restore the previous progress (and never loop back to Completed)
		task = create_progress_task("_Test Task Progress")
		task.progress = 50
		task.save()
		self.assertEqual(task.status, "Open")
		self.assertEqual(task.progress, 50)

		# complete via status -> progress forced to 100, previous progress remembered
		task.status = "Completed"
		task.save()
		self.assertEqual(task.progress, 100)
		self.assertEqual(task.prev_progress, 50)

		# re-saving a completed task must not change anything (no loop)
		task.save()
		self.assertEqual(task.status, "Completed")
		self.assertEqual(task.progress, 100)

		# reopen -> previous progress restored, status stays open, progress never 100
		task.status = "Open"
		task.save()
		self.assertEqual(task.status, "Open")
		self.assertEqual(task.progress, 50)

		# complete via progress -> status forced to Completed
		task.progress = 100
		task.save()
		self.assertEqual(task.status, "Completed")
		self.assertEqual(task.progress, 100)

	def test_progress_100_falls_back_to_zero_on_reopen(self):
		# if prev_progress is 100 for some reason, reopening must fall back to 0
		task = create_progress_task("_Test Task Progress Fallback")
		task.status = "Completed"
		task.save()
		# simulate a corrupt prev_progress value
		task.db_set("prev_progress", 100)
		task.reload()
		self.assertEqual(task.status, "Completed")

		task.status = "Open"
		task.save()
		self.assertEqual(task.status, "Open")
		self.assertEqual(task.progress, 0)

def create_progress_task(subject):
	# a project-less task, to keep the status/progress tests independent of test fixtures
	if frappe.db.exists("Task", subject):
		frappe.delete_doc("Task", subject, force=True)
	task = frappe.new_doc("Task")
	task.status = "Open"
	task.subject = subject
	task.insert()
	return task

def create_task(subject, start=None, end=None, depends_on=None, project=None, save=True):
	if not frappe.db.exists("Task", subject):
		task = frappe.new_doc('Task')
		task.status = "Open"
		task.subject = subject
		task.exp_start_date = start or nowdate()
		task.exp_end_date = end or nowdate()
		task.project = project or "_Test Project"
		if save:
			task.save()
	else:
		task = frappe.get_doc("Task", subject)

	if depends_on:
		task.append("depends_on", {
			"task": depends_on
		})
		if save:
			task.save()

	return task
