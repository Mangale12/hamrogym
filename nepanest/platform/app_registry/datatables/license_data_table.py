from django.db.models import Prefetch
from core.datatables.views import BaseDataTableView

from ..models import License, LicenseRenewHistory


LICENSE_COLUMNS = [
    ("id", "id"),
    ("client", lambda obj: str(obj.client) if obj.client else ""),
    ("plan", lambda obj: obj.get_plan_display()),
    ("issued_on", "issued_on"),
    ("expires_on", "expires_on"),
    ("max_users", "max_users"),
    ("max_branches", "max_branches"),
    ("grace_days", "grace_days"),
    ("is_current", "is_current"),
]


LICENSE_HISTORY_COLUMNS = [
    ("id", "id"),
    ("license", lambda obj: str(obj.license) if obj.license else ""),
    ("old_expiry", "old_expiry"),
    ("new_expiry", "new_expiry"),
    ("renewed_by", "renewed_by"),
    ("renewed_at", "renewed_at"),
    ("notes", "notes"),
]


class LicenseDataTableView(BaseDataTableView):
    model = License
    columns = LICENSE_COLUMNS

    def get_queryset(self):
        # Use select_related for ForeignKey to avoid N+1 queries
        # Use only() to fetch only necessary fields for better performance
        return self.model.objects.select_related("client").only(
            "id", "plan", "issued_on", "expires_on", "max_users", 
            "max_branches", "grace_days", "is_current", "client__id", 
            "client__business_name", "client__client_code"
        )
    
    searchable_columns = [
        "client__business_name",
        "client__client_code",
        "plan",
    ]
    orderable_columns = [
        "id",
        "client__business_name",  # Changed from "client" to avoid ambiguity
        "plan",
        "issued_on",
        "expires_on",
        "max_users",
        "max_branches",
        "grace_days",
        "is_current",
    ]


class LicenseRenewHistoryDataTableView(BaseDataTableView):
    model = LicenseRenewHistory
    columns = LICENSE_HISTORY_COLUMNS

    def get_queryset(self):
        # Use select_related for ForeignKey relationships to avoid N+1 queries
        # Fetch only necessary fields for better performance
        return self.model.objects.select_related("license", "license__client").only(
            "id", "old_expiry", "new_expiry", "renewed_by", "renewed_at", "notes",
            "license__id", "license__plan", "license__expires_on",
            "license__client__id", "license__client__business_name", 
            "license__client__client_code"
        )
    
    searchable_columns = [
        "license__client__business_name",
        "license__client__client_code",
        "old_expiry",
        "new_expiry",
        "renewed_by",
        "notes",
    ]
    orderable_columns = [
        "id",
        "license__client__business_name",  # Changed from "license"
        "old_expiry",
        "new_expiry",
        "renewed_by",
        "renewed_at",
        "notes",
    ]


LicenseHistoryDataTableView = LicenseRenewHistoryDataTableView
