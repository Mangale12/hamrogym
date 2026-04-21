from core.datatables.views import BaseDataTableView

from ..models import CreditTransaction


CREDIT_TRANSACTION_COLUMNS = [
    ("transaction_date", "transaction_date"),
    ("party", lambda obj: str(obj.party)),
    ("document_type", lambda obj: obj.get_document_type_display()),
    ("document_id", "document_id"),
    ("debit", "debit"),
    ("credit", "credit"),
    ("balance_after", "balance_after"),
    ("is_system_generated", "is_system_generated"),
    ("created_at", "created_at"),
    ("id", "id"),
]


class CreditTransactionDataTableView(BaseDataTableView):
    model = CreditTransaction
    columns = CREDIT_TRANSACTION_COLUMNS
    searchable_columns = [
        "party__name",
        "party__display_name",
        "document_type",
        "document_id",
        "remarks",
    ]
    orderable_columns = [
        "transaction_date",
        "party__name",
        "document_type",
        "document_id",
        "debit",
        "credit",
        "balance_after",
        "is_system_generated",
        "created_at",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("party", "branch", "fiscal_year")

