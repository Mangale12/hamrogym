from core.datatables.views import BaseDataTableView

from ..models import TaxGroupItem


TAX_GROUP_ITEM_COLUMNS = [
    ("tax_group", "tax_group.name"),
    ("tax", "tax.name"),
    ("sequence", "sequence"),
    ("override_rate", "override_rate"),
    ("is_compound", "is_compound"),
    ("is_active", "is_active"),
    ("id", "id"),
]


class TaxGroupItemDataTableView(BaseDataTableView):
    model = TaxGroupItem
    columns = TAX_GROUP_ITEM_COLUMNS
    searchable_columns = [
        "tax_group__code",
        "tax_group__name",
        "tax__code",
        "tax__name",
        "remarks",
    ]
    orderable_columns = [
        "tax_group__name",
        "tax__name",
        "sequence",
        "override_rate",
        "is_compound",
        "is_active",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related("tax_group", "tax")

