from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payroll_data_table import ReportTemplateDataTableView
from ...forms.payroll_form import ReportTemplateForm
from ...models import ReportTemplate


register_entity(
    EntityConfig(
        name="report_template",
        url_path="report-templates",
        verbose_name="Report Template",
        model=ReportTemplate,
        form_class=ReportTemplateForm,
        datatable_view=ReportTemplateDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "required": False, "col": 3, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 3, "url_name": "branch_select"},
            {"name": "layout", "label": "Layout", "type": "select", "required": True, "col": 3, "url_name": "report_layout_select"},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 1},
            {"name": "is_default", "label": "Default", "type": "checkbox", "required": False, "col": 2},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 3, "placeholder": "PAYSLIP_STD"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 5, "placeholder": "Standard Payslip"},
            {"name": "report_key", "label": "Report Key", "type": "text", "required": True, "col": 4, "placeholder": "payslip"},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "body_html", "label": "Body HTML", "type": "textarea", "required": True, "col": 12},
            {"name": "css_content", "label": "Extra CSS", "type": "textarea", "required": False, "col": 12},
            {"name": "header_html", "label": "Header Override", "type": "textarea", "required": False, "col": 6},
            {"name": "footer_html", "label": "Footer Override", "type": "textarea", "required": False, "col": 6},
            {"name": "sample_context", "label": "Sample Context JSON", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "organization", "title": "Organization"},
            {"name": "branch", "title": "Branch"},
            {"name": "layout", "title": "Layout"},
            {"name": "code", "title": "Code"},
            {"name": "name", "title": "Name"},
            {"name": "report_key", "title": "Report Key"},
            {"name": "is_default", "title": "Default"},
            {"name": "is_active", "title": "Active"},
            {"name": "updated_at", "title": "Updated At"},
        ],
        reset_defaults={
            "is_active": True,
            "is_default": False,
            "sample_context": "{\n  \"company_name\": \"HamroGym\",\n  \"report_title\": \"Sample Report\",\n  \"employee_name\": \"John Doe\"\n}",
            "body_html": "<section>\n  <h1>{{ report_title }}</h1>\n  <p>{{ company_name }}</p>\n  <p>{{ employee_name }}</p>\n</section>",
        },
    )
)
