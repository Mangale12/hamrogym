from core.datatables.views import BaseDataTableView

from ..models import Client


CLIENT_COLUMNS = [
    ("id", "id"),
    ("business_name", "business_name"),
    ("client_code", "client_code"),
    ("contact_email", "contact_email"),
    ("contact_phone", "contact_phone"),
    ("plan", lambda obj: obj.get_plan_display()),
    ("status", lambda obj: obj.get_status_display()),
    ("registered_on", "registered_on"),
]


class ClientDataTableView(BaseDataTableView):
    model = Client
    columns = CLIENT_COLUMNS
    
    def get_queryset(self):
        # Fetch only necessary fields for better performance
        return self.model.objects.only(
            "id", "business_name", "client_code", "contact_email", 
            "contact_phone", "plan", "status", "registered_on"
        )
    
    searchable_columns = [
        "business_name",
        "client_code",
        "contact_email",
        "contact_phone",
        "plan",
        "status",
    ]
    orderable_columns = [
        "id",
        "business_name",
        "client_code",
        "contact_email",
        "contact_phone",
        "plan",
        "status",
        "registered_on",
    ]
