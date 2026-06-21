from core.datatables.views import BaseDataTableView

from ..models import TenantDB


TENANT_DB_COLUMNS = [
    ("id", "id"),
    ("client", lambda obj: str(obj.client) if obj.client else ""),
    ("db_name", "db_name"),
    ("db_user", "db_user"),
    ("db_host", "db_host"),
    ("db_port", "db_port"),
    ("status", lambda obj: obj.get_status_display()),
]


class TenantDBDataTableView(BaseDataTableView):
    model = TenantDB
    columns = TENANT_DB_COLUMNS
    
    def get_queryset(self):
        # Use select_related for ForeignKey to avoid N+1 queries
        # Use only() to fetch only necessary fields for better performance
        return self.model.objects.select_related("client").only(
            "id", "db_name", "db_user", "db_host", "db_port", "status",
            "client__id", "client__business_name", "client__client_code"
        )
    
    searchable_columns = [
        "client__business_name",
        "client__client_code",
        "db_name",
        "db_user",
        "db_host",
        "db_port",
        "status",
    ]
    orderable_columns = [
        "id",
        "client__business_name",  # Changed from "client" to avoid ambiguity
        "db_name",
        "db_user",
        "db_host",
        "db_port",
        "status",
    ]
