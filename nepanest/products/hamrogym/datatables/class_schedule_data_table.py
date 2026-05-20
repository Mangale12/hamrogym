from core.datatables.views import BaseDataTableView
from ..models import ClassSchedule


CLASS_SCHEDULE_COLUMNS = [
    ("id", "id"),
    ("gym_class", lambda obj: obj.gym_class.name),
    ("class_room", lambda obj: obj.class_room.name if obj.class_room_id else ""),
    ("trainer", lambda obj: obj.trainer.employee.employee_id if obj.trainer_id else ""),
    ("trainer_name", lambda obj: obj.trainer.employee.full_name if obj.trainer_id else ""),
    ("day_of_week", lambda obj: obj.get_day_of_week_display()),
    ("start_time", lambda obj: obj.start_time.strftime("%H:%M:%S") if obj.start_time else ""),
    ("end_time", lambda obj: obj.end_time.strftime("%H:%M:%S") if obj.end_time else ""),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class ClassScheduleDataTableView(BaseDataTableView):
    model = ClassSchedule
    columns = CLASS_SCHEDULE_COLUMNS
    searchable_columns = [
        "gym_class__name",
        "class_room__name",
        "trainer__employee__employee_id",
        "trainer__employee__user__first_name",
        "trainer__employee__user__last_name",
        "day_of_week",
        "remarks",
    ]
    orderable_columns = [
        "gym_class__name",
        "class_room__name",
        "trainer__employee__employee_id",
        "trainer__employee__user__first_name",
        "day_of_week",
        "start_time",
        "end_time",
        "is_active",
        "remarks",
    ]

    def get_queryset(self):
        return self.model.objects.select_related(
            "gym_class",
            "class_room",
            "trainer__employee__user",
        )
