import random
import frappe
from frappe.utils import add_days, getdate, nowdate, flt
from frappe import _

def ensure_aruga_test_employee_exists(company):
    """Checks if ARUGA TEST exists; if not, automatically generates the Employee profile."""
    existing_emp = frappe.get_all(
        "Employee",
        filters={"employee_name": "ARUGA TEST"},
        fields=["name", "employee_name"]
    )
    
    if existing_emp:
        return existing_emp[0]

    # Calculate timestamps relative to the current year
    current_year = getdate(nowdate()).year
    
    # Date of birth set to 10 years before the current year
    calculated_dob = f"{current_year - 10}-01-01"
    
    # Date of joining set to 1 year before the current year
    calculated_doj = f"{current_year - 1}-01-01"

    # Automatically generate the profile document if missing
    new_emp = frappe.get_doc({
        "doctype": "Employee",
        "employee_name": "ARUGA TEST",
        "first_name": "ARUGA",
        "last_name": "TEST",
        "gender": "Male",
        "status": "Active",
        "company": company,
        "date_of_birth": calculated_dob,
        "date_of_joining": calculated_doj,
        "prefer_to_be_called_by": "ARUGA TEST"
    })
    
    # Insert safely bypassing standard validation checks
    new_emp.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return new_emp

@frappe.whitelist()
def generate_dummy_attendance_data():
    """Automatically ensures the test profile exists and generates 2 months of localized test logs."""
    company = frappe.defaults.get_user_default("company") or ""
    if not company:
        companies = frappe.get_all("Company", fields=["name"])
        if not companies:
            frappe.throw(_("Please create a Company record before generating attendance data."))
        company = companies[0].name

    # Step 1: Auto-generate or capture the specific testing profile
    emp = ensure_aruga_test_employee_exists(company)

    today_date = getdate(nowdate())
    start_date = add_days(today_date, -60)
    created_count = 0

    calendar_months = {}
    for day_offset in range(60):
        d = add_days(start_date, day_offset)
        m_key = d.strftime("%Y-%m")
        calendar_months.setdefault(m_key, []).append(d)

    for month_str, date_list in calendar_months.items():
        weekdays = [d for d in date_list if d.weekday() not in [5, 6]]
        if len(weekdays) < 6:
            weekdays = list(date_list)

        random.shuffle(weekdays)
        allocated_rest_days = weekdays[0:2]
        allocated_special_holidays = weekdays[2:4]
        allocated_legal_holidays = weekdays[4:6]
        standard_work_days = weekdays[6:]

        for current_date in date_list:
            if frappe.db.exists("Attendance", {"employee": emp.name, "attendance_date": current_date}):
                continue

            status = "Present"
            rest_day = 0
            special_holiday = 0
            legal_holiday = 0
            working_hours = 0.0
            expected_working_hours = 8.0
            leave = 0.0
            paid_leave = 0.0
            overtime = 0.0
            undertime = 0.0
            night_differential = 0.0
            night_differential_overtime = 0.0
            late_in = 0.0

            if current_date.weekday() in [5, 6]:
                status = "Absent"
                rest_day = 1
                expected_working_hours = 0.0
            elif current_date in allocated_rest_days:
                status = "Absent"
                rest_day = 1
                expected_working_hours = 0.0
            elif current_date in allocated_special_holidays:
                status = "Present"
                special_holiday = 1
                working_hours = 8.0
                overtime = 2.0
            elif current_date in allocated_legal_holidays:
                status = "Present"
                legal_holiday = 1
                working_hours = 8.0
                night_differential = 3.0
            elif current_date in standard_work_days:
                day_scenario = random.choice(["Normal", "Normal", "Late", "Undertime", "Leave", "NightShift"])
                
                if day_scenario == "Normal":
                    working_hours = 8.0
                elif day_scenario == "Late":
                    working_hours = 7.5
                    late_in = 0.5
                elif day_scenario == "Undertime":
                    working_hours = 6.0
                    undertime = 2.0
                elif day_scenario == "Leave":
                    status = "On Leave"
                    working_hours = 0.0
                    if random.choice([True, False]):
                        paid_leave = 1.0
                    else:
                        leave = 1.0
                elif day_scenario == "NightShift":
                    working_hours = 8.0
                    night_differential = 4.0
                    overtime = 1.5
                    night_differential_overtime = 1.5

            attendance_doc = frappe.get_doc({
                "doctype": "Attendance",
                "employee": emp.name,
                "employee_name": emp.employee_name,
                "attendance_date": current_date,
                "status": status,
                "company": company,
                "rest_day": rest_day,
                "special_holiday": special_holiday,
                "legal_holiday": legal_holiday,
                "working_hours": flt(working_hours, 2),
                "expected_working_hours": flt(expected_working_hours, 2),
                "leave": flt(leave, 2),
                "paid_leave": flt(paid_leave, 2),
                "overtime": flt(overtime, 2),
                "undertime": flt(undertime, 2),
                "night_differential": flt(night_differential, 2),
                "night_differential_overtime": flt(night_differential_overtime, 2),
                "late_in": flt(late_in, 2)
            })
            attendance_doc.insert(ignore_permissions=True)
            attendance_doc.submit()
            created_count += 1

    frappe.db.commit()
    return {"message": f"Successfully setup profile and generated {created_count} records for {emp.employee_name}."}


@frappe.whitelist()
def clear_dummy_attendance_data():
    """Purges past 60 days logs for the ARUGA TEST profile."""
    target_employee = frappe.get_all(
        "Employee",
        filters={"employee_name": "ARUGA TEST"},
        fields=["name"]
    )
    
    if not target_employee:
        return {"message": "No profile found matching ARUGA TEST to clear."}

    emp_id = target_employee[0].name
    today_date = getdate(nowdate())
    start_date = add_days(today_date, -61)

    dummy_records = frappe.get_all(
        "Attendance",
        filters={
            "employee": emp_id,
            "attendance_date": [">=", start_date],
            "docstatus": 1
        },
        fields=["name"]
    )
    
    purged_count = 0
    for record in dummy_records:
        attendance_doc = frappe.get_doc("Attendance", record.name)
        attendance_doc.cancel()
        attendance_doc.delete()
        purged_count += 1
        
    frappe.db.commit()
    return {"message": f"Successfully cleared {purged_count} records for ARUGA TEST."}