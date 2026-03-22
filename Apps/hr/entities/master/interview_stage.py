from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.interview_stage_data_table import InterviewStageDataTableView, INTERVIEW_STAGE_COLUMNS
from ...forms.interview_stage_form import InterviewStageForm
from ...models import InterviewStage


register_entity(
    EntityConfig(
        name="interview_stage",
        url_path="interview-stages",
        verbose_name="Interview Stage",
        model=InterviewStage,
        form_class=InterviewStageForm,
        datatable_view=InterviewStageDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "sequence", "label": "Sequence", "type": "number", "required": True, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in INTERVIEW_STAGE_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
