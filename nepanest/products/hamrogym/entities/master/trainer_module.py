from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.trainer_data_table import (
    MEMBER_PT_PACKAGE_COLUMNS,
    PT_SESSION_CANCELLATION_COLUMNS,
    PT_SESSION_COLUMNS,
    PT_SESSION_LOG_COLUMNS,
    PT_SESSION_PACKAGE_COLUMNS,
    PT_SESSION_RESCHEDULE_COLUMNS,
    TRAINER_AVAILABILITY_COLUMNS,
    TRAINER_COLUMNS,
    TRAINER_PERFORMANCE_COLUMNS,
    TRAINER_TIME_OFF_COLUMNS,
    MemberPTPackageDataTableView,
    PTSessionCancellationDataTableView,
    PTSessionDataTableView,
    PTSessionLogDataTableView,
    PTSessionPackageDataTableView,
    PTSessionRescheduleDataTableView,
    TrainerAvailabilityDataTableView,
    TrainerDataTableView,
    TrainerPerformanceDataTableView,
    TrainerTimeOffDataTableView,
)
from ...forms.trainer_forms import (
    MemberPTPackageForm,
    PTSessionCancellationForm,
    PTSessionForm,
    PTSessionLogForm,
    PTSessionPackageForm,
    PTSessionRescheduleForm,
    TrainerAvailabilityForm,
    TrainerForm,
    TrainerPerformanceForm,
    TrainerTimeOffForm,
)
from ...models import (
    MemberPTPackage,
    PTSession,
    PTSessionCancellation,
    PTSessionLog,
    PTSessionPackage,
    PTSessionReschedule,
    Trainer,
    TrainerAvailability,
    TrainerPerformance,
    TrainerTimeOff,
)


def _title(key, mapping=None):
    return (mapping or {}).get(key, key.replace("_", " ").title())


register_entity(
    EntityConfig(
        name="trainer",
        url_path="trainers",
        verbose_name="Trainer",
        model=Trainer,
        form_class=TrainerForm,
        datatable_view=TrainerDataTableView,
        fields=[
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {
                "name": "specialization",
                "label": "Specialization",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": [("", "Select Specialization"), *Trainer.Specialization.choices],
            },
            {"name": "experience_years", "label": "Experience Years", "type": "number", "required": True, "col": 3, "min": 0, "step": 1},
            {"name": "max_sessions_per_day", "label": "Max Sessions Per Day", "type": "number", "required": True, "col": 3, "min": 0, "step": 1},
            {"name": "rating", "label": "Rating", "type": "number", "required": False, "col": 3, "min": 0, "max": 5, "step": 0.01},
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 3,
                "options": [("", "Select Status"), *Trainer.Status.choices],
            },
            {"name": "certification_details", "label": "Certification Details", "type": "textarea", "required": False, "col": 12},
            {"name": "notes", "label": "Notes", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key, {"employee_id": "Employee ID", "employee_name": "Employee Name"})}
            for key, _accessor in TRAINER_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": Trainer.Status.ACTIVE, "experience_years": 0, "max_sessions_per_day": 0},
        select_search_fields=["employee__employee_id", "employee__user__first_name", "employee__user__last_name", "specialization"],
        select_label_func=lambda obj: f"{obj.employee.employee_id} - {obj.employee.full_name}",
    )
)

register_entity(
    EntityConfig(
        name="trainer_availability",
        url_path="trainer-availabilities",
        verbose_name="Trainer Availability",
        model=TrainerAvailability,
        form_class=TrainerAvailabilityForm,
        datatable_view=TrainerAvailabilityDataTableView,
        fields=[
            {"name": "trainer", "label": "Trainer", "type": "select", "required": True, "col": 4, "url_name": "trainer_select"},
            {
                "name": "day_of_week",
                "label": "Day Of Week",
                "type": "static_select",
                "required": True,
                "col": 3,
                "options": [("", "Select Day"), *TrainerAvailability.DayOfWeek.choices],
            },
            {"name": "start_time", "label": "Start Time", "type": "time", "required": True, "col": 2},
            {"name": "end_time", "label": "End Time", "type": "time", "required": True, "col": 2},
            {"name": "is_available", "label": "Is Available", "type": "checkbox", "required": False, "col": 1},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {
                "name": key,
                "title": _title(key, {"trainer_name": "Trainer Name"}),
                **({"render": "function(data){return data ? 'Yes' : 'No';}"} if key == "is_available" else {}),
            }
            for key, _accessor in TRAINER_AVAILABILITY_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_available": True},
        select_search_fields=["trainer__employee__employee_id", "trainer__employee__user__first_name", "day_of_week"],
        select_label_func=lambda obj: f"{obj.trainer.employee.employee_id} - {obj.get_day_of_week_display()} {obj.start_time:%H:%M}",
    )
)

register_entity(
    EntityConfig(
        name="trainer_time_off",
        url_path="trainer-time-offs",
        verbose_name="Trainer Time Off",
        model=TrainerTimeOff,
        form_class=TrainerTimeOffForm,
        datatable_view=TrainerTimeOffDataTableView,
        fields=[
            {"name": "trainer", "label": "Trainer", "type": "select", "required": True, "col": 4, "url_name": "trainer_select"},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": True, "col": 4},
            {"name": "end_date", "label": "End Date", "type": "date", "required": True, "col": 4},
            {"name": "reason", "label": "Reason", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key, {"trainer_name": "Trainer Name"})}
            for key, _accessor in TRAINER_TIME_OFF_COLUMNS
            if key != "id"
        ],
        select_search_fields=["trainer__employee__employee_id", "trainer__employee__user__first_name", "reason"],
        select_label_func=lambda obj: f"{obj.trainer.employee.employee_id} - {obj.start_date} to {obj.end_date}",
    )
)

register_entity(
    EntityConfig(
        name="pt_session_package",
        url_path="pt-session-packages",
        verbose_name="PT Session Package",
        model=PTSessionPackage,
        form_class=PTSessionPackageForm,
        datatable_view=PTSessionPackageDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "total_sessions", "label": "Total Sessions", "type": "number", "required": True, "col": 2, "min": 1, "step": 1},
            {"name": "validity_days", "label": "Validity Days", "type": "number", "required": True, "col": 2, "min": 1, "step": 1},
            {"name": "session_duration_minutes", "label": "Session Duration Minutes", "type": "number", "required": True, "col": 2, "min": 1, "step": 1},
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 4,
                "options": [("", "Select Status"), *PTSessionPackage.Status.choices],
            },
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key, {"session_duration_minutes": "Session Duration (Minutes)"})}
            for key, _accessor in PT_SESSION_PACKAGE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": PTSessionPackage.Status.ACTIVE},
        select_search_fields=["name", "description", "status", "branch__name"],
        select_label_func=lambda obj: f"{obj.name} ({obj.total_sessions} sessions)",
    )
)

register_entity(
    EntityConfig(
        name="member_pt_package",
        url_path="member-pt-packages",
        verbose_name="Member PT Package",
        model=MemberPTPackage,
        form_class=MemberPTPackageForm,
        datatable_view=MemberPTPackageDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "pt_session_package", "label": "PT Session Package", "type": "select", "required": True, "col": 4, "url_name": "pt_session_package_select"},
            {"name": "total_sessions", "label": "Total Sessions", "type": "number", "required": True, "col": 2, "min": 1, "step": 1},
            {"name": "used_sessions", "label": "Used Sessions", "type": "number", "required": False, "col": 2, "min": 0, "step": 1},
            {"name": "remaining_sessions", "label": "Remaining Sessions", "type": "number", "required": False, "col": 3, "min": 0, "step": 1},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": True, "col": 3},
            {"name": "end_date", "label": "End Date", "type": "date", "required": True, "col": 3},
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 3,
                "options": [("", "Select Status"), *MemberPTPackage.Status.choices],
            },
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key, {"pt_session_package": "PT Session Package", "member_name": "Member Name"})}
            for key, _accessor in MEMBER_PT_PACKAGE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": MemberPTPackage.Status.ACTIVE, "used_sessions": 0, "remaining_sessions": 0},
        select_search_fields=["member__member_code", "member__party__name", "pt_session_package__name"],
        select_label_func=lambda obj: f"{obj.member.member_code} - {obj.pt_session_package.name}",
    )
)

register_entity(
    EntityConfig(
        name="pt_session",
        url_path="pt-sessions",
        verbose_name="PT Session",
        model=PTSession,
        form_class=PTSessionForm,
        datatable_view=PTSessionDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "trainer", "label": "Trainer", "type": "select", "required": True, "col": 4, "url_name": "trainer_select"},
            {"name": "member_pt_package", "label": "Member PT Package", "type": "select", "required": True, "col": 4, "url_name": "member_pt_package_select"},
            {"name": "session_date", "label": "Session Date", "type": "date", "required": True, "col": 3},
            {"name": "start_time", "label": "Start Time", "type": "time", "required": True, "col": 3},
            {"name": "end_time", "label": "End Time", "type": "time", "required": True, "col": 3},
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 3,
                "options": [("", "Select Status"), *PTSession.Status.choices],
            },
            {"name": "checkin", "label": "Member Checkin", "type": "select", "required": False, "col": 6, "url_name": "member_checkin_select"},
            {"name": "notes", "label": "Notes", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {
                "name": key,
                "title": _title(key, {"trainer_name": "Trainer Name", "member_name": "Member Name", "package": "PT Package"}),
            }
            for key, _accessor in PT_SESSION_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": PTSession.Status.SCHEDULED},
        select_search_fields=["member__member_code", "trainer__employee__employee_id", "member_pt_package__pt_session_package__name"],
        select_label_func=lambda obj: f"{obj.member.member_code} - {obj.session_date} {obj.start_time:%H:%M}",
    )
)

register_entity(
    EntityConfig(
        name="pt_session_log",
        url_path="pt-session-logs",
        verbose_name="PT Session Log",
        model=PTSessionLog,
        form_class=PTSessionLogForm,
        datatable_view=PTSessionLogDataTableView,
        fields=[
            {"name": "pt_session", "label": "PT Session", "type": "select", "required": True, "col": 6, "url_name": "pt_session_select"},
            {"name": "actual_start_time", "label": "Actual Start Time", "type": "datetime-local", "required": True, "col": 3},
            {"name": "actual_end_time", "label": "Actual End Time", "type": "datetime-local", "required": True, "col": 3},
            {"name": "duration_minutes", "label": "Duration Minutes", "type": "number", "required": False, "col": 3, "min": 0, "step": 1},
            {"name": "trainer_notes", "label": "Trainer Notes", "type": "textarea", "required": False, "col": 12},
            {"name": "member_feedback", "label": "Member Feedback", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key, {"pt_session": "PT Session"})}
            for key, _accessor in PT_SESSION_LOG_COLUMNS
            if key != "id"
        ],
        select_search_fields=["pt_session__member__member_code", "pt_session__trainer__employee__employee_id"],
        select_label_func=lambda obj: f"{obj.pt_session.member.member_code} - {obj.actual_start_time:%Y-%m-%d %H:%M}",
    )
)

register_entity(
    EntityConfig(
        name="pt_session_reschedule",
        url_path="pt-session-reschedules",
        verbose_name="PT Session Reschedule",
        model=PTSessionReschedule,
        form_class=PTSessionRescheduleForm,
        datatable_view=PTSessionRescheduleDataTableView,
        fields=[
            {"name": "pt_session", "label": "PT Session", "type": "select", "required": True, "col": 6, "url_name": "pt_session_select"},
            {"name": "old_date", "label": "Old Date", "type": "date", "required": True, "col": 3},
            {"name": "old_start_time", "label": "Old Start Time", "type": "time", "required": True, "col": 3},
            {"name": "new_date", "label": "New Date", "type": "date", "required": True, "col": 3},
            {"name": "new_start_time", "label": "New Start Time", "type": "time", "required": True, "col": 3},
            {"name": "reason", "label": "Reason", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key, {"pt_session": "PT Session"})}
            for key, _accessor in PT_SESSION_RESCHEDULE_COLUMNS
            if key != "id"
        ],
        select_search_fields=["pt_session__member__member_code", "pt_session__trainer__employee__employee_id", "reason"],
        select_label_func=lambda obj: f"{obj.pt_session.member.member_code} - {obj.new_date} {obj.new_start_time:%H:%M}",
    )
)

register_entity(
    EntityConfig(
        name="pt_session_cancellation",
        url_path="pt-session-cancellations",
        verbose_name="PT Session Cancellation",
        model=PTSessionCancellation,
        form_class=PTSessionCancellationForm,
        datatable_view=PTSessionCancellationDataTableView,
        fields=[
            {"name": "pt_session", "label": "PT Session", "type": "select", "required": True, "col": 6, "url_name": "pt_session_select"},
            {
                "name": "cancelled_by",
                "label": "Cancelled By",
                "type": "static_select",
                "required": True,
                "col": 3,
                "options": [("", "Select Source"), *PTSessionCancellation.CancelledBy.choices],
            },
            {"name": "cancellation_time", "label": "Cancellation Time", "type": "datetime-local", "required": True, "col": 3},
            {"name": "reason", "label": "Reason", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key, {"pt_session": "PT Session"})}
            for key, _accessor in PT_SESSION_CANCELLATION_COLUMNS
            if key != "id"
        ],
        select_search_fields=["pt_session__member__member_code", "pt_session__trainer__employee__employee_id", "cancelled_by"],
        select_label_func=lambda obj: f"{obj.pt_session.member.member_code} - {obj.cancelled_by}",
    )
)

register_entity(
    EntityConfig(
        name="trainer_performance",
        url_path="trainer-performances",
        verbose_name="Trainer Performance",
        model=TrainerPerformance,
        form_class=TrainerPerformanceForm,
        datatable_view=TrainerPerformanceDataTableView,
        fields=[
            {"name": "trainer", "label": "Trainer", "type": "select", "required": True, "col": 4, "url_name": "trainer_select"},
            {"name": "date", "label": "Date", "type": "date", "required": True, "col": 2},
            {"name": "total_sessions", "label": "Total Sessions", "type": "number", "required": True, "col": 2, "min": 0, "step": 1},
            {"name": "completed_sessions", "label": "Completed Sessions", "type": "number", "required": True, "col": 2, "min": 0, "step": 1},
            {"name": "cancelled_sessions", "label": "Cancelled Sessions", "type": "number", "required": True, "col": 2, "min": 0, "step": 1},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key, {"trainer_name": "Trainer Name"})}
            for key, _accessor in TRAINER_PERFORMANCE_COLUMNS
            if key != "id"
        ],
        reset_defaults={"total_sessions": 0, "completed_sessions": 0, "cancelled_sessions": 0},
        select_search_fields=["trainer__employee__employee_id", "trainer__employee__user__first_name"],
        select_label_func=lambda obj: f"{obj.trainer.employee.employee_id} - {obj.date}",
    )
)
