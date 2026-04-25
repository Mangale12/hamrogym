from django.utils import timezone

from core.choices import APPROVAL_STATUS_CHOICES
from core.config import EntityConfig
from core.registry import register_entity
from nepanest.modules.recruitment.datatables import JOB_BATCH__COLUMNS, JobBatchesDataTableView
from nepanest.modules.recruitment.forms import JobBatchesForm
from nepanest.modules.recruitment.models import JobBatches


def _approve_job_batch(request, job_batch: JobBatches):
    job_batch.status = "approved"
    job_batch.approved_by = request.user
    job_batch.approved_at = timezone.now()
    job_batch.save(update_fields=["status", "approved_by", "approved_at"])
    return {"message": "Job Batch approved successfully."}


def _reject_job_batch(request, job_batch: JobBatches):
    job_batch.status = "rejected"
    job_batch.approved_by = request.user
    job_batch.approved_at = timezone.now()
    job_batch.save(update_fields=["status", "approved_by", "approved_at"])
    return {"message": "Job Batch rejected successfully."}


register_entity(
    EntityConfig(
        name="job_batch",
        url_path="job-batches",
        verbose_name="Job Batches",
        model=JobBatches,
        form_class=JobBatchesForm,
        datatable_view=JobBatchesDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "hiring_plan", "label": "Hiring Plan", "type": "select", "required": False, "col": 6, "url_name": "hiring_plan_select"},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 6, "url_name": "branch_select"},
            {"name": "status", "label": "Status", "type": "static_select", "required": False, "col": 6, "options": APPROVAL_STATUS_CHOICES},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": False, "col": 6},
            {"name": "end_date", "label": "End Date", "type": "date", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        row_actions={
            "approve": _approve_job_batch,
            "reject": _reject_job_batch,
        },
        action_state_field="status",
        hide_edit_on_values=["approved"],
        hide_delete_on_values=["approved"],
        action_buttons=[
            {
                "action_name": "approve",
                "title": "Approve Job Batch",
                "label": "",
                "icon_class": "fas fa-check",
                "class_name": "btn-outline-success",
                "confirm_text": "Are you sure you want to approve this job batch?",
                "success_message": "Job Batch approved successfully.",
                "hide_on_values": ["approved"],
            },
            {
                "action_name": "reject",
                "title": "Reject Job Batch",
                "label": "",
                "icon_class": "fas fa-times",
                "class_name": "btn-outline-warning",
                "confirm_text": "Are you sure you want to reject this job batch?",
                "success_message": "Job Batch rejected successfully.",
                "hide_on_values": ["approved"],
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_BATCH__COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
