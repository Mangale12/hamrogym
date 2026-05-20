from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.class_schedule_data_table import ClassScheduleDataTableView, CLASS_SCHEDULE_COLUMNS
from ...forms.class_schedule_form import ClassScheduleForm
from ...models import ClassSchedule
from ...models.class_schedule import DAY_OF_WEEK_CHOICES


register_entity(
    EntityConfig(
        name="class_schedule",
        url_path="class-schedules",
        verbose_name="Class Schedule",
        model=ClassSchedule,
        form_class=ClassScheduleForm,
        datatable_view=ClassScheduleDataTableView,
        show_view=False,
        fields=[
            {"name": "gym_class", "label": "Gym Class", "type": "select", "required": True, "col": 4, "url_name": "gym_class_select"},
            {"name": "class_room", "label": "Class Room", "type": "select", "required": False, "col": 4, "url_name": "class_room_select"},
            {"name": "trainer", "label": "Trainer", "type": "select", "required": False, "col": 4, "url_name": "trainer_select"},
            {
                "name": "day_of_week",
                "label": "Day Of Week",
                "type": "static_select",
                "required": True,
                "col": 4,
                "options": [("", "Select Day"), *DAY_OF_WEEK_CHOICES],
            },
            {"name": "start_time", "label": "Start Time", "type": "time", "required": True, "col": 4},
            {"name": "end_time", "label": "End Time", "type": "time", "required": True, "col": 4},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in CLASS_SCHEDULE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
        action_buttons=[
            {
                "label": "Open",
                "title": "Open schedule workspace",
                "icon_class": "fas fa-calendar-alt",
                "class_name": "btn-outline-dark",
                "href_url": "/class-schedules/{id}/view/",
            },
        ],
        select_search_fields=[
            "gym_class__name",
            "class_room__name",
            "trainer__employee__employee_id",
            "trainer__employee__user__first_name",
            "day_of_week",
        ],
        select_label_func=lambda obj: f"{obj.gym_class.name} - {obj.get_day_of_week_display()} {obj.start_time:%H:%M}",
    )
)
