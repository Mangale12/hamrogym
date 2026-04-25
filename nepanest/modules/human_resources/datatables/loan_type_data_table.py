from core.datatables.views import BaseDataTableView
from nepanest.modules.loans.models import LoanType


LOAN_TYPE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("interest_type", "interest_type"),
    ("default_interest_rate", "default_interest_rate"),
    ("max_loan_amount", "max_loan_amount"),
    ("max_tenure_months", "max_tenure_months"),
    ("min_tenure_months", "min_tenure_months"),
    ("requires_approval", "requires_approval"),
    ("requires_guarantor", "requires_guarantor"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class LoanTypeDataTableView(BaseDataTableView):
    model = LoanType
    columns = LOAN_TYPE_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "interest_type",
        "default_interest_rate",
        "max_loan_amount",
        "max_tenure_months",
        "min_tenure_months",
        "requires_approval",
        "requires_guarantor",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "code",
        "interest_type",
        "default_interest_rate",
        "max_loan_amount",
        "max_tenure_months",
        "min_tenure_months",
        "requires_approval",
        "requires_guarantor",
        "is_active",
        "remarks",
    ]
