# Copyright (c) 2025, Servio and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint


def after_install():
    setup_defaults()


def setup_defaults():
    """Main setup function that runs after app installation"""
    set_payroll_settings_defaults()
    create_ph_salary_components()
    frappe.db.commit()
    print("✅ PH Payroll Setup Completed Successfully")


def set_payroll_settings_defaults():
    """Set default Payroll Settings for PH payroll"""
    settings = frappe.get_single("Payroll Settings")
    
    # You can choose to force or only set if empty
    settings.payroll_based_on = "Attendance"
    settings.consider_unmarked_attendance_as = "Absent"        # Changed to Absent as you want
    
    # Optional: Only set if currently empty
    # if not settings.consider_unmarked_attendance_as:
    #     settings.consider_unmarked_attendance_as = "Absent"
    
    settings.save(ignore_permissions=True)
    frappe.db.commit()
    print("✓ Payroll Settings defaults applied")


def create_ph_salary_components():
    """Create or update all PH Salary Components"""
    
    components_data = _get_salary_components()
    
    for data in components_data:
        name = data["name"]
        
        if frappe.db.exists("Salary Component", name):
            doc = frappe.get_doc("Salary Component", name)
        else:
            doc = frappe.new_doc("Salary Component")
        
        # Set all standard fields
        for key, value in data.items():
            setattr(doc, key, value)
        
        # === FORCE CUSTOM FIELDS (This is the most important part) ===
        doc.formula_based_on_attendance = cint(data.get("formula_based_on_attendance", 0))
        doc.formula_effectivity = data.get("formula_effectivity", "Period")
        doc.formula_prorated = cint(data.get("formula_prorated", 0))
        doc.is_13th_month_pay_applicable = cint(data.get("is_13th_month_pay_applicable", 0))
        doc.is_basic_pay = cint(data.get("is_basic_pay", 0))

        # Set description (proration instructions visible in UI)
        if data.get("description"):
            doc.description = data["description"]
        
        doc.flags.ignore_mandatory = True
        doc.flags.ignore_permissions = True
        
        try:
            doc.save(ignore_permissions=True)
            print(f"✓ Updated: {name}")
        except Exception as e:
            print(f"✗ Failed {name}: {e}")

    print("All Salary Components processed.")


def _get_salary_components():
	return [
		{
			"name": "PH - REG",
			"salary_component": "PH - REG",
			"salary_component_abbr": "PH_REG",
			"type": "Earning",
			"formula": "working_hours * hourly_rate",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and not special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 1,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - REG SEMI MONTHLY",
			"salary_component": "PH - REG SEMI MONTHLY",
			"salary_component_abbr": "PH_REG_SM",
			"type": "Earning",
			"formula": "monthly_rate / 2",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"condition": " ",
			"is_tax_applicable": 1,
			"is_basic_pay": 1,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - REG MONTHLY",
			"salary_component": "PH - REG MONTHLY",
			"salary_component_abbr": "PH_REG_M",
			"type": "Earning",
			"formula": "(monthly_rate / 2) if total_working_days <= 16 else monthly_rate",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"condition": " ",
			"is_tax_applicable": 1,
			"is_basic_pay": 1,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - REG_OT",
			"salary_component": "PH - REG_OT",
			"salary_component_abbr": "PH_REG_OT",
			"type": "Earning",
			"formula": "overtime * hourly_rate * 1.25",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and not special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - ND",
			"salary_component": "PH - ND",
			"salary_component_abbr": "PH_ND",
			"type": "Earning",
			"formula": "night_differential * hourly_rate * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and not special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - ND_OT",
			"salary_component": "PH - ND_OT",
			"salary_component_abbr": "PH_ND_OT",
			"type": "Earning",
			"formula": "night_differential_overtime * hourly_rate * 1.25 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and not special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - RST",
			"salary_component": "PH - RST",
			"salary_component_abbr": "PH_RST",
			"type": "Earning",
			"formula": "working_hours * hourly_rate * 1.3",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and not special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - RST_OT",
			"salary_component": "PH - RST_OT",
			"salary_component_abbr": "PH_RST_OT",
			"type": "Earning",
			"formula": "overtime * hourly_rate * 1.69",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and not special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - RST_ND",
			"salary_component": "PH - RST_ND",
			"salary_component_abbr": "PH_RST_ND",
			"type": "Earning",
			"formula": "night_differential * hourly_rate * 1.3 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and not special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - RST_ND_OT",
			"salary_component": "PH - RST_ND_OT",
			"salary_component_abbr": "PH_RST_ND_OT",
			"type": "Earning",
			"formula": "night_differential_overtime * hourly_rate * 1.3 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and not special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SP",
			"salary_component": "PH - SP",
			"salary_component_abbr": "PH_SP",
			"type": "Earning",
			"formula": "working_hours * hourly_rate * 1.3",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SP_OT",
			"salary_component": "PH - SP_OT",
			"salary_component_abbr": "PH_SP_OT",
			"type": "Earning",
			"formula": "overtime * hourly_rate * 1.69",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SP_ND",
			"salary_component": "PH - SP_ND",
			"salary_component_abbr": "PH_SP_ND",
			"type": "Earning",
			"formula": "night_differential * hourly_rate * 1.3 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SP_ND_OT",
			"salary_component": "PH - SP_ND_OT",
			"salary_component_abbr": "PH_SP_ND_OT",
			"type": "Earning",
			"formula": "night_differential_overtime * hourly_rate * 1.3 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - LEG",
			"salary_component": "PH - LEG",
			"salary_component_abbr": "PH_LEG",
			"type": "Earning",
			"formula": "working_hours * hourly_rate * 2",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and not special_holiday and legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - LEG_OT",
			"salary_component": "PH - LEG_OT",
			"salary_component_abbr": "PH_LEG_OT",
			"type": "Earning",
			"formula": "overtime * hourly_rate * 2.6",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and not special_holiday and legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - LEG_ND",
			"salary_component": "PH - LEG_ND",
			"salary_component_abbr": "PH_LEG_ND",
			"type": "Earning",
			"formula": "night_differential * hourly_rate * 2 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and not special_holiday and legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - LEG_ND_OT",
			"salary_component": "PH - LEG_ND_OT",
			"salary_component_abbr": "PH_LEG_ND_OT",
			"type": "Earning",
			"formula": "night_differential_overtime * hourly_rate * 2 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "not rest_day and not special_holiday and legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SP_RST",
			"salary_component": "PH - SP_RST",
			"salary_component_abbr": "PH_SP_RST",
			"type": "Earning",
			"formula": "working_hours * hourly_rate * 1.5",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SP_RST_OT",
			"salary_component": "PH - SP_RST_OT",
			"salary_component_abbr": "PH_SP_RST_OT",
			"type": "Earning",
			"formula": "overtime * hourly_rate * 1.95",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SP_RST_ND",
			"salary_component": "PH - SP_RST_ND",
			"salary_component_abbr": "PH_SP_RST_ND",
			"type": "Earning",
			"formula": "night_differential * hourly_rate * 1.5 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SP_RST_ND_OT",
			"salary_component": "PH - SP_RST_ND_OT",
			"salary_component_abbr": "PH_SP_RST_ND_OT",
			"type": "Earning",
			"formula": "night_differential_overtime * hourly_rate * 1.5 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and special_holiday and not legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - LEG_RST",
			"salary_component": "PH - LEG_RST",
			"salary_component_abbr": "PH_LEG_RST",
			"type": "Earning",
			"formula": "working_hours * hourly_rate * 2.6",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and not special_holiday and legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - LEG_RST_OT",
			"salary_component": "PH - LEG_RST_OT",
			"salary_component_abbr": "PH_LEG_RST_OT",
			"type": "Earning",
			"formula": "overtime * hourly_rate * 3.38",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and not special_holiday and legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - LEG_RST_ND",
			"salary_component": "PH - LEG_RST_ND",
			"salary_component_abbr": "PH_LEG_RST_ND",
			"type": "Earning",
			"formula": "night_differential * hourly_rate * 2.6 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and not special_holiday and legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - LEG_RST_ND_OT",
			"salary_component": "PH - LEG_RST_ND_OT",
			"salary_component_abbr": "PH_LEG_RST_ND_OT",
			"type": "Earning",
			"formula": "night_differential_overtime * hourly_rate * 2.6 * 0.1",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "rest_day and not special_holiday and legal_holiday",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - Undertime",
			"salary_component": "PH - Undertime",
			"salary_component_abbr": "PH_UT",
			"type": "Earning",
			"formula": "undertime * -hourly_rate",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - Absence",
			"salary_component": "PH - Absence",
			"salary_component_abbr": "PH_A",
			"type": "Earning",
			"formula": "absent_days * -daily_rate",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"condition": "",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - Leave",
			"salary_component": "PH - Leave",
			"salary_component_abbr": "PH_L",
			"type": "Earning",
			"formula": "leave * hourly_rate",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 1,
			"formula_effectivity": "Period",
			"condition": "",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - REG (Fixed)",
			"salary_component": "PH - REG (Fixed)",
			"salary_component_abbr": "PH_REG_F",
			"type": "Earning",
			"formula": "(monthly_rate / 2) if total_working_days <= 16 else monthly_rate",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"condition": "",
			"is_tax_applicable": 1,
			"is_basic_pay": 1,
			"is_13th_month_pay_applicable": 1,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - 13th Month Pay",
			"salary_component": "PH - 13th Month Pay",
			"salary_component_abbr": "PH_13M_1",
			"type": "Earning",
			"formula": "ph_13th_month_pay()",
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"condition": "",
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		# --- Deductions ---
		#
		# PRORATION GUIDE (for salary structure component formula field):
		#   All PH statutory lambdas use formula_effectivity = Period.
		#   The lambda itself owns bimonthly detection — the framework's
		#   formula_prorated checkbox has NO effect on these components.
		#
		#   To switch between non-prorated and prorated, change ONLY the
		#   formula in the salary structure (not in this component master):
		#
		#     ph_phic()            → PHIC non-prorated  (0 on 1st, full on 2nd)
		#     ph_phic(True)        → PHIC prorated       (half on 1st, remainder on 2nd)
		#     ph_hdmf()            → HDMF non-prorated
		#     ph_hdmf(True)        → HDMF prorated
		#     ph_sss()             → SSS EE non-prorated
		#     ph_sss(prorated=True)→ SSS EE prorated
		#     ph_sss_er()          → SSS ER non-prorated
		#     ph_sss_er(prorated=True) → SSS ER prorated
		#     ph_sss_ec()          → SSS EC non-prorated
		#     ph_sss_ec(prorated=True) → SSS EC prorated
		#     ph_wtax()            → Withholding Tax (always non-prorated, 0 on 1st half)
		#
		{
			"name": "PH - PHIC Contribution",
			"salary_component": "PH - PHIC Contribution",
			"salary_component_abbr": "PH_PHIC",
			"type": "Deduction",
			# Default: non-prorated (0 on 1st period, full PHIC on 2nd period).
			# Change to ph_phic(True) in your salary structure for prorated split.
			"formula": "ph_phic()",
			"description": (
				"PhilHealth (PHIC) Employee Share.\n\n"
				"PRORATION — change formula in your Salary Structure (not here):\n"
				"  Non-prorated (default): ph_phic()\n"
				"    → 1st period: ₱0  |  2nd period: full monthly PHIC\n"
				"  Prorated: ph_phic(True)\n"
				"    → 1st period: half  |  2nd period: remainder\n\n"
				"formula_effectivity must always be 'Period'.\n"
				"formula_prorated checkbox has NO effect — the lambda owns bimonthly logic."
			),
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"formula_prorated": 0,
			"statistical_component": 0,
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - PHIC Employer Contribution",
			"salary_component": "PH - PHIC Employer Contribution",
			"salary_component_abbr": "PH_PHIC_ER",
			"type": "Deduction",
			# Statistical — tracks employer PHIC share, does not affect net pay.
			# Uses same ph_phic() lambda as EE share.
			"formula": "ph_phic()",
			"description": (
				"PhilHealth (PHIC) Employer Share — statistical, does not affect net pay.\n\n"
				"PRORATION — change formula in your Salary Structure (not here):\n"
				"  Non-prorated (default): ph_phic()\n"
				"  Prorated: ph_phic(True)\n\n"
				"formula_effectivity must always be 'Period'."
			),
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"formula_prorated": 0,
			"statistical_component": 1,
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - HDMF Contribution",
			"salary_component": "PH - HDMF Contribution",
			"salary_component_abbr": "PH_HDMF",
			"type": "Deduction",
			# Default: non-prorated (0 on 1st period, full HDMF on 2nd period).
			# The lambda applies the formula to combined monthly gross — never per-period gross.
			# Change to ph_hdmf(True) in your salary structure for prorated split.
			"formula": "ph_hdmf()",
			"description": (
				"Pag-IBIG (HDMF) Employee Share.\n\n"
				"The lambda always applies the HDMF formula to FULL MONTHLY gross, not\n"
				"per-period gross, so the ₱200 cap is never incorrectly consumed per period.\n\n"
				"PRORATION — change formula in your Salary Structure (not here):\n"
				"  Non-prorated (default): ph_hdmf()\n"
				"    → 1st period: ₱0  |  2nd period: full monthly HDMF\n"
				"  Prorated: ph_hdmf(True)\n"
				"    → 1st period: full/2  |  2nd period: remainder\n\n"
				"formula_effectivity must always be 'Period'.\n"
				"formula_prorated checkbox has NO effect — the lambda owns bimonthly logic."
			),
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"formula_prorated": 0,
			"statistical_component": 0,
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - HDMF Employer Contribution",
			"salary_component": "PH - HDMF Employer Contribution",
			"salary_component_abbr": "PH_HDMF_ER",
			"type": "Deduction",
			# Statistical — tracks employer HDMF share, does not affect net pay.
			"formula": "ph_hdmf()",
			"description": (
				"Pag-IBIG (HDMF) Employer Share — statistical, does not affect net pay.\n\n"
				"PRORATION — change formula in your Salary Structure (not here):\n"
				"  Non-prorated (default): ph_hdmf()\n"
				"  Prorated: ph_hdmf(True)\n\n"
				"formula_effectivity must always be 'Period'."
			),
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"formula_prorated": 0,
			"statistical_component": 1,
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SSS Contribution",
			"salary_component": "PH - SSS Contribution",
			"salary_component_abbr": "PH_SSS",
			"type": "Deduction",
			# Default: non-prorated.
			# SSS bracket uses assignment.base for Monthly-rate employees and
			# combined gross_pay for Daily/Hourly employees.
			# Change to ph_sss(prorated=True) in your salary structure for prorated.
			"formula": "ph_sss()",
			"description": (
				"SSS Employee Contribution.\n\n"
				"Bracket lookup uses:\n"
				"  Monthly rate  → assignment.base (contracted salary, unaffected by LWP)\n"
				"  Daily/Hourly  → combined gross_pay from both cutoffs\n\n"
				"PRORATION — change formula in your Salary Structure (not here):\n"
				"  Non-prorated (default): ph_sss()\n"
				"    → 1st period: ₱0  |  2nd period: full monthly SSS\n"
				"  Prorated: ph_sss(prorated=True)\n"
				"    → 1st period: full/2  |  2nd period: remainder\n\n"
				"NOTE: ph_sss(True) will NOT work — True binds to 'pay', not 'prorated'.\n"
				"Always use ph_sss(prorated=True).\n\n"
				"formula_effectivity must always be 'Period'.\n"
				"formula_prorated checkbox has NO effect."
			),
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"formula_prorated": 0,
			"statistical_component": 0,
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SSS Employer Contribution",
			"salary_component": "PH - SSS Employer Contribution",
			"salary_component_abbr": "PH_SSS_ER",
			"type": "Deduction",
			# Statistical — tracks employer SSS share, does not affect net pay.
			"formula": "ph_sss_er()",
			"description": (
				"SSS Employer Contribution — statistical, does not affect net pay.\n\n"
				"PRORATION — change formula in your Salary Structure (not here):\n"
				"  Non-prorated (default): ph_sss_er()\n"
				"  Prorated: ph_sss_er(prorated=True)\n\n"
				"formula_effectivity must always be 'Period'."
			),
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"formula_prorated": 0,
			"statistical_component": 1,
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - SSS Employee Compensation",
			"salary_component": "PH - SSS Employee Compensation",
			"salary_component_abbr": "PH_SSS_EC",
			"type": "Deduction",
			# Statistical — EC fund, employer pays, does not affect net pay.
			"formula": "ph_sss_ec()",
			"description": (
				"SSS Employee Compensation (EC) — statistical, does not affect net pay.\n\n"
				"PRORATION — change formula in your Salary Structure (not here):\n"
				"  Non-prorated (default): ph_sss_ec()\n"
				"  Prorated: ph_sss_ec(prorated=True)\n\n"
				"formula_effectivity must always be 'Period'."
			),
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"formula_prorated": 0,
			"statistical_component": 1,
			"is_tax_applicable": 1,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
		{
			"name": "PH - Withholding Tax",
			"salary_component": "PH - Withholding Tax",
			"salary_component_abbr": "PH_WTAX",
			"type": "Deduction",
			# WTax is always non-prorated by design:
			#   1st half → ₱0 (guard inside the lambda)
			#   2nd half → full tax on combined monthly taxable income
			# No prorated=True option — withholding tax is collected once per month.
			"formula": "ph_wtax()",
			"description": (
				"BIR Withholding Tax on Compensation.\n\n"
				"Always non-prorated — the lambda returns ₱0 on the 1st bimonthly half\n"
				"and computes the full monthly tax on the 2nd half using both periods' gross.\n\n"
				"There is no prorated option for WTax.\n\n"
				"formula_effectivity must always be 'Period'.\n"
				"formula_prorated checkbox has NO effect."
			),
			"amount_based_on_formula": 1,
			"formula_based_on_attendance": 0,
			"formula_effectivity": "Period",
			"formula_prorated": 0,
			"statistical_component": 0,
			"is_tax_applicable": 0,
			"is_basic_pay": 0,
			"is_13th_month_pay_applicable": 0,
			"depends_on_payment_days": 0,
		},
	]