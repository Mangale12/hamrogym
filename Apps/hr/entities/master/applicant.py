from core.choices import (
    APPLICANT_STATUS_CHOICES,
    BLOOD_GROUP_CHOICES,
    GENDER_CHOICES,
    MARITAL_STATUS_CHOICES,
    RELIGION_CHOICES,
)
from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.applicant_data_table import ApplicantDataTableView, APPLICANT_COLUMNS
from ...forms.applicant_form import ApplicantForm
from ...models import Applicant


register_entity(
    EntityConfig(
        name="applicant",
        url_path="applicants",
        verbose_name="Applicant",
        model=Applicant,
        form_class=ApplicantForm,
        datatable_view=ApplicantDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "email", "label": "Email", "type": "email", "required": False, "col": 6},
            {"name": "phone", "label": "Phone", "type": "text", "required": False, "col": 6},
            {"name": "date_of_birth", "label": "Date of Birth", "type": "date", "required": False, "col": 6},
            {
                "name": "gender",
                "label": "Gender",
                "type": "static_select",
                "required": False,
                "col": 6,
                "options": GENDER_CHOICES,
            },
            {
                "name": "marital_status",
                "label": "Marital Status",
                "type": "static_select",
                "required": False,
                "col": 6,
                "options": MARITAL_STATUS_CHOICES,
            },
            {
                "name": "job_posting",
                "label": "Job Posting",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "job_posting_select",
            },
            {
                "name": "address",
                "label": "Address",
                "type": "textarea",
                "required": False,
                "col": 12,
            },
            {
                "name": "country",
                "label": "Country",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "country_select",
            },
            {
                "name": "state",
                "label": "State",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "state_select",
            },
            {
                "name": "city",
                "label": "City",
                "type": "text",
                "required": False,
                "col": 6,
            },
            {
                "name": "cv",
                "label": "CV",
                "type": "file",
                "required": True,
                "col": 6,
            },
            {
                "name": "cover_letter",
                "label": "Cover Letter",
                "type": "file",
                "required": False,
                "col": 6,
            },
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": False,
                "col": 6,
                "options": APPLICANT_STATUS_CHOICES,
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
            (
                {
                    "name": key,
                    "title": key.replace("_", " ").title(),
                    "render": "function(data){return data ? `<a href='${data}' target='_blank'>View</a>` : '';}",
                }
                if key in {"cv", "cover_letter"}
                else {"name": key, "title": key.replace("_", " ").title()}
            )
            for key, _accessor in APPLICANT_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)
