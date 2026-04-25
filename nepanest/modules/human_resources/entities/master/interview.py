from core.choices import INTERVIEW_MODE_CHOICES, INTERVIEW_STATUS_CHOICES
from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)
from nepanest.modules.recruitment.datatables import INTERVIEW_COLUMNS, InterviewDataTableView
from nepanest.modules.recruitment.forms import InterviewForm
from nepanest.modules.recruitment.models import (
    Interview,
    InterviewFeedback,
    InterviewPanel,
    JobApplicationStatus,
)


def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


PANEL_SECTION = {
    "title": "Interview Panel",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "employee",
            "label": "Panel Member",
            "type": "select",
            "required": True,
            "url_name": "user_select",
        },
    ],
}


FEEDBACK_SECTION = {
    "title": "Interview Feedback",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "panel_member",
            "label": "Panel Member",
            "type": "select",
            "required": True,
            "url_name": "user_select",
        },
        {
            "name": "rating",
            "label": "Rating",
            "type": "number",
            "required": True,
            "min": 1,
        },
        {
            "name": "recommendation",
            "label": "Recommendation",
            "type": "static_select",
            "required": True,
            "options": InterviewFeedback._meta.get_field("recommendation").choices,
        },
        {
            "name": "comments",
            "label": "Comments",
            "type": "textarea",
            "required": False,
        },
    ],
}


PANEL_RELATION = RelatedDynamicSectionConfig(
    section_name="panel_members",
    related_model=InterviewPanel,
    parent_field="interview",
    fields=["employee"],
    required_fields=["employee"],
    empty_check_fields=["employee"],
    save_transformers={
        "employee": lambda value: (value or "").strip(),
    },
)


FEEDBACK_RELATION = RelatedDynamicSectionConfig(
    section_name="feedbacks",
    related_model=InterviewFeedback,
    parent_field="interview",
    fields=["panel_member", "rating", "recommendation", "comments"],
    required_fields=["panel_member", "rating", "recommendation"],
    empty_check_fields=["panel_member", "rating", "recommendation", "comments"],
    save_transformers={
        "panel_member": lambda value: (value or "").strip(),
        "rating": lambda value: max(1, _to_int(value, 1)),
        "recommendation": lambda value: (value or "").strip(),
        "comments": lambda value: (value or "").strip(),
    },
)


_save_panel_members = build_related_section_saver(PANEL_RELATION)
_load_panel_members = build_related_section_loader(PANEL_RELATION)
_save_feedbacks = build_related_section_saver(FEEDBACK_RELATION)
_load_feedbacks = build_related_section_loader(FEEDBACK_RELATION)


def _save_interview_relations(request, interview: Interview) -> None:
    _save_panel_members(request, interview)
    _save_feedbacks(request, interview)
    panel_member_ids = set(
        InterviewPanel.objects.filter(interview=interview).values_list("employee_id", flat=True)
    )
    InterviewFeedback.objects.filter(interview=interview).exclude(
        panel_member_id__in=panel_member_ids
    ).delete()


def _load_interview_relations(interview: Interview):
    data = {}
    data.update(_load_panel_members(interview))
    data.update(_load_feedbacks(interview))
    return data


def _sync_job_application_from_interview(request, interview: Interview) -> None:
    if interview.status in {"scheduled", "in_progress"}:
        next_status = "interview_scheduled"
    elif interview.status == "completed":
        next_status = "interviewed"
    else:
        return

    job_application = interview.job_application
    if job_application.status != next_status:
        job_application.status = next_status
        job_application.save(update_fields=["status", "updated_at"])

    latest_status = (
        JobApplicationStatus.objects.filter(job_application=job_application)
        .order_by("-changed_at", "-id")
        .first()
    )
    remarks = interview.remarks or ""
    if latest_status and latest_status.status == next_status:
        return

    JobApplicationStatus.objects.create(
        job_application=job_application,
        status=next_status,
        changed_by=request.user,
        remarks=remarks,
    )


register_entity(
    EntityConfig(
        name="interview",
        url_path="interviews",
        verbose_name="Interview",
        model=Interview,
        form_class=InterviewForm,
        datatable_view=InterviewDataTableView,
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
                "name": "interview_stage",
                "label": "Interview Stage",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "interview_stage_select",
            },
            {
                "name": "scheduled_date",
                "label": "Scheduled Date",
                "type": "date",
                "required": True,
                "col": 6,
            },
            {
                "name": "scheduled_time",
                "label": "Scheduled Time",
                "type": "time",
                "required": True,
                "col": 6,
            },
            {
                "name": "location",
                "label": "Location",
                "type": "text",
                "required": True,
                "col": 6,
            },
            {
                "name": "mode",
                "label": "Mode",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": INTERVIEW_MODE_CHOICES,
            },
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": INTERVIEW_STATUS_CHOICES,
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
        dynamic_sections={
            "panel_members": PANEL_SECTION,
            "feedbacks": FEEDBACK_SECTION,
        },
        dynamic_sections_loader=_load_interview_relations,
        dynamic_sections_saver=_save_interview_relations,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in INTERVIEW_COLUMNS
            if key != "id"
        ],
        post_save=_sync_job_application_from_interview,
        reset_defaults={},
    )
)
