from core.datatables.views import BaseDataTableView
from ..models import ApprovalEntity


APPROVAL_ENTITY_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class ApprovalEntityDataTableView(BaseDataTableView):
    model = ApprovalEntity
    columns = APPROVAL_ENTITY_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]
