from django.utils import timezone

from core.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

from ...models import EmployeeComponentOverride, PayrollRun, SalaryStructureComponent
from ...services import (
    approve_payroll_run,
    build_attendance_payroll_inputs,
    build_leave_payroll_inputs,
    lock_payroll_run,
    process_payroll_run,
    reset_payroll_run,
)


STRUCTURE_COMPONENT_SECTION = {
    "title": "Structure Components",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "salary_component",
            "label": "Component",
            "type": "select",
            "required": True,
            "url_name": "salary_component_select",
        },
        {
            "name": "percentage_of_component",
            "label": "Percentage Of",
            "type": "select",
            "required": False,
            "url_name": "salary_component_select",
        },
        {"name": "sequence", "label": "Sequence", "type": "number", "required": False},
        {"name": "default_value", "label": "Default Value", "type": "number", "required": False},
        {"name": "formula_expression", "label": "Formula", "type": "text", "required": False},
        {"name": "min_value", "label": "Min Value", "type": "number", "required": False},
        {"name": "max_value", "label": "Max Value", "type": "number", "required": False},
        {
            "name": "rounding_rule",
            "label": "Rounding",
            "type": "static_select",
            "required": True,
            "options": SalaryStructureComponent._meta.get_field("rounding_rule").choices,
        },
        {"name": "is_mandatory", "label": "Mandatory", "type": "checkbox", "required": False},
        {"name": "is_editable", "label": "Editable", "type": "checkbox", "required": False},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False},
    ],
}


COMPONENT_OVERRIDE_SECTION = {
    "title": "Component Overrides",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "salary_component",
            "label": "Component",
            "type": "select",
            "required": True,
            "url_name": "salary_component_select",
        },
        {"name": "override_value", "label": "Override Value", "type": "number", "required": False},
        {"name": "override_formula", "label": "Override Formula", "type": "text", "required": False},
        {"name": "effective_from", "label": "Effective From", "type": "date", "required": False},
        {"name": "effective_to", "label": "Effective To", "type": "date", "required": False},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False},
    ],
}


STRUCTURE_COMPONENT_RELATION = RelatedDynamicSectionConfig(
    section_name="structure_components",
    related_model=SalaryStructureComponent,
    parent_field="salary_structure",
    fields=[
        "salary_component",
        "percentage_of_component",
        "sequence",
        "default_value",
        "formula_expression",
        "min_value",
        "max_value",
        "rounding_rule",
        "is_mandatory",
        "is_editable",
        "remarks",
    ],
    required_fields=["salary_component", "rounding_rule"],
    bool_fields=["is_mandatory", "is_editable"],
    empty_check_fields=[
        "salary_component",
        "percentage_of_component",
        "default_value",
        "formula_expression",
        "min_value",
        "max_value",
        "remarks",
    ],
    order_by="sequence",
    save_transformers={
        "sequence": lambda value: int(value) if str(value or "").isdigit() else 1,
        "formula_expression": lambda value: (value or "").strip(),
        "rounding_rule": lambda value: (value or "").strip() or "round_2",
        "remarks": lambda value: (value or "").strip(),
    },
)


COMPONENT_OVERRIDE_RELATION = RelatedDynamicSectionConfig(
    section_name="component_overrides",
    related_model=EmployeeComponentOverride,
    parent_field="employee_salary_assignment",
    fields=[
        "salary_component",
        "override_value",
        "override_formula",
        "effective_from",
        "effective_to",
        "remarks",
    ],
    required_fields=["salary_component"],
    empty_check_fields=[
        "salary_component",
        "override_value",
        "override_formula",
        "effective_from",
        "effective_to",
        "remarks",
    ],
    order_by="salary_component__sequence",
    save_transformers={
        "override_formula": lambda value: (value or "").strip(),
        "remarks": lambda value: (value or "").strip(),
    },
)


load_structure_components = build_related_section_loader(STRUCTURE_COMPONENT_RELATION)
save_structure_components = build_related_section_saver(STRUCTURE_COMPONENT_RELATION)
load_component_overrides = build_related_section_loader(COMPONENT_OVERRIDE_RELATION)
save_component_overrides = build_related_section_saver(COMPONENT_OVERRIDE_RELATION)


salary_component_columns = [
    {"name": "code", "title": "Code"},
    {"name": "name", "title": "Component"},
    {"name": "component_type", "title": "Type"},
    {"name": "value_type", "title": "Value Type"},
    {"name": "tax_treatment", "title": "Tax Treatment"},
    {"name": "sequence", "title": "Sequence"},
    {
        "name": "is_active",
        "title": "Active",
        "render": "function(data){return data ? 'Yes' : 'No';}",
    },
]

salary_structure_columns = [
    {"name": "code", "title": "Code"},
    {"name": "name", "title": "Salary Structure"},
    {"name": "organization", "title": "Organization"},
    {"name": "branch", "title": "Branch"},
    {"name": "currency", "title": "Currency"},
    {"name": "effective_from", "title": "Effective From"},
    {"name": "effective_to", "title": "Effective To"},
    {
        "name": "is_active",
        "title": "Active",
        "render": "function(data){return data ? 'Yes' : 'No';}",
    },
]

employee_salary_assignment_columns = [
    {"name": "employee", "title": "Employee"},
    {"name": "salary_structure", "title": "Salary Structure"},
    {"name": "gross_salary", "title": "Gross Salary"},
    {"name": "annual_ctc", "title": "Annual CTC"},
    {"name": "payment_frequency", "title": "Frequency"},
    {"name": "effective_from", "title": "Effective From"},
    {"name": "effective_to", "title": "Effective To"},
    {
        "name": "is_active",
        "title": "Active",
        "render": "function(data){return data ? 'Yes' : 'No';}",
    },
    {"name": "updated_at", "title": "Updated At"},
]

payroll_run_columns = [
    {"name": "name", "title": "Payroll Run"},
    {"name": "payroll_year", "title": "Year"},
    {"name": "payroll_month", "title": "Month"},
    {"name": "period_start", "title": "Period Start"},
    {"name": "period_end", "title": "Period End"},
    {"name": "employee_count", "title": "Employees"},
    {"name": "total_gross", "title": "Total Gross"},
    {"name": "total_deductions", "title": "Total Deductions"},
    {"name": "total_net", "title": "Total Net"},
    {
        "name": "status",
        "title": "Status",
        "render": (
            "function(data){"
            "const map={draft:'secondary',processed:'primary',reviewed:'info',approved:'success',locked:'dark'};"
            "const cls=map[data]||'light';"
            "return `<span class=\"badge bg-${cls}\">${(data||'').replace('_',' ')}</span>`;"
            "}"
        ),
    },
    {"name": "processed_at", "title": "Processed At"},
]

payroll_run_employee_columns = [
    {"name": "payroll_run", "title": "Payroll Run"},
    {"name": "employee", "title": "Employee"},
    {"name": "salary_structure_name", "title": "Salary Structure"},
    {"name": "gross_salary", "title": "Gross Salary"},
    {"name": "gross_earnings", "title": "Gross Earnings"},
    {"name": "total_deductions", "title": "Deductions"},
    {"name": "net_salary", "title": "Net Salary"},
    {
        "name": "status",
        "title": "Status",
        "render": (
            "function(data){"
            "const map={processed:'success',pending:'warning',error:'danger'};"
            "const cls=map[data]||'secondary';"
            "return `<span class=\"badge bg-${cls}\">${data||''}</span>`;"
            "}"
        ),
    },
    {"name": "updated_at", "title": "Updated At"},
]

payroll_run_component_columns = [
    {"name": "payroll_run_employee", "title": "Payroll Employee"},
    {"name": "salary_component", "title": "Component"},
    {"name": "source_type", "title": "Source"},
    {"name": "sequence", "title": "Sequence"},
    {"name": "quantity", "title": "Quantity"},
    {"name": "rate", "title": "Rate"},
    {"name": "amount", "title": "Amount"},
    {"name": "created_at", "title": "Recorded At"},
]

attendance_payroll_summary_columns = [
    {"name": "payroll_run", "title": "Payroll Run"},
    {"name": "employee", "title": "Employee"},
    {"name": "present_days", "title": "Present"},
    {"name": "absent_days", "title": "Absent"},
    {"name": "half_days", "title": "Half Days"},
    {"name": "leave_days", "title": "Leave Days"},
    {"name": "payable_days", "title": "Payable Days"},
    {"name": "overtime_hours", "title": "Overtime Hours"},
    {"name": "late_instances", "title": "Late Count"},
    {"name": "updated_at", "title": "Updated At"},
]

leave_payroll_impact_columns = [
    {"name": "payroll_run", "title": "Payroll Run"},
    {"name": "employee", "title": "Employee"},
    {"name": "leave_request", "title": "Leave Request"},
    {"name": "leave_type", "title": "Leave Type"},
    {
        "name": "is_paid",
        "title": "Paid",
        "render": "function(data){return data ? 'Yes' : 'No';}",
    },
    {"name": "days", "title": "Days"},
    {"name": "deduction_amount", "title": "Deduction"},
    {"name": "updated_at", "title": "Updated At"},
]

payroll_adjustment_columns = [
    {"name": "payroll_run", "title": "Payroll Run"},
    {"name": "employee", "title": "Employee"},
    {"name": "salary_component", "title": "Component"},
    {"name": "adjustment_type", "title": "Adjustment Type"},
    {"name": "amount", "title": "Amount"},
    {"name": "reason", "title": "Business Reason"},
    {"name": "updated_at", "title": "Updated At"},
]


def process_payroll_action(request, payroll_run: PayrollRun):
    process_payroll_run(payroll_run=payroll_run, acting_user=request.user)
    return {"message": "Payroll run processed successfully."}


def reset_payroll_action(request, payroll_run: PayrollRun):
    reset_payroll_run(payroll_run=payroll_run)
    return {"message": "Payroll run reset to draft successfully."}


def approve_payroll_action(request, payroll_run: PayrollRun):
    approve_payroll_run(payroll_run=payroll_run, acting_user=request.user)
    return {"message": "Payroll run approved successfully."}


def lock_payroll_action(request, payroll_run: PayrollRun):
    lock_payroll_run(payroll_run=payroll_run, acting_user=request.user)
    return {"message": "Payroll run locked successfully."}


def build_attendance_inputs_action(request, payroll_run: PayrollRun):
    count = build_attendance_payroll_inputs(payroll_run=payroll_run)
    return {"message": f"Attendance payroll inputs rebuilt for {count} employee record(s)."}


def build_leave_inputs_action(request, payroll_run: PayrollRun):
    count = build_leave_payroll_inputs(payroll_run=payroll_run)
    return {"message": f"Leave payroll impacts rebuilt for {count} leave record(s)."}


today = timezone.localdate()
