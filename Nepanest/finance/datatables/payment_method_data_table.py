from core.datatables.views import BaseDataTableView

from ..models import PaymentMethod


PAYMENT_METHOD_COLUMNS = [
    ("code", "code"),
    ("name", "name"),
    ("category", lambda obj: obj.get_category_display()),
    ("provider", "provider"),
    ("sequence", "sequence"),
    ("is_digital", "is_digital"),
    ("supports_online", "supports_online"),
    ("supports_qr", "supports_qr"),
    ("requires_reference", "requires_reference"),
    ("is_default", "is_default"),
    ("is_active", "is_active"),
    ("id", "id"),
]


class PaymentMethodDataTableView(BaseDataTableView):
    model = PaymentMethod
    columns = PAYMENT_METHOD_COLUMNS
    searchable_columns = [
        "code",
        "name",
        "category",
        "provider",
        "remarks",
    ]
    orderable_columns = [
        "code",
        "name",
        "category",
        "provider",
        "sequence",
        "is_digital",
        "supports_online",
        "supports_qr",
        "requires_reference",
        "is_default",
        "is_active",
        "id",
    ]
