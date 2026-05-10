// Salary Structure Assignment — auto-compute rate breakdown
//
// Mirrors the server-side calculate_salary_structure_rates() in salary_slip.py exactly.
// Purely informational — does NOT write to the DB and does NOT affect salary slip computation.
//
// Display:
//   1. Always shown at the top of the form via frm.set_intro()
//   2. If a custom field named "computed_rates_display" (HTML or Long Text) exists,
//      it is populated as well so the breakdown can be embedded in the form layout.
//
// Triggers on changes to: base, rate_type, daily_hours, days_of_work_per_year

frappe.ui.form.on("Salary Structure Assignment", {
	refresh: function (frm) {
		render_computed_rates(frm);
	},
	base: function (frm) {
		render_computed_rates(frm);
	},
	rate_type: function (frm) {
		render_computed_rates(frm);
	},
	daily_hours: function (frm) {
		render_computed_rates(frm);
	},
	days_of_work_per_year: function (frm) {
		render_computed_rates(frm);
	},
});

function compute_rates(frm) {
	const base = flt(frm.doc.base) || 0;
	const rate_type = frm.doc.rate_type;
	const daily_hours = flt(frm.doc.daily_hours) || 8;
	const days_per_year = cint(frm.doc.days_of_work_per_year) || 0;

	let hourly_rate = 0,
		daily_rate = 0,
		monthly_rate = 0,
		yearly_rate = 0;

	if (rate_type === "Hourly") {
		hourly_rate = base;
		daily_rate = base * daily_hours;
		monthly_rate = days_per_year ? (base * daily_hours * days_per_year) / 12 : 0;
		yearly_rate = days_per_year ? base * daily_hours * days_per_year : 0;
	} else if (rate_type === "Daily") {
		hourly_rate = daily_hours ? base / daily_hours : 0;
		daily_rate = base;
		monthly_rate = days_per_year ? (base * days_per_year) / 12 : 0;
		yearly_rate = days_per_year ? base * days_per_year : 0;
	} else if (rate_type === "Monthly") {
		hourly_rate = days_per_year && daily_hours ? (base * 12) / days_per_year / daily_hours : 0;
		daily_rate = days_per_year ? (base * 12) / days_per_year : 0;
		monthly_rate = base;
		yearly_rate = base * 12;
	} else if (rate_type === "Yearly") {
		hourly_rate = days_per_year && daily_hours ? base / days_per_year / daily_hours : 0;
		daily_rate = days_per_year ? base / days_per_year : 0;
		monthly_rate = base / 12;
		yearly_rate = base;
	}

	return {
		base: base,
		rate_type: rate_type,
		daily_hours: daily_hours,
		days_per_year: days_per_year,
		hourly_rate: hourly_rate,
		daily_rate: daily_rate,
		monthly_rate: monthly_rate,
		yearly_rate: yearly_rate,
	};
}

function format_php(amount) {
	if (!amount && amount !== 0) return "—";
	return (
		"₱" +
		flt(amount, 2)
			.toFixed(2)
			.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
	);
}

function build_rates_html(r) {
	if (!r.rate_type) {
		return `<div style="padding:10px 14px;color:#6b7280;font-size:12px;">
			Select a <b>Rate Type</b> to see the computed rate breakdown.
		</div>`;
	}

	const missing_inputs = [];
	if (!r.base) missing_inputs.push("Base");
	if (!r.daily_hours) missing_inputs.push("Daily Hours");
	if (!r.days_per_year) missing_inputs.push("Days of Work per Year");

	const warning =
		missing_inputs.length > 0
			? `<div style="background:#fef3c7;border-left:3px solid #f59e0b;padding:6px 10px;margin-bottom:8px;font-size:12px;color:#92400e;">
				⚠ Missing input(s): <b>${missing_inputs.join(", ")}</b> — some rates may show as 0.
			</div>`
			: "";

	// Highlight the rate that matches the selected rate_type
	const highlight_for = {
		Hourly: "hourly",
		Daily: "daily",
		Monthly: "monthly",
		Yearly: "yearly",
	}[r.rate_type];

	const cell_style = (key) => {
		const base = "padding:6px 10px;border-bottom:1px solid #e5e7eb;";
		return key === highlight_for
			? base + "background:#dbeafe;font-weight:600;color:#1e40af;"
			: base;
	};

	const label_style = (key) => {
		const base = "padding:6px 10px;border-bottom:1px solid #e5e7eb;color:#374151;";
		return key === highlight_for
			? base + "background:#dbeafe;font-weight:600;color:#1e40af;"
			: base;
	};

	return `
		<div style="margin-top:6px;">
			${warning}
			<div style="display:flex;gap:14px;font-size:12px;color:#6b7280;margin-bottom:8px;">
				<div><b>Rate Type:</b> ${r.rate_type}</div>
				<div><b>Base:</b> ${format_php(r.base)}</div>
				<div><b>Daily Hours:</b> ${r.daily_hours}</div>
				<div><b>Days/Year:</b> ${r.days_per_year}</div>
			</div>
			<table style="width:100%;border-collapse:collapse;font-size:13px;background:#ffffff;border:1px solid #e5e7eb;border-radius:4px;overflow:hidden;">
				<thead>
					<tr style="background:#1f4e79;color:#ffffff;">
						<th style="padding:6px 10px;text-align:left;font-weight:600;">Rate Breakdown</th>
						<th style="padding:6px 10px;text-align:right;font-weight:600;">Amount</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td style="${label_style("hourly")}">Hourly Rate</td>
						<td style="${cell_style("hourly")};text-align:right;font-family:monospace;">${format_php(r.hourly_rate)}</td>
					</tr>
					<tr>
						<td style="${label_style("daily")}">Daily Rate</td>
						<td style="${cell_style("daily")};text-align:right;font-family:monospace;">${format_php(r.daily_rate)}</td>
					</tr>
					<tr>
						<td style="${label_style("monthly")}">Monthly Rate</td>
						<td style="${cell_style("monthly")};text-align:right;font-family:monospace;">${format_php(r.monthly_rate)}</td>
					</tr>
					<tr>
						<td style="${label_style("yearly")}">Yearly Rate</td>
						<td style="${cell_style("yearly")};text-align:right;font-family:monospace;">${format_php(r.yearly_rate)}</td>
					</tr>
				</tbody>
			</table>
			<div style="margin-top:6px;font-size:11px;color:#9ca3af;font-style:italic;">
				Highlighted row = matches selected Rate Type. Computed client-side, mirrors server formula.
			</div>
		</div>
	`;
}

function render_computed_rates(frm) {
	const r = compute_rates(frm);
	const html = build_rates_html(r);

	// 1. Always show at top of form via intro
	frm.set_intro(html, "blue");

	// 2. If a custom field "computed_rates_display" exists, populate it too
	if (frm.fields_dict && frm.fields_dict.computed_rates_display) {
		const $wrapper = frm.fields_dict.computed_rates_display.$wrapper;
		if ($wrapper) {
			$wrapper.html(html);
		} else {
			frm.set_value("computed_rates_display", html);
		}
	}
}