from core.datatables.views import BaseDataTableView

from ..models import VoucherType


VOUCHER_TYPE_COLUMNS = [
    ("id", "id"),
    ("code", "code"),
    ("name", "name"),
    ("category", lambda obj: obj.get_category_display()),
    ("nature", lambda obj: obj.get_nature_display()),
    ("affects_cash", "affects_cash"),
    ("affects_bank", "affects_bank"),
    ("auto_numbering", "auto_numbering"),
    ("prefix", "prefix"),
    ("last_number", "last_number"),
    ("requires_reference", "requires_reference"),
    ("requires_approval", "requires_approval"),
    ("allow_negative", "allow_negative"),
    ("is_system_generated", "is_system_generated"),
    ("is_active", "is_active"),
]


class VoucherTypeDataTableView(BaseDataTableView):
    model = VoucherType
    columns = VOUCHER_TYPE_COLUMNS
    searchable_columns = [
        "code",
        "name",
        "category",
        "nature",
        "description",
    ]
    orderable_columns = [
        "code",
        "name",
        "category",
        "nature",
        "affects_cash",
        "affects_bank",
        "auto_numbering",
        "prefix",
        "last_number",
        "requires_reference",
        "requires_approval",
        "allow_negative",
        "is_system_generated",
        "is_active",
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("organization", "branch").order_by("name", "id")
