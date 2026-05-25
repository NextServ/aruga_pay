frappe.listview_settings['Attendance'] = {
    refresh: function(listview) {
        // Safe elements wipeout loop
        if (listview.page && listview.page.inner_buttons) {
            listview.page.remove_inner_button(__('Generate Test Attendance'), __('Test Utilities'));
            listview.page.remove_inner_button(__('Clear Dummy Attendance'), __('Test Utilities'));
        }

        listview.page.add_inner_button(__('Generate 2-Month Test Attendance'), function() {
            frappe.confirm(
                __('This will generate 2 months of synthetic Philippine testing attendance sheets for all active employees. Proceed?'),
                function() {
                    frappe.call({
                        method: "aruga_pay.attendance_utils.generate_dummy_attendance_data",
                        callback: function(r) {
                            if (!r.exc) {
                                frappe.show_alert({
                                    message: __('Test attendance matrix generated successfully.'),
                                    indicator: 'green'
                                });
                                listview.refresh();
                            }
                        }
                    });
                }
            );
        }, __('Test Utilities'));

        listview.page.add_inner_button(__('Clear Dummy Attendance'), function() {
            frappe.confirm(
                __('Are you sure you want to permanently clear attendance log records within the past 60 days?'),
                function() {
                    frappe.call({
                        method: "aruga_pay.attendance_utils.clear_dummy_attendance_data",
                        callback: function(r) {
                            if (!r.exc) {
                                frappe.show_alert({
                                    message: __('Testing rows have been completely removed.'),
                                    indicator: 'orange'
                                });
                                listview.refresh();
                            }
                        }
                    });
                }
            );
        }, __('Test Utilities'));
    }
};