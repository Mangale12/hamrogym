from core.datatables.views import BaseDataTableView
from ..models import BillingDocument


BILLING_DOCUMENT_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class BillingDocumentDataTableView(BaseDataTableView):
    model = BillingDocument
    columns = BILLING_DOCUMENT_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
