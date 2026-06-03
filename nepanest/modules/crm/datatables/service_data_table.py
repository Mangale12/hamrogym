from core.datatables.views import BaseDataTableView
from ..models import Service


SERVICE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("service_type__name", "service_type.name"),
    ("default_price", "default_price"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
    # TODO: add columns
]


class ServiceDataTableView(BaseDataTableView):
    model = Service
    columns = SERVICE_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "service_type__name",
        "default_price",
        "is_active",
        "remarks",
        # TODO: add searchable fields
    ]
    orderable_columns = [
        "name",
        "code",
        "service_type__name",
        "default_price",
        "is_active",
        "remarks",
    ]
