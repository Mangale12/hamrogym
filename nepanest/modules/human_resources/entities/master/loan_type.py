from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)
from core.choices import INTEREST_TYPE_CHOICES
from nepanest.modules.loans.datatables import LOAN_TYPE_COLUMNS, LoanTypeDataTableView
from nepanest.modules.loans.forms import LoanTypeForm
from nepanest.modules.loans.models import LoanPolicy, LoanType


LOAN_TYPE_POLICY = {
    "title": "Loan Policies",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "employment_type", "label": "Employment Type", "type": "select", "required": True, "col": 6, "url_name": "employeement_type_select"},
        {"name": "max_eligible_amount", "label": "Max Eligible Amount", "type": "number", "required": True, "col": 6},
        {"name": "max_installment_amount", "label": "Max Installment Amount", "type": "number", "required": True, "col": 6},
        {"name": "max_tenure_months", "label": "Max Tenure (Months)", "type": "number", "required": True, "col": 6},
        {"name": "min_tenure_months", "label": "Min Tenure (Months)", "type": "number", "required": True, "col": 6},
        {"name": "interest_rate", "label": "Interest Rate Override", "type": "number", "required": False, "col": 6},
        {"name": "grace_period_days", "label": "Grace Period", "type": "number", "required": True, "col": 6},
        {"name": "min_credit_score", "label": "Min Credit Score", "type": "number", "required": False, "col": 6},
        {"name": "max_loan_percentage_of_salary", "label": "Max Loan Percentage of Salary", "type": "number", "required": False, "col": 6},
        {"name": "max_emi_percentage_of_salary", "label": "Max EMI Percentage of Salary", "type": "number", "required": False, "col": 6},
        {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
        {"name": "priority", "label": "Priority", "type": "number", "required": False, "col": 6},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12}
    ]
}

LOAN_TYPE_POLICY_RELATION = RelatedDynamicSectionConfig(
    section_name="loan_type_policy",
    related_model=LoanPolicy,
    parent_field="loan_type",
    fields=[
        "employment_type",
        "max_eligible_amount",
        "max_installment_amount",
        "max_tenure_months",
        "min_tenure_months",
        "interest_rate",
        "grace_period_days",
        "min_credit_score",
        "max_loan_percentage_of_salary",
        "max_emi_percentage_of_salary",
        "is_active",
        "priority",
        "remarks"
    ],
    required_fields=[
        "employment_type",
        "max_eligible_amount",
        "max_installment_amount",
        "max_tenure_months",
        "min_tenure_months",
        "grace_period_days",
    ],
    bool_fields=[
        "is_active"
    ],
    empty_check_fields=[
        "employment_type",
        "max_eligible_amount",
        "max_installment_amount",
        "max_tenure_months",
        "min_tenure_months",
        "interest_rate",
        "grace_period_days",
        "min_credit_score",
        "max_loan_percentage_of_salary",
        "max_emi_percentage_of_salary",
        "priority",
        "remarks"
    ],
    order_by="priority",
    save_transformers={
        "remarks": lambda value: (value or "").strip(),
    },
)

_save_loan_type_policy = build_related_section_saver(LOAN_TYPE_POLICY_RELATION)
_load_loan_type_policy = build_related_section_loader(LOAN_TYPE_POLICY_RELATION)

register_entity(
    EntityConfig(
        name="loan_type",
        url_path="loan-types",
        verbose_name="Loan Type",
        model=LoanType,
        form_class=LoanTypeForm,
        datatable_view=LoanTypeDataTableView,
        fields=[
            # TODO: define fields
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 6},
            {"name": "interest_type", "label": "Interest Type", "type": "static_select", "required": True, "col": 6, "options": INTEREST_TYPE_CHOICES},
            {"name": "default_interest_rate", "label": "Default Interest Rate", "type": "number", "required": True, "col": 6},
            {"name": "max_loan_amount", "label": "Max Loan Amount", "type": "number", "required": True, "col": 6},
            {"name": "max_tenure_months", "label": "Max Tenure (Months)", "type": "number", "required": True, "col": 6},
            {"name": "min_tenure_months", "label": "Min Tenure (Months)", "type": "number", "required": True, "col": 6},
            {"name": "requires_approval", "label": "Requires Approval", "type": "checkbox", "required": False, "col": 6},
            {"name": "requires_guarantor", "label": "Requires Guarantor", "type": "checkbox", "required": False, "col": 6},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 6},
        ],
        dynamic_sections={
            "loan_type_policy": LOAN_TYPE_POLICY,
        },
        dynamic_sections_saver=_save_loan_type_policy,
        dynamic_sections_loader=_load_loan_type_policy,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in LOAN_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "requires_approval": True,
            "requires_guarantor": False,
            "is_active": True,
        },
        select_search_fields=["name", "code", "interest_type"],
    )
)
