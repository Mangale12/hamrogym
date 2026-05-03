from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.daily_attendance_summary_data_table import (
    DAILY_ATTENDANCE_SUMMARY_COLUMNS,
    DailyAttendanceSummaryDataTableView,
)
from ...forms.daily_attendance_summary_form import DailyAttendanceSummaryForm
from ...models import DailyAttendanceSummary


register_entity(
    EntityConfig(
        name="daily_attendance_summary",
        url_path="daily-attendance-summaries",
        verbose_name="Daily Attendance Summary",
        model=DailyAttendanceSummary,
        form_class=DailyAttendanceSummaryForm,
        datatable_view=DailyAttendanceSummaryDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 6, "url_name": "member_select"},
            {"name": "date", "label": "Date", "type": "date", "required": True, "col": 3, "calendar_switchable": False, "calendar_mode": "ad"},
            {"name": "total_checkins", "label": "Total Check-ins", "type": "number", "required": True, "col": 3, "min": 0, "step": 1},
            {"name": "total_duration", "label": "Total Duration (Mins)", "type": "number", "required": True, "col": 4, "min": 0, "step": 1},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in DAILY_ATTENDANCE_SUMMARY_COLUMNS
            if key != "id"
        ],
        select_search_fields=["member__member_code", "member__party__name"],
        select_label_func=lambda obj: f"{obj.member.member_code} - {obj.date}",
    )
)
