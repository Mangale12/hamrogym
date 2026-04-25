from core.choices import APPROVAL_STATUS_CHOICES
from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

from nepanest.modules.recruitment.datatables import (
    JOB_OFFER_COLUMNS,
    JobOfferDataTableView,
)
from nepanest.modules.recruitment.forms import JobOfferForm
from nepanest.modules.recruitment.models import Hire, JobApplicationStatus, JobOffer, JobOfferAttachment


def _sync_job_application_status(request, job_offer: JobOffer, next_status: str) -> None:
    job_application = job_offer.job_application
    if job_application.status != next_status:
        job_application.status = next_status
        job_application.save(update_fields=["status", "updated_at"])

    latest_status = (
        JobApplicationStatus.objects.filter(job_application=job_application)
        .order_by("-changed_at", "-id")
        .first()
    )
    remarks = job_offer.remarks or ""
    if latest_status and latest_status.status == next_status:
        if latest_status.remarks != remarks:
            latest_status.remarks = remarks
            latest_status.changed_by = request.user
            latest_status.save(update_fields=["remarks", "changed_by", "updated_at"])
        return

    JobApplicationStatus.objects.create(
        job_application=job_application,
        status=next_status,
        changed_by=request.user,
        remarks=remarks,
    )


def _create_or_update_hire(job_offer: JobOffer) -> None:
    job_application = job_offer.job_application
    job_posting = job_application.job_posting
    job_position = job_posting.job_position if job_posting else None

    defaults = {
        "candidate": job_application.applicant,
        "hire_date": job_offer.joining_date,
        "designation": getattr(job_position, "designation", None),
        "department": getattr(job_position, "department", None),
        "status": "approved",
    }

    Hire.objects.update_or_create(
        job_offer=job_offer,
        defaults=defaults,
    )


def _approve_job_offer(request, job_offer: JobOffer):
    job_offer.status = "approved"
    job_offer.save(update_fields=["status"])
    _sync_job_application_status(request, job_offer, "hired")
    _create_or_update_hire(job_offer)
    return {"message": "Job offer approved successfully."}


def _reject_job_offer(request, job_offer: JobOffer):
    job_offer.status = "rejected"
    job_offer.save(update_fields=["status"])
    _sync_job_application_status(request, job_offer, "rejected")
    return {"message": "Job offer rejected successfully."}


ATTACHMENT_SECTION = {
    "title": "Attachments",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "document_type",
            "label": "Document Type",
            "type": "text",
            "required": False,
        },
        {
            "name": "file",
            "label": "File",
            "type": "file",
            "required": True,
            "accept": ".pdf,.doc,.docx,.jpg,.jpeg,.png",
        },
    ],
}


ATTACHMENT_SECTION_RELATION = RelatedDynamicSectionConfig(
    section_name="attachments",
    related_model=JobOfferAttachment,
    parent_field="job_offer",
    fields=["document_type", "file"],
    required_fields=["file"],
    empty_check_fields=["document_type", "file"],
    include_files=True,
    save_transformers={
        "document_type": lambda value: (value or "").strip(),
    },
)


_save_job_offer_attachments = build_related_section_saver(ATTACHMENT_SECTION_RELATION)
_load_job_offer_attachments = build_related_section_loader(ATTACHMENT_SECTION_RELATION)


register_entity(
    EntityConfig(
        name="job_offer",
        url_path="job-offers",
        verbose_name="Job Offer",
        model=JobOffer,
        form_class=JobOfferForm,
        datatable_view=JobOfferDataTableView,
        fields=[
            {
                "name": "job_application",
                "label": "Job Application",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "job_application_select",
            },
            {
                "name": "offer_date",
                "label": "Offer Date",
                "type": "date",
                "required": True,
                "col": 6,
            },
            {
                "name": "joining_date",
                "label": "Joining Date",
                "type": "date",
                "required": True,
                "col": 6,
            },
            {
                "name": "salary_offered",
                "label": "Salary Offered",
                "type": "number",
                "required": True,
                "col": 6,
                "attributes": {"min": "0", "step": "0.01"},
            },
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": APPROVAL_STATUS_CHOICES,
            },
            {
                "name": "remarks",
                "label": "Remarks",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
        ],
        dynamic_sections={
            "attachments": ATTACHMENT_SECTION,
        },
        dynamic_sections_loader=_load_job_offer_attachments,
        dynamic_sections_saver=_save_job_offer_attachments,
        row_actions={
            "approve": _approve_job_offer,
            "reject": _reject_job_offer,
        },
        action_state_field="status",
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_OFFER_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": "pending"},
        action_buttons=[
            {
                "action_name": "approve",
                "title": "Approve",
                "label": "",
                "icon_class": "fas fa-check",
                "class_name": "btn-outline-success",
                "confirm_text": "Are you sure you want to approve this job offer?",
                "success_message": "Job offer approved successfully.",
                "hide_on_values": ["approved", "rejected"],
            },
            {
                "action_name": "reject",
                "title": "Reject",
                "label": "",
                "icon_class": "fas fa-times",
                "class_name": "btn-outline-danger",
                "confirm_text": "Are you sure you want to reject this job offer?",
                "success_message": "Job offer rejected successfully.",
                "hide_on_values": ["approved", "rejected"],
            },
        ],
        select_search_fields=[
            "job_application__applicant__name",
            "job_application__applicant__email",
            "job_application__job_posting__title",
            "status",
        ],
    )
)
