from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.attendance_data_table import AttendanceDataTableView, ATTENDANCE_COLUMNS
from ...forms.attendance_form import AttendanceForm
from ...models import Attendance


register_entity(
    EntityConfig(
        name="attendance",
        url_path="attendances",
        verbose_name="Attendance",
        model=Attendance,
        form_class=AttendanceForm,
        datatable_view=AttendanceDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ATTENDANCE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
