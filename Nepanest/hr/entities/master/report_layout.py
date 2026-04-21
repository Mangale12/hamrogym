from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payroll_data_table import ReportLayoutDataTableView
from ...forms.payroll_form import ReportLayoutForm
from ...models import ReportLayout


register_entity(
    EntityConfig(
        name="report_layout",
        url_path="report-layouts",
        verbose_name="Report Layout",
        model=ReportLayout,
        form_class=ReportLayoutForm,
        datatable_view=ReportLayoutDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "required": False, "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 4},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 4, "placeholder": "DEFAULT_A4"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 8, "placeholder": "Default A4 Layout"},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "html_wrapper", "label": "HTML Wrapper", "type": "textarea", "required": True, "col": 12},
            {"name": "css_content", "label": "CSS", "type": "textarea", "required": False, "col": 12},
            {"name": "header_html", "label": "Header HTML", "type": "textarea", "required": False, "col": 6},
            {"name": "footer_html", "label": "Footer HTML", "type": "textarea", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "organization", "title": "Organization"},
            {"name": "branch", "title": "Branch"},
            {"name": "code", "title": "Code"},
            {"name": "name", "title": "Name"},
            {"name": "is_active", "title": "Active"},
            {"name": "updated_at", "title": "Updated At"},
        ],
        reset_defaults={
            "is_active": True,
            "html_wrapper": "<html><head><style>{{ report_styles }}</style></head><body><header>{{ report_header|safe }}</header><main>{{ report_body|safe }}</main><footer>{{ report_footer|safe }}</footer></body></html>",
        },
    )
)
