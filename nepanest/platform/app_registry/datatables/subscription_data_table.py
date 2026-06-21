from core.datatables.views import BaseDataTableView

from ..models import Subscription


SUBSCRIPTION_COLUMNS = [
    ("id", "id"),
    ("client", lambda obj: str(obj.client) if obj.client else ""),
    ("plan_name", "plan_name"),
    ("amount", "amount"),
    ("interval", "interval"),
    ("status", "status"),
    ("period_start", "period_start"),
    ("period_end", "period_end"),
]


class SubscriptionDataTableView(BaseDataTableView):
    model = Subscription
    columns = SUBSCRIPTION_COLUMNS

    def get_queryset(self):
        # Use select_related for ForeignKey to avoid N+1 queries
        # Use only() to fetch only necessary fields for better performance
        return self.model.objects.select_related("client").only(
            "id", "plan_name", "amount", "interval", "status", 
            "period_start", "period_end",
            "client__id", "client__business_name", "client__client_code"
        )

    searchable_columns = [
        "client__business_name",
        "client__client_code",
        "plan_name",
        "interval",
        "status",
    ]
    orderable_columns = [
        "id",
        "client__business_name",  # Changed from "client" to avoid ambiguity
        "plan_name",
        "amount",
        "interval",
        "status",
        "period_start",
        "period_end",
    ]
