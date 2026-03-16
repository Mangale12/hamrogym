from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.job_requiditon_data_table import JobRequisitionDataTableView, JOB_REQUIDITON_COLUMNS
from ...forms.job_requiditon_form import JobRequisitionForm
from ...models import JobRequisition


register_entity(
    EntityConfig(
        name="job_requiditon",
        url_path="job-requisitons",
        verbose_name="Job Requisition",
        model=JobRequisition,
        form_class=JobRequisitionForm,
        datatable_view=JobRequisitionDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_REQUIDITON_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
