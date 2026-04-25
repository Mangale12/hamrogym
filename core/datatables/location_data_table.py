from core.datatables.views import BaseDataTableView
from nepanest.foundation.geography import Location


LOCATION_COLUMNS = [
    ("name", "name"),
    ("location_type", "location_type.name"),
    ("code", "code"),
    ("is_active", "is_active"),
    ("id", "id"),
]


class LocationDataTableView(BaseDataTableView):
    model = Location
    columns = LOCATION_COLUMNS
    searchable_columns = ["name", "code", "location_type__name"]
    orderable_columns = ["name", "location_type__name", "code", "is_active", "id"]
