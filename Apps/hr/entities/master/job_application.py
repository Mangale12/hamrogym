from core.choices import JOB_APPLICATION_STATUS_CHOICES
from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.job_application_data_table import JobApplicationDataTableView, JOB_APPLICATION_COLUMNS
from ...forms.job_application_form import JobApplicationForm
from ...models import JobApplication, JobApplicationStatus


def _sync_job_application_status(request, job_application: JobApplication) -> None:
    latest_status = (
        JobApplicationStatus.objects.filter(job_application=job_application)
        .order_by("-changed_at", "-id")
        .first()
    )

    if latest_status and latest_status.status == job_application.status:
        if latest_status.remarks != (job_application.remarks or ""):
            latest_status.remarks = job_application.remarks or ""
            latest_status.changed_by = request.user
            latest_status.save(update_fields=["remarks", "changed_by", "updated_at"])
        return

    JobApplicationStatus.objects.create(
        job_application=job_application,
        status=job_application.status,
        changed_by=request.user,
        remarks=job_application.remarks or "",
    )


register_entity(
    EntityConfig(
        name="job_application",
        url_path="job-applications",
        verbose_name="Job Application",
        model=JobApplication,
        form_class=JobApplicationForm,
        datatable_view=JobApplicationDataTableView,
        fields=[
            {
                "name": "applicant",
                "label": "Applicant",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "applicant_select",
            },
            {
                "name": "job_posting",
                "label": "Job Posting",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "job_posting_select",
            },
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": JOB_APPLICATION_STATUS_CHOICES,
            },
            {
                "name": "is_active",
                "label": "Is Active",
                "type": "checkbox",
                "required": False,
                "col": 6,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_APPLICATION_COLUMNS
            if key != "id"
        ],
        post_save=_sync_job_application_status,
        reset_defaults={},
    )
)
