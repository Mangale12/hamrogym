from core.datatables.views import BaseDataTableView
from ..models import employeement_type


EMPLOYEEMENT_TYPE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class employeement_typeDataTableView(BaseDataTableView):
    model = employeement_type
    columns = EMPLOYEEMENT_TYPE_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "code",
        "is_active",
        "remarks",
    ]

    def filter_queryset(self, queryset, search_value):
        if search_value:
            return queryset.filter(name__istartswith=search_value)
        return queryset
