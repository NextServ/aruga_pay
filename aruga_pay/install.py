# Copyright (c) 2025, Servio and contributors
# For license information, please see license.txt

import frappe


def after_install():
	setup_defaults()


def setup_defaults():
	set_payroll_settings_defaults()


def set_payroll_settings_defaults():
	"""
	Set default Payroll Settings for PH payroll setup.
	Runs only once on fresh install — does not override user changes on migrate.
	"""
	settings = frappe.get_single("Payroll Settings")

	settings.payroll_based_on = "Attendance"
	settings.consider_unmarked_attendance_as = "Absent"


	settings.save(ignore_permissions=True)
	frappe.db.commit()