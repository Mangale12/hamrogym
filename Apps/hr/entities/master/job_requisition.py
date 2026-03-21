from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.job_requiditon_data_table import (
    JOB_REQUISITION_COLUMNS,
    JobRequisitionDataTableView,
)
from ...forms.job_requisition_form import JobRequisitionForm
from ...models import JobRequisition
from core.choices import APPROVAL_STATUS_CHOICES, PRIORITY_CHOICES, WORK_LOCATION_CHOICES

register_entity(
    EntityConfig(
        name="job_requisition",
        url_path="job-requisitions",
        verbose_name="Job Requisition",
        model=JobRequisition,
        form_class=JobRequisitionForm,
        datatable_view=JobRequisitionDataTableView,
        fields=[
            {"name": "batch", "label": "Batch", "type": "select", "required": True, "col": 6, "url_name": "job_batch_select"},
            {"name": "requisition_code", "label": "Job Requisition Code", "type": "text", "required": True, "col": 6},
            {"name": "branch", "label": "Branch", "type": "select", "required": True, "col": 6, "url_name": "branch_select"},
            {"name": "department", "label": "Department", "type": "select", "required": True, "col": 6, "url_name": "department_select"},
            {"name": "designation", "label": "Designation", "type": "select", "required": True, "col": 6, "url_name": "designation_select"},
            {"name": "employment_type", "label": "Employment Type", "type": "select", "required": True, "col": 6, "url_name": "employeement_type_select"},
            {"name": "requested_by", "label": "Requested By", "type": "select", "required": False, "col": 6, "url_name": "user_select"},
            {"name": "vacancies", "label": "Vacancies", "type": "number", "required": True, "col": 6},
            {"name": "job_title", "label": "Job Title", "type": "text", "required": True, "col": 6},
            {"name": "job_description", "label": "Job Description", "type": "textarea", "required": False, "col": 12},
            {"name": "job_responsibilities", "label": "Job Responsibilities", "type": "textarea", "required": False, "col": 12},
            {"name": "required_skills", "label": "Required Skills", "type": "textarea", "required": False, "col": 12},
            {"name": "required_experience", "label": "Required Experience", "type": "textarea", "required": True, "col": 12},
            {"name": "education_requirement", "label": "Education Requirement", "type": "textarea", "required": True, "col": 12},
            {"name": "salary_min", "label": "Minimum Salary", "type": "number", "required": False, "col": 6},
            {"name": "salary_max", "label": "Maximum Salary", "type": "number", "required": False, "col": 6},
            {"name": "job_location", "label": "Job Location", "type": "static_select", "required": False, "col": 6, "options": WORK_LOCATION_CHOICES},
            {"name": "priority", "label": "Priority", "type": "static_select", "required": True, "col": 6, "options": PRIORITY_CHOICES},
            {"name": "expected_joining_date", "label": "Expected Joining Date", "type": "date", "required": True, "col": 6},
            {"name": "recruitment_reason", "label": "Recruitment Reason", "type": "textarea", "required": True, "col": 12},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 6, "options": APPROVAL_STATUS_CHOICES},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12}
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_REQUISITION_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
