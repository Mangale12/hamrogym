from core.datatables.views import BaseDataTableView

from ..models import Payment


PAYMENT_COLUMNS = [
    ("payment_no", "payment_no"),
    ("date", "date"),
    ("payment_type", lambda obj: obj.get_payment_type_display()),
    ("party", lambda obj: getattr(obj.party, "name", "")),
    ("billing_profile", lambda obj: getattr(obj.billing_profile, "name", "")),
    ("payment_method", lambda obj: getattr(obj.payment_method, "name", "")),
    ("currency", lambda obj: getattr(obj.currency, "code", "")),
    ("amount", "amount"),
    ("allocated_amount", "allocated_amount"),
    ("unapplied_amount", "unapplied_amount"),
    ("status", lambda obj: obj.get_status_display()),
    ("reference", "reference"),
    ("journal_entry", lambda obj: getattr(obj.journal_entry, "entry_no", "")),
    ("id", "id"),
]


class PaymentDataTableView(BaseDataTableView):
    model = Payment
    columns = PAYMENT_COLUMNS
    searchable_columns = [
        "payment_no",
        "reference",
        "party__name",
        "party__display_name",
        "billing_profile__name",
        "payment_method__name",
        "currency__code",
        "journal_entry__entry_no",
        "remarks",
    ]
    orderable_columns = [
        "payment_no",
        "date",
        "payment_type",
        "party__name",
        "billing_profile__name",
        "payment_method__name",
        "currency__code",
        "amount",
        "allocated_amount",
        "unapplied_amount",
        "status",
        "reference",
        "journal_entry__entry_no",
        "id",
    ]

    def get_queryset(self):
        return self.model.objects.select_related(
            "party",
            "billing_profile",
            "payment_method",
            "currency",
            "journal_entry",
        )

