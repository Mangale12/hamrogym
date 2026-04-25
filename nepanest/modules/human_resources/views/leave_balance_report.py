from core.views.reports import BaseReportView

from nepanest.modules.leave.forms import LeaveBalanceReportForm
from nepanest.modules.leave.services import build_leave_balance_summary_report


class LeaveBalanceSummaryReportView(BaseReportView):
    form_class = LeaveBalanceReportForm
    report_title = "Leave Balance Summary Report"
    export_filename = "leave_balance_summary"
    report_table_id = "leaveBalanceSummaryReportTable"
    print_settings = {
        "page_size": "A4",
        "orientation": "portrait",
        "margin": "12mm",
        "summary_columns": 3,
    }
    table_columns = [
        ("employee_id", "Employee ID"),
        ("employee_name", "Employee"),
        ("leave_type", "Leave Type"),
        ("year", "Year"),
        ("opening_balance", "Opening"),
        ("accrued", "Accrued"),
        ("used", "Used"),
        ("encashed", "Encashed"),
        ("balance", "Balance"),
        ("updated_at", "Updated At"),
    ]
    filter_blocks = [
        {
            "title": "Primary Filters",
            "fields": [
                {"name": "employee", "label": "Employee", "col": "col-md-4"},
                {"name": "leave_type", "label": "Leave Type", "col": "col-md-4"},
                {"name": "year", "label": "Year", "col": "col-md-4"},
            ],
        },
        {
            "hidden": True,
            "fields": [
                {"name": "generate", "type": "hidden", "value": "1"},
            ],
        },
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

    def get_report_subtitle(self, report_data=None):
        if report_data and report_data.get("selected_year"):
            return f"Leave balances for {report_data['selected_year']}"
        return "Filter by employee, leave type, and year."

    def get_summary_cards(self, report_data):
        summary = (report_data or {}).get("summary", {})
        return [
            {"label": "Records", "value": summary.get("records", 0)},
            {"label": "Opening", "value": summary.get("total_opening", 0)},
            {"label": "Accrued", "value": summary.get("total_accrued", 0)},
            {"label": "Used", "value": summary.get("total_used", 0)},
            {"label": "Encashed", "value": summary.get("total_encashed", 0)},
            {"label": "Balance", "value": summary.get("total_balance", 0)},
        ]

    def build_report_data(self, cleaned_data):
        return build_leave_balance_summary_report(
            employee=cleaned_data.get("employee"),
            leave_type=cleaned_data.get("leave_type"),
            year=cleaned_data.get("year"),
        )
