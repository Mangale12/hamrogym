from core.datatables.views import BaseDataTableView

from ..models import TaxGroup


TAX_GROUP_COLUMNS = [
    ("code", "code"),
    ("name", "name"),
    ("application_scope", lambda obj: obj.get_application_scope_display()),
    ("is_default", "is_default"),
    ("is_active", "is_active"),
    ("id", "id"),
]


class TaxGroupDataTableView(BaseDataTableView):
    model = TaxGroup
    columns = TAX_GROUP_COLUMNS
    searchable_columns = [
        "code",
        "name",
        "application_scope",
        "remarks",
    ]
    orderable_columns = [
        "code",
        "name",
        "application_scope",
        "is_default",
        "is_active",
        "id",
    ]

