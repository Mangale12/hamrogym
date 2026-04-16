from core.datatables.views import BaseDataTableView

from ..models import JournalEntry


JOURNAL_ENTRY_COLUMNS = [
    ("id", "id"),
    ("entry_no", "entry_no"),
    ("date", lambda obj: obj.date.strftime("%Y-%m-%d") if obj.date else ""),
    ("voucher_type", lambda obj: obj.voucher_type.name if obj.voucher_type_id else ""),
    ("reference_no", "reference_no"),
    ("total_debit", "total_debit"),
    ("total_credit", "total_credit"),
    ("status", lambda obj: obj.get_status_display()),
]


class JournalEntryDataTableView(BaseDataTableView):
    model = JournalEntry
    columns = JOURNAL_ENTRY_COLUMNS
    searchable_columns = [
        "entry_no",
        "voucher_type__name",
        "voucher_type__code",
        "reference_no",
        "narration",
        "status",
        "remarks",
    ]
    orderable_columns = [
        "entry_no",
        "date",
        "voucher_type__name",
        "reference_no",
        "total_debit",
        "total_credit",
        "status",
    ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("voucher_type", "organization", "branch", "fiscal_year", "created_by")
            .order_by("-date", "-id")
        )
