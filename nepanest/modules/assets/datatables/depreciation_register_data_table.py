from core.datatables.views import BaseDataTableView
from nepanest.common.helpers.context import get_current_branch_id, get_current_fiscal_year_id

from ..models import AssetDepreciationRegister
from ..services import parse_schedule_month_value


ASSET_DEPRECIATION_REGISTER_COLUMNS = [
    ("id", "id"),
    ("asset", "asset.name"),
    ("schedule_month", "schedule_month"),
    ("period_start", "period_start"),
    ("period_end", "period_end"),
    ("depreciation_amount", "depreciation_amount"),
    ("opening_book_value", "opening_book_value"),
    ("closing_book_value", "closing_book_value"),
    ("status", "status"),
    ("journal_entry", "journal_entry.entry_no"),
]


class AssetDepreciationRegisterDataTableView(BaseDataTableView):
    model = AssetDepreciationRegister
    columns = ASSET_DEPRECIATION_REGISTER_COLUMNS
    searchable_columns = [
        "asset__name",
        "asset__code",
        "status",
        "journal_entry__entry_no",
        "remarks",
    ]
    orderable_columns = [
        "asset__name",
        "schedule_month",
        "period_start",
        "period_end",
        "depreciation_amount",
        "opening_book_value",
        "closing_book_value",
        "status",
        "journal_entry__entry_no",
    ]

    def get_queryset(self):
        queryset = self.model.objects.select_related(
            "asset",
            "branch",
            "fiscal_year",
            "journal_entry",
        )

        branch_id = get_current_branch_id(self.request)
        fiscal_year_id = get_current_fiscal_year_id(self.request)
        schedule_month = (self.request.GET.get("schedule_month") or "").strip()
        posting_status = (self.request.GET.get("posting_status") or "").strip()

        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        if fiscal_year_id:
            queryset = queryset.filter(fiscal_year_id=fiscal_year_id)
        if schedule_month:
            try:
                queryset = queryset.filter(schedule_month=parse_schedule_month_value(schedule_month))
            except Exception:
                queryset = queryset.none()
        if posting_status in {
            AssetDepreciationRegister.STATUS_UNPOSTED,
            AssetDepreciationRegister.STATUS_POSTED,
        }:
            queryset = queryset.filter(status=posting_status)

        return queryset
