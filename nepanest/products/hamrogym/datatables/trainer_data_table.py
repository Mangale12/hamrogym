from nepanest.common.helpers.helper import encode_date_for_display, encode_datetime_for_display

from core.datatables.views import BaseDataTableView

from ..models import (
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


TRAINER_COLUMNS = [
    ("id", "id"),
    ("employee_id", lambda obj: obj.employee.employee_id),
    ("employee_name", lambda obj: obj.employee.full_name),
    ("specialization", lambda obj: obj.get_specialization_display()),
    ("experience_years", "experience_years"),
    ("max_sessions_per_day", "max_sessions_per_day"),
    ("rating", "rating"),
    ("status", lambda obj: obj.get_status_display()),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class TrainerDataTableView(BaseDataTableView):
    model = Trainer
    columns = TRAINER_COLUMNS
    searchable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "specialization",
        "status",
        "notes",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "employee__employee_id",
        "employee__user__first_name",
        "specialization",
        "experience_years",
        "max_sessions_per_day",
        "rating",
        "status",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("employee__user", "branch")


TRAINER_AVAILABILITY_COLUMNS = [
    ("id", "id"),
    ("trainer", lambda obj: obj.trainer.employee.employee_id),
    ("trainer_name", lambda obj: obj.trainer.employee.full_name),
    ("day_of_week", lambda obj: obj.get_day_of_week_display()),
    ("start_time", lambda obj: obj.start_time.strftime("%H:%M:%S") if obj.start_time else ""),
    ("end_time", lambda obj: obj.end_time.strftime("%H:%M:%S") if obj.end_time else ""),
    ("is_available", "is_available"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class TrainerAvailabilityDataTableView(BaseDataTableView):
    model = TrainerAvailability
    columns = TRAINER_AVAILABILITY_COLUMNS
    searchable_columns = [
        "trainer__employee__employee_id",
        "trainer__employee__user__first_name",
        "trainer__employee__user__last_name",
        "day_of_week",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "trainer__employee__employee_id",
        "trainer__employee__user__first_name",
        "day_of_week",
        "start_time",
        "end_time",
        "is_available",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("trainer__employee__user", "branch")


TRAINER_TIME_OFF_COLUMNS = [
    ("id", "id"),
    ("trainer", lambda obj: obj.trainer.employee.employee_id),
    ("trainer_name", lambda obj: obj.trainer.employee.full_name),
    ("start_date", lambda obj, request: encode_date_for_display(obj.start_date, request)),
    ("end_date", lambda obj, request: encode_date_for_display(obj.end_date, request)),
    ("reason", "reason"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class TrainerTimeOffDataTableView(BaseDataTableView):
    model = TrainerTimeOff
    columns = TRAINER_TIME_OFF_COLUMNS
    searchable_columns = [
        "trainer__employee__employee_id",
        "trainer__employee__user__first_name",
        "trainer__employee__user__last_name",
        "reason",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "trainer__employee__employee_id",
        "trainer__employee__user__first_name",
        "start_date",
        "end_date",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("trainer__employee__user", "branch")


PT_SESSION_PACKAGE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("total_sessions", "total_sessions"),
    ("validity_days", "validity_days"),
    ("session_duration_minutes", "session_duration_minutes"),
    ("status", lambda obj: obj.get_status_display()),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class PTSessionPackageDataTableView(BaseDataTableView):
    model = PTSessionPackage
    columns = PT_SESSION_PACKAGE_COLUMNS
    searchable_columns = ["name", "description", "status", "branch__name", "remarks"]
    orderable_columns = [
        "name",
        "total_sessions",
        "validity_days",
        "session_duration_minutes",
        "status",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("branch")


MEMBER_PT_PACKAGE_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: obj.member.member_code),
    ("member_name", lambda obj: obj.member.party.display_name or obj.member.party.name),
    ("pt_session_package", lambda obj: obj.pt_session_package.name),
    ("total_sessions", "total_sessions"),
    ("used_sessions", "used_sessions"),
    ("remaining_sessions", "remaining_sessions"),
    ("start_date", lambda obj, request: encode_date_for_display(obj.start_date, request)),
    ("end_date", lambda obj, request: encode_date_for_display(obj.end_date, request)),
    ("status", lambda obj: obj.get_status_display()),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class MemberPTPackageDataTableView(BaseDataTableView):
    model = MemberPTPackage
    columns = MEMBER_PT_PACKAGE_COLUMNS
    searchable_columns = [
        "member__member_code",
        "member__party__name",
        "member__party__display_name",
        "pt_session_package__name",
        "status",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "member__member_code",
        "member__party__name",
        "pt_session_package__name",
        "total_sessions",
        "used_sessions",
        "remaining_sessions",
        "start_date",
        "end_date",
        "status",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("member__party", "pt_session_package", "branch")


PT_SESSION_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: obj.member.member_code),
    ("member_name", lambda obj: obj.member.party.display_name or obj.member.party.name),
    ("trainer", lambda obj: obj.trainer.employee.employee_id),
    ("trainer_name", lambda obj: obj.trainer.employee.full_name),
    ("package", lambda obj: obj.member_pt_package.pt_session_package.name),
    ("session_date", lambda obj, request: encode_date_for_display(obj.session_date, request)),
    ("start_time", lambda obj: obj.start_time.strftime("%H:%M:%S") if obj.start_time else ""),
    ("end_time", lambda obj: obj.end_time.strftime("%H:%M:%S") if obj.end_time else ""),
    ("status", lambda obj: obj.get_status_display()),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class PTSessionDataTableView(BaseDataTableView):
    model = PTSession
    columns = PT_SESSION_COLUMNS
    searchable_columns = [
        "member__member_code",
        "member__party__name",
        "member__party__display_name",
        "trainer__employee__employee_id",
        "trainer__employee__user__first_name",
        "trainer__employee__user__last_name",
        "member_pt_package__pt_session_package__name",
        "status",
        "notes",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "member__member_code",
        "member__party__name",
        "trainer__employee__employee_id",
        "trainer__employee__user__first_name",
        "member_pt_package__pt_session_package__name",
        "session_date",
        "start_time",
        "end_time",
        "status",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related(
            "member__party",
            "trainer__employee__user",
            "member_pt_package__pt_session_package",
            "branch",
        )


PT_SESSION_LOG_COLUMNS = [
    ("id", "id"),
    ("pt_session", lambda obj: f"{obj.pt_session.member.member_code} / {obj.pt_session.trainer.employee.employee_id}"),
    ("actual_start_time", lambda obj, request: encode_datetime_for_display(obj.actual_start_time, request)),
    ("actual_end_time", lambda obj, request: encode_datetime_for_display(obj.actual_end_time, request)),
    ("duration_minutes", "duration_minutes"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class PTSessionLogDataTableView(BaseDataTableView):
    model = PTSessionLog
    columns = PT_SESSION_LOG_COLUMNS
    searchable_columns = [
        "pt_session__member__member_code",
        "pt_session__member__party__name",
        "pt_session__trainer__employee__employee_id",
        "pt_session__trainer__employee__user__first_name",
        "trainer_notes",
        "member_feedback",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "pt_session__member__member_code",
        "actual_start_time",
        "actual_end_time",
        "duration_minutes",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("pt_session__member__party", "pt_session__trainer__employee", "branch")


PT_SESSION_RESCHEDULE_COLUMNS = [
    ("id", "id"),
    ("pt_session", lambda obj: f"{obj.pt_session.member.member_code} / {obj.pt_session.trainer.employee.employee_id}"),
    ("old_date", lambda obj, request: encode_date_for_display(obj.old_date, request)),
    ("old_start_time", lambda obj: obj.old_start_time.strftime("%H:%M:%S") if obj.old_start_time else ""),
    ("new_date", lambda obj, request: encode_date_for_display(obj.new_date, request)),
    ("new_start_time", lambda obj: obj.new_start_time.strftime("%H:%M:%S") if obj.new_start_time else ""),
    ("reason", "reason"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class PTSessionRescheduleDataTableView(BaseDataTableView):
    model = PTSessionReschedule
    columns = PT_SESSION_RESCHEDULE_COLUMNS
    searchable_columns = [
        "pt_session__member__member_code",
        "pt_session__member__party__name",
        "pt_session__trainer__employee__employee_id",
        "reason",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "pt_session__member__member_code",
        "old_date",
        "old_start_time",
        "new_date",
        "new_start_time",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("pt_session__member__party", "pt_session__trainer__employee", "branch")


PT_SESSION_CANCELLATION_COLUMNS = [
    ("id", "id"),
    ("pt_session", lambda obj: f"{obj.pt_session.member.member_code} / {obj.pt_session.trainer.employee.employee_id}"),
    ("cancelled_by", lambda obj: obj.get_cancelled_by_display()),
    ("reason", "reason"),
    ("cancellation_time", lambda obj, request: encode_datetime_for_display(obj.cancellation_time, request)),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class PTSessionCancellationDataTableView(BaseDataTableView):
    model = PTSessionCancellation
    columns = PT_SESSION_CANCELLATION_COLUMNS
    searchable_columns = [
        "pt_session__member__member_code",
        "pt_session__member__party__name",
        "pt_session__trainer__employee__employee_id",
        "cancelled_by",
        "reason",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "pt_session__member__member_code",
        "cancelled_by",
        "cancellation_time",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("pt_session__member__party", "pt_session__trainer__employee", "branch")


TRAINER_PERFORMANCE_COLUMNS = [
    ("id", "id"),
    ("trainer", lambda obj: obj.trainer.employee.employee_id),
    ("trainer_name", lambda obj: obj.trainer.employee.full_name),
    ("date", lambda obj, request: encode_date_for_display(obj.date, request)),
    ("total_sessions", "total_sessions"),
    ("completed_sessions", "completed_sessions"),
    ("cancelled_sessions", "cancelled_sessions"),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class TrainerPerformanceDataTableView(BaseDataTableView):
    model = TrainerPerformance
    columns = TRAINER_PERFORMANCE_COLUMNS
    searchable_columns = [
        "trainer__employee__employee_id",
        "trainer__employee__user__first_name",
        "trainer__employee__user__last_name",
        "branch__name",
        "remarks",
    ]
    orderable_columns = [
        "trainer__employee__employee_id",
        "trainer__employee__user__first_name",
        "date",
        "total_sessions",
        "completed_sessions",
        "cancelled_sessions",
        "branch__name",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("trainer__employee__user", "branch")
