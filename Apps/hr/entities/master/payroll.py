from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity
from core.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

from ...datatables.payroll_data_table import (
    ATTENDANCE_PAYROLL_SUMMARY_COLUMNS,
    EMPLOYEE_SALARY_ASSIGNMENT_COLUMNS,
    LEAVE_PAYROLL_IMPACT_COLUMNS,
    PAYROLL_ADJUSTMENT_COLUMNS,
    PAYROLL_RUN_COLUMNS,
    PAYROLL_RUN_COMPONENT_COLUMNS,
    PAYROLL_RUN_EMPLOYEE_COLUMNS,
    SALARY_COMPONENT_COLUMNS,
    SALARY_STRUCTURE_COLUMNS,
    AttendancePayrollSummaryDataTableView,
    EmployeeSalaryAssignmentDataTableView,
    LeavePayrollImpactDataTableView,
    PayrollAdjustmentDataTableView,
    PayrollRunComponentDataTableView,
    PayrollRunDataTableView,
    PayrollRunEmployeeDataTableView,
    SalaryComponentDataTableView,
    SalaryStructureDataTableView,
)
from ...forms.payroll_form import (
    AttendancePayrollSummaryForm,
    EmployeeSalaryAssignmentForm,
    LeavePayrollImpactForm,
    PayrollAdjustmentForm,
    PayrollRunComponentForm,
    PayrollRunEmployeeForm,
    PayrollRunForm,
    SalaryComponentForm,
    SalaryStructureForm,
)
from ...models import (
    AttendancePayrollSummary,
    EmployeeComponentOverride,
    EmployeeSalaryAssignment,
    LeavePayrollImpact,
    PayrollAdjustment,
    PayrollRun,
    PayrollRunComponent,
    PayrollRunEmployee,
    SalaryComponent,
    SalaryStructure,
    SalaryStructureComponent,
)
from ...services import (
    build_attendance_payroll_inputs,
    build_leave_payroll_inputs,
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


_load_structure_components = build_related_section_loader(STRUCTURE_COMPONENT_RELATION)
_save_structure_components = build_related_section_saver(STRUCTURE_COMPONENT_RELATION)
_load_component_overrides = build_related_section_loader(COMPONENT_OVERRIDE_RELATION)
_save_component_overrides = build_related_section_saver(COMPONENT_OVERRIDE_RELATION)


_salary_component_columns = [
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

_salary_structure_columns = [
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

_employee_salary_assignment_columns = [
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

_payroll_run_columns = [
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

_payroll_run_employee_columns = [
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

_payroll_run_component_columns = [
    {"name": "payroll_run_employee", "title": "Payroll Employee"},
    {"name": "salary_component", "title": "Component"},
    {"name": "source_type", "title": "Source"},
    {"name": "sequence", "title": "Sequence"},
    {"name": "quantity", "title": "Quantity"},
    {"name": "rate", "title": "Rate"},
    {"name": "amount", "title": "Amount"},
    {"name": "created_at", "title": "Recorded At"},
]

_attendance_payroll_summary_columns = [
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

_leave_payroll_impact_columns = [
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

_payroll_adjustment_columns = [
    {"name": "payroll_run", "title": "Payroll Run"},
    {"name": "employee", "title": "Employee"},
    {"name": "salary_component", "title": "Component"},
    {"name": "adjustment_type", "title": "Adjustment Type"},
    {"name": "amount", "title": "Amount"},
    {"name": "reason", "title": "Business Reason"},
    {"name": "updated_at", "title": "Updated At"},
]


def _process_payroll_action(request, payroll_run: PayrollRun):
    process_payroll_run(payroll_run=payroll_run, acting_user=request.user)
    return {"message": "Payroll run processed successfully."}


def _reset_payroll_action(request, payroll_run: PayrollRun):
    reset_payroll_run(payroll_run=payroll_run)
    return {"message": "Payroll run reset to draft successfully."}


def _build_attendance_inputs_action(request, payroll_run: PayrollRun):
    count = build_attendance_payroll_inputs(payroll_run=payroll_run)
    return {"message": f"Attendance payroll inputs rebuilt for {count} employee record(s)."}


def _build_leave_inputs_action(request, payroll_run: PayrollRun):
    count = build_leave_payroll_inputs(payroll_run=payroll_run)
    return {"message": f"Leave payroll impacts rebuilt for {count} leave record(s)."}


register_entity(
    EntityConfig(
        name="salary_component",
        url_path="salary-components",
        verbose_name="Salary Component",
        model=SalaryComponent,
        form_class=SalaryComponentForm,
        datatable_view=SalaryComponentDataTableView,
        fields=[
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 3, "placeholder": "BASIC"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 5, "placeholder": "Basic Salary"},
            {"name": "sequence", "label": "Sequence", "type": "number", "required": True, "col": 2},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 2},
            {"name": "component_type", "label": "Component Type", "type": "static_select", "required": True, "col": 4, "options": SalaryComponent._meta.get_field("component_type").choices},
            {"name": "value_type", "label": "Value Type", "type": "static_select", "required": True, "col": 4, "options": SalaryComponent._meta.get_field("value_type").choices},
            {"name": "tax_treatment", "label": "Tax Treatment", "type": "static_select", "required": True, "col": 4, "options": SalaryComponent._meta.get_field("tax_treatment").choices},
            {"name": "affects_gross", "label": "Affects Gross", "type": "checkbox", "required": False, "col": 4},
            {"name": "affects_net", "label": "Affects Net", "type": "checkbox", "required": False, "col": 4},
            {"name": "is_statutory", "label": "Statutory", "type": "checkbox", "required": False, "col": 4},
            {"name": "formula_expression", "label": "Formula Expression", "type": "textarea", "required": False, "col": 12, "placeholder": "Example: BASIC * 0.10 or GROSS * 0.40"},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "Optional implementation notes or compliance notes."},
        ],
        datatable_columns=_salary_component_columns,
        reset_defaults={
            "sequence": 1,
            "is_active": True,
            "affects_gross": True,
            "affects_net": True,
        },
    )
)


register_entity(
    EntityConfig(
        name="payroll_run",
        url_path="payroll-runs",
        verbose_name="Payroll Run",
        model=PayrollRun,
        form_class=PayrollRunForm,
        datatable_view=PayrollRunDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "required": False, "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "currency", "label": "Currency", "type": "select", "required": False, "col": 4, "url_name": "currency_select"},
            {"name": "name", "label": "Run Name", "type": "text", "required": True, "col": 4, "placeholder": "March 2026 Monthly Payroll"},
            {"name": "payroll_year", "label": "Payroll Year", "type": "number", "required": True, "col": 2},
            {"name": "payroll_month", "label": "Payroll Month", "type": "number", "required": True, "col": 2, "attributes": {"min": "1", "max": "12"}},
            {"name": "period_start", "label": "Period Start", "type": "date", "required": True, "col": 2},
            {"name": "period_end", "label": "Period End", "type": "date", "required": True, "col": 2},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "Optional run note, cutoff note, or approval comment."},
        ],
        row_actions={
            "build_attendance_inputs": _build_attendance_inputs_action,
            "build_leave_inputs": _build_leave_inputs_action,
            "process": _process_payroll_action,
            "reset_run": _reset_payroll_action,
        },
        action_state_field="status",
        hide_edit_on_values=["approved", "locked"],
        hide_delete_on_values=["processed", "reviewed", "approved", "locked"],
        action_buttons=[
            {
                "action_name": "build_attendance_inputs",
                "title": "Build Attendance Inputs",
                "label": "",
                "icon_class": "fas fa-clipboard-list",
                "class_name": "btn-outline-primary",
                "confirm_text": "Rebuild attendance payroll inputs for this payroll run?",
                "success_message": "Attendance payroll inputs rebuilt successfully.",
                "hide_on_values": ["approved", "locked"],
            },
            {
                "action_name": "build_leave_inputs",
                "title": "Build Leave Inputs",
                "label": "",
                "icon_class": "fas fa-calendar-minus",
                "class_name": "btn-outline-info",
                "confirm_text": "Rebuild leave payroll impacts for this payroll run?",
                "success_message": "Leave payroll impacts rebuilt successfully.",
                "hide_on_values": ["approved", "locked"],
            },
            {
                "action_name": "process",
                "title": "Process Payroll",
                "label": "",
                "icon_class": "fas fa-play",
                "class_name": "btn-outline-success",
                "confirm_text": "Process this payroll run now?",
                "success_message": "Payroll run processed successfully.",
                "hide_on_values": ["approved", "locked"],
            },
            {
                "action_name": "reset_run",
                "title": "Reset To Draft",
                "label": "",
                "icon_class": "fas fa-undo",
                "class_name": "btn-outline-warning",
                "confirm_text": "Reset this payroll run to draft and remove processed rows?",
                "success_message": "Payroll run reset to draft successfully.",
                "hide_on_values": ["draft", "approved", "locked"],
            },
        ],
        datatable_columns=_payroll_run_columns,
        reset_defaults={
            "payroll_year": timezone.localdate().year,
            "payroll_month": timezone.localdate().month,
            "period_start": timezone.localdate().replace(day=1).isoformat(),
            "period_end": timezone.localdate().isoformat(),
        },
        select_search_fields=["name", "status"],
    )
)


register_entity(
    EntityConfig(
        name="payroll_run_employee",
        url_path="payroll-run-employees",
        verbose_name="Payroll Run Employee",
        model=PayrollRunEmployee,
        form_class=PayrollRunEmployeeForm,
        datatable_view=PayrollRunEmployeeDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 6, "url_name": "payroll_run_select"},
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "employee_salary_assignment", "label": "Salary Assignment", "type": "select", "required": True, "col": 6, "url_name": "employee_salary_assignment_select"},
            {"name": "salary_structure_name", "label": "Salary Structure", "type": "text", "required": False, "col": 6},
            {"name": "gross_salary", "label": "Gross Salary", "type": "number", "required": False, "col": 4},
            {"name": "gross_earnings", "label": "Gross Earnings", "type": "number", "required": False, "col": 4},
            {"name": "total_deductions", "label": "Total Deductions", "type": "number", "required": False, "col": 4},
            {"name": "employer_contributions", "label": "Employer Contributions", "type": "number", "required": False, "col": 4},
            {"name": "taxable_income", "label": "Taxable Income", "type": "number", "required": False, "col": 4},
            {"name": "income_tax", "label": "Income Tax", "type": "number", "required": False, "col": 4},
            {"name": "net_salary", "label": "Net Salary", "type": "number", "required": False, "col": 4},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 4, "options": PayrollRunEmployee._meta.get_field("status").choices},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=_payroll_run_employee_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "payroll_run__name",
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "status",
        ],
    )
)


register_entity(
    EntityConfig(
        name="attendance_payroll_summary",
        url_path="attendance-payroll-summaries",
        verbose_name="Attendance Payroll Summary",
        model=AttendancePayrollSummary,
        form_class=AttendancePayrollSummaryForm,
        datatable_view=AttendancePayrollSummaryDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 6, "url_name": "payroll_run_select"},
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "present_days", "label": "Present Days", "type": "number", "required": False, "col": 3},
            {"name": "absent_days", "label": "Absent Days", "type": "number", "required": False, "col": 3},
            {"name": "half_days", "label": "Half Days", "type": "number", "required": False, "col": 3},
            {"name": "leave_days", "label": "Leave Days", "type": "number", "required": False, "col": 3},
            {"name": "payable_days", "label": "Payable Days", "type": "number", "required": False, "col": 4},
            {"name": "overtime_hours", "label": "Overtime Hours", "type": "number", "required": False, "col": 4},
            {"name": "late_instances", "label": "Late Instances", "type": "number", "required": False, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=_attendance_payroll_summary_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "payroll_run__name",
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
        ],
    )
)


register_entity(
    EntityConfig(
        name="leave_payroll_impact",
        url_path="leave-payroll-impacts",
        verbose_name="Leave Payroll Impact",
        model=LeavePayrollImpact,
        form_class=LeavePayrollImpactForm,
        datatable_view=LeavePayrollImpactDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 4, "url_name": "payroll_run_select"},
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 4, "url_name": "employee_select"},
            {"name": "leave_request", "label": "Leave Request", "type": "select", "required": False, "col": 4, "url_name": "leave_request_select"},
            {"name": "leave_type", "label": "Leave Type", "type": "select", "required": True, "col": 4, "url_name": "leave_type_select"},
            {"name": "days", "label": "Days", "type": "number", "required": False, "col": 3},
            {"name": "is_paid", "label": "Paid Leave", "type": "checkbox", "required": False, "col": 2},
            {"name": "deduction_amount", "label": "Deduction Amount", "type": "number", "required": False, "col": 3},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=_leave_payroll_impact_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "payroll_run__name",
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "leave_type__name",
        ],
    )
)


register_entity(
    EntityConfig(
        name="payroll_adjustment",
        url_path="payroll-adjustments",
        verbose_name="Payroll Adjustment",
        model=PayrollAdjustment,
        form_class=PayrollAdjustmentForm,
        datatable_view=PayrollAdjustmentDataTableView,
        fields=[
            {"name": "payroll_run", "label": "Payroll Run", "type": "select", "required": True, "col": 4, "url_name": "payroll_run_select"},
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 4, "url_name": "employee_select"},
            {"name": "salary_component", "label": "Salary Component", "type": "select", "required": False, "col": 4, "url_name": "salary_component_select"},
            {"name": "adjustment_type", "label": "Adjustment Type", "type": "static_select", "required": True, "col": 4, "options": PayrollAdjustment._meta.get_field("adjustment_type").choices},
            {"name": "amount", "label": "Amount", "type": "number", "required": True, "col": 4, "attributes": {"step": "0.01"}},
            {"name": "reason", "label": "Business Reason", "type": "textarea", "required": True, "col": 12, "placeholder": "Bonus, correction, arrear, reimbursement, or payroll recovery note."},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=_payroll_adjustment_columns,
        reset_defaults={},
        select_search_fields=[
            "payroll_run__name",
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "salary_component__name",
            "adjustment_type",
        ],
    )
)


register_entity(
    EntityConfig(
        name="payroll_run_component",
        url_path="payroll-run-components",
        verbose_name="Payroll Run Component",
        model=PayrollRunComponent,
        form_class=PayrollRunComponentForm,
        datatable_view=PayrollRunComponentDataTableView,
        fields=[
            {"name": "payroll_run_employee", "label": "Payroll Employee", "type": "select", "required": True, "col": 6, "url_name": "payroll_run_employee_select"},
            {"name": "salary_component", "label": "Salary Component", "type": "select", "required": True, "col": 6, "url_name": "salary_component_select"},
            {"name": "source_type", "label": "Source Type", "type": "static_select", "required": True, "col": 3, "options": PayrollRunComponent._meta.get_field("source_type").choices},
            {"name": "sequence", "label": "Sequence", "type": "number", "required": True, "col": 3},
            {"name": "quantity", "label": "Quantity", "type": "number", "required": False, "col": 3},
            {"name": "rate", "label": "Rate", "type": "number", "required": False, "col": 3},
            {"name": "amount", "label": "Amount", "type": "number", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=_payroll_run_component_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
        select_search_fields=[
            "payroll_run_employee__payroll_run__name",
            "payroll_run_employee__employee__employee_id",
            "salary_component__code",
            "salary_component__name",
        ],
    )
)


register_entity(
    EntityConfig(
        name="salary_structure",
        url_path="salary-structures",
        verbose_name="Salary Structure",
        model=SalaryStructure,
        form_class=SalaryStructureForm,
        datatable_view=SalaryStructureDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "required": False, "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "currency", "label": "Currency", "type": "select", "required": False, "col": 4, "url_name": "currency_select"},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 3, "placeholder": "SAL-STD-01"},
            {"name": "name", "label": "Structure Name", "type": "text", "required": True, "col": 5, "placeholder": "Monthly Staff Structure"},
            {"name": "effective_from", "label": "Effective From", "type": "date", "required": True, "col": 2},
            {"name": "effective_to", "label": "Effective To", "type": "date", "required": False, "col": 2},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12, "placeholder": "Describe which employees or salary policy this structure is meant for."},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 8, "placeholder": "Optional implementation note or approval note."},
        ],
        dynamic_sections={"structure_components": STRUCTURE_COMPONENT_SECTION},
        dynamic_sections_loader=_load_structure_components,
        dynamic_sections_saver=_save_structure_components,
        datatable_columns=_salary_structure_columns,
        reset_defaults={"effective_from": timezone.localdate().isoformat(), "is_active": True},
    )
)


register_entity(
    EntityConfig(
        name="employee_salary_assignment",
        url_path="employee-salary-assignments",
        verbose_name="Employee Salary Assignment",
        model=EmployeeSalaryAssignment,
        form_class=EmployeeSalaryAssignmentForm,
        datatable_view=EmployeeSalaryAssignmentDataTableView,
        fields=[
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "salary_structure", "label": "Salary Structure", "type": "select", "required": True, "col": 6, "url_name": "salary_structure_select"},
            {"name": "gross_salary", "label": "Gross Salary", "type": "number", "required": True, "col": 4, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "annual_ctc", "label": "Annual CTC", "type": "number", "required": False, "col": 4, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "payment_frequency", "label": "Payment Frequency", "type": "static_select", "required": True, "col": 4, "options": EmployeeSalaryAssignment._meta.get_field("payment_frequency").choices},
            {"name": "effective_from", "label": "Effective From", "type": "date", "required": True, "col": 4},
            {"name": "effective_to", "label": "Effective To", "type": "date", "required": False, "col": 4},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "Optional approval note, adjustment reason, or assignment context."},
        ],
        dynamic_sections={"component_overrides": COMPONENT_OVERRIDE_SECTION},
        dynamic_sections_loader=_load_component_overrides,
        dynamic_sections_saver=_save_component_overrides,
        datatable_columns=_employee_salary_assignment_columns,
        reset_defaults={
            "payment_frequency": "monthly",
            "effective_from": timezone.localdate().isoformat(),
            "is_active": True,
        },
        select_search_fields=[
            "employee__employee_id",
            "employee__user__first_name",
            "employee__user__last_name",
            "salary_structure__name",
            "salary_structure__code",
        ],
    )
)
