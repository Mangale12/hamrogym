from core.datatables.views import BaseDataTableView
from ..models import ApprovalEntity


APPROVAL_ENTITIES_COLUMNS = [
    ("id", "id"),
    ("erp_entity", "erp_entity.name"),
    ("name", "name"),
    ("code", "code"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class ApprovalEntityDataTableView(BaseDataTableView):
    model = ApprovalEntity
    columns = APPROVAL_ENTITIES_COLUMNS
    searchable_columns = [
        "erp_entity__name",
        "name",
        "code",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "erp_entity__name",
        "name",
        "code",
        "is_active",
        "remarks",
    ]
