from core.datatables.views import BaseDataTableView
from ..models import Brand


BRAND_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class BrandDataTableView(BaseDataTableView):
    model = Brand
    columns = BRAND_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "remarks",
    ]
    orderable_columns = [
        "id",
        "name",
        "code",
        "is_active",
        "remarks",
    ]
