from core.views.reports import BaseReportView

from ..forms.attendance_form import AttendanceHistoryReportForm
from ..services import build_employee_attendance_history_report


class AttendanceHistoryReportView(BaseReportView):
    form_class = AttendanceHistoryReportForm
    report_title = "Attendance History Report"
    export_filename = "employee_attendance_history"
    report_table_id = "attendanceHistoryReportTable"
    print_settings = {
        "page_size": "A4",
        "orientation": "landscape",
        "margin": "2mm",
        "summary_columns": 4,
    }
    table_columns = [
        ("employee_id", "Employee ID"),
        ("employee_name", "Employee"),
        ("date", "Date"),
        ("shift_name", "Shift"),
        ("check_in_time", "Check In"),
        ("check_out_time", "Check Out"),
        ("work_hours", "Work Hours"),
        ("status", "Status"),
        ("is_late", "Late"),
        ("is_half_day", "Half Day"),
        ("remarks", "Remarks"),
    ]
    print_columns = [
        ("employee_id", "Employee ID"),
        ("employee_name", "Employee"),
        ("date", "Date"),
        ("check_in_time", "Check In"),
        ("check_out_time", "Check Out"),
        ("work_hours", "Hours"),
        ("status", "Status"),
    ]
    filter_blocks = [
        {
            "title": "Primary Filters",
            "fields": [
                {"name": "employee", "label": "Employee", "col": "col-md-4"},
                {"name": "date_from", "label": "Date From", "col": "col-md-3", "calendar_switchable": True},
                {"name": "date_to", "label": "Date To", "col": "col-md-3", "calendar_switchable": True},
                {"name": "status", "label": "Status", "col": "col-md-2"},
            ]
        },
        {
            "hidden": True,
            "fields": [
                {"name": "generate", "type": "hidden", "value": "1"},
            ],
        }
    ]
    filter_actions = [
        {
            "label": "View Report",
            "name": "generate",
            "value": "1",
            "class_name": "btn btn-primary",
            "icon_class": "fas fa-chart-line",
        },
    ]
    def get_table_columns(self):
        return list(self.table_columns)

    def get_screen_columns(self):
        return list(self.table_columns)

    def get_print_columns(self):
        return list(self.print_columns)

    def get_export_columns(self):
        return list(self.table_columns)

    def get_report_subtitle(self, report_data=None):
        if report_data:
            return f"{report_data['date_from']} to {report_data['date_to']}"
        return "Filter by employee, date range, and status."

    def get_summary_cards(self, report_data):
        summary = (report_data or {}).get("summary", {})
        return [
            {"label": "Records", "value": summary.get("records", 0)},
            {"label": "Present", "value": summary.get("present", 0)},
            {"label": "Late Status", "value": summary.get("late", 0)},
            {"label": "Absent", "value": summary.get("absent", 0)},
            {"label": "Half Day Status", "value": summary.get("half_day_status", 0)},
            {"label": "Work Hours", "value": summary.get("total_work_hours", 0)},
        ]

    def build_report_data(self, cleaned_data):
        return build_employee_attendance_history_report(
            employee=cleaned_data.get("employee"),
            date_from=cleaned_data["date_from"],
            date_to=cleaned_data["date_to"],
            status=cleaned_data.get("status") or "",
        )
