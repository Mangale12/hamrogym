from core.datatables.views import BaseDataTableView
from ..models import ErpEntity


ERP_ENTITY_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("module", "module"),
    ("app_label", "app_label"),
    ("model_name", "model_name"),
    ("remarks", "remarks"),
    ("is_active", "is_active"),
]


class ErpEntityDataTableView(BaseDataTableView):
    model = ErpEntity
    columns = ERP_ENTITY_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "module",
        "app_label",
        "model_name",
        "remarks",
        "is_active",
    ]
    orderable_columns = [
        "name",
        "code",
        "module",
        "app_label",
        "model_name",
        "remarks",
        "is_active",
    ]
