# aruga_pay/aruga_payroll/overrides/salary_structure.py

from frappe.utils import cstr
from hrms.payroll.doctype.salary_structure.salary_structure import SalaryStructure


# Custom Salary Component fields to sync into Salary Structure Detail rows.
# Add more here if you create additional custom fields on Salary Component.
CUSTOM_OVERWRITTEN_FIELDS = [
    "formula_based_on_attendance",
    "formula_effectivity",
    "formula_prorated",
    "statistical_component",
    "is_basic_pay",
    "do_not_include_in_accounts",
]


class CustomSalaryStructure(SalaryStructure):
    """
    Extends HRMS SalaryStructure to also sync custom Salary Component fields
    into earnings/deductions rows when the structure is saved.

    The base set_missing_values() only copies its own hardcoded fields:
        overwritten_fields         = [depends_on_payment_days, variable_based_on_taxable_salary, ...]
        overwritten_fields_if_missing = [amount_based_on_formula, formula, amount]

    Our custom fields are not in those lists, so we extend the method here.
    """

    def set_missing_values(self):
        import frappe

        # Run all standard HRMS field-copy logic first
        super().set_missing_values()

        # Then sync our custom fields using the same "always overwrite" logic
        for table in ("earnings", "deductions"):
            for row in self.get(table):
                if not row.salary_component:
                    continue

                component_data = frappe.db.get_value(
                    "Salary Component",
                    cstr(row.salary_component),
                    CUSTOM_OVERWRITTEN_FIELDS,
                    as_dict=True,
                    cache=True,
                )

                if not component_data:
                    continue

                for fieldname in CUSTOM_OVERWRITTEN_FIELDS:
                    value = component_data.get(fieldname)
                    if row.get(fieldname) != value:
                        row.set(fieldname, value)