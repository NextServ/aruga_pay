import frappe
from frappe.utils import flt

def calculate_total_working_hours(doc, method=None):
    """
    Compute working hours for Salary Slip based on Attendance.
    Fields computed:
      - total_basic_hours: regular days (no rest, no special, no legal)
      - total_sp_hours: special holidays
      - total_lp_hours: legal holidays
      - total_rd_hours: rest days
      - total_reg_ot_hours: regular overtime hours
    """
    total_basic_hours = total_sp_hours = total_lp_hours = total_rd_hours = total_reg_ot_hours = 0.0

    attendance_records = frappe.get_all(
        "Attendance",
        filters={
            "employee": doc.employee,
            "attendance_date": ["between", [doc.start_date, doc.end_date]],
            "docstatus": 1
        },
        fields=["working_hours", "overtime", "rest_day", "special_holiday", "legal_holiday"]
    )

    for att in attendance_records:
        # Regular day
        if not att.rest_day and not att.special_holiday and not att.legal_holiday:
            total_basic_hours += flt(att.working_hours)
            total_reg_ot_hours += flt(att.overtime)
        # Rest day
        if att.rest_day:
            total_rd_hours += flt(att.working_hours)
        # Special holiday
        if att.special_holiday:
            total_sp_hours += flt(att.working_hours)
        # Legal holiday
        if att.legal_holiday:
            total_lp_hours += flt(att.working_hours)

    doc.total_basic_hours = total_basic_hours
    doc.total_rd_hours = total_rd_hours
    doc.total_sp_hours = total_sp_hours
    doc.total_lp_hours = total_lp_hours
    doc.total_reg_ot_hours = total_reg_ot_hours
    

def copy_salary_component_fields(doc, method=None):
    """
    Copy custom fields from Salary Structure Details into Salary Slip rows
    (same logic as copying from Salary Component, but using the Salary Structure tables).
    """
    if not doc.salary_structure:
        return

    salary_structure = frappe.get_cached_doc("Salary Structure", doc.salary_structure)

    for table in ("earnings", "deductions"):
        ss_rows = salary_structure.get(table)

        for slip_row in doc.get(table):
            if not slip_row.salary_component:
                continue

            # Find matching row in Salary Structure
            match = next(
                (r for r in ss_rows if r.salary_component == slip_row.salary_component),
                None
            )
            if not match:
                continue

            # The custom fields you want to copy
            custom_fields = [
                "formula_based_on_attendance",
                "formula_effectivity",
                "formula_prorated",
                "is_13th_month_pay_applicable",
                "is_basic_pay",
            ]

            # Copy field values
            for field in custom_fields:
                if hasattr(match, field):
                    setattr(slip_row, field, getattr(match, field))

    # Recalculate amounts after updating rows
    doc.calculate_net_pay()



# from frappe import _

# def copy_salary_component_fields(doc, method=None):
#     """
#     Copy custom fields safely without breaking formulas.
#     """
#     for table in ("earnings", "deductions"):
#         for row in doc.get(table):
#             if not row.salary_component:
#                 continue
#             sc = frappe.get_cached_doc("Salary Component", row.salary_component)
#             for field in [
#                 "formula_based_on_attendance",
#                 "formula_effectivity",
#                 "formula_prorated",
#                 "is_13th_month_pay_applicable",
#                 "is_basic_pay",
#             ]:
#                 if hasattr(sc, field):
#                     setattr(row, field, getattr(sc, field))

#     # Recalculate gross pay and basic pay after updating rows
#     doc.calculate_net_pay()



# def calculate_13th_month_pay(salary_slip):
# 	effective_year = getdate(salary_slip.posting_date).year

# 	if getdate(salary_slip.posting_date).month <= 4:
# 		# Last year
# 		effective_year -= 1

# 	gross_pay = db.sql("""
# 		SELECT sum(detail.amount) as sum
# 		FROM `tabSalary Detail` as detail
# 		INNER JOIN `tabSalary Slip` as salary_slip
# 		ON detail.parent = salary_slip.name
# 		WHERE
# 			salary_slip.employee = %(employee)s
# 			AND detail.parentfield = 'earnings'
# 			AND YEAR(salary_slip.posting_date) >= %(effective_year)s
# 			AND YEAR(salary_slip.posting_date) <= %(effective_year)s
# 			AND salary_slip.name != %(docname)s
# 			AND detail.is_13th_month_pay_applicable = 1
# 			AND salary_slip.docstatus = 1""",
# 			{'employee': salary_slip.employee, 'effective_year': effective_year, 'docname': salary_slip.name}
# 	)

# 	print(gross_pay)
# 	return (gross_pay[0][0] if gross_pay else 0) / 12