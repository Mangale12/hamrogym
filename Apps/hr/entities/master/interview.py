from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.interview_data_table import InterviewDataTableView, INTERVIEW_COLUMNS
from ...forms.interview_form import InterviewForm
from ...models import Interview


register_entity(
    EntityConfig(
        name="interview",
        url_path="interviews",
        verbose_name="Interview",
        model=Interview,
        form_class=InterviewForm,
        datatable_view=InterviewDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in INTERVIEW_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
