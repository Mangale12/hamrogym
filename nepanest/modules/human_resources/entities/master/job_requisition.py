from core.config import EntityConfig
from core.registry import register_entity

from core.choices import APPROVAL_STATUS_CHOICES, PRIORITY_CHOICES, WORK_LOCATION_CHOICES
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)
from nepanest.modules.recruitment.datatables import (
    JOB_REQUISITION_COLUMNS,
    JobRequisitionDataTableView,
)
from nepanest.modules.recruitment.forms import JobRequisitionForm
from nepanest.modules.recruitment.models import JobPositionSkill, JobRequisition, JobRequisitionPosition


JOB_REQUISITION_POSITION = {
    "title" : "Job Requisition Position",
    "layout" : "table",
    "allow_add" : True,
    "fields":[
        {
            "name": "position_title",
            "label": "Position Title",
            "type": "text",
            "required": True,
        },
        {
            "name": "designation",
            "label": "Designation",
            "type": "select",
            "required": True,
            "url_name": "designation_select"
        },
        {
            "name": "position_description",
            "label": "Position Description",
            "type": "textarea",
            "required": False,
        },
        {
            "name": "responsibilities",
            "label": "Responsibilities",
            "type": "textarea",
            "required": False,
            "col": 12
        },
        {
            "name": "requirements",
            "label": "Requirements",
            "type": "textarea",
            "required": False,
        },
        {
            "name": "salary",
            "label": "Salary",
            "type": "number",
            "required": False,
            "col": 6
        },
        {
            "name": "skills",
            "label": "Job Skills",
            "type": "select",
            "required": False,
            "multiple": True,
            "url_name": "job_skill_select"
        },
        {
            "name": "skill_level",
            "label": "Skill Level",
            "type": "select",
            "required": False,
            "url_name": "skill_level_select"
        },
        {
            "name": "location",
            "label": "Location",
            "type": "text",
            "required": False,
            "col": 6
        }
    ]
}


def _sync_position_skills(item: JobRequisitionPosition, row, _job_requisition: JobRequisition) -> None:
    raw_skill_ids = row.get("skills") or []
    skill_ids = []
    if isinstance(raw_skill_ids, list):
        skill_ids = [int(skill_id) for skill_id in raw_skill_ids if str(skill_id).isdigit()]
    elif str(raw_skill_ids).isdigit():
        skill_ids = [int(raw_skill_ids)]

    JobPositionSkill.objects.filter(job_position=item).exclude(skill_id__in=skill_ids).delete()
    existing_skill_ids = set(
        JobPositionSkill.objects.filter(job_position=item, skill_id__in=skill_ids).values_list(
            "skill_id",
            flat=True,
        )
    )
    skill_level_id = row.get("skill_level") if str(row.get("skill_level") or "").isdigit() else None
    for skill_id in skill_ids:
        if skill_id in existing_skill_ids:
            JobPositionSkill.objects.filter(job_position=item, skill_id=skill_id).update(
                skill_level_id=skill_level_id
            )
            continue
        JobPositionSkill.objects.create(
            job_position=item,
            skill_id=skill_id,
            skill_level_id=skill_level_id,
        )


def _serialize_position_skills(item: JobRequisitionPosition):
    return {
        "skills": [str(skill.skill_id) for skill in item.skills.select_related("skill").order_by("skill__name")],
        "skill_level": str(
            item.skills.filter(skill_level__isnull=False).values_list("skill_level_id", flat=True).first() or ""
        ),
    }


JOB_REQUISITION_POSITION_RELATION = RelatedDynamicSectionConfig(
    section_name="items",
    related_model=JobRequisitionPosition,
    parent_field="job_requisition",
    fields=[
        "position_title",
        "designation",
        "position_description",
        "responsibilities",
        "requirements",
        "salary",
        "location",
    ],
    required_fields=["position_title", "designation"],
    empty_check_fields=[
        "position_title",
        "designation",
        "position_description",
        "responsibilities",
        "requirements",
        "salary",
        "skills",
        "skill_level",
        "location",
    ],
    use_post_lists=True,
    save_transformers={
        "position_title": lambda value: (value or "").strip(),
        "position_description": lambda value: (value or "").strip(),
        "responsibilities": lambda value: (value or "").strip(),
        "requirements": lambda value: (value or "").strip(),
        "location": lambda value: (value or "").strip(),
    },
    row_save_hook=_sync_position_skills,
    row_load_hook=_serialize_position_skills,
)


_save_job_requisition_positions = build_related_section_saver(JOB_REQUISITION_POSITION_RELATION)
_load_job_requisition_positions = build_related_section_loader(JOB_REQUISITION_POSITION_RELATION)

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
        dynamic_sections ={
            "items" : JOB_REQUISITION_POSITION
        },
        dynamic_sections_loader=_load_job_requisition_positions,
        dynamic_sections_saver=_save_job_requisition_positions,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_REQUISITION_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
