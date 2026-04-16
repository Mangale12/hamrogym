from core.datatables.views import BaseDataTableView

from ..models import ChartOfAccount


LEDGER_COLUMNS = [
    ("id", "id"),
    ("code", "code"),
    ("name", "name"),
    ("parent", lambda obj: obj.parent.name if obj.parent_id else ""),
    ("account_type", lambda obj: obj.get_account_type_display()),
    ("pan_no", lambda obj: getattr(getattr(obj, "ledger_profile", None), "pan_no", "")),
    ("vat_no", lambda obj: getattr(getattr(obj, "ledger_profile", None), "vat_no", "")),
    ("contact_person", lambda obj: getattr(getattr(obj, "ledger_profile", None), "contact_person", "")),
    ("mobile_no", lambda obj: getattr(getattr(obj, "ledger_profile", None), "mobile_no", "")),
    ("is_active", "is_active"),
]


class LedgerDataTableView(BaseDataTableView):
    model = ChartOfAccount
    columns = LEDGER_COLUMNS
    searchable_columns = [
        "code",
        "name",
        "parent__name",
        "account_type",
        "ledger_profile__pan_no",
        "ledger_profile__vat_no",
        "ledger_profile__contact_person",
        "ledger_profile__mobile_no",
        "remarks",
    ]
    orderable_columns = [
        "code",
        "name",
        "parent__name",
        "account_type",
        "ledger_profile__pan_no",
        "ledger_profile__vat_no",
        "ledger_profile__contact_person",
        "ledger_profile__mobile_no",
        "is_active",
    ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_ledger=True)
            .select_related("parent", "organization", "branch", "fiscal_year", "ledger_profile")
            .order_by("code", "sort_order", "id")
        )
