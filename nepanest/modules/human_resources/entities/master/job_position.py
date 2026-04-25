from core.choices import SCREENING_QUESTION_TYPE_CHOICES
from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)
from nepanest.modules.recruitment.datatables import (
    JOB_POSITION_COLUMNS,
    JobPositionDataTableView,
)
from nepanest.modules.recruitment.forms import JobPositionForm
from nepanest.modules.recruitment.models import JobPosition, ScreeningQuestion


SCREENING_QUESTIONS_SECTION = {
    "title": "Screening Questions",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "question_text",
            "label": "Question",
            "type": "textarea",
            "required": True,
        },
        {
            "name": "question_type",
            "label": "Question Type",
            "type": "static_select",
            "required": True,
            "options": SCREENING_QUESTION_TYPE_CHOICES,
        },
        {
            "name": "is_required",
            "label": "Required",
            "type": "checkbox",
            "required": False,
        },
        {
            "name": "is_active",
            "label": "Active",
            "type": "checkbox",
            "required": False,
        },
    ],
}


SCREENING_QUESTION_RELATION = RelatedDynamicSectionConfig(
    section_name="screening_questions",
    related_model=ScreeningQuestion,
    parent_field="job_position",
    fields=["question_text", "question_type", "is_required", "is_active"],
    required_fields=["question_text", "question_type"],
    bool_fields=["is_required", "is_active"],
    empty_check_fields=["question_text", "question_type", "is_required", "is_active"],
    save_transformers={
        "question_text": lambda value: (value or "").strip(),
        "question_type": lambda value: (value or "").strip(),
    },
)


_save_screening_questions = build_related_section_saver(SCREENING_QUESTION_RELATION)
_load_screening_questions = build_related_section_loader(SCREENING_QUESTION_RELATION)


register_entity(
    EntityConfig(
        name="job_position",
        url_path="job_position",
        verbose_name="Job Position",
        model=JobPosition,
        form_class=JobPositionForm,
        datatable_view=JobPositionDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "department", "label": "Department", "type": "select",  "required": True, "col": 6, "url_name": "department_select"},
            {"name": "designation", "label": "Designation", "type": "select",  "required": True, "col": 6, "url_name": "designation_select"},
            {"name": "job_category", "label": "Job Category", "type": "select",  "required": True, "col": 6, "url_name": "job_category_select"},
            {"name": "vacancies", "label": "Vacancies", "type": "number", "required": True, "col": 6},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "employeement_type", "label": "Employment Type", "type": "select", "required": False, "col": 12, "url_name": "employeement_type_select"},
            {"name": "salary_min", "label": "Salary Min", "type": "number", "required": False, "col": 6},
            {"name": "salary_max", "label": "Salary Max", "type": "number", "required": False, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        dynamic_sections={
            "screening_questions": SCREENING_QUESTIONS_SECTION,
        },
        dynamic_sections_loader=_load_screening_questions,
        dynamic_sections_saver=_save_screening_questions,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in JOB_POSITION_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
    )
)
