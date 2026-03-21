from core.datatables.views import BaseDataTableView
from core.models import OrganizationSettings


class OrganizationSettingsDataTableView(BaseDataTableView):
    model = OrganizationSettings
    columns = [
        ("id", "id"),
        ("name", "name"),
        ("registration_number", "registration_number"),
        ("phone", "phone"),
        ("email", "email"),
        ("calendar", "calendar"),
    ]
    searchable_columns = ["name", "registration_number", "phone", "email", "contact_person"]
    orderable_columns = ["name", "registration_number", "phone", "email", "calendar"]
