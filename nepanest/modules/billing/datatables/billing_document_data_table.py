from core.datatables.views import BaseDataTableView
from ..models import BillingDocument


BILLING_DOCUMENT_COLUMNS = [
    ("id", "id"),
    ("document_number", "document_number"),
    ("document_type", lambda obj: obj.get_document_type_display()),
    ("status", lambda obj: obj.get_status_display()),
    ("billing_profile", lambda obj: getattr(obj.billing_profile, "name", "")),
    ("source_type", lambda obj: obj.get_source_type_display()),
    ("document_date", "document_date"),
    ("due_date", "due_date"),
    ("currency", lambda obj: getattr(obj.currency, "code", "")),
    ("total_amount", "total_amount"),
    ("paid_amount", "paid_amount"),
    ("due_amount", "due_amount"),
]


class BillingDocumentDataTableView(BaseDataTableView):
    model = BillingDocument
    columns = BILLING_DOCUMENT_COLUMNS
    searchable_columns = [
        "document_number",
        "document_type",
        "status",
        "billing_profile__name",
        "source_type",
        "currency__code",
        "terms_conditions",
    ]
    orderable_columns = [
        "document_number",
        "document_type",
        "status",
        "billing_profile__name",
        "source_type",
        "document_date",
        "due_date",
        "currency__code",
        "total_amount",
        "paid_amount",
        "due_amount",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("billing_profile", "currency")
