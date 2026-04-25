from datetime import date

from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

from nepanest.modules.leave.datatables import (
    HOLIDAY_CALENDAR_COLUMNS,
    HolidayCalendarDataTableView,
)
from nepanest.modules.leave.forms import HolidayCalendarForm
from nepanest.modules.leave.models import Holiday, HolidayCalendar, WeeklyOffRule


HOLIDAY_SECTION = {
    "title": "Holidays",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "name", "label": "Holiday Name", "type": "text", "required": True},
        {"name": "date", "label": "Date", "type": "date", "required": True},
        {"name": "is_optional", "label": "Optional", "type": "checkbox", "required": False},
        {"name": "is_half_day", "label": "Half Day", "type": "checkbox", "required": False},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False},
    ],
}


WEEKLY_OFF_SECTION = {
    "title": "Weekly Off Rules",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "weekday",
            "label": "Weekday",
            "type": "static_select",
            "required": True,
            "options": WeeklyOffRule._meta.get_field("weekday").choices,
        },
        {"name": "is_active", "label": "Active", "type": "checkbox", "required": False},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False},
    ],
}


HOLIDAY_RELATION = RelatedDynamicSectionConfig(
    section_name="holidays",
    related_model=Holiday,
    parent_field="holiday_calendar",
    fields=["name", "date", "is_optional", "is_half_day", "remarks"],
    required_fields=["name", "date"],
    bool_fields=["is_optional", "is_half_day"],
    empty_check_fields=["name", "date", "remarks"],
    order_by="date",
    save_transformers={
        "name": lambda value: (value or "").strip(),
        "remarks": lambda value: (value or "").strip(),
    },
)


WEEKLY_OFF_RELATION = RelatedDynamicSectionConfig(
    section_name="weekly_off_rules",
    related_model=WeeklyOffRule,
    parent_field="holiday_calendar",
    fields=["weekday", "is_active", "remarks"],
    required_fields=["weekday"],
    bool_fields=["is_active"],
    empty_check_fields=["weekday", "remarks"],
    order_by="weekday",
    save_transformers={
        "weekday": lambda value: (value or "").strip(),
        "remarks": lambda value: (value or "").strip(),
    },
)


_load_holidays = build_related_section_loader(HOLIDAY_RELATION)
_save_holidays = build_related_section_saver(HOLIDAY_RELATION)
_load_weekly_offs = build_related_section_loader(WEEKLY_OFF_RELATION)
_save_weekly_offs = build_related_section_saver(WEEKLY_OFF_RELATION)


def _load_holiday_calendar_sections(parent_obj):
    data = {}
    data.update(_load_holidays(parent_obj))
    data.update(_load_weekly_offs(parent_obj))
    return data


def _save_holiday_calendar_sections(request, parent_obj):
    _save_holidays(request, parent_obj)
    _save_weekly_offs(request, parent_obj)


register_entity(
    EntityConfig(
        name="holiday_calendar",
        url_path="holiday-calendars",
        verbose_name="Holiday Calendar",
        model=HolidayCalendar,
        form_class=HolidayCalendarForm,
        datatable_view=HolidayCalendarDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 4},
            {"name": "year", "label": "Year", "type": "number", "required": True, "col": 4},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        dynamic_sections={
            "holidays": HOLIDAY_SECTION,
            "weekly_off_rules": WEEKLY_OFF_SECTION,
        },
        dynamic_sections_loader=_load_holiday_calendar_sections,
        dynamic_sections_saver=_save_holiday_calendar_sections,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in HOLIDAY_CALENDAR_COLUMNS
            if key != "id"
        ],
        reset_defaults={"year": date.today().year, "is_active": True},
    )
)
