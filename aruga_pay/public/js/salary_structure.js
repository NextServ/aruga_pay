// aruga_pay/public/js/salary_structure.js
// Extends v15 Salary Structure form to copy custom Salary Component fields
// into earnings/deductions rows immediately upon component selection.

frappe.ui.form.on("Salary Detail", {
	salary_component(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.salary_component) return;

		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Salary Component",
				name: row.salary_component,
			},
			callback(r) {
				if (!r.message) return;
				const c = r.message;

				// Custom fields — the ones v15 doesn't copy automatically
				frappe.model.set_value(cdt, cdn, "formula_based_on_attendance", c.formula_based_on_attendance);
				frappe.model.set_value(cdt, cdn, "formula_effectivity", c.formula_effectivity);
				frappe.model.set_value(cdt, cdn, "formula_prorated", c.formula_prorated);
				frappe.model.set_value(cdt, cdn, "statistical_component", c.statistical_component);
				frappe.model.set_value(cdt, cdn, "is_basic_pay", c.is_basic_pay);
				frappe.model.set_value(cdt, cdn, "do_not_include_in_accounts", c.do_not_include_in_accounts);

				frm.refresh_field("earnings");
				frm.refresh_field("deductions");
			},
		});
	},
});