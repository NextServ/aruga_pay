import frappe
from frappe.utils import flt

def patch_salary_slip():
    from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
    from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip

    original_pull_sal_struct = SalarySlip.pull_sal_struct

    def pull_sal_struct(self):
        # === TIMESHEET LOGIC (unchanged) ===
        if self.salary_slip_based_on_timesheet:
            self.salary_structure = self._salary_structure_doc.name
            self.hour_rate = self._salary_structure_doc.hour_rate
            self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
            self.total_working_hours = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
            wages_amount = self.hour_rate * self.total_working_hours
            self.add_earning_for_hourly_wages(self, self._salary_structure_doc.salary_component, wages_amount)

        # === GENERATE FROM SALARY STRUCTURE ===
        make_salary_slip(self._salary_structure_doc.name, self)

        # === COPY CUSTOM FIELDS FROM SALARY STRUCTURE DETAIL ===
        for table in ('earnings', 'deductions'):
            for row in self.get(table):
                # Find the corresponding row in Salary Structure
                ss_row = next(
                    (r for r in self._salary_structure_doc.get(table) if r.salary_component == row.salary_component), None
                )
                if ss_row:
                    custom_fields = [
                        'formula_based_on_attendance',
                        'formula_effectivity',
                        'formula_prorated',
                        'is_13th_month_pay_applicable',
                        'is_basic_pay',
                    ]
                    for field in custom_fields:
                        if hasattr(ss_row, field):
                            setattr(row, field, getattr(ss_row, field))

                    # Formula vs Amount
                    if ss_row.amount_based_on_formula:
                        row.formula = ss_row.formula
                        row.amount = 0
                    else:
                        row.amount = ss_row.amount
                        row.formula = ""

        # Refresh tables
        self.set('earnings', self.earnings)

    SalarySlip.pull_sal_struct = pull_sal_struct
    print("Custom SalarySlip patchs applied ✅")





